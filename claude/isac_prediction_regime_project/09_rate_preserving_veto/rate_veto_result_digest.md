# Rate-Preserving Fallback Veto v2 — Result Digest

## Configuration

| Parameter | Conservative (v1) | Aggressive (v2) |
|---|---|---|
| `proposedv2_rate_regret_threshold` | 0.04 | 0.012 |
| `proposedv2_min_safety_gain_for_fallback` | 0.015 | 0.012 |

## Main Comparison

| Metric | Baseline (no veto) | Conservative (0.04/0.015) | Aggressive (0.012/0.012) |
|---|---|---|---|
| Average Rate | 5.0648 | 5.0648 | 5.0430 |
| Outage Prob | 0.0723 | 0.0723 | 0.0738 |
| Beam Success | 0.7933 | 0.7933 | 0.7918 |
| **Return** | **4.8809** | **4.8808** | **4.8545** |
| Latency (ms) | 0.2784 | 0.2795 | 0.2784 |

### Veto Diagnostics

| Metric | Conservative | Aggressive |
|---|---|---|
| Veto Fire Rate | 0.45% | 2.94% |
| Fallback Kept After Veto | 99.55% | 27.06% |

## Scene Sweep: Failure Point Comparison

### obs_noise = 0.00 (near-perfect observation)

| Method | Return (Conservative) | Return (Aggressive) |
|---|---|---|
| ProposedV2 | 4.9976 | 5.0245 |
| Reactive | 5.1828 | 5.1828 |
| Deficit | -0.1852 | -0.1584 |
| ProposedV2 Outage | 0.0465 | 0.04475 |

Deficit improved by **+0.0268**. Outage still better than Reactive (0.04475 vs 0.0495). ✓

### obs_noise = 0.02 (very low noise)

| Method | Return (Conservative) | Return (Aggressive) |
|---|---|---|
| ProposedV2 | 5.0631 | 5.1108 |
| Reactive | 5.2195 | 5.2195 |
| Deficit | -0.1564 | -0.1088 |
| ProposedV2 Outage | 0.05075 | 0.05225 |

Deficit improved by **+0.0476**. Outage still better than Reactive (0.05225 vs 0.05675). ✓

### blocker_density = 3.00 (most congested)

| Method | Return (Conservative) | Return (Aggressive) |
|---|---|---|
| ProposedV2 | 4.2601 | 4.2874 |
| Reactive | 4.3671 | 4.3671 |
| Deficit | -0.1070 | -0.0796 |
| ProposedV2 Outage | 0.1025 | 0.09925 |

Deficit improved by **+0.0274**. Outage still much better than Reactive (0.09925 vs 0.1455). ✓

## Key Finding

All three failure points improved with the aggressive veto. The veto correctly identifies and blocks fallback decisions where the safety gain does not justify the rate loss in these hard scenarios. However, the aggressive thresholds also block beneficial fallbacks in easy/medium scenarios, causing the **overall return to drop by 0.0263**.
