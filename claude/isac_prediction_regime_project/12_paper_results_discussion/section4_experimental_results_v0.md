# Section 4: Experimental Results

## 4.1 Evaluation Protocol

All methods are evaluated under a standardized protocol: 5 random seeds (0–4), 4 episodes per seed, 200 slots per episode. The primary metrics are time-averaged rate (bits/s/Hz), outage probability (fraction of slots with SNR below the outage threshold), beam success rate (fraction of slots where the chosen beam index matches the optimal beam), and aggregate return (a weighted combination of rate, outage penalty, and beam switching cost). Planning latency is reported in milliseconds per decision.

The environment models a multi-blocker dynamic channel with 32 candidate beams, 4 fixed reflectors, and pathloss + blockage-dependent SNR. Scene difficulty is varied along four dimensions: blocker density (0–3 blockers), blocker speed (0.5–2.0× baseline), observation noise (0.00–0.10 std), and reflection strength (weak/medium/strong).

## 4.2 Main Method Comparison

Table 1 reports the aggregate comparison across five methods.

| Method | Avg Rate | Outage Prob | Beam Success | Return | Latency (ms) |
|---|---|---|---|---|---|
| **ProposedV2 (Ours)** | **5.064** | **0.072** | **0.793** | **4.881** | 0.286 |
| Reactive | 5.010 | 0.106 | 0.742 | 4.744 | 0.003 |
| Belief-Aware Rollout | 4.900 | 0.108 | 0.745 | 4.633 | 0.815 |
| One-Step Predictive | 4.094 | 0.042 | 0.873 | 3.999 | 0.266 |
| Oracle (upper bound) | 6.033 | 0.000 | 0.920 | 6.016 | 1.568 |

**Key observations:**

1. **Rate**: ProposedV2 achieves 5.064 bits/s/Hz, a +0.054 gain over Reactive in aggregate and +0.163 over Belief-Aware Rollout. However, rate advantage is regime-dependent: ProposedV2 wins rate at only 6/16 scene sweep points. The aggregate rate gain is modest, while rate advantage is regime-dependent.

2. **Outage** (strongest claim): ProposedV2 reduces outage probability by 32% vs Reactive (0.072 vs 0.106) and by 33% vs Belief-Aware Rollout (0.072 vs 0.108). Outage wins at 16/16 scene sweep points. This is the primary and most robust reliability gain.

3. **Beam success** (strong claim): ProposedV2 achieves 0.793 beam success rate, +0.052 over Reactive. Beam success wins at 16/16 scene sweep points, confirming that predictive beam selection captures the correct beam more often than purely reactive angle-based selection.

4. **Return**: The aggregate return of 4.881 reflects a balanced tradeoff — modest rate advantage (+1.1%), substantially lower outage (-32%), and higher beam accuracy (+7.0%). Return wins at 11/16 sweep points; the 5 points where Reactive leads on return are documented as failure regimes below.

5. **Latency**: ProposedV2 adds ~0.29 ms of planning latency per slot compared to ~0.003 ms for Reactive. Planning latency is higher than Reactive but lower than Belief-Aware Rollout in the simplified simulator; real-time feasibility requires system-level validation.

6. **Relative to upper bound**: ProposedV2 achieves 81.1% of the Oracle return, while Reactive achieves 78.9%. The gap to Oracle is primarily from imperfect blockage prediction.

## 4.3 Scene Sweep: Regime-Dependent Performance

We evaluate all methods across 16 scene configurations spanning four difficulty dimensions. Table 2 summarizes the comparison between ProposedV2 and Reactive across the sweep.

| Dimension | Value | ProposedV2 Return | Reactive Return | Deficit | ProposedV2 Outage | Reactive Outage |
|---|---|---|---|---|---|---|
| blocker_density | 0.0 | 5.153 | 5.088 | **+0.065** | 0.055 | 0.071 |
| blocker_density | 1.0 | 4.825 | 4.777 | **+0.048** | 0.074 | 0.101 |
| blocker_density | 2.0 | 4.687 | 4.607 | **+0.081** | 0.084 | 0.120 |
| blocker_density | 3.0 | 4.258 | 4.367 | **-0.109** | 0.101 | 0.145 |
| obs_noise | 0.00 | 4.994 | 5.183 | **-0.189** | 0.046 | 0.050 |
| obs_noise | 0.02 | 5.065 | 5.220 | **-0.155** | 0.053 | 0.057 |
| obs_noise | 0.05 | 4.862 | 4.763 | **+0.098** | 0.071 | 0.099 |
| obs_noise | 0.10 | 4.407 | 3.731 | **+0.676** | 0.086 | 0.178 |
| blocker_speed | 0.5 | 4.748 | 4.695 | **+0.054** | 0.068 | 0.109 |
| blocker_speed | 1.0 | 4.881 | 4.744 | **+0.137** | 0.072 | 0.106 |
| blocker_speed | 1.5 | 4.841 | 4.821 | **+0.020** | 0.074 | 0.099 |
| blocker_speed | 2.0 | 4.724 | 4.771 | **-0.047** | 0.075 | 0.096 |
| reflection_strength | weak | 4.677 | 4.689 | -0.012 | 0.114 | 0.133 |
| reflection_strength | medium | 4.769 | 4.740 | **+0.030** | 0.081 | 0.107 |
| reflection_strength | baseline | 4.881 | 4.744 | **+0.137** | 0.072 | 0.106 |
| reflection_strength | strong | 4.876 | 4.705 | **+0.170** | 0.066 | 0.106 |

**Aggregate sweep statistics**: ProposedV2 beats or matches Reactive on outage at 16/16 sweep points and on beam success at 16/16 sweep points — these are the two most robust claims. Return advantage is narrower (11/16 wins) and rate advantage is regime-dependent (6/16 wins).

**Failure regimes**: The largest return deficits appear at:
- `obs_noise = 0.00` (deficit -0.189): With perfect observations, reactive beam selection is near-optimal and predictive fallback adds unnecessary switching cost.
- `obs_noise = 0.02` (deficit -0.155): Very low noise still favors reactive simplicity.
- `blocker_density = 3.00` (deficit -0.109): With 3 simultaneous blockers, the environment becomes chaotic; the predictor's world model rollouts degrade, causing incorrect fallback decisions.
- `blocker_speed = 2.00` (deficit -0.047): Fast-moving blockers reduce the effective prediction horizon.
- `reflection_strength = weak` (deficit -0.012): Weak multipath leaves less temporal structure for the predictor to exploit, narrowing the benefit relative to reactive selection.

**Strength regimes**: ProposedV2 outperforms Reactive most clearly at moderate-to-high observation noise (0.05–0.10, where reactive decisions are unreliable), low-to-moderate blocker speeds (0.5–1.5x, where prediction remains actionable), and strong reflection conditions (where multi-path information aids prediction).

## 4.4 Ablation Study

Table 3 reports the ablation results isolating the two core components of ProposedV2: the LoS guard and the predictive fallback mechanism.

| Variant | Rate | Outage | Bsucc | Return | Δ Return |
|---|---|---|---|---|---|
| ProposedV2 (Full) | 5.064 | 0.072 | 0.793 | **4.881** | — |
| No LoS Guard | 4.079 | 0.039 | 0.887 | 3.988 | **-0.893** |
| No Predictive Fallback | 5.010 | 0.083 | 0.779 | 4.798 | **-0.083** |
| Reactive | 5.010 | 0.106 | 0.742 | 4.744 | — |

**LoS Guard**: Removing the LoS guard (always-on predictive fallback) causes a large return drop of 0.893. While beam success rate increases (0.887 vs 0.793) and outage falls (0.039 vs 0.072), the rate collapses (4.079 vs 5.064) because the predictor overrides correct reactive beam choices in clear-channel conditions where no fallback is needed. This confirms the LoS guard is the single most critical component for preserving throughput.

**Predictive Fallback**: Removing predictive fallback entirely (reverting to pure reactive beam selection) costs 0.083 in return and increases outage by 0.011 (from 0.072 to 0.083). This is the reliability contribution of the predictive mechanism — it reduces outage events that reactive selection alone cannot prevent.

**Conclusion**: Both components are essential. The LoS guard ensures the predictor only intervenes when necessary (preserving rate), while the predictive fallback provides outage reduction when intervention is warranted.

## 4.5 Blockage Event Recovery

We analyze the 40 blockage events recorded across all episodes. Recovery time is defined as the number of slots from blockage onset until the rate returns to within 80% of the pre-blockage level.

| Method | Avg Recovery (slots) | Preemptive Switch Rate | Fallback Trigger Rate |
|---|---|---|---|
| ProposedV2 | **1.86** | 47.5% | 90.9% |
| Reactive | 2.03 | 65.0% | 0.0% |
| Belief-Aware Rollout | 3.16 | 72.5% | 0.0% |
| Oracle | N/A (no drop) | 5.0% | 0.0% |

ProposedV2 recovers 0.17 slots (8.4%) faster than Reactive on average. More importantly, ProposedV2 achieves this with fewer preemptive switches (47.5% vs 65.0%) — it correctly anticipates some blockages rather than reacting after the outage occurs. The fallback trigger rate of 90.9% confirms the LoS guard correctly activates the predictive mechanism around blockage onset events.

The Oracle baseline experiences no rate drop at blockage onset because it always selects the optimal beam, establishing the upper bound on recovery performance.

## 4.6 Threshold Sensitivity

A sweep over the three primary hyperparameters (LoS confidence threshold, risk threshold, path spread threshold) across 100 configurations reveals that the method is robust to threshold choice within a reasonable range. The best configuration achieves return 4.884 at (los_confidence=0.80, risk=0.25, path_spread=0.20), about 0.003 above the default thresholds (return 4.881). The top 10 configurations all achieve return within 0.005 of each other, indicating the method does not require precise threshold tuning.

## 4.7 Evidence Boundary

These results are controlled simulation evidence in a simplified 2D dynamic-blockage environment. They should not be interpreted as real-system performance or universal superiority over all predictive beamforming methods. All comparisons are limited to the five evaluated methods under the specified simulation protocol. The sweep points, ablation variants, and hyperparameter ranges reported here constitute the full set of conditions tested; performance outside these conditions is not characterized.
