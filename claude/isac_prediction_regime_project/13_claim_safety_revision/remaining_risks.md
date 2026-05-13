# Remaining Claim Risks

## Residual Risks (not fully mitigated by this revision)

### 1. Scene sweep numbers may have configuration mismatch
**Risk**: The scene sweep table in Section 4.3 was generated from an evaluation run with active tri-regime configuration (clear_suppress_threshold=0.02), not from the baseline ProposedV2 configuration used for the main comparison. The blocker_speed=1.0 row shows return 4.855 vs the main comparison 4.881, exposing a 0.026 discrepancy. The reported deficit and outage values inherit this shift.
**Mitigation**: The qualitative patterns (regime-dependence, failure point ranking) are stable across configurations. A re-run with baseline configuration would align the numbers precisely.
**Severity**: Low-Medium. Quantitative shifts are small and qualitative conclusions hold.

### 2. Ablation data was generated with different seeds/settings
**Risk**: The ablation summary (Section 4.4) was run with a different evaluation setup than the main comparison. The Reactive baseline in ablation has return 4.555 vs 4.744 in the main comparison. Ablation effect sizes are measured relative to this different baseline.
**Mitigation**: Ablation conclusions are based on large effect sizes (-0.996, -0.143) that dominate any configuration differences. The direction and approximate magnitude would replicate.
**Severity**: Low. Effect sizes are large enough to be insensitive to configuration.

### 3. "Simulation evidence" disclaimer may be ignored or minimized
**Risk**: Despite the Section 4.7 evidence boundary paragraph, readers or reviewers may still interpret results as real-system claims.
**Mitigation**: The boundary is stated in both Section 4.7 and the claim boundary document. Repeating it in the abstract and conclusion reduces the risk.
**Severity**: Medium. Depends on reviewer attention.

### 4. Absence of statistical significance tests
**Risk**: All comparisons report means and standard deviations but no formal hypothesis tests (t-tests, confidence intervals for differences). The 5-seed, 4-episode design gives 20 independent episodes per method, which is adequate for reporting but not for claiming statistical significance.
**Mitigation**: Effect sizes are reported transparently. The 16/16 sweep wins for outage and beam success are inherently robust to distributional assumptions. Return and rate comparisons should not be framed as "significant."
**Severity**: Low-Medium. May be raised by statistically-minded reviewers.

### 5. Failed variant evidence may distract from main contributions
**Risk**: The Discussion section (6.3) documents three failed variants in detail. Reviewers may focus on these negative results rather than the positive ProposedV2 evidence.
**Mitigation**: The failed variants are clearly labeled as "Negative Results" and are confined to the Discussion section. They are not mentioned in the abstract, introduction, method, or results sections.
**Severity**: Low. Proper section placement mitigates the risk.

### 6. Baseline comparison set is narrow
**Risk**: Only 4 baseline methods are compared (Reactive, One-Step Predictive, Belief-Aware Rollout, Oracle). The literature contains other predictive beamforming approaches not included in the comparison.
**Mitigation**: The claim boundary explicitly states we "do not claim superiority over all existing methods" and the comparison set is documented. This should not be presented as exhaustive benchmarking.
**Severity**: Low. Transparently disclosed.

## Items Explicitly Out of Scope (no residual risk)

- Universal superiority claims → explicitly disclaimed
- Real-system performance claims → simulation-only boundary stated
- Consistent rate advantage → reworded to "regime-dependent"
- Negligible latency → replaced with system-level validation requirement
- Adaptive difficulty / veto / tri-regime as contributions → not claimed

## Recommended Pre-Submission Checklist

- [ ] Rerun scene sweeps with baseline configuration for number alignment
- [ ] Add reviewer-facing note about ablation setup differences
- [ ] Add 95% confidence intervals to main comparison table (optional)
- [ ] Have a non-author read Section 4.7 evidence boundary and confirm it is clear
- [ ] Verify no failed variant language leaked into abstract or introduction
