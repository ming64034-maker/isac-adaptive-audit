# Section 6: Discussion and Limitations

## 6.1 Summary of Contributions

This work presents Regime-Aware Predictive Beam Control (ProposedV2), a method for integrated sensing and communication (ISAC) beam management that combines a LoS guard with one-step predictive fallback conditioned on a learned world model. The primary findings are:

1. **Reliability improvement**: ProposedV2 reduces outage probability by 32% compared to reactive beam selection while maintaining competitive rate (+1.1%).

2. **Regime-dependent performance**: The advantage of predictive control is not uniform. It is largest in moderate-noise, medium-complexity channel conditions and narrowest in near-perfect or extremely chaotic conditions.

3. **Component ablation**: Both the LoS guard and the predictive fallback mechanism are essential. Removing the LoS guard causes a large return drop (-0.893); removing predictive fallback reduces return (-0.083) and weakens the outage advantage.

4. **Blockage recovery**: ProposedV2 recovers from blockage events 8.4% faster than reactive methods while executing fewer preemptive beam switches.

## 6.2 Limitations

### 6.2.1 Regime-Dependent Performance

The most significant limitation is that ProposedV2 underperforms the reactive baseline on aggregate return at 5 of the 16 sweep points, spanning four regime families:

- **Zero or very low observation noise** (deficits -0.189 at `obs_noise=0.00` and -0.155 at `obs_noise=0.02`): When angle observations are near-perfect, reactive beam selection is near-optimal. The predictor's fallback mechanism adds switching cost without meaningful outage reduction because the reactive baseline already has low outage probability in these conditions.

- **Very high blocker density** (deficit -0.109 at 3 blockers): With multiple simultaneous blockers, the environment becomes chaotic and the predictor's world model rollouts lose accuracy. The predictor overestimates its ability to anticipate blocker motion, leading to incorrect fallback decisions that increase switching cost.

- **Very fast blockers** (deficit -0.047 at 2.0× speed): Fast-moving blockers reduce the effective prediction horizon, making the world model's look-ahead less valuable.

- **Weak reflections** (deficit -0.012 in the weak-reflection setting): When multi-path structure is weak, the predictor has less temporal information to exploit, so its fallback intervention has only marginal value relative to reactive beam selection.

These failure regimes are not artifacts of implementation — they reflect a fundamental tension in predictive beam control: the predictor must decide when to override the current reactive decision, and this decision gets harder at both extremes of the predictability spectrum (too easy → unnecessary override, too hard → unreliable override).

### 6.2.2 Simulation-to-Reality Gap

All experiments are conducted in a simulated environment with parametric channel models. Key simplifications include:
- Fixed reflector geometry (4 static reflectors at predefined positions)
- Synthetic blocker motion (constant-speed linear trajectories)
- Parametric pathloss and SNR models without measured channel traces
- No hardware impairments (phase noise, ADC quantization, beam squint)
- Perfect beam codebook alignment

Real-world mmWave channels exhibit more complex spatial structure, time-varying reflector conditions, and hardware non-idealities that may affect both the reactive and predictive components differently.

### 6.2.3 Fixed Hyperparameter Configuration

The method uses 3 primary hyperparameters (LoS confidence threshold, risk threshold, path spread threshold). While the threshold sweep (Section 4.6) shows robustness within a reasonable range, the optimal values may shift under different channel models, codebook sizes, or mobility patterns. The current values were tuned on the same simulation environment used for evaluation, which may introduce mild overfitting.

### 6.2.4 Computational Cost

The predictive fallback requires a forward pass through the predictor network and, when the world model is used, multi-step latent rollouts. The measured planning latency (0.29 ms) is higher than Reactive (0.003 ms) but lower than Belief-Aware Rollout (0.815 ms) in the simplified simulator. Real-time feasibility requires system-level validation including hardware-in-the-loop measurement. The method also assumes access to a learned world model that must be trained offline; training cost and data requirements are not analyzed in this work.

## 6.3 Negative Results: Attempts at Additional Gating

During development, we explored several extensions to improve performance in the identified failure regimes. We document these negative results for completeness and to inform future work.

### 6.3.1 Adaptive Difficulty (not integrated)

We implemented an adaptive difficulty estimator that computes a real-time hardness score from the observation vector and uses exponential smoothing to interpolate between "easy" and "hard" parameter profiles. The intent was to tighten fallback criteria in easy conditions and loosen them in hard conditions.

**Result**: The adaptive variant achieved return 4.849 vs 4.881 for the non-adaptive baseline in the ablation setup, a drop of 0.032. The EMA-based difficulty signal introduced lag that caused the method to use wrong-regime parameters during regime transitions.

**Conclusion**: The adaptive difficulty concept is directionally correct but the EMA-based implementation introduces unacceptable lag. This approach was not integrated into the main method.

### 6.3.2 Rate-Preserving Fallback Veto (not integrated)

We added a rate-preserving veto that blocks fallback decisions when the rate regret (predicted rate loss relative to reactive) exceeds a threshold while the safety gain (outage reduction) is below a minimum. Two threshold settings were tested: conservative (fire rate 0.45%) and aggressive (fire rate 2.94%).

**Result**: The aggressive veto improved all three original failure-point deficits by about 16–30% (e.g., obs_noise=0.00 deficit from -0.189 to -0.158, obs_noise=0.02 from -0.155 to -0.109). However, the main comparison return dropped from 4.881 to 4.855 because the veto also blocked beneficial fallback decisions in easy and medium regimes.

**Conclusion**: Rate-preserving veto provides directional improvement at failure points but the uniform threshold causes net regression. Regime-conditioned thresholds may resolve this, but were not pursued in this work.

### 6.3.3 Tri-Regime Fallback Gate (not integrated)

We implemented a three-regime gate that classifies each step as clear, medium, or extreme and applies different fallback policies: clear regime suppresses fallback unless safety gain exceeds a high threshold, medium regime keeps existing behavior, and extreme regime applies aggressive rate-preserving veto. The clear-suppress threshold was tuned across three values (0.06, 0.03, 0.02).

**Result**: All three original failure points showed consistent deficit reduction (about 12–42% at the best threshold of 0.03), but the main comparison return never reached the baseline (best: 4.842 vs 4.881, deficit -0.039). Lowering the clear-suppress threshold improved average return but weakened failure-point gains, revealing a structural tradeoff.

**Conclusion**: Regime-conditioned gating shows strong directional evidence as a concept, but the current implementation produces a net regression that could not be resolved through single-parameter tuning. The regime boundaries and threshold values require joint optimization that is beyond the scope of this work.

### 6.3.4 Lessons from Negative Results

The consistent pattern across all three failed extensions — directional improvement at failure points but net regression on average return — suggests that the current fallback mechanism sits on a difficult tradeoff surface for the present predictor and world model architecture. Additional gating logic can shift the tradeoff (helping hard cases at the cost of easy cases) but did not improve both failure points and average return simultaneously in the tested variants. Future work should focus on improving the predictor and world model quality rather than adding post-hoc gating layers.

## 6.4 Future Work

1. **Improved world model for chaotic regimes**: The predictor degrades most at high blocker density. A probabilistic world model with better uncertainty quantification (e.g., ensemble or variational approaches) could improve fallback quality in these conditions.

2. **Online threshold adaptation**: Rather than fixed or EMA-smoothed thresholds, online adaptation using contextual bandits or meta-learning could select regime-appropriate parameters without the lag issues observed in the EMA-based adaptive difficulty approach.

3. **Hardware-in-the-loop evaluation**: Validating the method with measured channel traces or software-defined radio platforms would address the simulation-to-reality gap.

4. **Multi-step predictor**: The current method uses a one-step predictor with world model rollouts. An end-to-end multi-step predictor might reduce the compounding error observed in chaotic regimes.

5. **Joint training of gate and predictor**: The LoS guard and predictor are currently independent components. Joint optimization of the gate condition and the predictive model could yield a better tradeoff surface.
