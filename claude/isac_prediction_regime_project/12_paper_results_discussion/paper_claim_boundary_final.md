# Paper Claim Boundary — Final

## Primary Claim

**ProposedV2 (Regime-Aware Predictive Beam Control) improves reliability-oriented metrics (outage probability, beam success rate) while preserving competitive aggregate rate, but gains are regime-dependent.**

This claim is supported by:
- 32% outage reduction vs Reactive (0.072 vs 0.106), 16/16 sweep points with better outage
- 7.0% beam success rate improvement (0.793 vs 0.742), 16/16 sweep points with better beam success
- Competitive aggregate rate (5.064 vs 5.010), though rate advantage is regime-dependent (6/16 wins)
- 8.4% faster blockage recovery (1.86 vs 2.03 slots)

## Claim Boundaries

### What we DO claim

1. **Reliability improvement in aggregate**: ProposedV2 reduces outage probability and improves beam selection accuracy across a wide range of operating conditions.

2. **Regime-dependent advantage**: The method provides the largest gains in noisy and medium-complexity conditions. In easy regimes (near-zero noise) and very hard regimes (3+ blockers, very fast motion), the reactive baseline can match or exceed ProposedV2 on return.

3. **Essential components**: Both the LoS guard and predictive fallback are individually necessary; removing either causes substantial degradation (ablation: -0.996 and -0.143 return respectively).

4. **Predictive value in noise**: The method's advantage grows with observation noise (+0.676 return advantage at obs_noise=0.10), demonstrating that learned dynamics models can filter sensing noise more effectively than reactive approaches.

5. **Simulation evidence**: All claims are bounded by the simulated environment described in the evaluation protocol. No claims are made about real-world deployment performance.

### What we DO NOT claim

1. **Universal superiority**: ProposedV2 does not outperform Reactive on all metrics in all regimes. Specifically, it underperforms on return at obs_noise ≈ 0.00 (-0.189), obs_noise ≈ 0.02 (-0.155), blocker_density = 3.00 (-0.109), blocker_speed = 2.00 (-0.047), and weak reflections (-0.012).

2. **State-of-the-art**: We do not claim superiority over all existing methods. The comparison set is limited to Reactive, One-Step Predictive, Belief-Aware Rollout, and Oracle baselines.

3. **Optimal gating**: We do not claim the current LoS guard thresholds are optimal. The threshold sweep shows robustness to variation, but better thresholds may exist for specific operating conditions.

4. **Real-world performance**: No claims are made about performance with measured channels, hardware impairments, or non-stationary environments.

5. **Computational efficiency advantage**: The method requires a trained predictor and world model. Training cost and data requirements are not compared to baselines.

6. **Real-time feasibility**: Planning latency is not validated in a real-time system context. Simulator-measured latency does not guarantee real-time operation on target hardware.

7. **Consistent rate advantage**: The aggregate rate gain (+1.1%) does not hold uniformly — rate advantage is regime-dependent and wins at only 6/16 sweep points.

### Failed variant claims

The following are explicitly NOT claimed:

1. ❌ Adaptive difficulty improves performance (evidence: -0.069 return regression)
2. ❌ Uniform rate-preserving veto improves main return (evidence: -0.026 return regression)
3. ❌ Tri-regime fallback gate matches baseline return (evidence: -0.039 return regression at best setting)
4. ❌ Additional gating layers can simultaneously improve failure points and average return (evidence: consistent structural tradeoff across all three attempts)

These negative results are documented in the Discussion section as partial directional evidence and to inform future work.

## Evidence Strength by Metric

| Metric | Evidence Strength | Notes |
|---|---|---|
| Outage reduction vs Reactive | **Strong** | Consistent at all 16 sweep points, 32% aggregate |
| Beam success improvement | **Strong** | 16/16 sweep point wins, consistent across regimes |
| Rate competitiveness | **Regime-dependent** | +1.1% aggregate, but wins at only 6/16 sweep points |
| Return advantage | **Regime-conditional** | Wins at 11/16 sweep points, loses at 5/16 |
| Blockage recovery speed | **Moderate** | 8.4% faster, but small sample (40 events) |
| Ablation necessity | **Strong** | Large effect sizes (-0.996 and -0.143) |

## Figures and Tables Supporting Claims

- **Table 1**: Main method comparison (aggregate metrics)
- **Table 2**: Scene sweep summary (regime-dependent performance)
- **Table 3**: Ablation study (component necessity)
- **Table 4**: Blockage event recovery (temporal advantage)
- **Figure 1**: Return difference vs Reactive across sweep dimensions
- **Figure 2**: Outage probability vs observation noise (cross-over visualization)
- **Figure 3**: Blocker density impact on rate-outage tradeoff

## Writing Guidelines

- Abstract: Claim ProposedV2 improves reliability while preserving rate; acknowledge regime-dependence
- Introduction: Motivate the regime-aware approach, do not mention failed variants
- Method: Describe LoS guard + predictive fallback without reference to adaptive/veto extensions
- Results: Present Tables 1–4, note both wins and losses transparently
- Regime Analysis: Characterize when predictive control helps vs hurts
- Discussion: Include failed variant evidence as limitations/future work context
- Conclusion: Restate reliability claim with regime caveat
