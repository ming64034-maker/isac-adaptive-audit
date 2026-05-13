# Adaptive vs ProposedV2_Full — Result Table

**Date**: 2026-05-13
**Data source**: `results/ablation/ablation_summary.csv` (rerun `--run-ablation --seeds 2 --eval-episodes 2`)
**Eval protocol**: seeds [0, 1], 2 episodes each, 200 slots per episode. Identical checkpoints, identical env seeds across variants.

---

## Main Comparison Table

| Method | Rate | Outage | Beam Success | Return | Latency (ms) |
|---|---|---|---|---|---|
| Reactive | 4.8230 | 0.1075 | 0.7388 | 4.5552 | 0.0027 |
| ProposedV2_Full | 4.8128 | 0.0675 | 0.7975 | 4.6392 | 0.2776 |
| **ProposedV2_Adaptive** | **4.7529** | **0.0725** | **0.7925** | **4.5700** | **0.2994** |
| Oracle (upper bound) | 5.7878 | 0.0000 | 0.9088 | 5.7735 | 1.5144 |

---

## Delta vs ProposedV2_Full

| Metric | ProposedV2_Full | ProposedV2_Adaptive | Δ (Adaptive − Full) | Direction |
|---|---|---|---|---|
| Rate | 4.8128 | 4.7529 | **−0.0599** | Worse |
| Outage | 0.0675 | 0.0725 | **+0.0050** | Worse |
| Beam Success | 0.7975 | 0.7925 | **−0.0050** | Worse |
| Return | 4.6392 | 4.5700 | **−0.0692** | Worse |
| Latency (ms) | 0.2776 | 0.2994 | **+0.0218** | Worse |

Adaptive **underperforms Full on all five metrics** in this 2-seed run.

---

## Delta vs Reactive

| Metric | Reactive | ProposedV2_Adaptive | Δ (Adaptive − Reactive) | Direction |
|---|---|---|---|---|
| Rate | 4.8230 | 4.7529 | −0.0701 | Worse |
| Outage | 0.1075 | 0.0725 | −0.0350 | Better |
| Beam Success | 0.7388 | 0.7925 | +0.0538 | Better |
| Return | 4.5552 | 4.5700 | +0.0149 | Better |
| Latency (ms) | 0.0027 | 0.2994 | +0.2967 | Worse |

Adaptive beats Reactive on outage (−0.035), beam success (+0.054), and return (+0.015), but loses on rate (−0.070) and latency (+0.297 ms).

---

## Per-Seed Breakdown (ablation_table.csv)

| Seed | Method | Rate | Outage | Beam Success | Return |
|---|---|---|---|---|---|
| 0 | Reactive | 4.6378 | 0.1175 | 0.7300 | 4.3514 |
| 0 | ProposedV2_Full | 4.7605 | 0.0750 | 0.7875 | 4.5696 |
| 0 | ProposedV2_Adaptive | 4.6961 | 0.0775 | 0.7800 | 4.5013 |
| 1 | Reactive | 5.0083 | 0.0975 | 0.7475 | 4.7589 |
| 1 | ProposedV2_Full | 4.8651 | 0.0600 | 0.8075 | 4.7087 |
| 1 | ProposedV2_Adaptive | 4.8097 | 0.0675 | 0.8050 | 4.6387 |

- Seed 0: Adaptive return = 4.5013 vs Full 4.5696 → **gap −0.0683**
- Seed 1: Adaptive return = 4.6387 vs Full 4.7087 → **gap −0.0699**
- Gap direction is **consistent across both seeds**.

---

## Missing Data

| Data Product | Status |
|---|---|
| Scene difficulty sweep with Adaptive rows | **Missing** — not run, not in sweep pipeline |
| Threshold sweep for Adaptive | **Missing** — not applicable (adaptive lerps thresholds) |
| Event analysis with Adaptive | **Missing** |
| Per-step diagnostics for Adaptive (fallback rate, veto rate, hardness) | **Missing** — ablation does not save step-level CSVs |
| Full 5-seed run | **Missing** — only 2 seeds evaluated |

**Cannot analyze**: whether adaptive fixes the obs_noise=0.00/0.02 and blocker_density=3.00 failure points identified in result_summary.md. Scene sweep data for adaptive does not exist.

---

## Caveats

1. **2 seeds only** — standard error of the mean is not reported. The 5-seed full run gives narrower confidence intervals.
2. **Default scene parameters** — Nb=1–2, default blocker speed, default noise. Failure regime analysis requires scene sweeps with adaptive enabled.
3. **Hand-tuned easy/hard profiles** — the adaptive profile coefficients were set by hand. These results reflect the current parameterization, not the best possible adaptive tuning.
