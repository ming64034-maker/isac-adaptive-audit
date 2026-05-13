# Tri-Regime Light Retune — Result Digest

## Configuration

| Parameter | Original (0.06) | Retune A (0.03) | Retune B (0.02) |
|---|---|---|---|
| `proposedv2_clear_suppress_threshold` | 0.06 | **0.03** | **0.02** |
| `proposedv2_extreme_rate_regret_threshold` | 0.012 | 0.012 | 0.012 |
| `proposedv2_extreme_min_safety_gain` | 0.012 | 0.012 | 0.012 |
| Tri-regime definitions | unchanged | unchanged | unchanged |
| Medium regime behavior | unchanged | unchanged | unchanged |

## Main Comparison

| Variant | Rate | Outage | Bsucc | Return | Δ vs Baseline |
|---|---|---|---|---|---|
| Baseline ProposedV2 | 5.0648 | 0.0723 | 0.7933 | **4.8809** | — |
| Tri-regime (0.06) | 5.0310 | 0.0788 | 0.7848 | 4.8298 | -0.0511 |
| Tri-regime (0.03) | 5.0385 | 0.0768 | 0.7875 | 4.8421 | -0.0388 |
| Tri-regime (0.02) | 5.0300 | 0.0772 | 0.7865 | 4.8328 | -0.0481 |

Both retunes remain below baseline. 0.03 performs best among the three tri-regime variants but still loses 0.0388 in average return.

## Scene Sweep: Failure Points (0.03 retune)

### obs_noise = 0.00

| Method | Return (baseline) | Return (0.03) |
|---|---|---|
| ProposedV2 | 4.9976 | 5.0370 |
| Reactive | 5.1828 | 5.1828 |
| Deficit | -0.1852 | **-0.1458** |
| ProposedV2 Outage | 0.0465 | 0.0450 |

Deficit improved by **+0.0394** (21.3% reduction). Outage better than Reactive (0.0450 vs 0.0495). ✓

### obs_noise = 0.02

| Method | Return (baseline) | Return (0.03) |
|---|---|---|
| ProposedV2 | 5.0631 | 5.1297 |
| Reactive | 5.2195 | 5.2195 |
| Deficit | -0.1564 | **-0.0898** |
| ProposedV2 Outage | 0.0508 | 0.0532 |

Deficit improved by **+0.0666** (42.6% reduction). Outage better than Reactive (0.0532 vs 0.0568). ✓

### blocker_density = 3.00

| Method | Return (baseline) | Return (0.03) |
|---|---|---|
| ProposedV2 | 4.2601 | 4.2704 |
| Reactive | 4.3671 | 4.3671 |
| Deficit | -0.1070 | **-0.0967** |
| ProposedV2 Outage | 0.1025 | 0.1030 |

Deficit improved by **+0.0103** (9.6% reduction). Outage massively better than Reactive (0.1030 vs 0.1455). ✓

## Diagnostics (0.03 retune)

| Metric | 0.06 | 0.03 | 0.02 |
|---|---|---|---|
| Tri-regime mode avg | 1.369 | — | 1.368 |
| Clear suppress rate | 4.46% | — | 3.93% |
| Extreme veto rate | 1.88% | — | 1.89% |
| Fallback kept after vetoes | 23.93% | — | 26.84% |

Clear suppress rate drops from 4.46% to 3.93% when lowering threshold from 0.06 to 0.02, but the structural over-suppression in clear regime persists.

## Key Finding

Lowering `clear_suppress_threshold` from 0.06 to 0.03 recovers about 25% of the lost average return (deficit from -0.0511 to -0.0388), confirming the clear-suppress is the dominant mechanism driving the regression. However, even the best retune (0.03) cannot reach baseline return. Further threshold reduction would converge to effectively disabling the clear suppress, at which point the tri-regime gate reduces to the original rate-preserving veto — which was already rejected for main return regression.
