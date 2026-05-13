# Result Configuration Consistency Report

## Verdict

Yes. The main comparison and the scene sweep were regenerated under the same baseline ProposedV2 configuration from `claude/isac_uploaded_repo/repo/config.py`.

The paper-facing baseline flags are now:

- `proposedv2_use_adaptive_difficulty = False`
- `proposedv2_rate_veto_enabled = False`
- `proposedv2_tri_regime_gate_enabled = False`

Section 4.2 and Section 4.3 are now internally consistent with each other. This task reran the main comparison and scene sweeps only; ablation, threshold-sweep, and blockage-event outputs were not regenerated in this pass.

## Evidence

Pre-fix artifacts showed active tri-regime behavior in the supposed baseline outputs:

- Old `results/method_comparison_steps.csv` for `ProposedV2` had `planner_clear_suppress_triggered` mean `0.0322` and `planner_extreme_veto_triggered` mean `0.0189`.
- Old `results/scene_difficulty_sweep_steps.csv` for `ProposedV2` had `planner_clear_suppress_triggered` mean `0.0330` and `planner_extreme_veto_triggered` mean `0.0186`.

Post-fix diagnostics from the regenerated baseline outputs show the experimental gates are not affecting the paper-facing results:

- New `results/method_comparison_diagnostics.csv`: `planner_rate_veto_triggered_mean = 0.0`, `planner_clear_suppress_triggered_mean = 0.0`, `planner_extreme_veto_triggered_mean = 0.0`
- New `results/scene_difficulty_sweep_diagnostics.csv`: `planner_rate_veto_triggered_mean = 0.0`, `planner_clear_suppress_triggered_mean = 0.0`, `planner_extreme_veto_triggered_mean = 0.0`

Notes:

- `planner_adaptive_difficulty_mean = 0.5` still appears in diagnostics because the non-adaptive code path emits a neutral placeholder profile; the config flag itself is disabled.
- `planner_tri_regime_mode_mean = 1.0` remains as the default recorded `"medium"` label even when the tri-regime gate is disabled. The zero trigger rates above are the relevant evidence that the gate is not acting on the baseline run.

## Commands Run

The shell did not expose a plain `python` binary, so the equivalent project-venv commands were used:

```bash
cd claude/isac_uploaded_repo/repo
./.venv/bin/python -B evaluate.py --skip-horizon-sweep --skip-scene-sweeps
./.venv/bin/python -B evaluate.py --run-scene-sweeps
./.venv/bin/python -B summarize_results.py
```

## Files Rerun Or Refreshed

Rerun result files:

- `results/method_comparison_raw.csv`
- `results/method_comparison.csv`
- `results/method_comparison_steps.csv`
- `results/method_comparison_diagnostics.csv`
- `results/scene_difficulty_sweep_raw.csv`
- `results/scene_difficulty_sweep.csv`
- `results/scene_difficulty_sweep_steps.csv`
- `results/scene_difficulty_sweep_diagnostics.csv`
- `results/sweeps/blocker_density_sweep.csv`
- `results/sweeps/blocker_speed_sweep.csv`
- `results/sweeps/obs_noise_sweep.csv`
- `results/sweeps/reflection_strength_sweep.csv`
- `results/sweeps/scene_sweep_summary.csv`

Refreshed summary files:

- `results/paper_tables/main_method_table.tex`
- `results/paper_tables/sweep_summary_table.tex`
- `results/paper_tables/result_summary.md`

Updated paper-facing markdown:

- `claude/isac_prediction_regime_project/12_paper_results_discussion/section4_experimental_results_v0.md`
- `claude/isac_prediction_regime_project/12_paper_results_discussion/section5_regime_analysis_v0.md`
- `claude/isac_prediction_regime_project/12_paper_results_discussion/paper_claim_boundary_final.md`

## Which Paper Numbers Changed

- The main ProposedV2 aggregate row changed back to the accepted baseline values: rate `5.030 -> 5.064`, outage `0.077 -> 0.072`, beam success `0.787 -> 0.793`, return `4.833 -> 4.881`.
- All 16 Section 4.3 ProposedV2 scene-sweep rows changed, with the largest gains at `obs_noise=0.10` and the largest remaining deficits at `obs_noise=0.00`, `obs_noise=0.02`, and `blocker_density=3.0`.
- The scene-sweep return win count changed from `10/16` to `11/16`.
- The return-loss set changed from 6 points to 5 points; `blocker_speed=1.5` is no longer a return-loss point, while `reflection_strength=weak` remains a small loss point.
- Table 1 latency cells were synced to the regenerated CSV values, including non-Proposed rows.

## Final Answer To The Review Questions

- Are main comparison and scene sweep generated under the same baseline ProposedV2 configuration?
  - Yes.
- Were tri-regime/adaptive/veto flags disabled?
  - Yes for the paper-facing baseline: adaptive `False`, rate veto `False`, tri-regime gate `False`.
- Which files were rerun?
  - The method-comparison outputs, scene-sweep outputs, sweep summary CSVs, and paper-table summaries listed above.
- Which paper numbers changed?
  - The Section 4.2 ProposedV2 aggregate row, the Section 4.3 scene-sweep table, the 10/16 to 11/16 return-win summary, and dependent values in the regime-analysis and claim-boundary markdown.
- Is Section 4 now internally consistent?
  - Yes for the rerun baseline comparison and scene-sweep evidence used in Sections 4.2 and 4.3.
