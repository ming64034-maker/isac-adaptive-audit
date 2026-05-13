# Failure Point Comparison — Tri-Regime Light Retune

## Setup

Comparing baseline ProposedV2 (no tri-regime gate) vs tri-regime gate with `clear_suppress_threshold = 0.03`.

## 1. obs_noise = 0.00

### Deficit: -0.1852 → -0.1458 (+21.3%)

The gap to Reactive shrinks from -0.1852 to -0.1458. The clear suppress correctly identifies this as a regime where the predictor gains are minimal (near-zero noise means reactive is near-optimal) and blocks some unnecessary fallbacks.

However, even with the relaxed threshold (0.03 vs 0.06), some beneficial fallbacks are still suppressed because safety gains in this regime are naturally small — the baseline outage is already very low (0.0465), so even correct fallback decisions produce modest safety gain values.

### Outage: 0.0450 vs Reactive 0.0495 ✓

ProposedV2 maintains lower outage than Reactive, preserving the key safety advantage.

## 2. obs_noise = 0.02

### Deficit: -0.1564 → -0.0898 (+42.6%)

The largest improvement among all three failure points. At this noise level, the predictor starts making marginal fallback errors, and both the clear suppress and extreme veto contribute. The relaxed threshold (0.03) catches many low-value fallbacks while letting through the ones with real safety benefit.

This is the sweet spot for the tri-regime gate — enough noise to produce bad fallback candidates, but clear enough that the regime classification is reliable.

### Outage: 0.0532 vs Reactive 0.0568 ✓

Narrower gap than at obs_noise=0.00, but still a clear advantage.

## 3. blocker_density = 3.00

### Deficit: -0.1070 → -0.0967 (+9.6%)

The smallest improvement among the three failure points. With 3 blockers, most steps are in extreme regime where the extreme veto applies (thresholds unchanged at 0.012/0.012). The clear suppress has minimal effect here. The extreme veto helps but the effect is limited by the inherent difficulty of predicting in dense blocker environments.

### Outage: 0.1030 vs Reactive 0.1455 ✓

Massive outage advantage preserved — ProposedV2 has 29.2% lower outage probability than Reactive.

## Why Main Return Didn't Recover

Three structural factors prevent the tri-regime gate from reaching baseline return regardless of threshold tuning:

1. **Medium regime is a no-op**: The majority of steps fall in medium regime where no tri-regime logic applies. Any average-return recovery must come from the subset of steps in clear or extreme regimes. This caps the mechanism's upside.

2. **Clear regime has a fundamental tension**: The clear suppress blocks unnecessary fallbacks (improving return) but also blocks some correct anticipatory fallbacks (hurting return). No single threshold perfectly separates these cases because they come from the same distribution of safety gain values.

3. **The fallback mechanism itself is not the bottleneck**: Most of the return deficit between ProposedV2 and Reactive in easy regimes comes from the beam scoring pipeline (shortlist construction, angle affinity, beam switching), not from fallback decisions. The tri-regime gate cannot fix these structural gaps.

## Conclusion

The tri-regime gate provides consistent directional improvement at failure points, but the clear suppress creates an inherent tradeoff: tighter thresholds improve failure points at the cost of average return. The optimal operating point (0.03) still produces net regression. Further threshold tuning cannot resolve this because the problem is structural, not parametric.
