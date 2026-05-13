# Updated Number Diff

## Main Comparison

CSV-to-CSV ProposedV2 baseline change after disabling paper-facing veto and tri-regime gates:

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Avg Rate | 5.030 | 5.064 | +0.034 |
| Outage Prob | 0.077 | 0.072 | -0.006 |
| Beam Success | 0.787 | 0.793 | +0.007 |
| Return | 4.833 | 4.881 | +0.048 |
| Latency (ms) | 0.302 | 0.286 | -0.017 |

Paper-table sync changes in Section 4.2:

| Cell | Old Paper | New Paper |
|---|---:|---:|
| ProposedV2 latency | 0.278 | 0.286 |
| Belief-Aware Rollout latency | 0.780 | 0.815 |
| One-Step Predictive latency | 0.258 | 0.266 |
| Oracle latency | 1.563 | 1.568 |

## Scene Sweep

Section 4.3 ProposedV2 vs Reactive table changes:

| Dimension | Value | ProposedV2 Return Before | ProposedV2 Return After | Delta | ProposedV2 Outage Before | ProposedV2 Outage After |
|---|---|---:|---:|---:|---:|---:|
| blocker_density | 0.0 | 5.132 | 5.153 | +0.021 | 0.060 | 0.055 |
| blocker_density | 1.0 | 4.813 | 4.825 | +0.012 | 0.077 | 0.074 |
| blocker_density | 2.0 | 4.638 | 4.687 | +0.049 | 0.089 | 0.084 |
| blocker_density | 3.0 | 4.270 | 4.258 | -0.013 | 0.103 | 0.101 |
| obs_noise | 0.00 | 4.998 | 4.994 | -0.043 | 0.047 | 0.046 |
| obs_noise | 0.02 | 5.063 | 5.065 | +0.002 | 0.051 | 0.053 |
| obs_noise | 0.05 | 4.839 | 4.862 | +0.025 | 0.074 | 0.071 |
| obs_noise | 0.10 | 4.349 | 4.407 | +0.058 | 0.090 | 0.086 |
| blocker_speed | 0.5 | 4.723 | 4.748 | +0.026 | 0.072 | 0.068 |
| blocker_speed | 1.0 | 4.842 | 4.881 | +0.039 | 0.077 | 0.072 |
| blocker_speed | 1.5 | 4.791 | 4.841 | +0.050 | 0.081 | 0.074 |
| blocker_speed | 2.0 | 4.735 | 4.724 | -0.011 | 0.080 | 0.075 |
| reflection_strength | weak | 4.676 | 4.677 | +0.001 | 0.120 | 0.114 |
| reflection_strength | medium | 4.769 | 4.769 | +0.000 | 0.085 | 0.081 |
| reflection_strength | baseline | 4.842 | 4.881 | +0.039 | 0.077 | 0.072 |
| reflection_strength | strong | 4.872 | 4.876 | +0.004 | 0.067 | 0.066 |

## Aggregate Sweep Summary Change

| Summary Item | Before | After |
|---|---:|---:|
| Return wins vs Reactive | 10/16 | 11/16 |
| Rate wins vs Reactive | 6/16 | 6/16 |
| Outage wins vs Reactive | 16/16 | 16/16 |
| Beam-success wins vs Reactive | 16/16 | 16/16 |

Return-loss points after the fix:

- `obs_noise = 0.00`: `-0.189`
- `obs_noise = 0.02`: `-0.155`
- `blocker_density = 3.00`: `-0.109`
- `blocker_speed = 2.00`: `-0.047`
- `reflection_strength = weak`: `-0.012`
