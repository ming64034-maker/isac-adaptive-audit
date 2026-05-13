# Section 5: Regime Analysis — When Predictive Beam Control Helps and Hurts

## 5.1 Motivation

The scene sweep results (Section 4.3) reveal that ProposedV2's advantage over Reactive is not uniform — it varies systematically with scene difficulty. Outage and beam success are robust across all regimes (16/16 wins each), while return and rate advantages are regime-dependent (10/16 and 6/16 wins respectively). This section characterizes the regime boundaries: the conditions under which predictive beam control provides the largest gains, and the conditions under which reactive baselines remain competitive or superior on return.

## 5.2 Regime Taxonomy

We define three operational regimes based on the observation vector components available to the predictor:

### Clear Regime
**Conditions**: blockage indicator < 0.20, no recent outage, reflection ratio < 0.15, path spread < 0.15, risk score below threshold.

**Characteristics**: LoS is dominant, channel state is stable, blockage events are rare. The reactive baseline makes accurate beam decisions from angle information alone.

**ProposedV2 behavior**: The LoS guard keeps the predictor inactive most of the time, preserving the efficiency of reactive beam selection. Occasional predictive fallbacks are triggered by the cooldown mechanism after rare blockage events.

**Observed performance**: Outage improvement is small in absolute terms (-0.01 to -0.02) because both methods achieve low outage. Return advantage is narrow; rate may be slightly above or below Reactive depending on the specific configuration. This regime is not where ProposedV2's value proposition lies.

### Medium-Risk Regime
**Conditions**: Moderate blockage indicator, some path spread, occasional reflection activity. Neither fully clear nor severely degraded.

**Characteristics**: This is the intended operating regime for predictive beam control. Channel dynamics are unpredictable enough that reactive methods make errors, but structured enough that the predictor's world model can anticipate changes.

**ProposedV2 behavior**: The LoS guard activates the predictive fallback with moderate confidence. The world model rollouts provide useful look-ahead, and the beam scoring mechanism balances rate preservation against outage prevention.

**Observed performance**: Largest return advantages over Reactive (+0.05 to +0.15). At `obs_noise = 0.05`, ProposedV2 achieves return 4.839 vs Reactive 4.763 (+0.076), with outage 0.071 vs 0.099 (-28%). At `blocker_speed = 1.5`, return advantage is +0.111 with outage reduction of 23%.

### Extreme Regime
**Conditions**: High blocker density (3 blockers), last_outage positive, path spread above threshold, risk score > 0.65.

**Characteristics**: The channel is chaotic. Multiple blockers create frequent LoS interruptions, and the predictor's world model rollouts become unreliable due to compounding uncertainty over multiple blocker trajectories.

**ProposedV2 behavior**: Predictive fallback is frequently active, but the quality of fallback decisions degrades. The world model overestimates predictability in chaotic environments, leading to fallback decisions that occasionally select worse beams than the reactive baseline.

**Observed performance**: Mixed. At `blocker_density = 3.00`, ProposedV2 return is 4.270 vs Reactive 4.367 (-0.097 deficit), though outage remains substantially better (0.103 vs 0.146, -29%). At `blocker_speed = 2.00`, return deficit is -0.047 despite outage improvement (0.076 vs 0.096). The predictor preserves outage advantage but at increasing rate cost.

## 5.3 The Observation Noise Spectrum

Observation noise creates a particularly informative regime gradient:

| obs_noise | ProposedV2 Return | Reactive Return | Δ | ProposedV2 Outage | Reactive Outage |
|---|---|---|---|---|---|
| 0.00 | 4.998 | 5.183 | **-0.185** | 0.047 | 0.050 |
| 0.02 | 5.063 | 5.220 | **-0.157** | 0.051 | 0.057 |
| 0.05 | 4.839 | 4.763 | **+0.076** | 0.071 | 0.099 |
| 0.10 | 4.349 | 3.731 | **+0.618** | 0.090 | 0.179 |

At zero or near-zero noise, the reactive baseline is near-optimal because angle-based beam selection is perfectly reliable. Predictive fallback adds switching cost without providing meaningful outage reduction.

At moderate noise (0.05), the reactive baseline degrades because noisy observations produce incorrect beam choices. The predictor's history-conditioned world model filters out observation noise, providing a cleaner signal for beam selection.

At high noise (0.10), the gap widens dramatically: ProposedV2 return is +16.6% over Reactive, with outage nearly halved (0.090 vs 0.179). The reactive baseline collapses because noisy angle estimates lead to frequent beam misalignment, while the predictor maintains reasonable accuracy by leveraging the learned dynamics model.

**Key insight**: The cross-over point where ProposedV2 begins to outperform Reactive on return is approximately at `obs_noise ≈ 0.03–0.04`. Below this threshold, reactive methods achieve higher return; above it, predictive control provides increasing advantage. Outage and beam success favor ProposedV2 across the full noise range.

## 5.4 Blocker Density and Predictability Limits

| Density | ProposedV2 Return | Reactive Return | Δ | ProposedV2 Outage | Reactive Outage |
|---|---|---|---|---|---|
| 0 | 5.132 | 5.088 | **+0.044** | 0.060 | 0.071 |
| 1 | 4.813 | 4.777 | **+0.036** | 0.077 | 0.101 |
| 2 | 4.638 | 4.607 | **+0.031** | 0.089 | 0.120 |
| 3 | 4.270 | 4.367 | **-0.097** | 0.103 | 0.146 |

As blocker density increases from 0 to 2, ProposedV2 maintains a consistent return advantage (+0.03 to +0.04) while accumulating outage advantages (-12% to -26%). The predictor successfully anticipates moderate multi-blocker dynamics.

At density 3, the return flips to a deficit (-0.097) while outage remains decisively better (-29%). This dissociation between return and outage suggests the predictor's decisions are directionally correct (reducing outages) but the rate cost of more frequent beam switches in a chaotic environment outweighs the outage benefit in aggregate return.

## 5.5 Reflection Strength

Stronger reflections (lower reflector_loss_db) provide richer multi-path information that the predictor can exploit. ProposedV2's advantage grows monotonically with reflection strength: from -0.022 at weak reflections to +0.154 at strong reflections. The predictor leverages reflection patterns in the observation history to better anticipate blockage transitions, while the reactive baseline cannot use this temporal structure.

## 5.6 Summary of Regime Boundaries

| Condition | Preferred Method | Reason |
|---|---|---|
| Near-zero observation noise | Reactive | Predictor adds switching cost without benefit |
| Very low noise (< 0.03) | Reactive (narrow) | Marginal predictor advantage |
| Moderate noise (0.03–0.10) | **ProposedV2** | Predictor filters noise, reactive degrades |
| High blocker density (3+) | Mixed | ProposedV2 wins outage, loses return |
| Fast blockers (> 1.5×) | Mixed | Short prediction horizon limits benefit |
| Strong reflections | **ProposedV2** | Predictor exploits multi-path temporal patterns |
| Weak reflections | Reactive (narrow) | Less temporal structure to exploit |

These boundaries are not sharp thresholds but identify the operating conditions where each approach is favored. In practice, a single deployment experiences all regimes over time, and the LoS guard in ProposedV2 already provides regime-adaptive behavior by controlling when the predictor intervenes.
