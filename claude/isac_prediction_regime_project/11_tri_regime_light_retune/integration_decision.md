# Integration Decision — Tri-Regime Light Retune

## Decision: **REJECT** — Stop algorithm iteration, return to paper writing

## Evidence Summary

| Criterion | Result |
|---|---|
| Main return >= baseline 4.8809 (0.03) | **4.8421 (-0.0388)** ❌ |
| Main return >= baseline 4.8809 (0.02) | **4.8328 (-0.0481)** ❌ |
| obs_noise=0.00 deficit reduction (0.03) | +0.0394 (21.3%) ✓ |
| obs_noise=0.02 deficit reduction (0.03) | +0.0666 (42.6%) ✓ |
| blocker_density=3.00 deficit reduction (0.03) | +0.0103 (9.6%) ✓ |
| Outage vs Reactive at failure points | Better at all 3 ✓ |
| Universal superiority claimed | No |

## Rationale

Per the decision rule:

> If both 0.02 and 0.03 fail main return, stop algorithm iteration and return to paper writing.

Both retunes fail to reach the baseline return of 4.8809. The best retune (0.03) achieves 4.8421, still 0.0388 below baseline.

The tri-regime approach has now been tested across 3 parameter settings (0.06, 0.03, 0.02). The pattern is consistent and monotonic:

| Threshold | Main Return | Pattern |
|---|---|---|
| 0.06 (aggressive) | 4.8298 | Over-suppresses, worst return |
| 0.03 (moderate) | 4.8421 | Best compromise, still below baseline |
| 0.02 (light) | 4.8328 | Under-suppresses clear, extreme veto dominates |

The inverse-U shape (0.03 as peak) confirms there is a fundamental tradeoff rather than a missing optimal setting: further lowering would reduce to the already-rejected uniform rate veto; further raising would worsen the over-suppression.

## Scope of Evidence

The tri-regime investigation produced:

1. **Strong directional evidence**: All 8 evaluation runs (3 threshold settings × multiple failure points) showed consistent deficit reduction at the 3 target failure points. The regime-conditioned architecture is validated as a concept.

2. **Net regression on main metric**: No setting achieved the primary integration criterion (main return >= baseline). The regime-conditioned improvements at failure points are real but come at the cost of degraded average performance.

3. **Structural limitation identified**: The clear-medium-extreme regime decomposition reveals that the return deficit in easy regimes is dominated by factors outside the fallback mechanism (beam scoring, shortlist construction), explaining why gate-style interventions cannot fully close the gap.

## Recommended Next Step

Return to paper writing. The paper's ProposedV2 baseline (4.8809 return, 0.0723 outage) is the strongest available result. Focus on:

- Presenting the failure regime analysis as a limitations/discussion section
- Documenting the regime-conditioned approach as future work
- Using the scene sweep data to characterize when and why predictive beamforming helps vs. reactive

The algorithm exploration phase is complete. The evidence supports ProposedV2 as the best current method, with clear documentation of its failure modes and regimes where reactive baselines dominate.
