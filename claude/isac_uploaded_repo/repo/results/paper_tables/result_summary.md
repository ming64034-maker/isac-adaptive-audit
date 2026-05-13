# Result Summary

## Source Files
- loaded: /Users/cccwm/Documents/New project/claude/isac_uploaded_repo/repo/results/method_comparison.csv
- loaded: /Users/cccwm/Documents/New project/claude/isac_uploaded_repo/repo/results/sweeps/scene_sweep_summary.csv
- loaded: /Users/cccwm/Documents/New project/claude/isac_uploaded_repo/repo/results/ablation/ablation_summary.csv
- loaded: /Users/cccwm/Documents/New project/claude/isac_uploaded_repo/repo/results/threshold_sweep/best_thresholds.csv
- loaded: /Users/cccwm/Documents/New project/claude/isac_uploaded_repo/repo/results/events/blockage_event_summary.csv

## Findings
- ProposedV2 vs Reactive: rate gain 0.0535, outage reduction 0.0340, beam-success gain 0.0515.
- Scene sweeps: across 16 comparable points, ProposedV2 beats or matches Reactive on outage at 16/16 points, on beam success at 16/16, on return at 11/16, and on rate at 6/16. The largest return deficits appear at `obs_noise=0.00`, `obs_noise=0.02`, `blocker_density=3.00`, which points to over-conservative fallback usage in easy scenes and at the hardest density setting.
- Ablation: `ProposedV2_NoLoSGuard` causes the largest return drop (0.9959); in the current thresholds this behaves close to always-on predictive fallback, so the result says the guard/gating logic is essential for preserving throughput. Removing predictive fallback costs 0.1429 return and raises outage by 0.0262.
- Recommended thresholds from the sweep: los_confidence=0.800, risk=0.250, path_spread=0.200.
- Blockage onset recovery: ProposedV2 recovers 0.166 slots faster than Reactive on average.

These statements are based only on the available CSV files and should be treated as controllable simulation evidence, not real-system performance.
