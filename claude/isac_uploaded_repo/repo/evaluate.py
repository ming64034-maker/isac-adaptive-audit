from __future__ import annotations

import argparse
import itertools
import math
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from baselines import BeliefAwareRolloutPolicy, OneStepPredictivePolicy, OraclePolicy, ProposedV2Policy, ReactivePolicy
from config import Config, get_config
from environment import DynamicBlockageEnv
from train import load_one_step_predictor, load_world_model_bundle, run_training
from utils import ensure_dir, set_seed


def ensure_checkpoints(cfg: Config) -> None:
    predictor_ckpt = cfg.checkpoints_dir / "one_step_predictor.pt"
    world_ckpt = cfg.checkpoints_dir / "belief_world_model.pt"
    ckpt_paths = [predictor_ckpt, world_ckpt]
    compatible = True
    for ckpt_path in ckpt_paths:
        if not ckpt_path.exists():
            compatible = False
            break
        checkpoint = torch.load(ckpt_path, map_location="cpu")
        if checkpoint.get("checkpoint_version") != cfg.checkpoint_version:
            compatible = False
            break
    if not compatible:
        print("Checkpoints not found or incompatible with current model version. Running training first...")
        run_training(cfg)


def reward_from_metrics(cfg: Config, metrics: dict, action: int, prev_beam: int) -> float:
    switching_cost = float(action != prev_beam)
    return (
        cfg.reward_alpha * float(metrics["rate"])
        - cfg.reward_beta * float(metrics["outage"])
        - cfg.reward_gamma * switching_cost
    )


def optional_value(diagnostics: dict, key: str) -> float:
    value = diagnostics.get(key)
    return float(value) if value is not None else np.nan


def diagnostics_flag(diagnostics: dict, key: str) -> bool:
    value = diagnostics.get(key)
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return False
    return bool(float(value) > 0.5)


def evaluate_policy(cfg: Config, method: str, policy_factory, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    episode_rows = []
    step_rows = []
    for seed in seeds:
        set_seed(seed)
        env = DynamicBlockageEnv(cfg, seed=seed)
        for episode in range(cfg.num_eval_episodes):
            obs = env.reset(seed=seed * 1000 + episode)
            policy = policy_factory()
            policy.reset(obs, env)

            total_reward = 0.0
            total_rate = 0.0
            total_outage = 0.0
            total_success = 0.0
            latencies = []
            steps = 0
            done = False

            while not done:
                start = time.perf_counter()
                action = policy.select_action(obs, env)
                planning_latency_ms = (time.perf_counter() - start) * 1000.0
                latencies.append(planning_latency_ms)

                oracle_action = env.oracle_action()
                los_beam = env.nearest_beam(math.atan2(float(env.user_pos[1]), float(env.user_pos[0])))
                chosen_true = env.metrics_for_action(action, measurement_noise=False)
                oracle_true = env.metrics_for_action(oracle_action, measurement_noise=False)
                chosen_true_reward = reward_from_metrics(cfg, chosen_true, action, env.prev_beam)
                oracle_true_reward = reward_from_metrics(cfg, oracle_true, oracle_action, env.prev_beam)

                next_obs, reward, done, info = env.step(action)
                policy.observe(action, next_obs)
                diagnostics = policy.get_diagnostics() if hasattr(policy, "get_diagnostics") else {}

                total_reward += reward
                total_rate += info["rate"]
                total_outage += info["outage"]
                total_success += info["beam_success"]

                step_rows.append(
                    {
                        "method": method,
                        "seed": seed,
                        "episode": episode,
                        "step": steps,
                        "action": int(action),
                        "selected_beam": int(action),
                        "oracle_action": int(oracle_action),
                        "oracle_beam": int(oracle_action),
                        "los_beam": int(los_beam),
                        "oracle_action_match": float(action == oracle_action),
                        "measured_reward": float(reward),
                        "true_reward": float(chosen_true_reward),
                        "oracle_true_reward": float(oracle_true_reward),
                        "oracle_reward_gap": float(oracle_true_reward - chosen_true_reward),
                        "true_rate": float(chosen_true["rate"]),
                        "oracle_true_rate": float(oracle_true["rate"]),
                        "oracle_rate_gap": float(oracle_true["rate"] - chosen_true["rate"]),
                        "true_outage": float(chosen_true["outage"]),
                        "true_beam_success": float(chosen_true["beam_success"]),
                        "rate": float(info["rate"]),
                        "outage": float(info["outage"]),
                        "beam_success": float(info["beam_success"]),
                        "los_flag": float(chosen_true["los_flag"]),
                        "reflection_ratio": float(chosen_true["reflection_ratio"]),
                        "num_available_paths": int(chosen_true["num_available_paths"]),
                        "dominant_path_type": chosen_true["dominant_path_type"],
                        "planning_latency_ms": float(planning_latency_ms),
                        "latency_ms": float(planning_latency_ms),
                        "fallback_triggered": diagnostics_flag(diagnostics, "planner_predictive_fallback_used"),
                        "guard_triggered": diagnostics_flag(diagnostics, "planner_los_guard_used"),
                        "policy_confidence": optional_value(diagnostics, "policy_confidence"),
                        "policy_margin": optional_value(diagnostics, "policy_margin"),
                        "policy_entropy": optional_value(diagnostics, "policy_entropy"),
                        "planner_value": optional_value(diagnostics, "planner_value"),
                        "planner_terminal_value": optional_value(diagnostics, "planner_terminal_value"),
                        "planner_beam_gain_value": optional_value(diagnostics, "planner_beam_gain_value"),
                        "planner_predictor_mix": optional_value(diagnostics, "planner_predictor_mix"),
                        "planner_rate_signal": optional_value(diagnostics, "planner_rate_signal"),
                        "planner_outage_signal": optional_value(diagnostics, "planner_outage_signal"),
                        "planner_adaptive_difficulty": optional_value(diagnostics, "planner_adaptive_difficulty"),
                        "planner_adaptive_difficulty_ema": optional_value(
                            diagnostics,
                            "planner_adaptive_difficulty_ema",
                        ),
                        "planner_adaptive_los_threshold": optional_value(
                            diagnostics,
                            "planner_adaptive_los_threshold",
                        ),
                        "planner_adaptive_risk_threshold": optional_value(
                            diagnostics,
                            "planner_adaptive_risk_threshold",
                        ),
                        "planner_adaptive_path_threshold": optional_value(
                            diagnostics,
                            "planner_adaptive_path_threshold",
                        ),
                        "planner_adaptive_reflection_threshold": optional_value(
                            diagnostics,
                            "planner_adaptive_reflection_threshold",
                        ),
                        "planner_adaptive_global_pool_threshold": optional_value(
                            diagnostics,
                            "planner_adaptive_global_pool_threshold",
                        ),
                        "planner_adaptive_cooldown": optional_value(diagnostics, "planner_adaptive_cooldown"),
                        "planner_adaptive_local_candidates": optional_value(
                            diagnostics,
                            "planner_adaptive_local_candidates",
                        ),
                        "planner_adaptive_global_topk": optional_value(
                            diagnostics,
                            "planner_adaptive_global_topk",
                        ),
                        "planner_score_gap": optional_value(diagnostics, "planner_score_gap"),
                        "planner_score_std": optional_value(diagnostics, "planner_score_std"),
                        "planner_candidates": optional_value(diagnostics, "planner_candidates"),
                        "planner_reactive_rate_regret": optional_value(diagnostics, "planner_reactive_rate_regret"),
                        "planner_reactive_safety_gain": optional_value(diagnostics, "planner_reactive_safety_gain"),
                        "planner_reactive_veto_triggered": optional_value(
                            diagnostics,
                            "planner_reactive_veto_triggered",
                        ),
                        "planner_rate_veto_triggered": optional_value(
                            diagnostics,
                            "planner_rate_veto_triggered",
                        ),
                        "planner_tri_regime_mode": optional_value(diagnostics, "planner_tri_regime_mode"),
                        "planner_clear_suppress_triggered": optional_value(
                            diagnostics,
                            "planner_clear_suppress_triggered",
                        ),
                        "planner_extreme_veto_triggered": optional_value(
                            diagnostics,
                            "planner_extreme_veto_triggered",
                        ),
                        "planner_fallback_kept_after_veto": optional_value(
                            diagnostics,
                            "planner_fallback_kept_after_veto",
                        ),
                        "planner_los_recovery_gate": optional_value(diagnostics, "planner_los_recovery_gate"),
                        "planner_los_recovery_bias_max": optional_value(diagnostics, "planner_los_recovery_bias_max"),
                        "planner_los_recovery_bias_chosen": optional_value(
                            diagnostics,
                            "planner_los_recovery_bias_chosen",
                        ),
                        "planner_los_guard_used": optional_value(diagnostics, "planner_los_guard_used"),
                        "planner_predictive_fallback_used": optional_value(
                            diagnostics,
                            "planner_predictive_fallback_used",
                        ),
                        "shortlist_size": optional_value(diagnostics, "shortlist_size"),
                        "shortlist_local_size": optional_value(diagnostics, "shortlist_local_size"),
                        "shortlist_global_fallback_count": optional_value(diagnostics, "shortlist_global_fallback_count"),
                        "shortlist_los_reserved": optional_value(diagnostics, "shortlist_los_reserved"),
                        "shortlist_reflection_reserved": optional_value(diagnostics, "shortlist_reflection_reserved"),
                        "shortlist_prev_beam_kept": optional_value(diagnostics, "shortlist_prev_beam_kept"),
                        "shortlist_max_los_prob": optional_value(diagnostics, "shortlist_max_los_prob"),
                        "shortlist_max_reflection_prob": optional_value(diagnostics, "shortlist_max_reflection_prob"),
                        "shortlist_max_beam_gain": optional_value(diagnostics, "shortlist_max_beam_gain"),
                        "shortlist_beam_gain_weight": optional_value(diagnostics, "shortlist_beam_gain_weight"),
                        "shortlist_blockage_hint": optional_value(diagnostics, "shortlist_blockage_hint"),
                        "shortlist_reflection_hint": optional_value(diagnostics, "shortlist_reflection_hint"),
                        "shortlist_used_global_pool": optional_value(diagnostics, "shortlist_used_global_pool"),
                        "shortlist_base_pool_size": optional_value(diagnostics, "shortlist_base_pool_size"),
                    }
                )
                steps += 1
                obs = next_obs

            episode_rows.append(
                {
                    "method": method,
                    "seed": seed,
                    "episode": episode,
                    "average_rate": total_rate / steps,
                    "outage_prob": total_outage / steps,
                    "beam_success_rate": total_success / steps,
                    "average_return": total_reward / steps,
                    "planning_latency_ms": sum(latencies) / len(latencies),
                }
            )
    return pd.DataFrame(episode_rows), pd.DataFrame(step_rows)


def summarize(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    grouped = df.groupby(group_cols)
    metric_cols = ["average_rate", "outage_prob", "beam_success_rate", "average_return", "planning_latency_ms"]
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {group_cols[idx]: value for idx, value in enumerate(keys)}
        for metric in metric_cols:
            row[f"{metric}_mean"] = group[metric].mean()
            row[f"{metric}_std"] = group[metric].std(ddof=0)
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_step_diagnostics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    metric_cols = [
        "oracle_action_match",
        "oracle_reward_gap",
        "oracle_rate_gap",
        "true_outage",
        "true_beam_success",
        "los_flag",
        "reflection_ratio",
        "num_available_paths",
        "planning_latency_ms",
        "policy_confidence",
        "policy_margin",
        "policy_entropy",
        "planner_value",
        "planner_terminal_value",
        "planner_beam_gain_value",
        "planner_predictor_mix",
        "planner_rate_signal",
        "planner_outage_signal",
        "planner_adaptive_difficulty",
        "planner_adaptive_difficulty_ema",
        "planner_adaptive_los_threshold",
        "planner_adaptive_risk_threshold",
        "planner_adaptive_path_threshold",
        "planner_adaptive_reflection_threshold",
        "planner_adaptive_global_pool_threshold",
        "planner_adaptive_cooldown",
        "planner_adaptive_local_candidates",
        "planner_adaptive_global_topk",
        "planner_score_gap",
        "planner_score_std",
        "planner_candidates",
        "planner_reactive_rate_regret",
        "planner_reactive_safety_gain",
        "planner_reactive_veto_triggered",
        "planner_rate_veto_triggered",
        "planner_tri_regime_mode",
        "planner_clear_suppress_triggered",
        "planner_extreme_veto_triggered",
        "planner_fallback_kept_after_veto",
        "planner_los_recovery_gate",
        "planner_los_recovery_bias_max",
        "planner_los_recovery_bias_chosen",
        "planner_los_guard_used",
        "planner_predictive_fallback_used",
        "shortlist_size",
        "shortlist_local_size",
        "shortlist_global_fallback_count",
        "shortlist_los_reserved",
        "shortlist_reflection_reserved",
        "shortlist_prev_beam_kept",
        "shortlist_max_los_prob",
        "shortlist_max_reflection_prob",
        "shortlist_max_beam_gain",
        "shortlist_beam_gain_weight",
        "shortlist_blockage_hint",
        "shortlist_reflection_hint",
        "shortlist_used_global_pool",
        "shortlist_base_pool_size",
    ]
    rows = []
    grouped = df.groupby(group_cols)
    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {group_cols[idx]: value for idx, value in enumerate(keys)}
        for metric in metric_cols:
            row[f"{metric}_mean"] = group[metric].mean()
            row[f"{metric}_std"] = group[metric].std(ddof=0)
        row["dominant_reflection_fraction"] = (group["dominant_path_type"] == "reflection").mean()
        row["dominant_los_fraction"] = (group["dominant_path_type"] == "los").mean()
        rows.append(row)
    return pd.DataFrame(rows)


def build_proposedv2_factory(
    cfg: Config,
    predictor,
    encoder: HistoryEncoder | None,
    world_model: WorldModel | None,
):
    def factory(c=cfg):
        return ProposedV2Policy(c, predictor, encoder, world_model, c.device)

    return factory


def run_method_comparison(cfg: Config, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    predictor = load_one_step_predictor(cfg, device=cfg.device)
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)
    proposedv2_factory = build_proposedv2_factory(cfg, predictor, encoder, world_model)

    episode_frames = []
    step_frames = []
    for episode_df, step_df in [
        evaluate_policy(cfg, "Reactive", lambda: ReactivePolicy(cfg), seeds),
        evaluate_policy(cfg, "OneStepPredictive", lambda: OneStepPredictivePolicy(cfg, predictor, cfg.device), seeds),
        evaluate_policy(cfg, "ProposedV2", proposedv2_factory, seeds),
        evaluate_policy(cfg, "Oracle", lambda: OraclePolicy(cfg), seeds),
        evaluate_policy(
            cfg,
            "BeliefAwareRollout",
            lambda: BeliefAwareRolloutPolicy(cfg, encoder, world_model, cfg.device, horizon=cfg.rollout_horizon),
            seeds,
        ),
    ]:
        episode_frames.append(episode_df)
        step_frames.append(step_df)
    raw_df = pd.concat(episode_frames, ignore_index=True)
    steps_df = pd.concat(step_frames, ignore_index=True)
    summary_df = summarize(raw_df, ["method"]).sort_values("method").reset_index(drop=True)
    diagnostics_df = summarize_step_diagnostics(steps_df, ["method"]).sort_values("method").reset_index(drop=True)
    return raw_df, summary_df, steps_df, diagnostics_df


def run_horizon_sweep(cfg: Config, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)
    episode_frames = []
    step_frames = []
    for horizon in cfg.horizon_values:
        episode_df, step_df = evaluate_policy(
            cfg,
            "BeliefAwareRollout",
            lambda h=horizon: BeliefAwareRolloutPolicy(cfg, encoder, world_model, cfg.device, horizon=h),
            seeds,
        )
        episode_df["horizon"] = horizon
        step_df["horizon"] = horizon
        episode_frames.append(episode_df)
        step_frames.append(step_df)
    raw_df = pd.concat(episode_frames, ignore_index=True)
    steps_df = pd.concat(step_frames, ignore_index=True)
    summary_df = summarize(raw_df, ["horizon"]).sort_values("horizon").reset_index(drop=True)
    diagnostics_df = summarize_step_diagnostics(steps_df, ["horizon"]).sort_values("horizon").reset_index(drop=True)
    return raw_df, summary_df, steps_df, diagnostics_df


def scenario_sweep_configs(cfg: Config) -> list[tuple[dict[str, object], Config]]:
    scenarios: list[tuple[dict[str, object], Config]] = []

    for order, num_blockers in enumerate(cfg.blocker_density_values):
        scenario_cfg = replace(cfg, num_blockers_min=num_blockers, num_blockers_max=num_blockers)
        metadata = {
            "sweep": "blocker_density",
            "sweep_name": "blocker_density",
            "scenario": f"Nb={num_blockers}",
            "scenario_order": order,
            "scenario_value": float(num_blockers),
            "sweep_value": float(num_blockers),
            "num_blockers_min": num_blockers,
            "num_blockers_max": num_blockers,
            "blocker_speed": scenario_cfg.blocker_speed,
            "blocker_speed_scale": scenario_cfg.blocker_speed_scale,
            "obs_noise_std": scenario_cfg.obs_noise_std,
            "obs_angle_noise_los": scenario_cfg.obs_angle_noise_los,
            "obs_angle_noise_nlos": scenario_cfg.obs_angle_noise_nlos,
            "obs_power_noise_std": scenario_cfg.obs_power_noise_std,
            "obs_blockage_noise_std": scenario_cfg.obs_blockage_noise_std,
            "obs_reflection_noise_std": scenario_cfg.obs_reflection_noise_std,
            "reflector_loss_db": scenario_cfg.reflector_loss_db,
            "reflection_gain_scale": scenario_cfg.reflection_gain_scale,
        }
        scenarios.append((metadata, scenario_cfg))

    for order, speed_scale in enumerate(cfg.blocker_speed_scale_values):
        scenario_cfg = replace(cfg, blocker_speed_scale=float(speed_scale))
        metadata = {
            "sweep": "blocker_speed",
            "sweep_name": "blocker_speed",
            "scenario": f"{speed_scale:g}x",
            "scenario_order": order,
            "scenario_value": float(speed_scale),
            "sweep_value": float(speed_scale),
            "num_blockers_min": scenario_cfg.num_blockers_min,
            "num_blockers_max": scenario_cfg.num_blockers_max,
            "blocker_speed": scenario_cfg.blocker_speed,
            "blocker_speed_scale": float(speed_scale),
            "obs_noise_std": scenario_cfg.obs_noise_std,
            "obs_angle_noise_los": scenario_cfg.obs_angle_noise_los,
            "obs_angle_noise_nlos": scenario_cfg.obs_angle_noise_nlos,
            "obs_power_noise_std": scenario_cfg.obs_power_noise_std,
            "obs_blockage_noise_std": scenario_cfg.obs_blockage_noise_std,
            "obs_reflection_noise_std": scenario_cfg.obs_reflection_noise_std,
            "reflector_loss_db": scenario_cfg.reflector_loss_db,
            "reflection_gain_scale": scenario_cfg.reflection_gain_scale,
        }
        scenarios.append((metadata, scenario_cfg))

    for order, obs_noise_std in enumerate(cfg.obs_noise_std_values):
        scenario_cfg = replace(
            cfg,
            obs_noise_std=float(obs_noise_std),
        )
        metadata = {
            "sweep": "obs_noise",
            "sweep_name": "obs_noise",
            "scenario": f"{obs_noise_std:g}",
            "scenario_order": order,
            "scenario_value": float(obs_noise_std),
            "sweep_value": float(obs_noise_std),
            "num_blockers_min": scenario_cfg.num_blockers_min,
            "num_blockers_max": scenario_cfg.num_blockers_max,
            "blocker_speed": scenario_cfg.blocker_speed,
            "blocker_speed_scale": scenario_cfg.blocker_speed_scale,
            "obs_noise_std": float(obs_noise_std),
            "obs_angle_noise_los": float(obs_noise_std),
            "obs_angle_noise_nlos": float(obs_noise_std),
            "obs_power_noise_std": float(obs_noise_std),
            "obs_blockage_noise_std": float(obs_noise_std),
            "obs_reflection_noise_std": float(obs_noise_std),
            "reflector_loss_db": scenario_cfg.reflector_loss_db,
            "reflection_gain_scale": scenario_cfg.reflection_gain_scale,
        }
        scenarios.append((metadata, scenario_cfg))

    for order, reflection_gain_scale in enumerate(cfg.reflection_gain_scale_values):
        scenario_cfg = replace(cfg, reflection_gain_scale=float(reflection_gain_scale))
        metadata = {
            "sweep": "reflection_strength",
            "sweep_name": "reflection_strength",
            "scenario": f"{reflection_gain_scale:g}x",
            "scenario_order": order,
            "scenario_value": float(reflection_gain_scale),
            "sweep_value": float(reflection_gain_scale),
            "num_blockers_min": scenario_cfg.num_blockers_min,
            "num_blockers_max": scenario_cfg.num_blockers_max,
            "blocker_speed": scenario_cfg.blocker_speed,
            "blocker_speed_scale": scenario_cfg.blocker_speed_scale,
            "obs_noise_std": scenario_cfg.obs_noise_std,
            "obs_angle_noise_los": scenario_cfg.obs_angle_noise_los,
            "obs_angle_noise_nlos": scenario_cfg.obs_angle_noise_nlos,
            "obs_power_noise_std": scenario_cfg.obs_power_noise_std,
            "obs_blockage_noise_std": scenario_cfg.obs_blockage_noise_std,
            "obs_reflection_noise_std": scenario_cfg.obs_reflection_noise_std,
            "reflector_loss_db": scenario_cfg.reflector_loss_db,
            "reflection_gain_scale": float(reflection_gain_scale),
        }
        scenarios.append((metadata, scenario_cfg))

    return scenarios


def add_metadata(df: pd.DataFrame, metadata: dict[str, object]) -> pd.DataFrame:
    df = df.copy()
    for key, value in metadata.items():
        df[key] = value
    return df


def run_scene_difficulty_sweeps(
    cfg: Config,
    seeds: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    predictor = load_one_step_predictor(cfg, device=cfg.device)
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)

    episode_frames = []
    step_frames = []
    for metadata, scenario_cfg in scenario_sweep_configs(cfg):
        scenario_proposedv2_factory = build_proposedv2_factory(scenario_cfg, predictor, encoder, world_model)
        for episode_df, step_df in [
            evaluate_policy(scenario_cfg, "Reactive", lambda c=scenario_cfg: ReactivePolicy(c), seeds),
            evaluate_policy(
                scenario_cfg,
                "OneStepPredictive",
                lambda c=scenario_cfg: OneStepPredictivePolicy(c, predictor, c.device),
                seeds,
            ),
            evaluate_policy(scenario_cfg, "ProposedV2", scenario_proposedv2_factory, seeds),
            evaluate_policy(scenario_cfg, "Oracle", lambda c=scenario_cfg: OraclePolicy(c), seeds),
            evaluate_policy(
                scenario_cfg,
                "BeliefAwareRollout",
                lambda c=scenario_cfg: BeliefAwareRolloutPolicy(
                    c,
                    encoder,
                    world_model,
                    c.device,
                    horizon=c.rollout_horizon,
                ),
                seeds,
            ),
        ]:
            episode_frames.append(add_metadata(episode_df, metadata))
            step_frames.append(add_metadata(step_df, metadata))

    raw_df = pd.concat(episode_frames, ignore_index=True)
    steps_df = pd.concat(step_frames, ignore_index=True)
    group_cols = ["sweep", "scenario", "scenario_order", "scenario_value", "method"]
    summary_df = (
        summarize(raw_df, group_cols)
        .sort_values(["sweep", "scenario_order", "method"])
        .reset_index(drop=True)
    )
    diagnostics_df = (
        summarize_step_diagnostics(steps_df, group_cols)
        .sort_values(["sweep", "scenario_order", "method"])
        .reset_index(drop=True)
    )
    return raw_df, summary_df, steps_df, diagnostics_df


def aggregate_episode_metrics(
    episode_df: pd.DataFrame,
    group_cols: list[str],
    *,
    rename_method_to_variant: bool = False,
) -> pd.DataFrame:
    if episode_df.empty:
        return pd.DataFrame()
    grouped = (
        episode_df.groupby(group_cols, dropna=False, as_index=False)
        .agg(
            avg_rate=("average_rate", "mean"),
            outage=("outage_prob", "mean"),
            beam_success=("beam_success_rate", "mean"),
            avg_return=("average_return", "mean"),
            latency_ms=("planning_latency_ms", "mean"),
        )
    )
    if rename_method_to_variant and "method" in grouped.columns:
        grouped = grouped.rename(columns={"method": "variant"})
    return grouped


def summarize_required_metrics(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    metric_cols = ["avg_rate", "outage", "beam_success", "avg_return", "latency_ms"]
    rows = []
    if df.empty:
        return pd.DataFrame(columns=group_cols + [f"{metric}_{suffix}" for metric in metric_cols for suffix in ("mean", "std")])
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {group_cols[idx]: value for idx, value in enumerate(keys)}
        for metric in metric_cols:
            row[f"{metric}_mean"] = group[metric].mean()
            row[f"{metric}_std"] = group[metric].std(ddof=0)
        rows.append(row)
    return pd.DataFrame(rows)


def scene_sweep_file_name(sweep_name: str) -> str:
    names = {
        "blocker_density": "blocker_density_sweep.csv",
        "blocker_speed": "blocker_speed_sweep.csv",
        "obs_noise": "obs_noise_sweep.csv",
        "reflection_strength": "reflection_strength_sweep.csv",
    }
    return names[sweep_name]


def write_scene_sweep_outputs(
    cfg: Config,
    raw_scene: pd.DataFrame,
    *,
    suffix: str = "",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    sweeps_dir = ensure_dir(cfg.results_dir / "sweeps")
    seed_rows = aggregate_episode_metrics(
        raw_scene,
        ["sweep_name", "sweep_value", "method", "seed"],
    )
    seed_rows = seed_rows.sort_values(["sweep_name", "sweep_value", "method", "seed"]).reset_index(drop=True)
    summary_df = summarize_required_metrics(seed_rows, ["sweep_name", "sweep_value", "method"])
    summary_df = summary_df.sort_values(["sweep_name", "sweep_value", "method"]).reset_index(drop=True)

    for sweep_name in ["blocker_density", "blocker_speed", "obs_noise", "reflection_strength"]:
        out_name = scene_sweep_file_name(sweep_name)
        if suffix:
            out_name = out_name.replace(".csv", f"{suffix}.csv")
        sweep_df = seed_rows[seed_rows["sweep_name"] == sweep_name].copy()
        sweep_df.to_csv(sweeps_dir / out_name, index=False)
        print(f"[scene-sweeps] saved {sweeps_dir / out_name}")

    summary_name = f"scene_sweep_summary{suffix}.csv"
    summary_df.to_csv(sweeps_dir / summary_name, index=False)
    print(f"[scene-sweeps] saved {sweeps_dir / summary_name}")
    return seed_rows, summary_df


def append_trigger_rates(seed_rows: pd.DataFrame, step_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if step_df.empty:
        seed_rows["fallback_rate"] = np.nan
        seed_rows["reactive_guard_rate"] = np.nan
        return seed_rows
    trigger_df = (
        step_df.groupby(group_cols, dropna=False, as_index=False)
        .agg(
            fallback_rate=("fallback_triggered", "mean"),
            reactive_guard_rate=("guard_triggered", "mean"),
        )
    )
    return seed_rows.merge(trigger_df, on=group_cols, how="left")


def run_ablation_study(cfg: Config, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    predictor = load_one_step_predictor(cfg, device=cfg.device)
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)
    notes: list[str] = []
    rows = []

    v1_cfg = replace(
        cfg,
        rollout_use_beam_gain_head=False,
        rollout_use_los_guard=False,
        rollout_use_auxiliary_shortlist=False,
        rollout_shortlist_global_on_demand=False,
    )
    modelv2_cfg = replace(cfg, rollout_use_beam_gain_head=True, rollout_use_los_guard=False)
    adaptive_cfg = replace(cfg, proposedv2_use_adaptive_difficulty=True)
    no_guard_cfg = replace(
        cfg,
        los_confidence_threshold=1.1,
        risk_threshold=-1.0,
        path_spread_threshold=-1.0,
        rollout_shortlist_reflection_threshold=-1.0,
    )
    no_fallback_cfg = replace(
        cfg,
        los_confidence_threshold=-1.0,
        risk_threshold=1.1,
        path_spread_threshold=1.1,
        rollout_shortlist_reflection_threshold=1.1,
    )

    runnable_variants = [
        ("Reactive", cfg, lambda c=cfg: ReactivePolicy(c)),
        ("OneStepPredictive", cfg, lambda c=cfg: OneStepPredictivePolicy(c, predictor, c.device)),
        (
            "BeliefAwareRollout_V1",
            v1_cfg,
            lambda c=v1_cfg: BeliefAwareRolloutPolicy(c, encoder, world_model, c.device, horizon=c.rollout_horizon),
        ),
        (
            "BeliefAwareRollout_ModelV2",
            modelv2_cfg,
            lambda c=modelv2_cfg: BeliefAwareRolloutPolicy(c, encoder, world_model, c.device, horizon=c.rollout_horizon),
        ),
        (
            "ProposedV2_NoLoSGuard",
            no_guard_cfg,
            build_proposedv2_factory(no_guard_cfg, predictor, encoder, world_model),
        ),
        (
            "ProposedV2_NoPredictiveFallback",
            no_fallback_cfg,
            build_proposedv2_factory(no_fallback_cfg, predictor, encoder, world_model),
        ),
        (
            "ProposedV2_Adaptive",
            adaptive_cfg,
            build_proposedv2_factory(adaptive_cfg, predictor, encoder, world_model),
        ),
        ("ProposedV2_Full", cfg, build_proposedv2_factory(cfg, predictor, encoder, world_model)),
        ("Oracle", cfg, lambda c=cfg: OraclePolicy(c)),
    ]
    notes.append(
        "BeliefAwareRollout_V1 disables beam-gain use, LoS guard, auxiliary shortlist, and global fallback at inference. "
        "It reuses the available Model v2 checkpoint, so it is an inference-side V1 proxy rather than a separately "
        "trained no-ranking checkpoint."
    )
    notes.append(
        "ProposedV2_NoLoSGuard widens the fallback thresholds enough that predictive fallback is active for most "
        "timesteps. Treat it as an almost always-on fallback stress test, not as a pure one-line removal of the "
        "LoS confidence check."
    )

    for variant, variant_cfg, factory in runnable_variants:
        print(f"[ablation] running {variant}")
        episode_df, _ = evaluate_policy(variant_cfg, variant, factory, seeds)
        variant_rows = aggregate_episode_metrics(episode_df, ["method", "seed"], rename_method_to_variant=True)
        variant_rows["status"] = "ok"
        variant_rows["skipped_reason"] = ""
        rows.append(variant_rows)

    skipped_reason = (
        "Skipped: no separate checkpoint trained with beam_gain_pairwise_rank_loss_weight=0 is present. "
        "The current ProposedV2Policy uses the one-step predictor for fallback, so pairwise ranking affects "
        "the BeliefAwareRollout model path rather than this policy directly."
    )
    skipped = pd.DataFrame(
        [
            {
                "variant": "ProposedV2_NoPairwise",
                "seed": np.nan,
                "avg_rate": np.nan,
                "outage": np.nan,
                "beam_success": np.nan,
                "avg_return": np.nan,
                "latency_ms": np.nan,
                "status": "skipped",
                "skipped_reason": skipped_reason,
            }
        ]
    )
    rows.append(skipped)
    notes.append(skipped_reason)

    table_df = pd.concat(rows, ignore_index=True)
    summary_df = summarize_required_metrics(
        table_df[table_df["status"] == "ok"],
        ["variant"],
    ).sort_values("variant").reset_index(drop=True)
    if not skipped.empty:
        skipped_summary = skipped.drop(columns=["seed"]).copy()
        for metric in ["avg_rate", "outage", "beam_success", "avg_return", "latency_ms"]:
            skipped_summary[f"{metric}_mean"] = np.nan
            skipped_summary[f"{metric}_std"] = np.nan
        summary_df = pd.concat(
            [
                summary_df,
                skipped_summary[
                    [
                        "variant",
                        "avg_rate_mean",
                        "avg_rate_std",
                        "outage_mean",
                        "outage_std",
                        "beam_success_mean",
                        "beam_success_std",
                        "avg_return_mean",
                        "avg_return_std",
                        "latency_ms_mean",
                        "latency_ms_std",
                        "status",
                        "skipped_reason",
                    ]
                ],
            ],
            ignore_index=True,
        )
    return table_df, summary_df, notes


def run_threshold_sweep(cfg: Config, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictor = load_one_step_predictor(cfg, device=cfg.device)
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)
    rows = []
    los_values = [0.5, 0.6, 0.7, 0.8, 0.9]
    risk_values = [0.15, 0.25, 0.35, 0.45, 0.55]
    spread_values = [0.2, 0.4, 0.6, 0.8]
    for los_threshold, risk_threshold, spread_threshold in itertools.product(los_values, risk_values, spread_values):
        print(
            "[threshold-sweep] "
            f"los={los_threshold:.2f} risk={risk_threshold:.2f} spread={spread_threshold:.2f}"
        )
        sweep_cfg = replace(
            cfg,
            los_confidence_threshold=float(los_threshold),
            risk_threshold=float(risk_threshold),
            path_spread_threshold=float(spread_threshold),
        )
        episode_df, step_df = evaluate_policy(
            sweep_cfg,
            "ProposedV2",
            build_proposedv2_factory(sweep_cfg, predictor, encoder, world_model),
            seeds,
        )
        seed_rows = aggregate_episode_metrics(episode_df, ["seed"])
        seed_rows = append_trigger_rates(seed_rows, step_df, ["seed"])
        seed_rows["los_confidence_threshold"] = float(los_threshold)
        seed_rows["risk_threshold"] = float(risk_threshold)
        seed_rows["path_spread_threshold"] = float(spread_threshold)
        rows.append(seed_rows)

    table_df = pd.concat(rows, ignore_index=True)
    table_df = table_df[
        [
            "los_confidence_threshold",
            "risk_threshold",
            "path_spread_threshold",
            "seed",
            "avg_rate",
            "outage",
            "beam_success",
            "avg_return",
            "latency_ms",
            "fallback_rate",
            "reactive_guard_rate",
        ]
    ].sort_values(["los_confidence_threshold", "risk_threshold", "path_spread_threshold", "seed"])

    aggregate_df = (
        table_df.groupby(["los_confidence_threshold", "risk_threshold", "path_spread_threshold"], as_index=False)
        .agg(
            avg_rate=("avg_rate", "mean"),
            avg_rate_std=("avg_rate", lambda values: values.std(ddof=0)),
            outage=("outage", "mean"),
            outage_std=("outage", lambda values: values.std(ddof=0)),
            beam_success=("beam_success", "mean"),
            beam_success_std=("beam_success", lambda values: values.std(ddof=0)),
            avg_return=("avg_return", "mean"),
            avg_return_std=("avg_return", lambda values: values.std(ddof=0)),
            latency_ms=("latency_ms", "mean"),
            latency_ms_std=("latency_ms", lambda values: values.std(ddof=0)),
            fallback_rate=("fallback_rate", "mean"),
            reactive_guard_rate=("reactive_guard_rate", "mean"),
        )
        .sort_values(["avg_return", "outage", "avg_rate", "latency_ms"], ascending=[False, True, False, True])
        .reset_index(drop=True)
    )
    aggregate_df["rank"] = np.arange(1, len(aggregate_df) + 1)
    return table_df.reset_index(drop=True), aggregate_df


def collect_blockage_event_windows(
    steps_df: pd.DataFrame,
    *,
    pre_window: int = 5,
    post_window: int = 10,
) -> pd.DataFrame:
    columns = [
        "episode_id",
        "seed",
        "method",
        "event_id",
        "relative_t",
        "absolute_t",
        "rate",
        "outage",
        "selected_beam",
        "oracle_beam",
        "beam_success",
        "los_flag",
        "fallback_triggered",
        "guard_triggered",
        "los_beam",
    ]
    required = {"method", "seed", "episode", "step", "los_flag"}
    if steps_df.empty or not required.issubset(steps_df.columns):
        return pd.DataFrame(columns=columns)
    rows = []
    for (method, seed, episode), group in steps_df.groupby(["method", "seed", "episode"]):
        group = group.sort_values("step").reset_index(drop=True)
        los = group["los_flag"].to_numpy() > 0.5
        previous_los = np.concatenate([[los[0]], los[:-1]])
        onset_indices = np.flatnonzero(previous_los & ~los)
        for local_event_id, onset_idx in enumerate(onset_indices):
            onset_step = int(group.loc[onset_idx, "step"])
            start = max(0, onset_idx - pre_window)
            end = min(len(group) - 1, onset_idx + post_window)
            for idx in range(start, end + 1):
                rows.append(
                    {
                        "episode_id": int(episode),
                        "seed": int(seed),
                        "method": method,
                        "event_id": int(local_event_id),
                        "relative_t": int(group.loc[idx, "step"] - onset_step),
                        "absolute_t": int(group.loc[idx, "step"]),
                        "rate": float(group.loc[idx, "rate"]),
                        "outage": float(group.loc[idx, "outage"]),
                        "selected_beam": int(group.loc[idx, "selected_beam"]),
                        "oracle_beam": int(group.loc[idx, "oracle_beam"]),
                        "beam_success": float(group.loc[idx, "beam_success"]),
                        "los_flag": float(group.loc[idx, "los_flag"]),
                        "fallback_triggered": bool(group.loc[idx, "fallback_triggered"]),
                        "guard_triggered": bool(group.loc[idx, "guard_triggered"]),
                        "los_beam": int(group.loc[idx, "los_beam"]) if "los_beam" in group.columns else np.nan,
                    }
                )
    return pd.DataFrame(rows, columns=columns)


def summarize_blockage_events(cfg: Config, windows_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "method",
        "seed",
        "episode_id",
        "event_id",
        "pre_blockage_avg_rate",
        "post_blockage_avg_rate",
        "recovery_time",
        "preemptive_switch_rate",
        "fallback_trigger_rate_around_onset",
    ]
    if windows_df.empty:
        return pd.DataFrame(columns=columns)
    r_threshold = math.log2(1.0 + 10.0 ** (cfg.snr_outage_db / 10.0))
    rows = []
    for keys, group in windows_df.groupby(["method", "seed", "episode_id", "event_id"]):
        method, seed, episode_id, event_id = keys
        pre = group[(group["relative_t"] >= -5) & (group["relative_t"] <= -1)]
        post = group[(group["relative_t"] >= 0) & (group["relative_t"] <= 5)]
        after = group[group["relative_t"] >= 0].sort_values("relative_t")
        outage_after = after[after["outage"] > 0.5]
        recovery_time = np.nan
        if not outage_after.empty:
            first_outage_t = int(outage_after.iloc[0]["relative_t"])
            recovered = after[(after["relative_t"] >= first_outage_t) & (after["rate"] >= r_threshold)]
            if not recovered.empty:
                recovery_time = int(recovered.iloc[0]["relative_t"] - first_outage_t)

        preemptive_switch = np.nan
        if "los_beam" in group.columns and not pre.empty:
            preemptive_switch = float((pre["selected_beam"] != pre["los_beam"]).any())

        around = group[(group["relative_t"] >= -5) & (group["relative_t"] <= 5)]
        rows.append(
            {
                "method": method,
                "seed": int(seed),
                "episode_id": int(episode_id),
                "event_id": int(event_id),
                "pre_blockage_avg_rate": pre["rate"].mean() if not pre.empty else np.nan,
                "post_blockage_avg_rate": post["rate"].mean() if not post.empty else np.nan,
                "recovery_time": recovery_time,
                "preemptive_switch_rate": preemptive_switch,
                "fallback_trigger_rate_around_onset": around["fallback_triggered"].mean() if not around.empty else np.nan,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def run_event_analysis(cfg: Config, seeds: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictor = load_one_step_predictor(cfg, device=cfg.device)
    encoder, world_model = load_world_model_bundle(cfg, device=cfg.device)
    proposedv2_factory = build_proposedv2_factory(cfg, predictor, encoder, world_model)
    frames = []
    methods = [
        ("Reactive", lambda: ReactivePolicy(cfg)),
        (
            "BeliefAwareRollout",
            lambda: BeliefAwareRolloutPolicy(cfg, encoder, world_model, cfg.device, horizon=cfg.rollout_horizon),
        ),
        ("ProposedV2", proposedv2_factory),
        ("Oracle", lambda: OraclePolicy(cfg)),
    ]
    for method, factory in methods:
        print(f"[event-analysis] running {method}")
        _, step_df = evaluate_policy(cfg, method, factory, seeds)
        frames.append(step_df)
    steps_df = pd.concat(frames, ignore_index=True)
    windows_df = collect_blockage_event_windows(steps_df, pre_window=5, post_window=10)
    summary_df = summarize_blockage_events(cfg, windows_df)
    return windows_df, summary_df


def write_notes(path: Path, notes: list[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("# Ablation Notes\n\n")
        for note in notes:
            handle.write(f"- {note}\n")


def resolve_eval_seeds(cfg: Config, requested_count: int | None) -> list[int]:
    configured = list(cfg.seeds) if getattr(cfg, "seeds", None) else [0, 1, 2, 3, 4]
    if requested_count is None:
        return configured
    if requested_count <= len(configured):
        return configured[:requested_count]
    extra_start = max(configured) + 1 if configured else 0
    return configured + list(range(extra_start, extra_start + requested_count - len(configured)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate predictive beamforming baselines.")
    parser.add_argument("--eval-episodes", type=int, default=None)
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--fast", action="store_true", help="Fast evaluation: fewer episodes/seeds and skip horizon sweep.")
    parser.add_argument("--quick", action="store_true", help="Quick smoke test: one seed, one episode, shortened horizon.")
    parser.add_argument("--skip-horizon-sweep", action="store_true", help="Only run method comparison.")
    parser.add_argument("--with-horizon-sweep", action="store_true", help="Run horizon sweep even in fast mode.")
    parser.add_argument("--skip-scene-sweeps", action="store_true", help="Skip blocker/noise/reflection difficulty sweeps.")
    parser.add_argument("--with-scene-sweeps", action="store_true", help="Run scene difficulty sweeps even in fast mode.")
    parser.add_argument("--run-scene-sweeps", action="store_true", help="Run scene difficulty sweeps as a standalone experiment.")
    parser.add_argument("--run-ablation", action="store_true", help="Run ablation study.")
    parser.add_argument("--run-threshold-sweep", action="store_true", help="Run ProposedV2 threshold grid search.")
    parser.add_argument("--run-event-analysis", action="store_true", help="Run blockage onset event-level analysis.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cfg = get_config()
    suffix = "_quick" if args.quick else ("_fast" if args.fast else "")
    explicit_experiment = any(
        [
            args.run_scene_sweeps,
            args.run_ablation,
            args.run_threshold_sweep,
            args.run_event_analysis,
        ]
    )
    run_horizon_sweep_flag = not args.skip_horizon_sweep
    run_scene_sweeps_flag = not args.skip_scene_sweeps
    if args.fast or args.quick:
        if args.eval_episodes is None:
            cfg.num_eval_episodes = 1
        if args.seeds is None:
            cfg.num_seeds = 1
        cfg.episode_length = min(cfg.episode_length, 60 if args.quick else 80)
        run_horizon_sweep_flag = args.with_horizon_sweep
        run_scene_sweeps_flag = args.with_scene_sweeps and not args.skip_scene_sweeps
    if args.eval_episodes is not None:
        cfg.num_eval_episodes = args.eval_episodes
    if args.seeds is not None:
        cfg.num_seeds = args.seeds
    if explicit_experiment:
        run_horizon_sweep_flag = False
        run_scene_sweeps_flag = args.run_scene_sweeps

    ensure_dir(cfg.results_dir)
    ensure_checkpoints(cfg)
    seeds = resolve_eval_seeds(cfg, cfg.num_seeds if (args.fast or args.quick or args.seeds is not None) else None)
    print(f"[evaluate] seeds={seeds} eval_episodes={cfg.num_eval_episodes} episode_length={cfg.episode_length}")

    if not explicit_experiment:
        raw_methods, summary_methods, method_steps, method_diag = run_method_comparison(cfg, seeds)
        raw_methods.to_csv(cfg.results_dir / f"method_comparison_raw{suffix}.csv", index=False)
        summary_methods.to_csv(cfg.results_dir / f"method_comparison{suffix}.csv", index=False)
        method_steps.to_csv(cfg.results_dir / f"method_comparison_steps{suffix}.csv", index=False)
        method_diag.to_csv(cfg.results_dir / f"method_comparison_diagnostics{suffix}.csv", index=False)

        print("Saved evaluation results:")
        print(f"  - {cfg.results_dir / f'method_comparison{suffix}.csv'}")
        print(f"  - {cfg.results_dir / f'method_comparison_diagnostics{suffix}.csv'}")

        if run_horizon_sweep_flag:
            raw_horizon, summary_horizon, horizon_steps, horizon_diag = run_horizon_sweep(cfg, seeds)
            raw_horizon.to_csv(cfg.results_dir / f"horizon_sweep_raw{suffix}.csv", index=False)
            summary_horizon.to_csv(cfg.results_dir / f"horizon_sweep{suffix}.csv", index=False)
            horizon_steps.to_csv(cfg.results_dir / f"horizon_sweep_steps{suffix}.csv", index=False)
            horizon_diag.to_csv(cfg.results_dir / f"horizon_sweep_diagnostics{suffix}.csv", index=False)
            print(f"  - {cfg.results_dir / f'horizon_sweep{suffix}.csv'}")
            print(f"  - {cfg.results_dir / f'horizon_sweep_diagnostics{suffix}.csv'}")

    if run_scene_sweeps_flag:
        print("[scene-sweeps] running blocker density, speed, observation noise, and reflection strength sweeps")
        raw_scene, summary_scene, scene_steps, scene_diag = run_scene_difficulty_sweeps(cfg, seeds)
        raw_scene.to_csv(cfg.results_dir / f"scene_difficulty_sweep_raw{suffix}.csv", index=False)
        summary_scene.to_csv(cfg.results_dir / f"scene_difficulty_sweep{suffix}.csv", index=False)
        scene_steps.to_csv(cfg.results_dir / f"scene_difficulty_sweep_steps{suffix}.csv", index=False)
        scene_diag.to_csv(cfg.results_dir / f"scene_difficulty_sweep_diagnostics{suffix}.csv", index=False)
        write_scene_sweep_outputs(cfg, raw_scene, suffix=suffix)
        print(f"  - {cfg.results_dir / f'scene_difficulty_sweep{suffix}.csv'}")
        print(f"  - {cfg.results_dir / f'scene_difficulty_sweep_diagnostics{suffix}.csv'}")

    if args.run_ablation:
        ablation_dir = ensure_dir(cfg.results_dir / "ablation")
        table_df, summary_df, notes = run_ablation_study(cfg, seeds)
        table_path = ablation_dir / f"ablation_table{suffix}.csv"
        summary_path = ablation_dir / f"ablation_summary{suffix}.csv"
        notes_path = ablation_dir / "ablation_notes.md"
        table_df.to_csv(table_path, index=False)
        summary_df.to_csv(summary_path, index=False)
        write_notes(notes_path, notes)
        print(f"[ablation] saved {table_path}")
        print(f"[ablation] saved {summary_path}")
        print(f"[ablation] saved {notes_path}")

    if args.run_threshold_sweep:
        threshold_dir = ensure_dir(cfg.results_dir / "threshold_sweep")
        table_df, best_df = run_threshold_sweep(cfg, seeds)
        table_path = threshold_dir / f"threshold_sweep{suffix}.csv"
        best_path = threshold_dir / f"best_thresholds{suffix}.csv"
        table_df.to_csv(table_path, index=False)
        best_df.to_csv(best_path, index=False)
        print(f"[threshold-sweep] saved {table_path}")
        print(f"[threshold-sweep] saved {best_path}")

    if args.run_event_analysis:
        events_dir = ensure_dir(cfg.results_dir / "events")
        windows_df, event_summary_df = run_event_analysis(cfg, seeds)
        windows_path = events_dir / f"blockage_event_windows{suffix}.csv"
        summary_path = events_dir / f"blockage_event_summary{suffix}.csv"
        windows_df.to_csv(windows_path, index=False)
        event_summary_df.to_csv(summary_path, index=False)
        print(f"[event-analysis] saved {windows_path}")
        print(f"[event-analysis] saved {summary_path}")
