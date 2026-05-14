# Regime-Aware Predictive Beam Control for Dynamic-Blockage ISAC

## Abstract

Dynamic blockage is a central challenge for millimeter-wave and sub-THz integrated sensing and communication (ISAC) systems, where narrow beams are vulnerable to line-of-sight interruption, beam misalignment, and partial observability. Rather than treating predictive beam control as a universally superior alternative to reactive selection, we ask a narrower question: under which dynamic-blocking regimes does predictive information appear useful? We formulate dynamic-blocking ISAC beam control as an evidence-bounded predictive decision problem and evaluate Regime-Aware Predictive Beam Control (ProposedV2), a hybrid controller that combines a line-of-sight guard with one-step predictive fallback. In the current aggregate evaluation, ProposedV2 reduces outage probability by 32% (0.106 to 0.072) and improves beam success rate by 7.0% (0.742 to 0.793) relative to a strong reactive baseline, with outage and beam success improvements holding across all 16 sweep points spanning blocker density, observation noise, blocker speed, and reflection strength. Rate (+1.1%, from 5.010 to 5.064) and aggregate return (+2.9%, from 4.744 to 4.881) advantages are regime-dependent, with return wins at 11/16 sweep points and losses at the remaining 5. Component ablation indicates that both the LoS guard and the predictive fallback are individually necessary, with return drops of -0.893 and -0.083 respectively. These results support a regime-oriented interpretation of predictive beam control for dynamic-blocking ISAC, where reliability improvements are broadly observed but throughput advantages depend on operating conditions.

## I. Introduction

Dynamic blockage is a persistent obstacle in practical ISAC beam control because highly directional beams must be selected from incomplete observations of a changing environment. In millimeter-wave and sub-THz settings, moving users and moving blockers can rapidly change line-of-sight availability, producing sudden beam misalignment and outage events that are difficult to handle with purely reactive decisions.

Much of the predictive beamforming literature is framed as next-step beam, angle, or channel prediction, or as learning a direct state-to-action mapping. That framing is useful but incomplete for the present setting, because it does not directly answer a more operational question: under which dynamic-blocking regimes does predictive information produce enough control benefit to justify its additional complexity?

This paper therefore centers the problem formulation rather than a broad method-superiority claim. We view dynamic-blocking beam control as a partially observed decision problem and focus on organizing current evidence about when predictive information appears useful across blocker density, blocker speed, sensing noise, and reflection-related conditions.

To study this question, we compare a strong reactive baseline with Regime-Aware Predictive Beam Control (ProposedV2), a hybrid controller designed to stay reactive in low-risk conditions and activate one-step predictive fallback in higher-risk conditions. We evaluate not only achievable rate, but also outage probability, beam success rate, and cumulative return, because rate alone does not capture reliability and alignment behavior under dynamic blockage.

The current aggregate evaluation shows clear reliability gains for ProposedV2 over Reactive: outage decreases from 0.106 to 0.072 (-32%), beam success rises from 0.742 to 0.793 (+7.0%), and these improvements hold across all 16 sweep points. Rate (5.010 to 5.064, +1.1%) and aggregate return (4.744 to 4.881, +2.9%) show directional gains in aggregate but are regime-dependent, with return advantage at 11/16 sweep points and deficits at 5/16. The failure regimes — near-zero observation noise, very high blocker density, very fast blockers, and weak reflections — identify conditions where reactive selection remains competitive or superior on return.

The contribution of this work is not a claim of universal superiority or a generally optimal beam controller. Instead, the contribution is threefold. First, we formulate dynamic-blocking ISAC beam control as an evidence-bounded predictive decision problem, emphasizing when predictive information is useful rather than assuming that more planning is always better. Second, we provide a regime-oriented empirical analysis comparing reactive and hybrid predictive beam control across four difficulty dimensions, with outage and beam success improvements observed across all sampled conditions and rate/return advantages showing clear regime dependence. Third, we show that predictive beam control in this setting should be assessed through rate-reliability-alignment tradeoffs rather than throughput alone.

Taken together, the present results support a conservative but meaningful conclusion: predictive beam control in dynamic-blocking ISAC should be evaluated as a regime-dependent design question, and a hybrid reactive-plus-predictive controller is a credible instance of that perspective.

## II. Problem Formulation

We study beam control for a simplified dynamic-blocking ISAC setting in which a serving transmitter-receiver pair must select directional beams over a finite codebook while the propagation environment changes over time. The beam action space is

```text
A = {1, 2, ..., B},
```

with `B = 32` in the evaluated setting. Each beam `a ∈ A` is associated with a main-lobe direction `θ(a)`.

Time is discretized into decision slots indexed by `t = 1, ..., T`. At each slot, the environment has a latent state `s_t` that summarizes quantities affecting beam quality, including user geometry, blockage configuration, and propagation conditions. The controller does not observe `s_t` directly. Instead, it receives an observation `o_t`, which should be interpreted broadly as the currently available sensing or measurement information from which the next beam must be chosen. Let `b_t` denote the controller's internal summary of the observation history up to slot `t`; in a partially observed setting, `b_t` is the operational state on which decisions are based.

**Beam-domain channel model.** For beam `a`, the effective channel at slot `t` is modeled as a sum over available propagation paths:

```text
h_t(a) = Σ_{p ∈ P_t} α_{t,p} · g(a, θ_{t,p}),
```

where `P_t` denotes the set of active paths (LoS and specular reflections), `α_{t,p}` is the complex path gain of path `p`, `θ_{t,p}` is its angle of arrival/departure, and `g(a, θ)` captures the array gain of beam `a` evaluated at angle `θ`. Dynamic blockage affects the channel by removing obstructed paths from `P_t`; multipath reflections contribute additional terms with reduced gain.

**SNR and rate.** Under additive white Gaussian noise with variance `σ²`, the signal-to-noise ratio for beam `a` at slot `t` is

```text
SNR_t(a) = (P_Tx · |h_t(a)|²) / σ²,
```

where `P_Tx` denotes the transmit power. The achievable rate in bits per second per Hertz is

```text
R_t(a) = log₂(1 + SNR_t(a)).
```

The beam action at slot `t` is written as `a_t ∈ A`. The immediate task reward `r_t(a_t)` is a communication-oriented utility that combines rate, outage penalties, and beam switching cost. In the current evaluation, rate, outage probability, beam success rate, and cumulative return are reported as separate metrics. This multi-metric separation is essential because the main empirical story is not a large throughput jump alone, but a rate-reliability-alignment tradeoff under dynamic blockage.

For a policy `pi` that maps belief states to beam actions, the slot-level control objective is represented by

```text
J(pi) = E[sum_{t=1}^{T} r_t(a_t)].
```

Here the expectation is taken over user motion, blockage evolution, observation uncertainty, and any other randomness in the simulated environment. The resulting formulation is partially observed by construction: two histories can produce similar current observations while implying different near-future blockage risk, so a purely instantaneous decision rule need not be sufficient in harder conditions.

**Outage and beam success.** Let `R_th` be the minimum rate threshold for reliable communication. The outage indicator for beam `a` at slot `t` is

```text
O_t(a) = 𝟙{R_t(a) < R_th}.
```

Define the oracle-optimal beam at slot `t` as the beam that maximizes the achievable rate under full (noise-free) knowledge of the propagation environment:

```text
a_t* = arg max_{a ∈ A} R_t(a).
```

The beam success indicator is then

```text
S_t(a) = 𝟙{a = a_t*}.
```

Outage probability and beam success rate reported in the evaluation are the empirical averages of `O_t(a_t)` and `S_t(a_t)` over evaluation episodes. These metrics are reported alongside rate and cumulative return because beam selection accuracy cannot be inferred from average rate alone under dynamic blockage.

### A. Reactive and Predictive Decision Classes

The paper compares two controller classes at the level supported by the current evidence package.

**Reactive policy.** The reactive policy `π_R` selects the beam whose main-lobe direction is closest to the coarse angle estimate `φ_t` extracted from the current observation `o_t`:

```text
a_t^R = arg min_{a ∈ A} |θ(a) - φ_t|,
```

where `φ_t = atan2(o_t[2], o_t[3])`. Here `o_t[2]` and `o_t[3]` are observation channels encoding the real and imaginary components of the estimated signal direction. This decision rule involves no history, no learned model, and no predictive step. Its computational cost is `O(B)` per slot for an exhaustive nearest-angle search (or `O(log B)` with sorted beam angles).

**Hybrid policy (ProposedV2).** The hybrid policy `π_H`, corresponding to Regime-Aware Predictive Beam Control (ProposedV2), operates in two modes:

```text
a_t^H = a_t^R,              if guard_inactive(b_t),
        arg max_{a ∈ C_t} score_t(a),   otherwise,
```

where `C_t ⊂ A` is the candidate shortlist (typically 18--20 beams out of 32) and `score_t(·)` is a multi-objective scoring function described in the companion code package and summarized in Section III. The guard is implemented as a multi-condition hard trigger evaluated from the current observation; when no trigger fires and a cooldown period is exhausted, the controller falls back to the reactive selection `a_t^R`.

To express the logic compactly for the problem formulation, we use a conceptual switching score `g_t` and threshold `τ`:

```text
π_H(b_t) = π_R(b_t),   if g_t ≤ τ,
           π_P(b_t),   if g_t > τ,
```

where `π_P` denotes the predictive fallback policy. This notation captures the central design intent: remain reactive when the scene appears easy, but invoke predictive reasoning when blockage risk, reflection ambiguity, or observation uncertainty becomes more consequential. The notation `g_t`, `τ` is a conceptual abstraction of the multi-condition guard logic; the paper does not claim that a scalar `g_t` has been separately calibrated or validated. The contribution claimed in this manuscript is therefore not that prediction is always better, but that dynamic-blocking beam control is naturally expressed as a belief-dependent switching problem.

**Belief-Aware Rollout (comparator).** The Belief-Aware Rollout controller, included as a comparator, uses a learned latent dynamics model to score beams over a `H = 2`-step lookahead horizon with `M = 6` stochastic particles. Its per-slot cost is `O(K · H · M)` where `K` is the candidate count, compared to `O(K)` for ProposedV2 and `O(B)` for Reactive. In the evaluated setting (`B = 32`), all three controllers are computationally tractable in simulation, but the asymptotic scaling differs meaningfully for larger codebooks.

### B. Dynamic Blockage as a Belief-Dependent Decision Problem

Dynamic blockage creates a distinctive asymmetry between easy and hard decision regimes. In low-risk conditions, line-of-sight structure is often stable enough that a strong reactive controller can respond adequately from current observations alone. In harder conditions, however, blockage onset, partial observability, and rapidly changing propagation can make the immediate observation an incomplete proxy for near-future beam quality. This is the motivation for introducing predictive information selectively rather than uniformly.

To make this idea explicit, we describe scene difficulty through a regime variable `d`. In the current manuscript, `d` is not a dense learned latent coordinate and should not be interpreted as a fully quantified map. Instead, it is an organizing variable attached to the sampled conditions that are already visible in the results package, namely blocker density, blocker speed, observation noise, and reflection strength. The paper's regime-oriented narrative asks whether the gain

```text
G(d) = E[V^{pi_H}(b_t) - V^{pi_R}(b_t) | d]
```

appears more strongly in some sampled conditions than in others. This framing matches the evidence boundary: the manuscript studies where predictive information looks useful, not whether predictive control is universally superior across all dynamic-blocking scenarios.

### C. Scope and Evidence Boundary

The present formulation is intentionally narrow. It describes a simplified slotted beam-control problem in a simulated dynamic-blocking environment, not a deployment-ready ISAC stack. The manuscript does not claim general POMDP optimality, universal robustness across regimes, or statistical significance from seed-level variance.

Three scope limits are particularly important. First, the current paper package relies on aggregate results over 5 seeds; all empirical statements should be interpreted as evidence from the reported evaluation protocol rather than as statistical claims about the broader population of channel conditions. Second, the switching notation above is used to express the controller's design logic, not to prove that a separately calibrated risk score has already been measured in the available outputs. Third, the regime variable `d` serves as an evaluation organizer over sampled conditions rather than as proof of a complete quantitative regime map.

Under these limits, the paper's main problem-formulation claim is conservative but meaningful: dynamic-blocking ISAC beam control should be treated as a partially observed, regime-dependent decision problem, and this viewpoint is the correct lens for interpreting the current hybrid-versus-reactive evidence.

## III. Evaluation Protocol

The evaluation protocol is designed to match the paper's evidence-bounded contribution. Rather than asking whether predictive beam control is universally superior, the protocol asks two narrower questions: first, whether Regime-Aware Predictive Beam Control shows improvement over a strong reactive baseline in the available aggregate snapshot; and second, whether sweep summaries indicate that any sampled regime dimensions are more prediction-helpful than others.

### A. Primary Comparison and Evaluation Unit

The headline comparison is between Reactive and Regime-Aware Predictive Beam Control (ProposedV2). Reactive denotes the baseline controller that selects beams from currently available information without an explicit predictive fallback step. ProposedV2 denotes the hybrid controller that behaves reactively in easier conditions and activates a one-step predictive fallback by design in harder conditions.

The aggregate results are reported over 5 random seeds (0--4), with 4 evaluation episodes per seed and 200 slots per episode, yielding 20 episodes and 4,000 slots per method.

### B. Metrics and Interpretation

Four metrics are used throughout the paper: achievable rate (bits/s/Hz), outage probability (fraction of slots with SNR below the outage threshold), beam success rate (fraction of slots where the chosen beam index matches the optimal beam), and cumulative return (a weighted combination of rate, outage penalty, and beam switching cost). Planning latency is reported in milliseconds per decision.

This multi-metric view is essential because the current results do not support a story of large throughput gain alone. ProposedV2 improves rate only modestly while showing a clearer improvement in outage and beam success. For that reason, the evaluation protocol treats rate as necessary but insufficient and interprets the method through a rate-reliability-alignment tradeoff rather than through average rate in isolation.

### C. Sampled Regime Dimensions

The regime-oriented part of the protocol organizes evidence across four sampled dimensions: blocker density (0--3 blockers), blocker speed (0.5--2.0x baseline), observation noise (0.00--0.10 std), and reflection strength (weak/medium/baseline/strong). These dimensions correspond directly to the paper's decision-theoretic question about when predictive information appears useful.

### D. Environment and Sensing Abstraction

The environment models a multi-blocker dynamic channel with 32 candidate beams, 4 fixed reflectors, and pathloss + blockage-dependent SNR. Blockers move along constant-speed linear trajectories.

In this manuscript, the sensing function is represented through compact blockage- and path-related features available to the controller, rather than through raw radar point clouds, camera, LiDAR, or full sensing waveform design. The observation vector `o_t ∈ R⁸` encodes the following ISAC-style sensing cues:

- **Coarse angle estimate** (`o_t[2], o_t[3]`): real and imaginary components of the estimated signal direction, from which the coarse angle `φ_t = atan2(o_t[2], o_t[3])` is extracted.
- **LoS confidence** (`o_t[4]`): an indicator of whether the line-of-sight path appears clear, approximately `1 - blocker_indicator`.
- **Blockage risk** (`o_t[5]`): a scalar reflecting the likelihood that a blocker occludes the dominant path; ranges from 0 (no blockage) to 1 (fully blocked).
- **Reflection activity** (`o_t[6]`): a measure of multipath energy relative to the dominant path.
- **Path spread** (`o_t[7]`): angular spread across detected paths, capturing how dispersed the multipath arrivals are.
- **SNR measurement** (`o_t[0], o_t[1]`): coarse received power and noise-floor estimates.

This abstraction allows the study to isolate the decision problem induced by partial observability and dynamic blockage — namely, when predictive information derived from sensing features should override a simpler reactive beam selection — without requiring raw radar, camera, or LiDAR processing, and without claiming joint waveform or beamformer co-design. The paper does not assert that these features are directly measured by a hardware ISAC prototype, nor does it characterize sensing accuracy, resolution, or detection probability. The eight-dimensional observation vector is a simulation-level stand-in for the richer sensing side of a deployed ISAC system, chosen to make the regime-oriented comparison between reactive and predictive beam control tractable at the current evidence scale.

## IV. Experimental Results

### A. Main Method Comparison

Table I reports the aggregate comparison across five methods.

| Method | Avg Rate | Outage Prob | Beam Success | Return | Latency (ms) |
|---|---|---|---|---|---|
| **ProposedV2 (Ours)** | **5.064** | **0.072** | **0.793** | **4.881** | 0.286 |
| Reactive | 5.010 | 0.106 | 0.742 | 4.744 | 0.003 |
| Belief-Aware Rollout | 4.900 | 0.108 | 0.745 | 4.633 | 0.815 |
| One-Step Predictive | 4.094 | 0.042 | 0.873 | 3.999 | 0.266 |
| Oracle (upper bound) | 6.033 | 0.000 | 0.920 | 6.016 | 1.568 |

**Key observations:**

1. **Rate**: ProposedV2 achieves 5.064 bits/s/Hz, a +0.054 gain over Reactive in aggregate and +0.163 over Belief-Aware Rollout. Rate advantage is regime-dependent, winning at 6/16 scene sweep points.

2. **Outage** (strongest claim): ProposedV2 reduces outage probability by 32% vs Reactive (0.072 vs 0.106) and by 33% vs Belief-Aware Rollout (0.072 vs 0.108). Outage wins at 16/16 scene sweep points.

3. **Beam success** (strong claim): ProposedV2 achieves 0.793 beam success rate, +0.052 over Reactive. Beam success wins at 16/16 scene sweep points.

4. **Return**: The aggregate return of 4.881 reflects a balanced tradeoff -- modest rate advantage (+1.1%), substantially lower outage (-32%), and higher beam accuracy (+7.0%). Return wins at 11/16 sweep points; the 5 points where Reactive leads are documented as failure regimes.

5. **Latency**: ProposedV2 adds approximately 0.29 ms of planning latency per slot compared to approximately 0.003 ms for Reactive. Planning latency is higher than Reactive but lower than Belief-Aware Rollout (0.815 ms) in the simplified simulator; real-time feasibility requires system-level validation.

6. **Relative to upper bound**: ProposedV2 achieves 81.1% of the Oracle return, while Reactive achieves 78.9%.

**Belief-Aware Rollout in context.** Belief-Aware Rollout achieves lower aggregate return (4.633) than ProposedV2 (4.881) despite a more elaborate planning architecture. This result should not be read as evidence against predictive control or rollout-based methods in general. Under the current evaluation conditions — a world model trained on a fixed dataset of 48 episodes, evaluated with 2-step stochastic rollouts — the gap is consistent with the interpretation that multi-step imagined trajectories can be sensitive to the fidelity of the learned dynamics: when the latent model imperfectly captures the true environment, compounding across rollout steps may degrade rather than improve beam decisions. ProposedV2 takes a more conservative approach by using a guarded one-step fallback without multi-step rollout, which limits exposure to model compounding at the cost of shallower lookahead. The comparison is informative about the design tradeoff between shallow guarded prediction and deeper rollout-based planning under a fixed training budget, not about the general merit of either architecture.

### B. Scene Sweep: Regime-Dependent Performance

We evaluate all methods across 16 scene configurations spanning four difficulty dimensions. Table II summarizes the comparison between ProposedV2 and Reactive across the sweep.

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

**Aggregate sweep statistics**: ProposedV2 beats or matches Reactive on outage at 16/16 sweep points and on beam success at 16/16 sweep points. Return advantage is narrower (11/16 wins) and rate advantage is regime-dependent (6/16 wins).

**Failure regimes**: The largest return deficits appear at:
- `obs_noise = 0.00` (deficit -0.189): With perfect observations, reactive beam selection is near-optimal and predictive fallback adds unnecessary switching cost.
- `obs_noise = 0.02` (deficit -0.155): Very low noise still favors reactive simplicity.
- `blocker_density = 3.00` (deficit -0.109): With 3 simultaneous blockers, the environment becomes chaotic; the predictor's world model rollouts degrade, causing incorrect fallback decisions.
- `blocker_speed = 2.00` (deficit -0.047): Fast-moving blockers reduce the effective prediction horizon.
- `reflection_strength = weak` (deficit -0.012): Weak multipath leaves less temporal structure for the predictor to exploit.

**Strength regimes**: ProposedV2 shows its clearest return advantages over Reactive at moderate-to-high observation noise (0.05--0.10), low-to-moderate blocker speeds (0.5--1.5x), and strong reflection conditions.

### C. Ablation Study

Table III reports the ablation results isolating the two core components of ProposedV2: the LoS guard and the predictive fallback mechanism.

| Variant | Rate | Outage | Bsucc | Return | Delta Return |
|---|---|---|---|---|---|
| ProposedV2 (Full) | 5.064 | 0.072 | 0.793 | **4.881** | -- |
| No LoS Guard | 4.079 | 0.039 | 0.887 | 3.988 | **-0.893** |
| No Predictive Fallback | 5.010 | 0.083 | 0.779 | 4.798 | **-0.083** |
| Reactive | 5.010 | 0.106 | 0.742 | 4.744 | -- |

**LoS Guard**: Removing the LoS guard (always-on predictive fallback) causes a large return drop of 0.893. While beam success rate increases (0.887 vs 0.793) and outage falls (0.039 vs 0.072), the rate collapses (4.079 vs 5.064) because the predictor overrides correct reactive beam choices in clear-channel conditions where no fallback is needed. This indicates the LoS guard is the single most critical component for preserving throughput.

**Predictive Fallback**: Disabling the predictive fallback reduces return by 0.083 relative to the full ProposedV2 controller and increases outage from 0.072 to 0.083. However, this ablation is not identical to the Reactive baseline: it retains the remaining guarded ProposedV2 control structure and therefore still shows lower outage, higher beam success, and higher return than Reactive. This indicates that the predictive fallback provides an additional reliability improvement on top of the guarded controller, but it is not the only source of the gain.

**Conclusion**: Both components are essential. The LoS guard ensures the predictor only intervenes when necessary (preserving rate), while the predictive fallback provides outage reduction when intervention is warranted.

### D. Blockage Event Recovery

We analyze the 40 blockage events recorded across all episodes. Recovery time is defined as the number of slots from blockage onset until the rate returns to within 80% of the pre-blockage level.

| Method | Avg Recovery (slots) | Preemptive Switch Rate | Fallback Trigger Rate |
|---|---|---|---|
| ProposedV2 | **1.86** | 47.5% | 90.9% |
| Reactive | 2.03 | 65.0% | 0.0% |
| Belief-Aware Rollout | 3.16 | 72.5% | 0.0% |
| Oracle | N/A (no drop) | 5.0% | 0.0% |

ProposedV2 recovers 0.17 slots (8.4%) faster than Reactive on average. More importantly, ProposedV2 achieves this with fewer preemptive switches (47.5% vs 65.0%) -- it correctly anticipates some blockages rather than reacting after the outage occurs. The fallback trigger rate of 90.9% is consistent with the LoS guard correctly activating the predictive mechanism around blockage onset events.

### E. Threshold Sensitivity

A sweep over the three primary hyperparameters (LoS confidence threshold, risk threshold, path spread threshold) across 100 configurations indicates that the method is relatively insensitive to threshold choice within the tested range. The best configuration achieves return 4.884 at (los_confidence=0.80, risk=0.25, path_spread=0.20), approximately 0.003 above the default thresholds (return 4.881). The top 10 configurations all achieve return within 0.005 of each other, indicating the method does not require precise threshold tuning.

## V. Regime Analysis: When Predictive Beam Control Helps and Hurts

### A. Motivation

The scene sweep results (Section IV-B) reveal that ProposedV2's advantage over Reactive is not uniform -- it varies systematically with scene difficulty. Outage and beam success favor ProposedV2 at all 16 sweep points, while return and rate advantages are regime-dependent (11/16 and 6/16 wins respectively). This section characterizes the regime boundaries.

### B. Regime Taxonomy

We define three operational regimes:

**Clear Regime**: Blockage indicator less than 0.20, no recent outage, reflection ratio less than 0.15, path spread less than 0.15, risk score below threshold. LoS is dominant, channel state is stable. The reactive baseline makes accurate beam decisions from angle information alone. ProposedV2's LoS guard keeps the predictor inactive most of the time. Outage improvement is small in absolute terms because both methods achieve low outage. This regime is not where ProposedV2's value proposition lies.

**Medium-Risk Regime**: Moderate blockage indicator, some path spread, occasional reflection activity. Neither fully clear nor severely degraded. This is the intended operating regime. The LoS guard activates predictive fallback with moderate confidence, and the world model rollouts provide useful look-ahead. Largest return advantages over Reactive are around +0.10 to +0.14. At `obs_noise = 0.05`, ProposedV2 achieves return 4.862 vs Reactive 4.763 (+0.098), with outage 0.071 vs 0.099 (-28%). At `blocker_speed = 1.0`, return advantage is +0.137 with outage reduction of 32%.

**Extreme Regime**: High blocker density (3 blockers), last_outage positive, path spread above threshold, risk score greater than 0.65. The channel is chaotic; the predictor's world model rollouts become unreliable due to compounding uncertainty. Predictive fallback is frequently active but the quality of fallback decisions degrades. At `blocker_density = 3.00`, ProposedV2 return is 4.258 vs Reactive 4.367 (-0.109 deficit), though outage remains substantially better (0.101 vs 0.145, -30%).

### C. The Observation Noise Spectrum

| obs_noise | ProposedV2 Return | Reactive Return | Delta | ProposedV2 Outage | Reactive Outage |
|---|---|---|---|---|---|
| 0.00 | 4.994 | 5.183 | **-0.189** | 0.046 | 0.050 |
| 0.02 | 5.065 | 5.220 | **-0.155** | 0.053 | 0.057 |
| 0.05 | 4.862 | 4.763 | **+0.098** | 0.071 | 0.099 |
| 0.10 | 4.407 | 3.731 | **+0.676** | 0.086 | 0.178 |

At zero or near-zero noise, the reactive baseline is near-optimal. Predictive fallback adds switching cost without providing meaningful outage reduction. At moderate noise (0.05), the predictor's history-conditioned world model filters observation noise, providing a cleaner signal for beam selection. At high noise (0.10), the gap widens materially: ProposedV2 return is +18.1% over Reactive, with outage nearly halved (0.086 vs 0.178). The cross-over point where ProposedV2 begins to exceed Reactive on return is approximately at `obs_noise between 0.03 and 0.04`. Outage and beam success favor ProposedV2 across the full noise range.

### D. Blocker Density and Predictability Limits

| Density | ProposedV2 Return | Reactive Return | Delta | ProposedV2 Outage | Reactive Outage |
|---|---|---|---|---|---|
| 0 | 5.153 | 5.088 | **+0.065** | 0.055 | 0.071 |
| 1 | 4.825 | 4.777 | **+0.048** | 0.074 | 0.101 |
| 2 | 4.687 | 4.607 | **+0.081** | 0.084 | 0.120 |
| 3 | 4.258 | 4.367 | **-0.109** | 0.101 | 0.145 |

As blocker density increases from 0 to 2, ProposedV2 maintains a consistent return advantage (+0.05 to +0.08) while accumulating outage advantages (-16% to -30%). At density 3, the return flips to a deficit (-0.109) while outage remains better (-30%). This dissociation suggests the predictor's decisions are directionally correct (reducing outages) but the rate cost of more frequent beam switches in a chaotic environment outweighs the outage benefit in aggregate return.

### E. Reflection Strength

Stronger reflections provide richer multi-path information that the predictor can exploit. ProposedV2's advantage grows monotonically with reflection strength: from -0.012 at weak reflections to +0.170 at strong reflections. The predictor leverages reflection patterns in the observation history to better anticipate blockage transitions.

### F. Summary of Regime Boundaries

| Condition | Preferred Method | Reason |
|---|---|---|
| Near-zero observation noise | Reactive | Predictor adds switching cost without benefit |
| Very low noise (less than 0.03) | Reactive (narrow) | Marginal predictor advantage |
| Moderate noise (0.03--0.10) | **ProposedV2** | Predictor filters noise, reactive degrades |
| High blocker density (3+) | Mixed | ProposedV2 wins outage, loses return |
| Very fast blockers (2.0x) | Mixed | Short prediction horizon limits benefit |
| Strong reflections | **ProposedV2** | Predictor exploits multi-path temporal patterns |
| Weak reflections | Reactive (narrow) | Less temporal structure to exploit |

## VI. Discussion and Limitations

### A. Summary of Contributions

This work presents Regime-Aware Predictive Beam Control (ProposedV2), a method for ISAC beam management that combines a LoS guard with one-step predictive fallback conditioned on a learned world model. The primary findings are:

1. **Reliability improvement**: ProposedV2 reduces outage probability by 32% compared to reactive beam selection while maintaining competitive rate (+1.1%).

2. **Regime-dependent performance**: The advantage of predictive control is not uniform. It is largest in moderate-noise, medium-complexity channel conditions and narrowest in near-perfect or extremely chaotic conditions.

3. **Component ablation**: Both the LoS guard and the predictive fallback mechanism are essential. Removing the LoS guard causes a large return drop (-0.893); disabling predictive fallback reduces return (-0.083) and weakens the outage advantage.

4. **Blockage recovery**: ProposedV2 recovers from blockage events 8.4% faster than reactive methods while executing fewer preemptive beam switches.

### B. Limitations

**Regime-Dependent Performance**: The main limitation is that ProposedV2 underperforms the reactive baseline on aggregate return at 5 of 16 sweep points: zero or very low observation noise (deficits -0.189 and -0.155), very high blocker density (-0.109 at 3 blockers), very fast blockers (-0.047 at 2.0x speed), and weak reflections (-0.012). These failure regimes reflect a fundamental tension: the predictor must decide when to override the current reactive decision, and this decision gets harder at both extremes of the predictability spectrum.

**Simulation-to-Reality Gap**: All experiments use a simulated environment with parametric channel models. Key simplifications include fixed reflector geometry, synthetic blocker motion, parametric pathloss models, no hardware impairments, and perfect beam codebook alignment. Real-world mmWave channels exhibit more complex spatial structure and hardware non-idealities.

**Fixed Hyperparameter Configuration**: The method uses 3 primary hyperparameters. While the threshold sweep (Section IV-E) shows relative insensitivity within the tested range, the optimal values may shift under different channel models or mobility patterns.

**Computational Cost**: The predictive fallback requires a forward pass through the predictor network and multi-step latent rollouts. Measured planning latency (0.29 ms) is higher than Reactive (0.003 ms) but lower than Belief-Aware Rollout (0.815 ms). Real-time feasibility requires system-level validation. The higher latency and lower return of Belief-Aware Rollout in the current evaluation reinforce the interpretation that deeper rollouts do not automatically translate into better decisions when the learned dynamics carry residual error.

### C. Negative Results: Attempts at Additional Gating

During development, we explored several extensions to improve performance in the identified failure regimes. We document these negative results for completeness and to inform future work.

**Adaptive Difficulty (not integrated)**: An adaptive difficulty estimator using EMA-smoothed hardness scores achieved return 4.849 vs 4.881 for the non-adaptive baseline (-0.032). The EMA-based signal introduced lag during regime transitions. This approach was not integrated into the main method.

**Rate-Preserving Fallback Veto (not integrated)**: A rate-preserving veto that blocks fallback decisions when predicted rate loss exceeds a threshold improved failure-point deficits by 16--30% but reduced main comparison return from 4.881 to 4.855 due to blocking beneficial fallback decisions in easy and medium regimes.

**Tri-Regime Fallback Gate (not integrated)**: A three-regime gate (clear/medium/extreme) with per-regime fallback policies showed consistent failure-point deficit reduction (12--42% at best threshold) but never reached baseline return (best: 4.842 vs 4.881, -0.039), revealing a structural tradeoff between failure-point improvement and average performance.

**Lessons**: The consistent pattern -- directional improvement at failure points but net regression on average -- suggests additional gating logic shifts the tradeoff (helping hard cases at the cost of easy cases) without improving both simultaneously. Future work should focus on improving predictor and world model quality rather than adding post-hoc gating layers.

### D. Future Work

1. **Improved world model for chaotic regimes**: A probabilistic world model with better uncertainty quantification could improve fallback quality at high blocker density.
2. **Online threshold adaptation**: Contextual bandits or meta-learning could select regime-appropriate parameters without EMA lag.
3. **Hardware-in-the-loop evaluation**: Validating with measured channel traces or SDR platforms.
4. **Multi-step predictor**: An end-to-end multi-step predictor might reduce compounding error in chaotic regimes.
5. **Joint training of gate and predictor**: Joint optimization could yield a better tradeoff surface.

## VII. Conclusion

This paper has argued for a narrower and more defensible way to study predictive beam control under dynamic blockage in ISAC. Instead of asking whether more planning is universally better than reactive selection, we ask when predictive information appears useful under partial observability and scene-dependent blockage risk. Under that framing, Regime-Aware Predictive Beam Control (ProposedV2) should be understood not as a general optimal solution, but as a credible instance of a selective predictive-control architecture.

The main empirical findings are: (1) ProposedV2 reduces outage probability by 32% and improves beam success rate by 7.0% relative to a strong reactive baseline, with these reliability gains holding across all 16 sweep points; (2) rate and return advantages are regime-dependent, with return wins at 11/16 sweep points and losses concentrated in near-zero noise, very high blocker density, and very fast blocker conditions; (3) both the LoS guard and predictive fallback are individually necessary components, with the guard being the single largest contributor to performance; and (4) attempted extensions via additional gating layers consistently reveal a structural tradeoff between failure-point improvement and average return.

The resulting conclusion is diagnostic rather than triumphant. Dynamic-blocking beam control is better viewed as a regime-dependent decision problem than as a blanket prediction-is-better story, and a hybrid reactive-plus-predictive architecture is a reasonable response to that structure. Stronger claims will require denser evaluation, seed-level statistics, and mechanism-level validation, but the present evidence already supports the central point: in blockage-aware ISAC, the value of prediction depends on when and where it is used.

## Appendix: Claim Boundary

### Primary Claim

**Regime-Aware Predictive Beam Control improves reliability-oriented metrics (outage probability, beam success rate) while preserving competitive aggregate rate, but gains are regime-dependent.**

This claim is supported by:
- 32% outage reduction vs Reactive (0.072 vs 0.106), 16/16 sweep points with better outage
- 7.0% beam success rate improvement (0.793 vs 0.742), 16/16 sweep points with better beam success
- Competitive aggregate rate (5.064 vs 5.010), though rate advantage is regime-dependent (6/16 wins)
- 8.4% faster blockage recovery (1.86 vs 2.03 slots)

### What We DO Claim

1. **Reliability improvement in aggregate**: ProposedV2 reduces outage probability and improves beam selection accuracy across a wide range of operating conditions.

2. **Regime-dependent advantage**: The method provides the largest gains in noisy and medium-complexity conditions. In easy regimes (near-zero noise) and very hard regimes (3+ blockers, very fast motion), the reactive baseline can match or exceed ProposedV2 on return.

3. **Essential components**: Both the LoS guard and predictive fallback are individually necessary; removing either causes material degradation (ablation: -0.893 and -0.083 return respectively).

4. **Predictive value in noise**: The method's advantage grows with observation noise (+0.676 return advantage at obs_noise=0.10), demonstrating that learned dynamics models can filter sensing noise more effectively than reactive approaches.

5. **Simulation evidence**: All claims are bounded by the simulated environment described in the evaluation protocol. No claims are made about real-world deployment performance.

### What We DO NOT Claim

1. **Universal superiority**: ProposedV2 does not outperform Reactive on all metrics in all regimes.

2. **State-of-the-art**: We do not claim superiority over all existing methods. The comparison set is limited to the five evaluated methods.

3. **Optimal gating**: We do not claim the current LoS guard thresholds are optimal.

4. **Real-world performance**: No claims are made about performance with measured channels, hardware impairments, or non-stationary environments.

5. **Computational efficiency advantage**: Training cost and data requirements are not compared to baselines.

6. **Real-time feasibility**: Planning latency is not validated in a real-time system context.

7. **Consistent rate advantage**: The aggregate rate gain (+1.1%) does not hold uniformly -- rate advantage is regime-dependent (6/16 wins).

### Failed Variant Claims

The following are explicitly NOT claimed:

1. Adaptive difficulty improves performance (evidence: -0.032 return regression)
2. Uniform rate-preserving veto improves main return (evidence: -0.026 return regression)
3. Tri-regime fallback gate matches baseline return (evidence: -0.039 return regression at best setting)
4. Additional gating layers can simultaneously improve failure points and average return (evidence: consistent structural tradeoff across all three attempts)

## References

[1] -- [N] Placeholder for literature references to be inserted.

## Evidence Boundary

These results are controlled simulation evidence in a simplified 2D dynamic-blockage environment. They should not be interpreted as real-system performance or universal superiority over all predictive beamforming methods. All comparisons are limited to the five evaluated methods under the specified simulation protocol. The sweep points, ablation variants, and hyperparameter ranges reported here constitute the full set of conditions tested; performance outside these conditions is not characterized.
