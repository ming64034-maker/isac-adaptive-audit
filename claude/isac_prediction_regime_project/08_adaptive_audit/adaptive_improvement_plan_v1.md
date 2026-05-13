# Adaptive Improvement Plan v1

**Date**: 2026-05-13
**Scope**: 3 code-level improvements, prioritized by risk of invalidating comparison.

---

## Improvement 1 — Fix: Adaptive variant missing from ablation output despite being registered

**Priority**: 1 (blocker — no results means no paper)

**Objective**: Verify that `ProposedV2_Adaptive` actually runs to completion and writes valid CSV rows. Currently it is registered in `run_ablation_study()` but absent from all output CSV files.

**Exact file/function to edit**:
- `repo/evaluate.py`, function `run_ablation_study()` (line 636–772)
- Specifically the `runnable_variants` list (lines 666–696)

**Signal/output changed**: After fix, `ablation/ablation_summary.csv` and `ablation/ablation_table.csv` must contain rows with `variant = "ProposedV2_Adaptive"` and `status = "ok"` (not NaN, not skipped).

**Expected benefit**: Produces the first quantitative evidence for the adaptive variant — rate, outage, beam success, return, latency — comparable to ProposedV2_Full and Reactive.

**Failure mode it targets**: Silent skip or crash during evaluation. Possible root causes:
1. Exception in `_adaptive_profile()` when `proposedv2_use_adaptive_difficulty=True` that gets swallowed.
2. The `adaptive_cfg` passed to `build_proposedv2_factory()` loses the flag in a dataclass replace chain.
3. OOM or NaN in scorer output due to extreme lerp values.

**Evaluation command**:
```bash
cd repo && python evaluate.py --run-ablation --seeds 2 --eval-episodes 2
```

This runs a quick 2-seed, 2-episode ablation that should complete in < 2 minutes. Check `results/ablation/ablation_table.csv` for a `ProposedV2_Adaptive` row.

**Stop condition**: A row with `variant = "ProposedV2_Adaptive"` and `status = "ok"` appears in the output CSV AND all five metrics (avg_rate, outage, beam_success, avg_return, latency_ms) are finite floats, not NaN.

---

## Improvement 2 — Reduce hard-coded magic numbers to configurable parameters

**Priority**: 2 (required before paper — the current implementation is not reproducible without code reading)

**Objective**: Move the seven hard-coded coefficients in the `instant_difficulty` calculation and the four hard-coded floor constants into `Config` dataclass fields, with documented defaults.

**Exact file/function to edit**:
- `repo/config.py` — add fields:
  ```python
  # _adaptive_profile coefficients
  proposedv2_difficulty_blocker_weight: float = 0.30
  proposedv2_difficulty_reflection_weight: float = 0.18
  proposedv2_difficulty_path_spread_weight: float = 0.16
  proposedv2_difficulty_snr_weight: float = 0.18
  proposedv2_difficulty_outage_weight: float = 0.10
  proposedv2_difficulty_spike_weight: float = 0.06
  proposedv2_difficulty_cooldown_weight: float = 0.02
  proposedv2_difficulty_snr_reference: float = 0.62
  proposedv2_difficulty_snr_divisor: float = 0.42
  proposedv2_difficulty_ema_hardness_weight: float = 0.62
  proposedv2_difficulty_instant_hardness_weight: float = 0.23
  proposedv2_difficulty_delta_pressure_weight: float = 0.15
  proposedv2_difficulty_risk_floor_base: float = 0.45
  proposedv2_difficulty_risk_floor_slope: float = 0.35
  proposedv2_difficulty_outage_floor: float = 0.72
  proposedv2_difficulty_mixed_floor: float = 0.68
  ```
- `repo/baselines.py` lines 207–256 — replace literal floats with `self.cfg.<field>`.

**Signal/output changed**: Identical behavior by default, but coefficients are now visible in `Config.to_dict()` output and can be swept without code edits.

**Expected benefit**:
- Enables coefficient sensitivity analysis for the paper.
- Makes the algorithm reproducible from config alone.
- Moves from "magic numbers in code" to "tunable hyperparameters" — a requirement for peer review.

**Failure mode it targets**: Reviewer challenge: "How were these coefficients chosen?" Without config exposure, the answer is "they are hard-coded in a private method with no derivation." This is a rejection risk.

**Evaluation command**:
```bash
cd repo && python -c "
from config import get_config
c = get_config()
print(c.to_dict()['proposedv2_difficulty_blocker_weight'])
"
# Expected: 0.30
```

**Stop condition**: All 16 new fields appear in `Config.__dataclass_fields__`; `_adaptive_profile()` references them via `self.cfg`; existing tests pass; a quick sanity run produces non-NaN adaptive diagnostics.

---

## Improvement 3 — Add adaptive vs best-fixed-threshold comparison in evaluation

**Priority**: 3 (required for paper — must show adaptive scheduling beats static tuning)

**Objective**: The threshold sweep (`run_threshold_sweep`, line 775) already finds the best fixed-threshold combination. The adaptive variant must be compared against that best configuration, not just against the default ProposedV2.

**Exact file/function to edit**:
- `repo/evaluate.py` — add a new function `run_adaptive_vs_best_fixed(cfg, seeds)` that:
  1. Loads the best threshold configuration from `results/threshold_sweep/best_thresholds.csv`.
  2. Creates a `best_fixed_cfg` with those thresholds and `proposedv2_use_adaptive_difficulty = False`.
  3. Creates an `adaptive_cfg` with default thresholds and `proposedv2_use_adaptive_difficulty = True`.
  4. Evaluates both side-by-side with identical seeds/episodes.
  5. Writes the result to `results/adaptive_vs_best_fixed.csv`.

**Signal/output changed**: A new CSV with columns: method, seed, avg_rate, outage, beam_success, avg_return, latency_ms — for both `ProposedV2_Adaptive` and `ProposedV2_BestFixed`.

**Expected benefit**: The key paper claim — "adaptive scheduling outperforms the best hand-tuned static configuration" — becomes testable. Without this comparison, the adaptive variant is just a more complex way to achieve what static tuning already does.

**Failure mode it targets**: Reviewer counter-argument: "You added 24 parameters and claim improvement, but did you compare against the best 3-parameter static configuration found by your own grid search?" Without this comparison, the contribution is not defensible.

**Evaluation command**:
```bash
cd repo && python evaluate.py --run-threshold-sweep --seeds 5 --eval-episodes 4
# Wait for completion, then:
# (after implementing the new function)
python -c "
from evaluate import run_adaptive_vs_best_fixed
from config import get_config
cfg = get_config()
run_adaptive_vs_best_fixed(cfg, [0,1,2,3,4])
"
```

**Stop condition**: `results/adaptive_vs_best_fixed.csv` exists; adaptive return >= best-fixed return OR the gap is negative but small (< 0.02) with overlapping error bars — in either case, the comparison is documented and citable.
