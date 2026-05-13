from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class Config:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    checkpoints_dir: Path = field(init=False)
    results_dir: Path = field(init=False)
    plots_dir: Path = field(init=False)
    data_dir: Path = field(init=False)

    seed: int = 7
    device: str = "cpu"
    checkpoint_version: int = 5

    episode_length: int = 200
    num_train_episodes: int = 48
    num_eval_episodes: int = 4
    num_seeds: int = 2
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

    codebook_size: int = 32
    history_length: int = 8

    num_blockers_min: int = 1
    num_blockers_max: int = 2
    user_speed: float = 0.60
    blocker_speed: float = 0.55
    blocker_speed_scale: float = 1.0
    blocker_radius: float = 1.15

    num_reflectors: int = 4
    reflector_points: Tuple[Tuple[float, float], ...] = (
        (12.0, -14.0),
        (18.0, -6.0),
        (18.0, 6.0),
        (12.0, 14.0),
    )
    reflector_loss_db: float = 6.0
    reflector_pathloss_exponent: float = 2.2

    user_x_range: tuple[float, float] = (18.0, 36.0)
    user_y_range: tuple[float, float] = (-10.0, 10.0)
    x_bounds: tuple[float, float] = (6.0, 42.0)
    y_bounds: tuple[float, float] = (-18.0, 18.0)

    los_snr_ref_db: float = 24.0
    ref_distance: float = 20.0
    pathloss_exponent: float = 1.8
    nlos_penalty_db: float = 10.0
    snr_noise_std_db: float = 0.75
    snr_outage_db: float = 2.0
    beam_gain_floor_db: float = -24.0

    obs_angle_noise_los: float = 0.05
    obs_angle_noise_nlos: float = 0.16
    obs_power_noise_std: float = 0.06
    obs_blockage_noise_std: float = 0.05
    obs_reflection_noise_std: float = 0.04
    obs_noise_std: float | None = None
    reflection_gain_scale: float = 1.0

    blocker_density_values: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    blocker_speed_scale_values: List[float] = field(default_factory=lambda: [0.5, 1.0, 1.5, 2.0])
    obs_noise_std_values: List[float] = field(default_factory=lambda: [0.0, 0.02, 0.05, 0.1])
    reflection_gain_scale_values: List[float] = field(default_factory=lambda: [0.3, 0.6, 1.0, 1.5])
    blocker_speed_values: Tuple[Tuple[str, float], ...] = (
        ("slow", 0.30),
        ("medium", 0.55),
        ("fast", 0.95),
    )
    observation_noise_values: Tuple[Tuple[str, float, float, float, float, float], ...] = (
        ("low", 0.03, 0.10, 0.03, 0.025, 0.02),
        ("medium", 0.05, 0.16, 0.06, 0.05, 0.04),
        ("high", 0.10, 0.28, 0.12, 0.10, 0.08),
    )
    reflection_strength_values: Tuple[Tuple[str, float], ...] = (
        ("weak", 10.0),
        ("medium", 6.0),
        ("strong", 2.5),
    )

    reward_alpha: float = 1.0
    reward_beta: float = 2.0
    reward_gamma: float = 0.15

    latent_dim: int = 64
    hidden_dim: int = 128
    transformer_layers: int = 2
    transformer_heads: int = 4
    transformer_dropout: float = 0.1

    predictor_epochs: int = 12
    world_model_epochs: int = 15
    batch_size: int = 64
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    predictor_soft_loss_weight: float = 0.75
    predictor_target_temperature: float = 0.50
    predictor_rank_loss_weight: float = 0.10
    predictor_risk_reweight_alpha: float = 0.00
    predictor_rate_loss_weight: float = 0.15
    predictor_outage_loss_weight: float = 0.15
    value_loss_weight: float = 0.5
    beam_gain_loss_weight: float = 1.0
    beam_gain_rank_loss_weight: float = 0.2
    beam_gain_pairwise_rank_loss_weight: float = 0.05
    beam_gain_topk: int = 5
    beam_gain_rank_temperature: float = 1.0
    beam_gain_rank_margin: float = 0.5
    beam_gain_rank_negative_count: int = 8

    behavior_oracle_fraction: float = 0.35
    behavior_reactive_fraction: float = 0.00
    discount: float = 0.95
    rollout_horizon: int = 2
    rollout_candidate_count: int = 8
    rollout_preselect_count: int = 16
    rollout_strategy: str = "greedy"
    rollout_risk_penalty: float = 0.5
    rollout_use_beam_gain_head: bool = True
    rollout_beam_gain_score_weight: float = 1.0
    rollout_use_los_guard: bool = True
    rollout_use_los_recovery_bias: bool = True
    rollout_los_recovery_bias: float = 2.0
    rollout_use_terminal_value: bool = False
    rollout_terminal_value_scale: float = 0.0
    rollout_num_hypotheses: int = 6
    rollout_use_auxiliary_shortlist: bool = True
    rollout_shortlist_full_codebook: bool = False
    rollout_shortlist_global_on_demand: bool = True
    rollout_local_shortlist_count: int = 6
    rollout_global_fallback_count: int = 2
    rollout_global_fallback_min_gap: int = 4
    rollout_shortlist_utility_keep: int = 4
    rollout_shortlist_los_keep: int = 2
    rollout_shortlist_reflection_keep: int = 2
    rollout_shortlist_blockage_threshold: float = 0.55
    rollout_shortlist_reflection_threshold: float = 0.20
    rollout_shortlist_pathspread_threshold: float = 0.12
    los_confidence_threshold: float = 0.60
    risk_threshold: float = 0.25
    path_spread_threshold: float = 0.20
    proposedv2_fallback_cooldown_steps: int = 2
    proposedv2_risk_spike_threshold: float = 0.10
    proposedv2_local_candidate_count: int = 12
    proposedv2_global_topk_count: int = 6
    proposedv2_min_predictive_weight: float = 0.55
    proposedv2_max_predictive_weight: float = 0.90
    proposedv2_prev_beam_bonus: float = 0.08
    proposedv2_switch_penalty: float = 0.04
    proposedv2_reactive_bonus: float = 0.12
    proposedv2_reactive_distance_penalty: float = 0.06
    proposedv2_reactive_override_gap: float = 0.08
    proposedv2_global_pool_risk_threshold: float = 0.90
    proposedv2_reward_rerank_weight: float = 0.0
    proposedv2_reward_rerank_temperature: float = 0.75
    proposedv2_predictor_utility_weight: float = 0.60
    proposedv2_predictor_utility_temperature: float = 0.75
    proposedv2_use_adaptive_difficulty: bool = False
    proposedv2_rate_veto_enabled: bool = True
    proposedv2_rate_regret_threshold: float = 0.012
    proposedv2_min_safety_gain_for_fallback: float = 0.012
    proposedv2_difficulty_ema_alpha: float = 0.25
    proposedv2_easy_los_confidence_threshold: float = 0.54
    proposedv2_hard_los_confidence_threshold: float = 0.72
    proposedv2_easy_risk_threshold: float = 0.30
    proposedv2_hard_risk_threshold: float = 0.18
    proposedv2_easy_path_spread_threshold: float = 0.24
    proposedv2_hard_path_spread_threshold: float = 0.14
    proposedv2_easy_reflection_threshold: float = 0.24
    proposedv2_hard_reflection_threshold: float = 0.16
    proposedv2_easy_global_pool_risk_threshold: float = 0.95
    proposedv2_hard_global_pool_risk_threshold: float = 0.72
    proposedv2_easy_fallback_cooldown_steps: int = 1
    proposedv2_hard_fallback_cooldown_steps: int = 3
    proposedv2_easy_local_candidate_count: int = 10
    proposedv2_hard_local_candidate_count: int = 16
    proposedv2_easy_global_topk_count: int = 4
    proposedv2_hard_global_topk_count: int = 10
    proposedv2_easy_reactive_override_gap: float = 0.10
    proposedv2_hard_reactive_override_gap: float = 0.05
    proposedv2_easy_switch_penalty: float = 0.05
    proposedv2_hard_switch_penalty: float = 0.03
    proposedv2_easy_reactive_distance_penalty: float = 0.07
    proposedv2_hard_reactive_distance_penalty: float = 0.04
    proposedv2_easy_predictive_weight_scale: float = 0.92
    proposedv2_hard_predictive_weight_scale: float = 1.08
    rollout_shortlist_los_bias: float = 0.50
    rollout_shortlist_reflection_bias: float = 0.50
    rollout_shortlist_angle_bias: float = 0.25
    rollout_shortlist_include_prev_beam: bool = True
    horizon_values: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])

    rssm_min_logvar: float = -4.0
    rssm_max_logvar: float = 2.0

    def __post_init__(self) -> None:
        self.checkpoints_dir = self.project_root / "checkpoints"
        self.results_dir = self.project_root / "results"
        self.plots_dir = self.project_root / "plots"
        self.data_dir = self.project_root / "data"

    @property
    def observation_dim(self) -> int:
        return 8

    def to_dict(self) -> dict:
        data = asdict(self)
        for key in ("project_root", "checkpoints_dir", "results_dir", "plots_dir", "data_dir"):
            data[key] = str(data[key])
        return data


def get_config() -> Config:
    return Config()
