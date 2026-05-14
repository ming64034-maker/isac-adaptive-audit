# Ablation Wording Fix Log

## Files Inspected

- `claude/isac_prediction_regime_project/12_paper_results_discussion/section4_experimental_results_v0.md`
- `claude/isac_prediction_regime_project/12_paper_results_discussion/paper_claim_boundary_final.md`

## Files Changed

- `claude/isac_prediction_regime_project/12_paper_results_discussion/section4_experimental_results_v0.md` (Section 4.4, Predictive Fallback paragraph)

## Exact Issue Fixed

Section 4.4 previously described the No Predictive Fallback ablation as "reverting to pure reactive beam selection." This was incorrect: the ablation table shows distinct values for No Predictive Fallback (outage 0.083, beam success 0.779) and Reactive (outage 0.106, beam success 0.742). The corrected interpretation is that No Predictive Fallback retains the guarded ProposedV2 control structure and the gap between it and Reactive is explained by the guard mechanism, not the (disabled) predictive fallback.

## Grep Verification

```
grep -RniE "pure reactive|reverting to pure reactive|reverting to reactive|No Predictive Fallback" \
  claude/isac_prediction_regime_project/12_paper_results_discussion \
  claude/isac_prediction_regime_project/14_result_consistency_check
```

Result: zero matches for "pure reactive" / "reverting to ... reactive" phrasing. Remaining "No Predictive Fallback" hits are table headers and metric names, not interpretive prose.

## No Experiment Rerun

## No Numeric Value Changed
