# Failure Point Regime Analysis — Rate-Preserving Veto v2

## 1. obs_noise = 0.00 (near-perfect observation, low noise regime)

### Why ProposedV2 underperforms Reactive here

When observation noise is near zero, the predictor has near-perfect information. Reactive baseline exploits this by making fast, accurate beam decisions purely from current observation. ProposedV2's predictive fallback adds no value because the predictor gains are minimal, but the rate penalty from occasional wrong fallback decisions still applies.

### Veto effect (aggressive, 0.012/0.012)

- Return deficit: -0.1852 → -0.1584 (14.5% reduction)
- Outage: 0.04475 (still better than Reactive's 0.0495)
- The veto blocks ~3% of fallback decisions that have high rate regret with low safety benefit
- In this regime, most fallbacks are unnecessary — the reactive decision is already near-optimal
- Improvement is real but modest because the regime is inherently bottlenecked by the rate-outage tradeoff

### Remaining gap

Even with aggressive veto, ProposedV2 still trails Reactive by 0.1584 in return. The residual gap comes from the fundamental beam selection pipeline, not the fallback mechanism — ProposedV2's beam shortlist construction and scoring have non-zero latency and suboptimal selection in low-noise regimes.

## 2. obs_noise = 0.02 (very low noise)

### Why ProposedV2 underperforms Reactive here

Similar to obs_noise=0.00 but with slightly more predictor value. The world model starts to provide marginal benefit, but the reactive baseline still dominates because noise is too low to degrade reactive decisions meaningfully.

### Veto effect (aggressive, 0.012/0.012)

- Return deficit: -0.1564 → -0.1088 (30.5% reduction)
- Outage: 0.05225 (still better than Reactive's 0.05675)
- Larger improvement than obs_noise=0.00 because at this noise level, the predictor confidence is slightly higher, more fallback candidates pass the LoS guard, and more of them are marginal — creating more opportunities for the veto to filter
- Outage gap to Reactive remains healthy (ProposedV2 has ~8% lower outage)

### Remaining gap

The -0.1088 deficit is still significant. The veto addresses the rate side of the problem, but in this regime the predictor overestimates its own value in some situations, producing confident-but-wrong fallback suggestions that the rate veto does not catch (because the predicted rate looks good but the true rate is worse).

## 3. blocker_density = 3.00 (most congested, 3 blockers always present)

### Why ProposedV2 underperforms Reactive here

High blocker density means frequent LoS blockages. ProposedV2's predictor tries to anticipate blockages and proactively switch beams, which should help — but with 3 blockers, the environment becomes chaotic and hard to predict. The predictor's world model rollouts become noisier, leading to fallback decisions that over-fit to imagined trajectories that don't materialize. Meanwhile, Reactive simply responds to what it sees, avoiding the cost of bad predictions.

### Veto effect (aggressive, 0.012/0.012)

- Return deficit: -0.1070 → -0.0796 (25.7% reduction)
- Outage: 0.09925 (massively better than Reactive's 0.1455 — 32% lower)
- The veto is most impactful here because fallback decisions with high rate regret are more common when the predictor is uncertain
- Outage advantage is well preserved: ProposedV2 maintains a ~32% outage reduction over Reactive
- Rate loss is partially mitigated: the veto blocks fallback decisions where the safety gain is marginal relative to rate cost

### Remaining gap

The -0.0796 deficit is the smallest among the 3 failure points. The outage advantage is large enough that a higher `proposedv2_min_safety_gain_for_fallback` threshold specifically in high-density regimes could be justified. In other words, in dense environments, we should be even more selective about fallback decisions because outage is more sensitive to wrong beam choices.

## Overall Assessment

The aggressive veto (0.012/0.012) improves all 3 failure points at the cost of degrading easy-regime performance. The regime-specific analysis suggests the veto threshold should be **regime-adaptive**: looser in easy regimes (to avoid killing good fallbacks that drive average return) and tighter in hard regimes (where fallback decisions are riskier and the veto adds more value).
