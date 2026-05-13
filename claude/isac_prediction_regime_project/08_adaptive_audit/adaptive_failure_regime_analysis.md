# Adaptive Failure Regime Analysis

**Date**: 2026-05-13
**Motivation**: `result_summary.md` identifies three failure points where ProposedV2 underperforms Reactive on return — obs_noise=0.00, obs_noise=0.02, blocker_density=3.00. PI asks: does adaptive fix the "over-conservative fallback in easy scenes and hardest density" problem?

---

## 1. Baseline: ProposedV2 Failure Points (from scene_sweep_summary.csv, 5 seeds)

### obs_noise=0.00 (cleanest scene)

| Method | Rate | Outage | Beam Success | Return | Return vs Reactive |
|---|---|---|---|---|---|
| Reactive | 5.3130 | 0.0495 | 0.8475 | 5.1828 | — |
| ProposedV2 | 5.1183 | 0.0460 | 0.8613 | 5.0023 | **−0.1805** |

ProposedV2 sacrifices 0.195 rate to save 0.0035 outage. The rate-outage trade is highly unfavorable. Fallback engages too often in a scene that doesn't need it.

### obs_noise=0.02 (quiet scene)

| Method | Rate | Outage | Beam Success | Return | Return vs Reactive |
|---|---|---|---|---|---|
| Reactive | 5.3685 | 0.0568 | 0.8245 | 5.2195 | — |
| ProposedV2 | 5.2069 | 0.0523 | 0.8370 | 5.0745 | **−0.1450** |

Same pattern: −0.162 rate for −0.0045 outage. Fallback is net-negative.

### blocker_density=3.00 (hardest scene)

| Method | Rate | Outage | Beam Success | Return | Return vs Reactive |
|---|---|---|---|---|---|
| Reactive | 4.7145 | 0.1455 | 0.7250 | 4.3671 | — |
| ProposedV2 | 4.4951 | 0.1030 | 0.7808 | 4.2575 | **−0.1096** |

This scene IS hard (14.55% outage). ProposedV2 reduces outage by 4.25pp, but the rate cost (−0.219) outweighs the safety gain. Return is still lower.

---

## 2. Can Adaptive Fix These? Expected Mechanism

The adaptive variant computes per-timestep `hardness` from:
- Blocker indicator (weight 0.30)
- SNR stress (weight 0.18)
- Reflection ratio (weight 0.18)
- Path spread (weight 0.16)
- Outage history (weight 0.10)
- Risk spike (weight 0.06)
- Cooldown pressure (weight 0.02)

**Expected behavior by scene**:

| Scene | Observed Signals | Expected Hardness | Expected Effect |
|---|---|---|---|
| obs_noise=0.00 | Clean SNR, low blocker, low spread | LOW (~0.2–0.3) | Relax thresholds → less fallback → rate recovery |
| obs_noise=0.02 | Near-clean SNR, low blocker | LOW (~0.25–0.35) | Relax thresholds → less fallback |
| blocker_density=3.00 | High blocker, frequent outage, high spread | HIGH (~0.7–0.9) | Tighten thresholds → more candidates, higher safety weight (intended) BUT: this DOES NOT fix the rate deficit when the scene is inherently rate-limited |

**Critical tension**: For blocker_density=3.00, making fallback more aggressive (as adaptive does at high hardness) INCREASES the rate penalty because more fallback means more predictor-driven actions that sacrifice angle alignment for predicted safety. The return deficit at Nb=3 may be **structural** (the predictor cannot find high-rate beams in dense blockage), not a tuning issue.

---

## 3. Actual Adaptive Performance vs Full (Default Scene, 2-seed Ablation)

The only data available with Adaptive is the default-scene ablation (Nb=1–2, default speed/noise):

| Method | Rate | Outage | Return | Δ Return vs Reactive | Δ Return vs Full |
|---|---|---|---|---|---|
| Reactive | 4.8230 | 0.1075 | 4.5552 | — | −0.0840 |
| ProposedV2_Full | 4.8128 | 0.0675 | 4.6392 | +0.0840 | — |
| ProposedV2_Adaptive | 4.7529 | 0.0725 | 4.5700 | +0.0149 | **−0.0692** |

**Finding**: In the default scene (moderate difficulty), Adaptive underperforms Full by 0.0692 return. It is closer to Reactive than to Full.

This suggests the adaptive difficulty is pushing thresholds in the **wrong direction** for the default scene — it's either:
- (a) Not relaxing enough in the moderate/default scene, causing unnecessary fallback, OR
- (b) Relaxing too much in some segments and losing outage protection, OR
- (c) The hand-tuned easy/hard profiles are miscalibrated

Without per-step diagnostics (hardness, fallback rate, veto rate per timestep), we cannot distinguish between these hypotheses.

---

## 4. Missing Data for Regime Analysis

| Required Analysis | Status | Why Missing |
|---|---|---|
| Adaptive at obs_noise=0.00 | **No data** | Scene sweep pipeline does not include adaptive variant |
| Adaptive at obs_noise=0.02 | **No data** | Same |
| Adaptive at blocker_density=3.00 | **No data** | Same |
| Per-step hardness per regime | **No data** | Ablation doesn't save step-level diagnostics |
| Adaptive fallback rate vs Full fallback rate | **No data** | Not tracked in ablation summary |
| Adaptive reactive veto rate | **No data** | Not tracked in ablation summary |

To get this data, `evaluate.py:run_scene_difficulty_sweeps()` would need to be modified to include an Adaptive variant (it currently runs Reactive, OneStepPredictive, ProposedV2, Oracle, BeliefAwareRollout only).

---

## 5. Partial Inference from Available Data

**From default-scene ablation (2 seeds)**:
- Adaptive return = 4.5700 vs Full 4.6392 → **gap −0.0692**
- Adaptive rate = 4.7529 vs Full 4.8128 → Adaptive sacrifices **more rate** (−0.0599)
- Adaptive outage = 0.0725 vs Full 0.0675 → Adaptive has **worse outage** (+0.0050)

If Adaptive is sacrificing MORE rate for WORSE outage in the default scene, it is unlikely to fix the rate deficit at obs_noise=0.00 or obs_noise=0.02. The adaptive thresholds appear to be too conservative on average, not too relaxed.

**For blocker_density=3.00**: Even if adaptive correctly identifies high hardness and tightens fallback, the fundamental problem is that predictor-driven actions in dense blockage cannot find high-rate beams. Making fallback MORE aggressive (higher safety weight, more candidates) would INCREASE the rate gap, not reduce it.

---

## 6. Verdict on Failure Regime Fixes

| Failure Point | Does Adaptive Fix It? | Evidence |
|---|---|---|
| obs_noise=0.00 (easy, return deficit) | **Unlikely** — Adaptive is more conservative than Full overall | Default scene: Adaptive rate < Full rate |
| obs_noise=0.02 (easy, return deficit) | **Unlikely** — same reason | Default scene: Adaptive rate < Full rate |
| blocker_density=3.00 (hard, return deficit) | **Unlikely** — structural predictor limitation | Hardness ↑ → more fallback → more rate penalty, not less |

**Bottom line**: Based on currently available data, the adaptive variant does not address ProposedV2's core failure modes. In the default scene, it is strictly worse than Full. The hand-tuned easy/hard profiles push thresholds toward over-conservatism rather than adaptive relaxation. The blocker_density=3.00 return deficit is likely a predictor quality limitation, not a threshold-scheduling problem.
