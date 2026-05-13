# Adaptive Variant Audit v1

**Date**: 2026-05-13
**Scope**: ISAC prediction regime project — adaptive difficulty feature on ProposedV2Policy
**Reviewer**: automated code audit (no human sign-off yet)

---

## 1. Changed Files

Only two files contain the adaptive logic; it is a **feature flag**, not a new policy class.

| File | Lines | Change |
|---|---|---|
| `repo/config.py` | 164–193 | Adds `proposedv2_use_adaptive_difficulty` bool + 24 new "easy/hard" parameter pairs |
| `repo/baselines.py` | 161–342, 542–553, 720, 745 | Adds `_adaptive_profile()`, `_adaptive_diagnostics()`, integrates into `_fallback_state()` and `select_action()` |
| `repo/evaluate.py` | 142–174, 265–274, 650, 690–692 | Adds adaptive diagnostics columns to step/diag recording; wires `ProposedV2_Adaptive` into ablation study |

**No new file was created.** The adaptive variant is `ProposedV2Policy` with `cfg.proposedv2_use_adaptive_difficulty = True`.

---

## 2. New Class / Function Names

- **`ProposedV2Policy._adaptive_profile(obs, risk_score, risk_delta) -> dict[str, float]`** — baselines.py:161
  Computes per-timestep `hardness` and lerps all thresholds/scoring params between "easy" and "hard" profiles.
- **`ProposedV2Policy._adaptive_diagnostics(profile) -> dict[str, float]`** — baselines.py:542
  Exports the dynamically adjusted thresholds into step-level diagnostics.

There is no new policy class. The ablation is registered under the string `"ProposedV2_Adaptive"` in `evaluate.py:690`.

---

## 3. Algorithm Difference vs ProposedV2 (default)

| Mechanism | ProposedV2 (default) | Adaptive variant |
|---|---|---|
| `risk_threshold` | Fixed `cfg.risk_threshold = 0.25` | Lerped between `easy=0.30` and `hard=0.18` based on `hardness` |
| `los_confidence_threshold` | Fixed `0.60` | Lerped between `easy=0.54` and `hard=0.72` |
| `path_spread_threshold` | Fixed `0.20` | Lerped between `easy=0.24` and `hard=0.14` |
| `reflection_threshold` | Fixed `0.20` | Lerped between `easy=0.24` and `hard=0.16` |
| `global_pool_risk_threshold` | Fixed `0.90` | Lerped between `easy=0.95` and `hard=0.72` |
| Fallback cooldown steps | Fixed `2` | Lerped between `easy=1` and `hard=3` |
| Local candidate count | Fixed `12` | Lerped between `easy=10` and `hard=16` |
| Global top-k count | Fixed `6` | Lerped between `easy=4` and `hard=10` |
| Risk spike threshold | Fixed `0.10` | Lerped between `easy=1.1×base` and `hard=0.8×base` |
| Reactive override gap | Fixed `0.08` | Lerped between `easy=0.10` and `hard=0.05` |
| Reactive distance penalty | Fixed `0.06` | Lerped between `easy=0.07` and `hard=0.04` |
| Switch penalty | Fixed `0.04` | Lerped between `easy=0.05` and `hard=0.03` |
| Predictive weight scale | Fixed `1.0` | Lerped between `easy=0.92` and `hard=1.08` |
| Reactive bonus scale | Fixed `1.0` | Lerped between `1.05` and `0.92` |
| Predictor mix delta | Fixed `0.0` | Lerped between `-0.06` and `0.08` |
| Reward weight delta | Fixed `0.0` | Lerped between `-0.02` and `0.10` |
| Safety bonus scale | Fixed `1.0` | Lerped between `0.95` and `1.22` |
| Outage penalty scale | Fixed `1.0` | Lerped between `0.95` and `1.18` |

**Hardness is computed per-timestep as:**

```
instant_difficulty = clip(
    0.30 * blocker_indicator
    + 0.18 * reflection_ratio
    + 0.16 * path_spread
    + 0.18 * snr_stress
    + 0.10 * last_outage
    + 0.06 * spike
    + 0.02 * cooldown_pressure,
    0, 1
)
hardness = clip(0.62 * difficulty_ema + 0.23 * instant_difficulty + 0.15 * delta_pressure, 0, 1)
```

Where:
- `snr_stress = clip((0.62 - snr_norm) / 0.42, 0, 1)` — low SNR → harder
- `spike = clip(risk_delta / risk_spike_threshold, 0, 1)` — sudden risk increase → harder
- `cooldown_pressure = clip(fallback_cooldown / hard_fallback_cooldown_steps, 0, 1)` — active cooldown → harder
- `difficulty_ema` and `risk_delta_ema` are EMA-smoothed with `alpha = 0.25`

Hardness floor logic:
- If `risk_score >= risk_threshold` → `hardness >= 0.45 + 0.35 * normalized_risk`
- If `last_outage > 0` → `hardness >= 0.72`
- If both `blocker_indicator >= risk_threshold` AND `reflection_ratio >= reflection_threshold` → `hardness >= 0.68`

**Design intent**: In easy scenes (clear LoS, low noise), the adaptive variant should relax thresholds (wider gating, less fallback). In hard scenes (blockage, reflection, low SNR), it should tighten thresholds (more aggressive fallback, more candidates, higher safety weight).

---

## 4. New Hyperparameters

All listed below are in `Config` (config.py:164–193) and only active when `proposedv2_use_adaptive_difficulty = True`:

| Parameter | Default | Role |
|---|---|---|
| `proposedv2_use_adaptive_difficulty` | `False` | Master toggle |
| `proposedv2_difficulty_ema_alpha` | `0.25` | EMA smoothing rate for difficulty/risk_delta |
| `proposedv2_easy_los_confidence_threshold` | `0.54` | LoS conf threshold at hardness=0 |
| `proposedv2_hard_los_confidence_threshold` | `0.72` | LoS conf threshold at hardness=1 |
| `proposedv2_easy_risk_threshold` | `0.30` | Risk threshold at hardness=0 |
| `proposedv2_hard_risk_threshold` | `0.18` | Risk threshold at hardness=1 |
| `proposedv2_easy_path_spread_threshold` | `0.24` | Path-spread threshold at hardness=0 |
| `proposedv2_hard_path_spread_threshold` | `0.14` | Path-spread threshold at hardness=1 |
| `proposedv2_easy_reflection_threshold` | `0.24` | Reflection threshold at hardness=0 |
| `proposedv2_hard_reflection_threshold` | `0.16` | Reflection threshold at hardness=1 |
| `proposedv2_easy_global_pool_risk_threshold` | `0.95` | Global pool risk threshold at hardness=0 |
| `proposedv2_hard_global_pool_risk_threshold` | `0.72` | Global pool risk threshold at hardness=1 |
| `proposedv2_easy_fallback_cooldown_steps` | `1` | Cooldown duration at hardness=0 |
| `proposedv2_hard_fallback_cooldown_steps` | `3` | Cooldown duration at hardness=1 |
| `proposedv2_easy_local_candidate_count` | `10` | Local shortlist size at hardness=0 |
| `proposedv2_hard_local_candidate_count` | `16` | Local shortlist size at hardness=1 |
| `proposedv2_easy_global_topk_count` | `4` | Global top-k at hardness=0 |
| `proposedv2_hard_global_topk_count` | `10` | Global top-k at hardness=1 |
| `proposedv2_easy_reactive_override_gap` | `0.10` | Reactive override gap at hardness=0 |
| `proposedv2_hard_reactive_override_gap` | `0.05` | Reactive override gap at hardness=1 |
| `proposedv2_easy_switch_penalty` | `0.05` | Switch penalty at hardness=0 |
| `proposedv2_hard_switch_penalty` | `0.03` | Switch penalty at hardness=1 |
| `proposedv2_easy_reactive_distance_penalty` | `0.07` | Reactive distance penalty at hardness=0 |
| `proposedv2_hard_reactive_distance_penalty` | `0.04` | Reactive distance penalty at hardness=1 |
| `proposedv2_easy_predictive_weight_scale` | `0.92` | Predictive weight scale at hardness=0 |
| `proposedv2_hard_predictive_weight_scale` | `1.08` | Predictive weight scale at hardness=1 |

---

## 5. Checkpoint Dependency

**None added.** The adaptive variant uses the same checkpoints as ProposedV2:
- `checkpoints/one_step_predictor.pt` (predictor)
- `checkpoints/belief_world_model.pt` (encoder + world_model, used for reward reranking)

No retraining, no new heads, no additional model parameters. It is purely inference-side.

---

## 6. Fairness Check

### Does it use oracle information?
**No.** Difficulty is computed from `obs[0..7]` (current observation vector) and internal state (cooldown counter, EMA history). No `env.oracle_action()` or true labels are referenced.

### Does it use future true labels?
**No.** All inputs to `_adaptive_profile()` are available at decision time — current observation, previous risk score, cooldown counter, EMA accumulators.

### Does it use different seeds / episodes / horizon?
**No.** The ablation runs it inside `run_ablation_study()` which uses the same `seeds` list as all other variants. The same `cfg.num_eval_episodes` and `cfg.episode_length` apply.

### Does it skip hard scenarios?
**No.** The difficulty computation doesn't gate or skip scenarios. It only adjusts internal thresholds. All timesteps from all episodes are processed.

### Potential concern: adaptive hardness is self-fulfilling
In easy scenes, the adaptive variant widens gates (less fallback → higher rate, lower latency). In hard scenes, it tightens gates (more fallback → higher safety). This means the adaptive variant is **optimized to trade rate-for-safety dynamically**, which is the claimed design intent. However, it introduces 24 new hyperparameters whose easy/hard split is **hand-tuned, not learned**. This should be disclosed as a limitation.

**Verdict: Fair comparison.** No oracle leakage, no future-label leakage, same seeds/horizon. The hand-tuned nature of the easy/hard profiles is a parameter-tuning concern, not a fairness concern.

---

## 7. Available Result Files

**There are NO result files for the adaptive variant.**

Searching all CSVs in `repo/results/`:
- `method_comparison.csv` — contains Reactive, OneStepPredictive, ProposedV2, Oracle, BeliefAwareRollout. No Adaptive.
- `scene_difficulty_sweep*.csv` — same five methods. No Adaptive.
- `ablation/ablation_summary.csv` — contains 9 variants (incl. ProposedV2_Full, ProposedV2_NoLoSGuard, etc.). **ProposedV2_Adaptive is absent.**
- `ablation/ablation_table.csv` — same, no Adaptive row.
- `ablation/ablation_summary_quick.csv` — same, no Adaptive row.
- `ablation/ablation_table_quick.csv` — same, no Adaptive row.
- `threshold_sweep/` — only ProposedV2 with fixed thresholds.
- `sweeps/` — blocker, speed, noise, reflection per-method-sweeps, no Adaptive.
- `paper_tables/` — LaTeX tables from the above CSVs, no Adaptive.

**Status**: The ablation pipeline (evaluate.py:690–692) registers `ProposedV2_Adaptive` in its variant list, but either:
1. The latest ablation run predates the code addition, OR
2. The run errored/failed silently on that variant and was dropped before CSV write.

---

## 8. Missing Result Files

All of the following are missing:

- [ ] `method_comparison.csv` row for `ProposedV2_Adaptive`
- [ ] `scene_difficulty_sweep*.csv` rows for `ProposedV2_Adaptive` across blocker_density, blocker_speed, obs_noise, reflection_strength sweeps
- [ ] `ablation/ablation_summary.csv` row for `ProposedV2_Adaptive`
- [ ] Per-seed breakdown in `ablation/ablation_table.csv` for `ProposedV2_Adaptive`
- [ ] Regime sweep summaries: `sweeps/blocker_density_sweep.csv`, `sweeps/blocker_speed_sweep.csv`, `sweeps/obs_noise_sweep.csv`, `sweeps/reflection_strength_sweep.csv` with Adaptive rows

---

## 9. Is This Paper-Claimable Now?

**No.**

Reasons:
1. No evaluation results exist for the adaptive variant — zero quantitative evidence.
2. The 24 easy/hard hyperparameters are hand-tuned, not learned; no sensitivity analysis has been performed.
3. The hardness formula uses hard-coded coefficients (0.30, 0.18, 0.16, 0.18, 0.10, 0.06, 0.02) and hard-coded thresholds (0.62 for SNR normalizer, 0.42 denominator, 0.45+0.35 risk floor, 0.72 outage floor, 0.68 mixed floor). These have no documented derivation or ablation.
4. The adaptive variant is not a separate algorithm — it is a parameter-scheduling layer on top of ProposedV2. Calling it a distinct contribution requires demonstrating that the scheduling produces statistically significant improvement beyond what hand-tuning fixed thresholds achieves.
5. The threshold sweep (evaluate.py:775) already shows that fixed-threshold tuning can improve return. The adaptive variant must be compared against the *best* fixed-threshold configuration, not just the default.

**What's needed for paper claim**:
- Run ablation with `--run-ablation` to get baseline adaptive vs full.
- Run scene sweeps with adaptive to get regime-level data.
- Compare adaptive vs best fixed thresholds from the threshold grid sweep.
- Report whether adaptive's dynamic scheduling outperforms the best static configuration, and in which regimes.
- Disclose the hand-tuned nature of the easy/hard profiles as a limitation.
