# Failure Point Comparison — Tri-Regime Fallback Gate

## 1. obs_noise = 0.00 (near-perfect observation)

### Regime distribution
With zero observation noise, the predictor has perfect information. Most steps fall in **clear** or **medium** regime, depending on the specific blockage/reflection context. The clear regime suppress frequently activates (blockage < 0.20, no outage, low path spread), preventing unnecessary fallback deviations from reactive.

### Why tri-regime helps
In near-zero noise, the reactive baseline is near-optimal. The tri-regime gate correctly identifies these as clear-regime steps where fallback decisions need high justification. By requiring `safety_gain >= 0.06` to override reactive, the gate filters out low-confidence fallback suggestions.

### Deficit improvement: -0.1852 → -0.1443 (+22.1%)
The improvement is smaller than at obs_noise=0.02 because at zero noise, the predictor is already quite accurate, so the gap between reactive and predictive is naturally narrower.

## 2. obs_noise = 0.02 (very low noise)

### Regime distribution
At obs_noise=0.02, predictor accuracy degrades slightly but is still reliable. The regime distribution shifts slightly toward medium (more uncertainty). Extreme regime triggers occasionally when path_spread or reflection_ratio creeps up.

### Why tri-regime helps most here
This is the sweet spot: noise is just high enough that the predictor starts making marginal fallback errors, but the overall channel quality is still good enough that the clear regime suppress remains active. The extreme veto catches the occasional bad fallback in extreme conditions, while the clear suppress prevents low-value fallbacks in normal conditions.

### Deficit improvement: -0.1564 → -0.0803 (+48.7%)
The largest improvement among all three failure points. The tri-regime gate nearly halves the return deficit to Reactive.

## 3. blocker_density = 3.00 (most congested)

### Regime distribution
With 3 blockers, most steps fall in **extreme** regime (blockage_indicator >= 0.25, frequent outages, high path_spread). The extreme veto is the primary active mechanism, applying the rate-preserving check. The clear regime suppress is rarely active here.

### Why tri-regime helps
In dense blocker environments, the predictor's world model rollouts become noisy. Fallback decisions based on poor rollouts can have high rate regret with minimal safety benefit. The extreme veto catches these cases by checking `rate_regret > 0.012 AND safety_gain < 0.012`.

### Deficit improvement: -0.1070 → -0.0632 (+40.9%)
Substantial improvement. The outage advantage over Reactive remains massive (0.1055 vs 0.1455, 27.5% lower).

## Why Main Return Dropped

Despite all three failure points improving, the main comparison return dropped 0.0511. Root cause:

1. **Clear suppress over-fires**: The 0.06 safety_gain threshold blocks fallbacks in normal operating conditions where the predictor's suggestions are actually correct. In clear regime, safety gains are naturally small (because the baseline risk is low), so requiring 0.06 is too stringent.

2. **Medium regime unaffected**: The medium regime, which covers the majority of steps, uses the standard ProposedV2 behavior. It does not benefit from the tri-regime improvements because neither clear suppress nor extreme veto applies.

3. **Net negative**: The gains in hard regimes (+0.04–0.08 per failure point) are offset by losses in easy/medium regimes where the clear suppress kills beneficial fallbacks.

## Tuning Suggestion

The `proposedv2_clear_suppress_threshold` of 0.06 should be lowered to ~0.02–0.03 to reduce false positives while still blocking truly unnecessary fallbacks in clear conditions. This would preserve most of the failure-point gains while recovering the lost average return.
