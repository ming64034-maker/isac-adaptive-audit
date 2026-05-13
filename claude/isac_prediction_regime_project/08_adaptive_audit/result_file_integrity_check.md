# Result File Integrity Check

**Date**: 2026-05-13
**Repo root**: `/Users/cccwm/Documents/New project/`

---

## 1. Required Files — Existence and Git Status

| File | Local Exists | Git Tracked | Has ProposedV2_Adaptive |
|---|---|---|---|
| `results/method_comparison.csv` | Yes | No | No (only 5 methods) |
| `results/method_comparison_raw.csv` | Yes | No | No |
| `results/method_comparison_steps.csv` | Yes | No | No |
| `results/method_comparison_diagnostics.csv` | Yes | No | No |
| `results/sweeps/scene_sweep_summary.csv` | Yes | No | No |
| `results/ablation/ablation_summary.csv` | Yes | No | **Yes** (row added after rerun) |
| `results/ablation/ablation_table.csv` | Yes | No | **Yes** (per-seed, 2 seeds) |
| `results/ablation/ablation_notes.md` | Yes | No | No |
| `results/threshold_sweep/best_thresholds.csv` | Yes | No | N/A (threshold sweep is ProposedV2 only) |
| `results/events/blockage_event_summary.csv` | Yes | No | No |
| `results/paper_tables/result_summary.md` | Yes | No | No (summary text doesn't mention adaptive) |
| `results/paper_tables/ablation_table.tex` | Yes | No | **Yes** (regenerated, includes Adaptive) |

---

## 2. Git Tracking Status

**No result files are tracked by git.** All CSVs, plots, and paper_tables exist locally but were never staged or committed. The only commit in this repo (`8995500`) includes:

```
08_adaptive_audit/adaptive_variant_audit_v1.md
08_adaptive_audit/adaptive_result_digest_v1.md
08_adaptive_audit/adaptive_improvement_plan_v1.md
adaptive_progress_grep.txt
local_file_inventory.txt
```

---

## 3. Whether ProposedV2_Adaptive Has Raw CSV Support

- **Ablation**: Yes — `ablation_summary.csv` and `ablation_table.csv` now contain `ProposedV2_Adaptive` rows (2 seeds, 2 episodes per seed).
- **Method comparison**: No — `run_method_comparison()` does not include adaptive.
- **Scene sweeps**: No — `run_scene_difficulty_sweeps()` does not include adaptive.
- **Threshold sweep**: Not applicable.
- **Event analysis**: No — `run_event_analysis()` does not include adaptive.

**To add adaptive to scene sweeps**, `evaluate.py:run_scene_difficulty_sweeps()` would need modification to add a `ProposedV2_Adaptive` variant.

---

## 4. Whether Adaptive Can Be Paper-Claimable Now

**No.** Three blockers:

1. **No regime-level data** — scene sweep data for adaptive does not exist. Cannot assess whether adaptive fixes the obs_noise=0.00, obs_noise=0.02, or blocker_density=3.00 failure points.
2. **Default-scene result is negative** — in the 2-seed ablation, Adaptive return (4.5700) is below Full (4.6392) by −0.0692. This is consistent across both seeds.
3. **No step-level diagnostics** — cannot explain why adaptive underperforms. Without hardness/fallback/veto time-series, the failure mode is opaque.

---

## 5. What Was Done in This Session

- Ran `python -B evaluate.py --run-ablation --seeds 2 --eval-episodes 2`
- Confirmed `ProposedV2_Adaptive` now appears in ablation outputs
- Ran `python -B summarize_results.py` to regenerate paper tables (includes Adaptive in ablation_table.tex)
- Generated 3 analysis files + this integrity check

---

## 6. Next Steps (not in this session)

For adaptive to be reconsidered:
1. Add adaptive to `run_scene_difficulty_sweeps()` and rerun
2. Add adaptive to `run_method_comparison()` and rerun
3. Save step-level diagnostics for adaptive (hardness, fallback rate, veto rate)
4. Compare adaptive vs best fixed thresholds from threshold_sweep
