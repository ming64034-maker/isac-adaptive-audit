from __future__ import annotations

import math

import numpy as np
import torch

from config import Config
from model import HistoryEncoder, OneStepPredictor, WorldModel
from planner import RolloutPlanner
from utils import HistoryBuffer, angle_difference


class ReactivePolicy:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.last_diagnostics: dict[str, float] = {}

    def reset(self, initial_obs: np.ndarray, env) -> None:
        self.last_diagnostics = {}
        return None

    def select_action(self, obs: np.ndarray, env) -> int:
        coarse_angle = math.atan2(float(obs[2]), float(obs[3]))
        action = env.nearest_beam(coarse_angle)
        self.last_diagnostics = {
            "policy_confidence": 1.0,
            "policy_margin": 0.0,
            "reactive_angle": float(coarse_angle),
        }
        return action

    def observe(self, action: int, next_obs: np.ndarray) -> None:
        return None

    def get_diagnostics(self) -> dict[str, float]:
        return dict(self.last_diagnostics)


class OraclePolicy:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.last_diagnostics: dict[str, float] = {}

    def reset(self, initial_obs: np.ndarray, env) -> None:
        self.last_diagnostics = {}
        return None

    def select_action(self, obs: np.ndarray, env) -> int:
        action = env.oracle_action()
        self.last_diagnostics = {
            "policy_confidence": 1.0,
            "policy_margin": 0.0,
        }
        return action

    def observe(self, action: int, next_obs: np.ndarray) -> None:
        return None

    def get_diagnostics(self) -> dict[str, float]:
        return dict(self.last_diagnostics)


class OneStepPredictivePolicy:
    def __init__(self, cfg: Config, predictor: OneStepPredictor, device: str = "cpu") -> None:
        self.cfg = cfg
        self.predictor = predictor.to(device)
        self.predictor.eval()
        self.device = device
        self.buffer: HistoryBuffer | None = None
        self.last_diagnostics: dict[str, float] = {}

    def reset(self, initial_obs: np.ndarray, env) -> None:
        self.buffer = HistoryBuffer(self.cfg.history_length, self.cfg.observation_dim, env.prev_beam)
        self.buffer.reset(initial_obs, env.prev_beam)
        self.last_diagnostics = {}

    @torch.no_grad()
    def select_action(self, obs: np.ndarray, env) -> int:
        assert self.buffer is not None
        obs_seq, action_seq = self.buffer.get_window(self.cfg.history_length)
        obs_tensor = torch.tensor(obs_seq, dtype=torch.float32, device=self.device).unsqueeze(0)
        action_tensor = torch.tensor(action_seq, dtype=torch.long, device=self.device).unsqueeze(0)
        logits = self.predictor(obs_tensor, action_tensor)
        probabilities = torch.softmax(logits, dim=-1)[0]
        values, indices = torch.topk(probabilities, k=min(2, probabilities.numel()))
        action = int(indices[0].item())
        margin = float((values[0] - values[1]).item()) if values.numel() > 1 else float(values[0].item())
        entropy = float((-(probabilities * torch.log(probabilities.clamp_min(1e-8))).sum()).item())
        self.last_diagnostics = {
            "policy_confidence": float(values[0].item()),
            "policy_margin": margin,
            "policy_entropy": entropy,
        }
        return action

    def observe(self, action: int, next_obs: np.ndarray) -> None:
        assert self.buffer is not None
        self.buffer.append(action, next_obs)

    def get_diagnostics(self) -> dict[str, float]:
        return dict(self.last_diagnostics)


class ProposedV2Policy:
    """LoS guard with predictive fallback for dynamic blockage events."""

    def __init__(
        self,
        cfg: Config,
        predictor: OneStepPredictor,
        encoder: HistoryEncoder | str | None = None,
        world_model: WorldModel | None = None,
        device: str = "cpu",
    ) -> None:
        if isinstance(encoder, str) and world_model is None and device == "cpu":
            device = encoder
            encoder = None
        self.cfg = cfg
        self.predictor = predictor.to(device)
        self.predictor.eval()
        self.encoder = encoder.to(device) if encoder is not None else None
        if self.encoder is not None:
            self.encoder.eval()
        self.world_model = world_model.to(device) if world_model is not None else None
        if self.world_model is not None:
            self.world_model.eval()
        self.device = device
        self.buffer: HistoryBuffer | None = None
        self.last_diagnostics: dict[str, float] = {}
        self.prev_risk_score: float = 0.0
        self.fallback_cooldown: int = 0
        self.difficulty_ema: float = 0.5
        self.risk_delta_ema: float = 0.0

    def reset(self, initial_obs: np.ndarray, env) -> None:
        self.buffer = HistoryBuffer(self.cfg.history_length, self.cfg.observation_dim, env.prev_beam)
        self.buffer.reset(initial_obs, env.prev_beam)
        self.last_diagnostics = {}
        self.prev_risk_score = 0.0
        self.fallback_cooldown = 0
        self.difficulty_ema = 0.5
        self.risk_delta_ema = 0.0

    def _risk_score(self, obs: np.ndarray) -> float:
        blocker_indicator = float(obs[4])
        last_outage = float(obs[5])
        reflection_ratio = float(obs[6])
        path_spread = float(obs[7])
        return max(
            blocker_indicator,
            last_outage,
            0.85 * reflection_ratio,
            0.90 * path_spread,
        )

    @staticmethod
    def _lerp(easy: float, hard: float, hardness: float) -> float:
        return float(easy + (hard - easy) * hardness)

    def _adaptive_profile(self, obs: np.ndarray, risk_score: float, risk_delta: float) -> dict[str, float]:
        if not self.cfg.proposedv2_use_adaptive_difficulty:
            return {
                "difficulty": 0.5,
                "difficulty_ema": 0.5,
                "los_confidence_threshold": float(self.cfg.los_confidence_threshold),
                "risk_threshold": float(self.cfg.risk_threshold),
                "path_spread_threshold": float(self.cfg.path_spread_threshold),
                "reflection_threshold": float(self.cfg.rollout_shortlist_reflection_threshold),
                "global_pool_risk_threshold": float(self.cfg.proposedv2_global_pool_risk_threshold),
                "cooldown_steps": float(self.cfg.proposedv2_fallback_cooldown_steps),
                "local_candidate_count": float(self.cfg.proposedv2_local_candidate_count),
                "global_topk_count": float(self.cfg.proposedv2_global_topk_count),
                "risk_spike_threshold": float(self.cfg.proposedv2_risk_spike_threshold),
                "reactive_override_gap": float(self.cfg.proposedv2_reactive_override_gap),
                "reactive_distance_penalty": float(self.cfg.proposedv2_reactive_distance_penalty),
                "switch_penalty": float(self.cfg.proposedv2_switch_penalty),
                "predictive_weight_scale": 1.0,
                "reactive_bonus_scale": 1.0,
                "predictor_mix_delta": 0.0,
                "reward_weight_delta": 0.0,
                "safety_bonus_scale": 1.0,
                "outage_penalty_scale": 1.0,
            }

        blocker_indicator = float(obs[4])
        last_outage = float(obs[5])
        reflection_ratio = float(obs[6])
        path_spread = float(obs[7])
        snr_norm = float(obs[0])
        cooldown_pressure = float(
            np.clip(
                self.fallback_cooldown / max(float(self.cfg.proposedv2_hard_fallback_cooldown_steps), 1.0),
                0.0,
                1.0,
            )
        )
        snr_stress = float(np.clip((0.62 - snr_norm) / 0.42, 0.0, 1.0))
        spike = float(
            np.clip(
                max(0.0, risk_delta) / max(float(self.cfg.proposedv2_risk_spike_threshold), 1e-6),
                0.0,
                1.0,
            )
        )
        instant_difficulty = float(
            np.clip(
                0.30 * blocker_indicator
                + 0.18 * reflection_ratio
                + 0.16 * path_spread
                + 0.18 * snr_stress
                + 0.10 * last_outage
                + 0.06 * spike
                + 0.02 * cooldown_pressure,
                0.0,
                1.0,
            )
        )
        instant_difficulty = max(instant_difficulty, float(np.clip(0.82 * risk_score, 0.0, 1.0)))
        alpha = float(np.clip(self.cfg.proposedv2_difficulty_ema_alpha, 0.05, 1.0))
        self.difficulty_ema = (1.0 - alpha) * self.difficulty_ema + alpha * instant_difficulty
        self.risk_delta_ema = (1.0 - alpha) * self.risk_delta_ema + alpha * abs(risk_delta)
        delta_pressure = float(
            np.clip(
                self.risk_delta_ema / max(float(self.cfg.proposedv2_risk_spike_threshold), 1e-6),
                0.0,
                1.0,
            )
        )
        hardness = float(
            np.clip(
                0.62 * self.difficulty_ema
                + 0.23 * instant_difficulty
                + 0.15 * delta_pressure,
                0.0,
                1.0,
            )
        )
        if risk_score >= float(self.cfg.risk_threshold):
            normalized_risk = float(
                np.clip(
                    (risk_score - float(self.cfg.risk_threshold))
                    / max(1.0 - float(self.cfg.risk_threshold), 1e-6),
                    0.0,
                    1.0,
                )
            )
            hardness = max(hardness, 0.45 + 0.35 * normalized_risk)
        if last_outage > 0.0:
            hardness = max(hardness, 0.72)
        if (
            blocker_indicator >= float(self.cfg.risk_threshold)
            and reflection_ratio >= float(self.cfg.rollout_shortlist_reflection_threshold)
        ):
            hardness = max(hardness, 0.68)

        return {
            "difficulty": hardness,
            "difficulty_ema": float(self.difficulty_ema),
            "los_confidence_threshold": self._lerp(
                self.cfg.proposedv2_easy_los_confidence_threshold,
                self.cfg.proposedv2_hard_los_confidence_threshold,
                hardness,
            ),
            "risk_threshold": self._lerp(
                self.cfg.proposedv2_easy_risk_threshold,
                self.cfg.proposedv2_hard_risk_threshold,
                hardness,
            ),
            "path_spread_threshold": self._lerp(
                self.cfg.proposedv2_easy_path_spread_threshold,
                self.cfg.proposedv2_hard_path_spread_threshold,
                hardness,
            ),
            "reflection_threshold": self._lerp(
                self.cfg.proposedv2_easy_reflection_threshold,
                self.cfg.proposedv2_hard_reflection_threshold,
                hardness,
            ),
            "global_pool_risk_threshold": self._lerp(
                self.cfg.proposedv2_easy_global_pool_risk_threshold,
                self.cfg.proposedv2_hard_global_pool_risk_threshold,
                hardness,
            ),
            "cooldown_steps": float(
                round(
                    self._lerp(
                        float(self.cfg.proposedv2_easy_fallback_cooldown_steps),
                        float(self.cfg.proposedv2_hard_fallback_cooldown_steps),
                        hardness,
                    )
                )
            ),
            "local_candidate_count": float(
                round(
                    self._lerp(
                        float(self.cfg.proposedv2_easy_local_candidate_count),
                        float(self.cfg.proposedv2_hard_local_candidate_count),
                        hardness,
                    )
                )
            ),
            "global_topk_count": float(
                round(
                    self._lerp(
                        float(self.cfg.proposedv2_easy_global_topk_count),
                        float(self.cfg.proposedv2_hard_global_topk_count),
                        hardness,
                    )
                )
            ),
            "risk_spike_threshold": self._lerp(
                1.10 * float(self.cfg.proposedv2_risk_spike_threshold),
                0.80 * float(self.cfg.proposedv2_risk_spike_threshold),
                hardness,
            ),
            "reactive_override_gap": self._lerp(
                self.cfg.proposedv2_easy_reactive_override_gap,
                self.cfg.proposedv2_hard_reactive_override_gap,
                hardness,
            ),
            "reactive_distance_penalty": self._lerp(
                self.cfg.proposedv2_easy_reactive_distance_penalty,
                self.cfg.proposedv2_hard_reactive_distance_penalty,
                hardness,
            ),
            "switch_penalty": self._lerp(
                self.cfg.proposedv2_easy_switch_penalty,
                self.cfg.proposedv2_hard_switch_penalty,
                hardness,
            ),
            "predictive_weight_scale": self._lerp(
                self.cfg.proposedv2_easy_predictive_weight_scale,
                self.cfg.proposedv2_hard_predictive_weight_scale,
                hardness,
            ),
            "reactive_bonus_scale": self._lerp(1.05, 0.92, hardness),
            "predictor_mix_delta": self._lerp(-0.06, 0.08, hardness),
            "reward_weight_delta": self._lerp(-0.02, 0.10, hardness),
            "safety_bonus_scale": self._lerp(0.95, 1.22, hardness),
            "outage_penalty_scale": self._lerp(0.95, 1.18, hardness),
        }

    def _fallback_state(self, obs: np.ndarray) -> tuple[bool, float, float, dict[str, float]]:
        los_confidence = 1.0 - float(obs[4])
        risk_score = self._risk_score(obs)
        risk_delta = risk_score - self.prev_risk_score
        profile = self._adaptive_profile(obs, risk_score, risk_delta)
        hard_trigger = (
            los_confidence < profile["los_confidence_threshold"]
            or float(obs[4]) >= profile["risk_threshold"]
            or float(obs[6]) >= profile["reflection_threshold"]
            or float(obs[7]) >= profile["path_spread_threshold"]
            or float(obs[5]) > 0.0
            or risk_delta >= profile["risk_spike_threshold"]
        )
        if hard_trigger:
            self.fallback_cooldown = max(0, int(profile["cooldown_steps"]))
        use_fallback = hard_trigger or self.fallback_cooldown > 0
        if use_fallback and self.fallback_cooldown > 0:
            self.fallback_cooldown -= 1
        self.prev_risk_score = risk_score
        return use_fallback, risk_score, risk_delta, profile

    def _scene_mode(
        self,
        obs: np.ndarray,
        risk_score: float,
        risk_threshold: float | None = None,
        reflection_threshold: float | None = None,
        path_spread_threshold: float | None = None,
        global_pool_risk_threshold: float | None = None,
    ) -> str:
        blockage_indicator = float(obs[4])
        last_outage = float(obs[5])
        reflection_ratio = float(obs[6])
        path_spread = float(obs[7])
        effective_risk_threshold = float(self.cfg.risk_threshold if risk_threshold is None else risk_threshold)
        effective_reflection_threshold = float(
            self.cfg.rollout_shortlist_reflection_threshold
            if reflection_threshold is None
            else reflection_threshold
        )
        effective_path_spread_threshold = float(
            self.cfg.path_spread_threshold if path_spread_threshold is None else path_spread_threshold
        )
        effective_global_pool_threshold = float(
            self.cfg.proposedv2_global_pool_risk_threshold
            if global_pool_risk_threshold is None
            else global_pool_risk_threshold
        )
        reflection_active = reflection_ratio >= effective_reflection_threshold
        blockage_active = (
            blockage_indicator >= effective_risk_threshold
            or last_outage > 0.0
            or path_spread >= effective_path_spread_threshold
            or risk_score >= effective_global_pool_threshold
        )
        if reflection_active and blockage_active:
            return "mixed"
        if reflection_active:
            return "reflection"
        if blockage_active:
            return "blockage"
        return "normal"

    def _predictor_outputs(self) -> dict[str, torch.Tensor]:
        assert self.buffer is not None
        obs_seq, action_seq = self.buffer.get_window(self.cfg.history_length)
        obs_tensor = torch.tensor(obs_seq, dtype=torch.float32, device=self.device).unsqueeze(0)
        action_tensor = torch.tensor(action_seq, dtype=torch.long, device=self.device).unsqueeze(0)
        outputs = self.predictor.predict_outputs(obs_tensor, action_tensor)
        logits = outputs["logits"][0]
        return {
            "probabilities": torch.softmax(logits, dim=-1),
            "rate_logits": outputs["rate"][0],
            "outage_probs": torch.sigmoid(outputs["outage_logit"][0]),
        }

    def _candidate_actions(
        self,
        obs: np.ndarray,
        env,
        probabilities: torch.Tensor,
        risk_score: float,
        reactive_action: int,
        profile: dict[str, float],
    ) -> tuple[list[int], bool, int, int]:
        local_count = min(int(profile["local_candidate_count"]), self.cfg.codebook_size)
        global_topk = min(int(profile["global_topk_count"]), self.cfg.codebook_size)
        blockage_active = bool(
            float(obs[4]) >= profile["risk_threshold"]
            or float(obs[7]) >= 0.85 * profile["path_spread_threshold"]
            or risk_score >= max(profile["risk_threshold"], 0.75 * profile["global_pool_risk_threshold"])
        )
        if blockage_active:
            local_count = min(local_count + 2, self.cfg.codebook_size)
            global_topk = min(global_topk + 2, self.cfg.codebook_size)
        local_candidates = env.candidate_actions_from_observation(obs, local_count)
        use_global_pool = bool(
            float(obs[5]) > 0.0
            or float(obs[6]) >= profile["reflection_threshold"]
            or blockage_active
            or risk_score >= profile["global_pool_risk_threshold"]
        )
        global_candidates = (
            torch.topk(probabilities, k=global_topk).indices.tolist()
            if use_global_pool and global_topk > 0
            else []
        )
        candidate_actions = list(
            dict.fromkeys(
                local_candidates
                + [int(action) for action in global_candidates]
                + [int(env.prev_beam), int(reactive_action)]
            )
        )
        return [int(action) for action in candidate_actions], use_global_pool, len(local_candidates), len(global_candidates)

    def _candidate_expert_maps(
        self,
        candidate_actions: list[int],
        predictor_outputs: dict[str, torch.Tensor],
        reward_scores: dict[int, float],
        scene_mode: str,
        profile: dict[str, float],
    ) -> tuple[dict[int, float], dict[int, float], dict[int, float], dict[int, float], float, float]:
        candidate_tensor = torch.tensor(candidate_actions, dtype=torch.long, device=self.device)
        temp = max(float(self.cfg.proposedv2_predictor_utility_temperature), 1e-6)
        rate_logits = predictor_outputs["rate_logits"].gather(0, candidate_tensor)
        outage_probs = predictor_outputs["outage_probs"].gather(0, candidate_tensor)
        rate_scores = torch.softmax(rate_logits / temp, dim=0)
        safety_scores = torch.softmax((1.0 - outage_probs) / temp, dim=0)

        reward_weight = float(np.clip(self.cfg.proposedv2_reward_rerank_weight, 0.0, 0.9))
        if reward_scores and reward_weight <= 0.0:
            reward_weight = {
                "normal": 0.10,
                "blockage": 0.18,
                "reflection": 0.30,
                "mixed": 0.24,
            }[scene_mode]
        reward_weight = float(np.clip(reward_weight + profile["reward_weight_delta"], 0.0, 0.9))

        predictor_mix = float(np.clip(self.cfg.proposedv2_predictor_utility_weight, 0.0, 1.0))
        predictor_mix = {
            "normal": min(0.80, predictor_mix + 0.10),
            "blockage": predictor_mix,
            "reflection": max(0.35, predictor_mix - 0.20),
            "mixed": max(0.45, predictor_mix - 0.10),
        }[scene_mode]
        predictor_mix = float(np.clip(predictor_mix + profile["predictor_mix_delta"], 0.25, 0.90))

        rate_map = {
            int(action): float(score.item())
            for action, score in zip(candidate_actions, rate_scores)
        }
        outage_map = {
            int(action): float(score.item())
            for action, score in zip(candidate_actions, outage_probs)
        }
        safety_map = {
            int(action): float(score.item())
            for action, score in zip(candidate_actions, safety_scores)
        }
        utility_map: dict[int, float] = {}
        for action in candidate_actions:
            action = int(action)
            predictive_signal = float(predictor_outputs["probabilities"][action].item())
            base_signal = predictor_mix * predictive_signal + (1.0 - predictor_mix) * rate_map[action]
            reward_signal = reward_scores.get(action, base_signal)
            utility_map[action] = (1.0 - reward_weight) * base_signal + reward_weight * reward_signal
        return utility_map, rate_map, outage_map, safety_map, reward_weight, predictor_mix

    def _reward_rerank_scores(self, candidate_actions: list[int]) -> tuple[dict[int, float], float, float]:
        if self.encoder is None or self.world_model is None or self.buffer is None or not candidate_actions:
            return {}, float("nan"), float("nan")

        obs_seq, action_seq = self.buffer.get_window(self.cfg.history_length)
        obs_tensor = torch.tensor(obs_seq, dtype=torch.float32, device=self.device).unsqueeze(0)
        action_tensor = torch.tensor(action_seq, dtype=torch.long, device=self.device).unsqueeze(0)
        latent = self.encoder(obs_tensor, action_tensor)[0]
        candidate_tensor = torch.tensor(candidate_actions, dtype=torch.long, device=self.device)
        repeated_latent = latent.unsqueeze(0).expand(candidate_tensor.size(0), -1)
        reward_pred = self.world_model.predict_stats(repeated_latent, candidate_tensor)["reward"]
        temperature = max(float(self.cfg.proposedv2_reward_rerank_temperature), 1e-6)
        reward_scores = torch.softmax(reward_pred / temperature, dim=0)
        reward_gap = (
            float((reward_pred.max() - reward_pred.min()).item())
            if reward_pred.numel() > 1
            else float(reward_pred[0].item())
        )
        return (
            {
                int(action): float(score.item())
                for action, score in zip(candidate_actions, reward_scores)
            },
            float(reward_pred.max().item()),
            reward_gap,
        )

    def _adaptive_diagnostics(self, profile: dict[str, float]) -> dict[str, float]:
        return {
            "planner_adaptive_difficulty": float(profile["difficulty"]),
            "planner_adaptive_difficulty_ema": float(profile["difficulty_ema"]),
            "planner_adaptive_los_threshold": float(profile["los_confidence_threshold"]),
            "planner_adaptive_risk_threshold": float(profile["risk_threshold"]),
            "planner_adaptive_path_threshold": float(profile["path_spread_threshold"]),
            "planner_adaptive_reflection_threshold": float(profile["reflection_threshold"]),
            "planner_adaptive_global_pool_threshold": float(profile["global_pool_risk_threshold"]),
            "planner_adaptive_cooldown": float(profile["cooldown_steps"]),
            "planner_adaptive_local_candidates": float(profile["local_candidate_count"]),
            "planner_adaptive_global_topk": float(profile["global_topk_count"]),
        }

    def _select_fallback_action(
        self,
        obs: np.ndarray,
        env,
        predictor_outputs: dict[str, torch.Tensor],
        risk_score: float,
        profile: dict[str, float],
    ) -> tuple[int, dict[str, float]]:
        probabilities = predictor_outputs["probabilities"]
        coarse_angle = math.atan2(float(obs[2]), float(obs[3]))
        reactive_action = env.nearest_beam(coarse_angle)
        candidate_actions, use_global_pool, local_size, global_size = self._candidate_actions(
            obs,
            env,
            probabilities,
            risk_score,
            reactive_action,
            profile,
        )
        reward_scores, reward_peak, reward_gap = self._reward_rerank_scores(candidate_actions)
        scene_mode = self._scene_mode(
            obs,
            risk_score,
            risk_threshold=profile["risk_threshold"],
            reflection_threshold=profile["reflection_threshold"],
            path_spread_threshold=profile["path_spread_threshold"],
            global_pool_risk_threshold=profile["global_pool_risk_threshold"],
        )
        utility_map, rate_map, outage_map, safety_map, reward_rerank_weight, predictor_mix = self._candidate_expert_maps(
            candidate_actions,
            predictor_outputs,
            reward_scores,
            scene_mode,
            profile,
        )
        predictive_weight = float(
            np.clip(
                self.cfg.proposedv2_min_predictive_weight
                + (
                    self.cfg.proposedv2_max_predictive_weight
                    - self.cfg.proposedv2_min_predictive_weight
                )
                * risk_score,
                self.cfg.proposedv2_min_predictive_weight,
                self.cfg.proposedv2_max_predictive_weight,
            )
        )
        predictive_weight = float(
            np.clip(
                predictive_weight * profile["predictive_weight_scale"],
                self.cfg.proposedv2_min_predictive_weight * 0.85,
                self.cfg.proposedv2_max_predictive_weight,
            )
        )
        local_weight = 1.0 - predictive_weight

        values, indices = torch.topk(probabilities, k=min(2, probabilities.numel()))
        top_confidence = float(values[0].item())
        margin = float((values[0] - values[1]).item()) if values.numel() > 1 else top_confidence
        uncertainty = float(np.clip(1.0 - top_confidence, 0.0, 1.0))
        switch_penalty = float(profile["switch_penalty"] * max(0.0, 1.0 - risk_score))
        reactive_bonus = float(self.cfg.proposedv2_reactive_bonus * profile["reactive_bonus_scale"])
        safety_bonus = {
            "normal": 0.04,
            "blockage": 0.12,
            "reflection": 0.06,
            "mixed": 0.09,
        }[scene_mode] * float(profile["safety_bonus_scale"])
        outage_penalty_scale = {
            "normal": 0.55,
            "blockage": 1.00,
            "reflection": 0.65,
            "mixed": 0.85,
        }[scene_mode] * float(profile["outage_penalty_scale"])

        score_by_action: dict[int, float] = {}
        scored_candidates: list[tuple[float, int]] = []
        total_actions = max(1, self.cfg.codebook_size)
        for action in candidate_actions:
            action = int(action)
            angle_affinity = max(
                0.0,
                1.0 - angle_difference(float(env.beam_angles[action]), coarse_angle) / math.pi,
            )
            beam_gap = abs(action - int(env.prev_beam))
            circular_gap = min(beam_gap, total_actions - beam_gap)
            prev_affinity = max(0.0, 1.0 - circular_gap / max(1.0, total_actions / 2.0))
            reactive_gap = abs(action - int(reactive_action))
            reactive_circular_gap = min(reactive_gap, total_actions - reactive_gap)
            reactive_affinity = max(0.0, 1.0 - reactive_circular_gap / max(1.0, total_actions / 2.0))
            utility_signal = utility_map[action]
            score = (
                predictive_weight * utility_signal
                + local_weight * angle_affinity
                + float(self.cfg.proposedv2_prev_beam_bonus) * uncertainty * prev_affinity
                + reactive_bonus * reactive_affinity
                + safety_bonus * safety_map[action]
            )
            score -= float(outage_penalty_scale * outage_map[action])
            if action != int(env.prev_beam):
                score -= switch_penalty
            if action != int(reactive_action):
                score -= (
                    float(profile["reactive_distance_penalty"])
                    * (1.0 - reactive_affinity)
                    * max(0.35, 1.0 - risk_score)
                )
            score_by_action[action] = score
            scored_candidates.append((score, action))

        scored_candidates.sort(reverse=True)
        chosen_score, chosen_action = scored_candidates[0]
        reactive_score = score_by_action[int(reactive_action)]
        if int(chosen_action) != int(reactive_action):
            required_advantage = float(profile["reactive_override_gap"]) * max(0.5, 1.2 - risk_score)
            if chosen_score < reactive_score + required_advantage:
                chosen_action = int(reactive_action)
                chosen_score = reactive_score
        rate_regret = max(0.0, rate_map[int(reactive_action)] - rate_map[int(chosen_action)])
        safety_gain = max(0.0, outage_map[int(reactive_action)] - outage_map[int(chosen_action)])
        veto_scale = {
            "normal": 0.90,
            "blockage": 1.30,
            "reflection": 0.70,
            "mixed": 0.85,
        }[scene_mode]
        min_safety_gain = {
            "normal": 0.020,
            "blockage": 0.035,
            "reflection": 0.012,
            "mixed": 0.020,
        }[scene_mode]
        veto_triggered = False
        if int(chosen_action) != int(reactive_action):
            regret_budget = float(profile["reactive_override_gap"] * veto_scale)
            if rate_regret > regret_budget and safety_gain < min_safety_gain:
                chosen_action = int(reactive_action)
                chosen_score = reactive_score
                veto_triggered = True
        rate_veto_triggered = False
        if (
            self.cfg.proposedv2_rate_veto_enabled
            and int(chosen_action) != int(reactive_action)
            and rate_regret > float(self.cfg.proposedv2_rate_regret_threshold)
            and safety_gain < float(self.cfg.proposedv2_min_safety_gain_for_fallback)
        ):
            chosen_action = int(reactive_action)
            chosen_score = reactive_score
            rate_veto_triggered = True
        fallback_kept = 1.0 if int(chosen_action) != int(reactive_action) else 0.0
        score_margin = chosen_score - scored_candidates[1][0] if len(scored_candidates) > 1 else chosen_score
        diagnostics = {
            "policy_confidence": top_confidence,
            "policy_margin": margin,
            "policy_entropy": float((-(probabilities * torch.log(probabilities.clamp_min(1e-8))).sum()).item()),
            "planner_candidates": float(len(candidate_actions)),
            "planner_predictive_weight": predictive_weight,
            "planner_local_weight": local_weight,
            "planner_score_gap": float(score_margin),
            "planner_value": float(reward_peak),
            "planner_terminal_value": float(reward_gap),
            "planner_beam_gain_value": float(reward_rerank_weight),
            "planner_predictor_mix": float(predictor_mix),
            "planner_rate_signal": float(rate_map[int(chosen_action)]),
            "planner_outage_signal": float(outage_map[int(chosen_action)]),
            "planner_reactive_rate_regret": float(rate_regret),
            "planner_reactive_safety_gain": float(safety_gain),
            "planner_reactive_veto_triggered": 1.0 if veto_triggered else 0.0,
            "planner_rate_veto_triggered": 1.0 if rate_veto_triggered else 0.0,
            "planner_rate_regret": float(rate_regret),
            "planner_safety_gain": float(safety_gain),
            "planner_fallback_kept_after_veto": float(fallback_kept),
            "planner_los_guard_used": 0.0,
            "planner_predictive_fallback_used": 1.0,
            "shortlist_used_global_pool": 1.0 if use_global_pool else 0.0,
            "shortlist_size": float(len(candidate_actions)),
            "shortlist_local_size": float(local_size),
            "shortlist_global_fallback_count": float(global_size),
        }
        diagnostics.update(self._adaptive_diagnostics(profile))
        return int(chosen_action), diagnostics

    @torch.no_grad()
    def select_action(self, obs: np.ndarray, env) -> int:
        assert self.buffer is not None
        use_fallback, risk_score, risk_delta, profile = self._fallback_state(obs)
        if not use_fallback:
            coarse_angle = math.atan2(float(obs[2]), float(obs[3]))
            action = env.nearest_beam(coarse_angle)
            self.last_diagnostics = {
                "policy_confidence": 1.0,
                "policy_margin": 0.0,
                "policy_entropy": 0.0,
                "planner_candidates": float(min(int(self.cfg.proposedv2_local_candidate_count), self.cfg.codebook_size)),
                "planner_predictive_weight": 0.0,
                "planner_local_weight": 1.0,
                "planner_score_gap": 0.0,
                "planner_los_guard_used": 1.0,
                "planner_predictive_fallback_used": 0.0,
                "shortlist_used_global_pool": 0.0,
                "planner_risk_score": float(risk_score),
                "planner_risk_delta": float(risk_delta),
                "planner_fallback_cooldown": float(self.fallback_cooldown),
            }
            self.last_diagnostics.update(self._adaptive_diagnostics(profile))
            return int(action)

        predictor_outputs = self._predictor_outputs()
        action, diagnostics = self._select_fallback_action(obs, env, predictor_outputs, risk_score, profile)
        diagnostics["planner_risk_score"] = float(risk_score)
        diagnostics["planner_risk_delta"] = float(risk_delta)
        diagnostics["planner_fallback_cooldown"] = float(self.fallback_cooldown)
        self.last_diagnostics = diagnostics
        return action

    def observe(self, action: int, next_obs: np.ndarray) -> None:
        assert self.buffer is not None
        self.buffer.append(action, next_obs)

    def get_diagnostics(self) -> dict[str, float]:
        return dict(self.last_diagnostics)


class BeliefAwareRolloutPolicy:
    def __init__(
        self,
        cfg: Config,
        encoder: HistoryEncoder,
        world_model: WorldModel,
        device: str = "cpu",
        horizon: int | None = None,
    ) -> None:
        self.cfg = cfg
        self.encoder = encoder.to(device)
        self.world_model = world_model.to(device)
        self.encoder.eval()
        self.world_model.eval()
        self.device = device
        self.horizon = cfg.rollout_horizon if horizon is None else int(horizon)
        self.buffer: HistoryBuffer | None = None
        self.planner = RolloutPlanner(cfg, self.world_model, device=device)
        self.last_diagnostics: dict[str, float] = {}

    def reset(self, initial_obs: np.ndarray, env) -> None:
        self.buffer = HistoryBuffer(self.cfg.history_length, self.cfg.observation_dim, env.prev_beam)
        self.buffer.reset(initial_obs, env.prev_beam)
        self.last_diagnostics = {}

    def _global_fallback_actions(self, env, coarse_angle: float, exclude: list[int], count: int) -> list[int]:
        if count <= 0:
            return []

        total_actions = self.cfg.codebook_size
        excluded = set(int(action) for action in exclude)
        opposite_center = (env.nearest_beam(coarse_angle) + total_actions // 2) % total_actions
        ranked = [opposite_center]

        available = [action for action in range(total_actions) if action not in excluded and action != opposite_center]
        available.sort(
            key=lambda action: angle_difference(float(env.beam_angles[action]), coarse_angle),
            reverse=True,
        )
        ranked.extend(available)

        selected: list[int] = []
        min_gap = max(1, self.cfg.rollout_global_fallback_min_gap)

        def circular_gap(a: int, b: int) -> int:
            raw = abs(int(a) - int(b))
            return min(raw, total_actions - raw)

        for action in ranked:
            if action in excluded or action in selected:
                continue
            if any(circular_gap(action, kept) < min_gap for kept in selected):
                continue
            selected.append(int(action))
            if len(selected) >= count:
                break

        return selected

    def _los_recovery_biases(
        self,
        env,
        obs: np.ndarray,
        candidate_actions: list[int],
        suppress: bool,
    ) -> tuple[dict[int, float], dict[str, float]]:
        if not self.cfg.rollout_use_los_recovery_bias or suppress:
            return {}, {
                "planner_los_recovery_gate": 0.0,
                "planner_los_recovery_bias_max": 0.0,
                "planner_los_recovery_bias_chosen": 0.0,
            }

        coarse_angle = math.atan2(float(obs[2]), float(obs[3]))
        threshold = max(float(self.cfg.rollout_shortlist_blockage_threshold), 1e-6)
        blockage_hint = float(obs[4])
        los_gate = float(np.clip(1.0 - blockage_hint / threshold, 0.0, 1.0))
        if los_gate <= 0.0:
            return {}, {
                "planner_los_recovery_gate": 0.0,
                "planner_los_recovery_bias_max": 0.0,
                "planner_los_recovery_bias_chosen": 0.0,
            }

        biases: dict[int, float] = {}
        for action in candidate_actions:
            angle_error = angle_difference(float(env.beam_angles[int(action)]), coarse_angle)
            angle_affinity = max(0.0, 1.0 - angle_error / math.pi)
            biases[int(action)] = float(self.cfg.rollout_los_recovery_bias * los_gate * angle_affinity)

        return biases, {
            "planner_los_recovery_gate": los_gate,
            "planner_los_recovery_bias_max": max(biases.values()) if biases else 0.0,
            "planner_los_recovery_bias_chosen": 0.0,
        }

    @torch.no_grad()
    def select_action(self, obs: np.ndarray, env) -> int:
        assert self.buffer is not None
        obs_seq, action_seq = self.buffer.get_window(self.cfg.history_length)
        obs_tensor = torch.tensor(obs_seq, dtype=torch.float32, device=self.device).unsqueeze(0)
        action_tensor = torch.tensor(action_seq, dtype=torch.long, device=self.device).unsqueeze(0)
        latent = self.encoder(obs_tensor, action_tensor)[0]
        if self.cfg.rollout_use_auxiliary_shortlist:
            coarse_angle = math.atan2(float(obs[2]), float(obs[3]))
            local_base_candidates = (
                list(range(self.cfg.codebook_size))
                if self.cfg.rollout_shortlist_full_codebook
                else env.candidate_actions_from_observation(obs, self.cfg.rollout_preselect_count)
            )
            use_global_fallback = (
                self.cfg.rollout_shortlist_global_on_demand
                and (
                    float(obs[4]) >= self.cfg.rollout_shortlist_blockage_threshold
                    or float(obs[6]) >= self.cfg.rollout_shortlist_reflection_threshold
                    or float(obs[7]) >= self.cfg.rollout_shortlist_pathspread_threshold
                )
            )
            local_target = self.cfg.rollout_candidate_count
            if use_global_fallback:
                local_target = max(1, self.cfg.rollout_candidate_count - self.cfg.rollout_global_fallback_count)

            shortlist_output = self.planner.shortlist_actions(
                latent,
                local_base_candidates,
                beam_angles=env.beam_angles,
                coarse_angle=coarse_angle,
                blockage_indicator=float(obs[4]),
                reflection_hint=float(obs[6]),
                prev_action=int(env.prev_beam),
                final_k=local_target,
            )
            global_fallback_actions = self._global_fallback_actions(
                env,
                coarse_angle=coarse_angle,
                exclude=shortlist_output.actions,
                count=self.cfg.rollout_global_fallback_count if use_global_fallback else 0,
            )
            candidate_actions = list(dict.fromkeys(shortlist_output.actions + global_fallback_actions))
            if len(candidate_actions) < self.cfg.rollout_candidate_count:
                for action in local_base_candidates:
                    if action not in candidate_actions:
                        candidate_actions.append(int(action))
                    if len(candidate_actions) >= self.cfg.rollout_candidate_count:
                        break

            shortlist_diag = shortlist_output.diagnostics
            shortlist_diag["shortlist_local_size"] = float(len(shortlist_output.actions))
            shortlist_diag["shortlist_global_fallback_count"] = float(len(global_fallback_actions))
            shortlist_diag["shortlist_used_global_pool"] = float(use_global_fallback)
            shortlist_diag["shortlist_base_pool_size"] = float(len(local_base_candidates))
        else:
            use_global_fallback = False
            candidate_actions = env.candidate_actions_from_observation(obs, self.cfg.rollout_candidate_count)
            shortlist_diag = {
                "shortlist_size": float(len(candidate_actions)),
                "shortlist_los_reserved": 0.0,
                "shortlist_reflection_reserved": 0.0,
                "shortlist_prev_beam_kept": float(env.prev_beam in candidate_actions),
                "shortlist_max_los_prob": 0.0,
                "shortlist_max_reflection_prob": 0.0,
                "shortlist_max_beam_gain": 0.0,
                "shortlist_beam_gain_weight": 0.0,
                "shortlist_blockage_hint": float(obs[4]),
                "shortlist_reflection_hint": float(obs[6]),
                "shortlist_local_size": float(len(candidate_actions)),
                "shortlist_global_fallback_count": 0.0,
                "shortlist_used_global_pool": 0.0,
                "shortlist_base_pool_size": float(len(candidate_actions)),
            }

        if self.cfg.rollout_use_los_guard and not use_global_fallback:
            action = env.nearest_beam(math.atan2(float(obs[2]), float(obs[3])))
            action_score_biases, los_recovery_diag = self._los_recovery_biases(
                env,
                obs,
                candidate_actions,
                suppress=False,
            )
            los_recovery_diag["planner_los_recovery_bias_chosen"] = float(action_score_biases.get(int(action), 0.0))
            self.last_diagnostics = {
                "planner_value": np.nan,
                "planner_terminal_value": 0.0,
                "planner_beam_gain_value": np.nan,
                "planner_score_gap": 0.0,
                "planner_score_std": 0.0,
                "planner_candidates": float(len(candidate_actions)),
                "planner_los_guard_used": 1.0,
                "policy_confidence": 1.0,
                "policy_margin": 0.0,
            }
            self.last_diagnostics.update(shortlist_diag)
            self.last_diagnostics.update(los_recovery_diag)
            return int(action)

        action_score_biases, los_recovery_diag = self._los_recovery_biases(
            env,
            obs,
            candidate_actions,
            suppress=bool(shortlist_diag.get("shortlist_used_global_pool", 0.0)),
        )
        planner_output = self.planner.plan(
            latent,
            candidate_actions,
            horizon=self.horizon,
            action_score_biases=action_score_biases,
        )
        sorted_scores = sorted(planner_output.scores.values(), reverse=True)
        planner_gap = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else sorted_scores[0]
        planner_std = float(np.std(sorted_scores)) if sorted_scores else 0.0
        los_recovery_diag["planner_los_recovery_bias_chosen"] = float(
            action_score_biases.get(int(planner_output.action), 0.0)
        )
        self.last_diagnostics = {
            "planner_value": float(planner_output.value),
            "planner_terminal_value": float(planner_output.terminal_value),
            "planner_beam_gain_value": float(planner_output.beam_gain_value),
            "planner_score_gap": float(planner_gap),
            "planner_score_std": planner_std,
            "planner_candidates": float(len(candidate_actions)),
            "planner_los_guard_used": 0.0,
            "policy_confidence": 0.0,
            "policy_margin": float(planner_gap),
        }
        self.last_diagnostics.update(shortlist_diag)
        self.last_diagnostics.update(los_recovery_diag)
        return planner_output.action

    def observe(self, action: int, next_obs: np.ndarray) -> None:
        assert self.buffer is not None
        self.buffer.append(action, next_obs)

    def get_diagnostics(self) -> dict[str, float]:
        return dict(self.last_diagnostics)
