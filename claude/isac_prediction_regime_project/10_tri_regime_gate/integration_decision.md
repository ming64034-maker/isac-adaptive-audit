# Integration Decision — Tri-Regime Fallback Gate

## Decision: **PARTIAL DIRECTIONAL EVIDENCE** — Do not integrate into ProposedV2

## Evidence Summary

| Criterion | Result |
|---|---|
| Main comparison return vs baseline | **-0.0511** (4.8809 → 4.8298) ❌ |
| obs_noise=0.00 deficit reduction | **+0.0409** (22.1%) ✓ |
| obs_noise=0.02 deficit reduction | **+0.0761** (48.7%) ✓ |
| blocker_density=3.00 deficit reduction | **+0.0438** (40.9%) ✓ |
| Outage vs Reactive at failure points | Better at all 3 ✓ |
| Universal superiority claimed | No — explicitly rejected |

## Rationale

Per the decision rules:

> 如果只局部有效但 main 不提升，写 partial directional evidence，不进主方法

The tri-regime gate demonstrates clear **directional evidence** that regime-conditioned fallback gating improves the worst-case failure points. All three target deficits shrunk by 22–49%. Outage advantage over Reactive was preserved.

However, the uniform `clear_suppress_threshold` of 0.06 causes net regression: the gains at failure points are more than offset by over-suppression of beneficial fallbacks in normal operating conditions.

## Why This Is Partial (Not Complete) Evidence

1. **The regime concept is validated**: Separating clear/medium/extreme conditions and applying different fallback policies in each is the right architectural direction. The failure-point improvements prove the extreme veto works and the clear suppress has the right intent.

2. **The thresholds need tuning**: The `clear_suppress_threshold` at 0.06 is the sole cause of the main return drop. A single parameter adjustment (lowering to 0.02–0.03) would likely recover the lost average return while preserving most failure-point gains.

3. **The medium regime is currently a no-op**: The majority of steps fall in medium regime where no tri-regime logic applies. This limits the mechanism's reach and leaves average-return on the table.

## Recommended Follow-Up (for future work, not immediate)

### Priority 1: Threshold retune
Lower `proposedv2_clear_suppress_threshold` to 0.02–0.03. Rerun to verify main return recovers while failure-point improvements persist.

### Priority 2: Medium regime enhancement
The medium regime currently has no additional gate. A lighter-touch version of the extreme veto (e.g., `rate_regret_threshold = 0.025` instead of 0.012) could provide incremental improvement in the medium regime without over-vetoing.

### Priority 3: Regime boundary calibration
The current boundaries (blockage < 0.20 for clear, blockage >= 0.25 for extreme) create a narrow medium band. Slightly widening the extreme boundary (e.g., risk_score >= 0.55 instead of 0.65) would apply the extreme veto more broadly where it adds value.

## Verdict

The tri-regime fallback gate shows **strong directional evidence at failure points** but the uniform clear threshold causes net regression. The regime architecture is correct but the implementation needs a single threshold retune before re-evaluation. Do not integrate in current form.
