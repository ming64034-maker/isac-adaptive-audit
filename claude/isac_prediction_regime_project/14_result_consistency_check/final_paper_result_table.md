# Final Paper Result Table

## Table 1. Main Method Comparison

| Method | Avg Rate | Outage Prob | Beam Success | Return | Latency (ms) |
|---|---:|---:|---:|---:|---:|
| ProposedV2 (Ours) | **5.064** | **0.072** | **0.793** | **4.881** | 0.286 |
| Reactive | 5.010 | 0.106 | 0.742 | 4.744 | 0.003 |
| Belief-Aware Rollout | 4.900 | 0.108 | 0.745 | 4.633 | 0.815 |
| One-Step Predictive | 4.094 | 0.042 | 0.873 | 3.999 | 0.266 |
| Oracle (upper bound) | 6.033 | 0.000 | 0.920 | 6.016 | 1.568 |

## Table 2. Scene Sweep Summary: ProposedV2 vs Reactive

| Dimension | Value | ProposedV2 Return | Reactive Return | Delta | ProposedV2 Outage | Reactive Outage |
|---|---|---:|---:|---:|---:|---:|
| blocker_density | 0.0 | 5.153 | 5.088 | +0.065 | 0.055 | 0.071 |
| blocker_density | 1.0 | 4.825 | 4.777 | +0.048 | 0.074 | 0.101 |
| blocker_density | 2.0 | 4.687 | 4.607 | +0.081 | 0.084 | 0.120 |
| blocker_density | 3.0 | 4.258 | 4.367 | -0.109 | 0.101 | 0.145 |
| obs_noise | 0.00 | 4.994 | 5.183 | -0.189 | 0.046 | 0.050 |
| obs_noise | 0.02 | 5.065 | 5.220 | -0.155 | 0.053 | 0.057 |
| obs_noise | 0.05 | 4.862 | 4.763 | +0.098 | 0.071 | 0.099 |
| obs_noise | 0.10 | 4.407 | 3.731 | +0.676 | 0.086 | 0.178 |
| blocker_speed | 0.5 | 4.748 | 4.695 | +0.054 | 0.068 | 0.109 |
| blocker_speed | 1.0 | 4.881 | 4.744 | +0.137 | 0.072 | 0.106 |
| blocker_speed | 1.5 | 4.841 | 4.821 | +0.020 | 0.074 | 0.099 |
| blocker_speed | 2.0 | 4.724 | 4.771 | -0.047 | 0.075 | 0.096 |
| reflection_strength | weak | 4.677 | 4.689 | -0.012 | 0.114 | 0.133 |
| reflection_strength | medium | 4.769 | 4.740 | +0.030 | 0.081 | 0.107 |
| reflection_strength | baseline | 4.881 | 4.744 | +0.137 | 0.072 | 0.106 |
| reflection_strength | strong | 4.876 | 4.705 | +0.170 | 0.066 | 0.106 |

## Final Headline Counts

- Outage wins vs Reactive: `16/16`
- Beam-success wins vs Reactive: `16/16`
- Return wins vs Reactive: `11/16`
- Rate wins vs Reactive: `6/16`
