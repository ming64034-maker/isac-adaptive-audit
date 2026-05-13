# Tri-Regime Fallback Gate — Result Digest

## Configuration

| Parameter | Value |
|---|---|
| `proposedv2_tri_regime_gate_enabled` | True |
| `proposedv2_clear_suppress_threshold` | 0.06 |
| `proposedv2_extreme_rate_regret_threshold` | 0.012 |
| `proposedv2_extreme_min_safety_gain` | 0.012 |

## Regime Definitions

| Regime | Condition | Behavior |
|---|---|---|
| **clear** | blockage < 0.20, no outage, reflection < 0.15, path_spread < 0.15, risk < 0.25 | Suppress fallback unless safety_gain >= 0.06 |
| **medium** | Neither clear nor extreme | Keep existing ProposedV2 fallback behavior |
| **extreme** | blockage >= 0.25, outage > 0, path_spread >= 0.20, or risk >= 0.65 | Allow fallback, veto if rate_regret > 0.012 AND safety_gain < 0.012 |

## Main Comparison

| Method | Rate | Outage | Bsucc | Return | Latency (ms) |
|---|---|---|---|---|---|
| ProposedV2 (baseline) | 5.0648 | 0.0723 | 0.7933 | **4.8809** | 0.2784 |
| ProposedV2 (tri-regime) | 5.0310 | 0.0788 | 0.7848 | **4.8298** | 0.2868 |
| Reactive | 5.0102 | 0.1058 | 0.7415 | 4.7439 | 0.0028 |

**Return change vs baseline: -0.0511**

## Tri-Regime Diagnostics

| Metric | Value |
|---|---|
| Avg regime mode (0=clear, 1=medium, 2=extreme) | 1.369 |
| Clear suppress trigger rate | 4.46% |
| Extreme veto trigger rate | 1.88% |
| Reactive veto trigger rate | 0.38% |
| Fallback kept after all vetoes | 23.93% |

## Scene Sweep: Failure Point Comparison

### obs_noise = 0.00

| Method | Return (baseline) | Return (tri-regime) |
|---|---|---|
| ProposedV2 | 4.9976 | 5.0385 |
| Reactive | 5.1828 | 5.1828 |
| Deficit | -0.1852 | **-0.1443** |
| ProposedV2 Outage | 0.0465 | 0.0450 |

Deficit improved by **+0.0409** (22.1% reduction). Outage better than Reactive (0.0450 vs 0.0495). ✓

### obs_noise = 0.02

| Method | Return (baseline) | Return (tri-regime) |
|---|---|---|
| ProposedV2 | 5.0631 | 5.1392 |
| Reactive | 5.2195 | 5.2195 |
| Deficit | -0.1564 | **-0.0803** |
| ProposedV2 Outage | 0.0508 | 0.0525 |

Deficit improved by **+0.0761** (48.7% reduction). Outage better than Reactive (0.0525 vs 0.0568). ✓

### blocker_density = 3.00

| Method | Return (baseline) | Return (tri-regime) |
|---|---|---|
| ProposedV2 | 4.2601 | 4.3039 |
| Reactive | 4.3671 | 4.3671 |
| Deficit | -0.1070 | **-0.0632** |
| ProposedV2 Outage | 0.1025 | 0.1055 |

Deficit improved by **+0.0438** (40.9% reduction). Outage massively better than Reactive (0.1055 vs 0.1455). ✓

## Key Finding

All three failure points improved substantially (22–49% deficit reduction). Outage advantage over Reactive preserved at all points. However, the main comparison return dropped by 0.0511 due to over-suppression in the clear regime — the clear_suppress_threshold of 0.06 blocks too many beneficial fallbacks in normal operating conditions, outweighing the gains in hard regimes.
