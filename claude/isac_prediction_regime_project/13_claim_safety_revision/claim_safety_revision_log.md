# Claim Safety Revision Log

## Files Modified

| File | Changes |
|---|---|
| `section4_experimental_results_v0.md` | 5 edits |
| `section5_regime_analysis_v0.md` | 3 edits |
| `section6_discussion_limitations_v0.md` | 1 edit |
| `paper_claim_boundary_final.md` | 4 edits |

## Edit Details

### Edit 1: Rate claim wording (Section 4.2, Key observation #1)
- **Before**: "The gain over Reactive is modest but consistent."
- **After**: "However, rate advantage is regime-dependent: ProposedV2 wins rate at only 6/16 scene sweep points. The aggregate rate gain is modest, while rate advantage is regime-dependent."
- **Reason**: "Consistent" rate gain was misleading — rate wins only 6/16 sweep points.

### Edit 2: Latency claim (Section 4.2, Key observation #5)
- **Before**: "This is negligible relative to typical slot durations in mmWave systems."
- **After**: "Planning latency is higher than Reactive but lower than Belief-Aware Rollout in the simplified simulator; real-time feasibility requires system-level validation."
- **Reason**: Cannot claim negligible latency without real-system validation.

### Edit 3: Outage and beam success emphasis (Section 4.2, Key observations #2, #3, #4)
- Added "(strongest claim)" label to outage
- Added "(strong claim)" label to beam success
- Added explicit 16/16 sweep point wins for both
- Added failure regime reference to return observation
- **Reason**: Outage and beam success are the two strongest claims; rate and return are regime-conditional.

### Edit 4: Aggregate sweep statistics reorder (Section 4.3)
- **Before**: Listed outage, beam success, return, rate without prioritization
- **After**: Lead with outage and beam success as "two most robust claims"; return as "narrower"; rate as "regime-dependent"
- **Reason**: Consistent emphasis hierarchy.

### Edit 5: Evidence boundary paragraph (New Section 4.7)
- Added explicit evidence boundary: simulation only, no real-system claims, no universal superiority, conditions tested are the full set
- **Reason**: Required guardrail to prevent over-interpretation.

### Edit 6: Regime analysis framing (Section 5.1)
- Added upfront statement that outage and beam success are robust (16/16 each), return and rate are regime-dependent
- **Reason**: Align section framing with claim hierarchy.

### Edit 7: Clear regime performance (Section 5.2)
- **Before**: "Modest gains over Reactive in rate (+0.03 to +0.05)"
- **After**: "Return advantage is narrow; rate may be slightly above or below Reactive depending on the specific configuration"
- **Reason**: In clear regime, rate advantage is not guaranteed and the specific numbers depend on configuration. Softer, more honest language.

### Edit 8: Cross-over point language (Section 5.3)
- **Before**: "the cross-over point where ProposedV2 becomes clearly superior"
- **After**: "the cross-over point where ProposedV2 begins to outperform Reactive on return" + "Outage and beam success favor ProposedV2 across the full noise range"
- **Reason**: "Clearly superior" overclaims; also adds the nuance that outage/beam success are always better.

### Edit 9: Computational cost language (Section 6.2.4)
- **Before**: "The measured planning latency (0.28 ms) is acceptable for typical mmWave slot durations (0.125–1.0 ms)"
- **After**: "Real-time feasibility requires system-level validation including hardware-in-the-loop measurement"
- **Reason**: Consistent with softened latency claim in Section 4.

### Edit 10: Primary claim support bullets (paper_claim_boundary_final.md)
- Reordered to list outage 16/16 first, beam success 16/16 second, rate with caveat third
- **Reason**: Claim hierarchy alignment.

### Edit 11: Evidence strength table — rate competitiveness (paper_claim_boundary_final.md)
- **Before**: "Moderate — +1.1% aggregate, but loses at 10/16 sweep points"
- **After**: "Regime-dependent — +1.1% aggregate, but wins at only 6/16 sweep points"
- **Reason**: "Regime-dependent" is more accurate than "Moderate"; framing as "wins at 6/16" avoids the ambiguous "loses at 10/16".

### Edit 12: "DO NOT claim" additions (paper_claim_boundary_final.md)
- Added #6 Real-time feasibility and #7 Consistent rate advantage
- **Reason**: These were identified as over-claim risks needing explicit exclusion.

## Revised Claim Hierarchy

| Priority | Claim | Sweep Evidence |
|---|---|---|
| 1 (strongest) | Outage reduction | 16/16 wins |
| 2 (strong) | Beam success improvement | 16/16 wins |
| 3 (moderate) | Aggregate return advantage | 10/16 wins |
| 4 (regime-dependent) | Rate competitiveness | 6/16 wins |
