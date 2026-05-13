# Adaptive Result Digest v1

**Date**: 2026-05-13
**Status**: **No paper-claimable result yet.**

---

## Result Availability

| Data type | Reactive | ProposedV2 | ProposedV2_Adaptive |
|---|---|---|---|
| Method comparison (rate, outage, success, return, latency) | Present | Present | **Missing** |
| Regime sweep — blocker_density | Present | Present | **Missing** |
| Regime sweep — blocker_speed | Present | Present | **Missing** |
| Regime sweep — obs_noise | Present | Present | **Missing** |
| Regime sweep — reflection_strength | Present | Present | **Missing** |
| Ablation study | Present | Present | **Missing** |
| Threshold sweep | N/A | Present | N/A |
| Event analysis (blockage onset recovery) | Present | Present | **Missing** |
| Per-step diagnostics (adaptive thresholds logged) | N/A | Always 0.5 (default) | **Missing** |

---

## If Results Existed, the Expected Comparison Table Would Look Like

This is a **template only** — no data has been produced.

| Method | Rate | Outage | Beam Success | Return | Latency (ms) |
|---|---|---|---|---|---|
| Reactive | 5.0102 | 0.1058 | 0.7415 | 4.7439 | ~0.003 |
| ProposedV2 (default, fixed) | 5.0637 | 0.0718 | 0.7930 | 4.8809 | ~0.283 |
| ProposedV2_Adaptive | ? | ? | ? | ? | ? |
| Oracle (upper bound) | 6.0327 | 0.0000 | 0.9200 | 6.0163 | ~1.550 |

Expected deltas to compute once data exists:

| Comparison | Expected Columns |
|---|---|
| Adaptive vs Reactive | Δ rate, Δ outage, Δ beam_success, Δ return, %Δ return, Δ latency |
| Adaptive vs ProposedV2 (default) | Δ rate, Δ outage, Δ beam_success, Δ return, %Δ return, Δ latency |

---

## Regime Sweep Summary

**No data exists.** The expected sweep dimensions are:

| Sweep | Values | H0 |
|---|---|---|
| blocker_density | Nb = 0, 1, 2, 3 | Adaptive should show largest advantage at Nb=2,3 (hardest) |
| blocker_speed | 0.5x, 1.0x, 1.5x, 2.0x | Adaptive should handle speed transients better via spike detection |
| obs_noise | 0.00, 0.02, 0.05, 0.10 | Adaptive should be conditionally better at high noise |
| reflection_strength | 0.3x, 0.6x, 1.0x, 1.5x | Adaptive should adjust thresholds for reflection-dominated scenes |

---

## Latency Comparison

**No data exists.** Expected metrics:
- ProposedV2 (default) median latency: ~0.28 ms (from existing results)
- Adaptive should have **slightly higher** latency than default ProposedV2 (extra computation in `_adaptive_profile()`), but likely within measurement noise since the overhead is ~10 float operations.
- When hardness is low, adaptive may save latency by using fewer candidates; when hardness is high, adaptive may spend more latency with more candidates and more global pool usage.

---

## What the Existing Baseline Results Say (Context Only)

From `method_comparison.csv` (seeds 0–4, 4 episodes each, 200 slots, existing checkpoints):

| Method | Rate | Outage | Beam Success | Return |
|---|---|---|---|---|
| Reactive | 5.0102 | 0.1058 | 0.7415 | 4.7439 |
| ProposedV2 | 5.0637 | 0.0718 | 0.7930 | 4.8809 |

- ProposedV2 over Reactive: +0.0535 rate, −0.0340 outage, +0.0515 beam success, +0.1370 return (+2.89%).
- The adaptive variant should be compared against both of these baselines, and ideally also against the best fixed-threshold configuration from the threshold sweep.

---

## Bottom Line

**No adaptive evaluation has been produced. The variant code exists but has never been executed in any evaluation run visible in the results directory.** The audit in `adaptive_variant_audit_v1.md` confirms the code is fairly designed (no oracle leakage), but until results are generated, zero claims can be made.
