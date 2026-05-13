# Adaptive Integration Decision

**Date**: 2026-05-13
**Decision**: **C — Adaptive 暂时不进论文**
**Basis**: Ablation result table (2-seed), scene sweep baseline, failure regime analysis.

---

## Decision Options

| Option | Label | Criteria |
|---|---|---|
| A | Adaptive 替代 ProposedV2 成为主方法 | Adaptive > Full on return AND ≥1 regime where it fixes a known failure |
| B | Adaptive 作为 ablation / enhancement | Adaptive ≤ Full but demonstrates regime-specific benefit that is explainable |
| C | Adaptive 暂时不进论文 | Adaptive < Full AND does not address any documented failure point |

---

## Evidence Supporting Decision C

### Point 1: Adaptive underperforms Full on all metrics

From `ablation_summary.csv` (2 seeds, 2 episodes, default scene):

| Metric | ProposedV2_Full | ProposedV2_Adaptive | Δ |
|---|---|---|---|
| Rate | 4.8128 | 4.7529 | −0.0599 |
| Outage | 0.0675 | 0.0725 | +0.0050 |
| Beam Success | 0.7975 | 0.7925 | −0.0050 |
| Return | 4.6392 | 4.5700 | −0.0692 |
| Latency (ms) | 0.2776 | 0.2994 | +0.0218 |

Direction is consistent across both seeds (seed 0: −0.0683 return, seed 1: −0.0699 return).

**This alone disqualifies option A.** A replacement must be at least non-inferior.

### Point 2: No regime-level evidence of benefit

The three documented ProposedV2 failure points require scene sweep data with adaptive — none exists:

- obs_noise=0.00: no adaptive data
- obs_noise=0.02: no adaptive data
- blocker_density=3.00: no adaptive data

**This disqualifies option B for now.** Without regime data, there is no way to claim adaptive has regime-specific value.

### Point 3: The design direction may be wrong for the hardest regime

The blocker_density=3.00 return deficit arises because ProposedV2's predictor-driven fallback actions sacrifice too much rate. The adaptive variant at high hardness makes fallback *more aggressive* (tightens thresholds, increases candidate count, raises safety weight). This would amplify the rate penalty, not reduce it. The root cause is predictor quality in dense blockage, not threshold scheduling.

### Point 4: 24 hand-tuned parameters with no sensitivity analysis

The adaptive profile uses 24 config parameters (easy/hard pairs), all set by hand. No ablation exists for coefficient weights (0.30 blocker, 0.18 reflection, etc.). A reviewer will ask how these were chosen. Without a sensitivity analysis or a principled derivation, the adaptive variant is a parameter tuning exercise, not an algorithmic contribution.

---

## What Would Be Needed for Option B (future)

For adaptive to be paper-claimable as an ablation/enhancement:

1. **Scene sweep data** — run adaptive across all 16 scene sweep points (blocker ×4, speed ×4, noise ×4, reflection ×4)
2. **Regime-specific benefit** — show at least one regime where Adaptive > Full on return, with diagnostic evidence that hardness correctly tracks scene difficulty
3. **Coefficient justification** — either derive the difficulty weights from data or ablate them
4. **Comparison against best fixed thresholds** — from threshold_sweep, select the best static configuration and show adaptive beats it in at least one regime
5. **Ablation of adaptive components** — show which part of the adaptive profile (threshold lerping, candidate expansion, safety scaling) drives the benefit

---

## What Happens Now

- Adaptive code stays in `baselines.py` and `config.py` (no removal).
- `ProposedV2_Adaptive` stays registered in `run_ablation_study()` for future reference.
- Paper continues with ProposedV2 (fixed thresholds) as the main hybrid method.
- Adaptive is not mentioned in abstract, introduction, or conclusion.
- If mentioned at all, it belongs in an "attempted extensions" paragraph in discussion/limitations, with the negative result disclosed.

---

## Verification

The following table summarizes the evidence against each integration option:

| Requirement | A (replace) | B (ablation) | C (not in paper) |
|---|---|---|---|
| Adaptive return ≥ Full return | ❌ −0.0692 | Not required | — |
| Adaptive fixes ≥1 known failure | No data | No data | — |
| Regime sweep data exists | No | No | — |
| Coefficient derivation exists | No | No | — |
| Comparison vs best fixed threshold | No | No | — |

All paths currently point to C.

**Final decision: Adaptive 暂时不进论文。保留代码，待后续补数据后重新评估。**
