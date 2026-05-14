# Method: Regime-Aware Predictive Beam Control

This section describes the evaluated controllers at the level of architecture, decision logic, and design intent. The description is grounded in the current implementation and is sufficient for a reader to interpret the main comparison table (Table I) and the ablation study (Table III). Implementation-level details omitted here can be found in the companion code package. The notation follows Section II: time is slotted, `b_t` denotes the controller's internal state at slot `t`, and the beam codebook `A` has size `N = 32`.

---

## 1. Evaluated Controllers

Five controllers are evaluated in the main comparison. All share the same observation interface (8-dimensional vector per slot) and the same 32-beam codebook. They differ in whether and how they use history, learned models, and predictive reasoning.

### 1.1 Reactive (Baseline)

Reactive selects the beam whose departure angle is closest to the coarse angle estimate extracted from the current observation vector `o_t`. No observation history, no learned model, and no predictive step are used.

```
Algorithm: Reactive
  Input: observation o_t (8-dim), environment env
  angle = atan2(o_t[2], o_t[3])
  action = env.nearest_beam(angle)
  return action
```

Reactive serves as the primary baseline because it represents the simplest plausible beam selection rule under dynamic blockage: point the beam toward the estimated signal direction. It is also a component retained inside the hybrid controller (Section 2).

### 1.2 One-Step Predictive

One-Step Predictive uses a learned transformer model (`OneStepPredictor`) to predict the next-best beam from an 8-step observation-action history window. The predictor outputs logits over the 32-beam codebook, and the highest-probability beam is selected. No guard, no fallback logic, and no world-model rollout are used. The predictor is trained with a composite loss combining cross-entropy toward oracle actions, soft targets from oracle value vectors, and a pairwise ranking loss. Training uses 48 episodes of behavior data (35% oracle, 65% random) collected in the default simulator configuration.

### 1.3 Belief-Aware Rollout

Belief-Aware Rollout uses a learned history encoder (`HistoryEncoder`, a 2-layer transformer) to produce a 64-dimensional latent belief state `z_t`, a stochastic world model (`WorldModel`, RSSM-inspired) to simulate future latent transitions, and a multi-hypothesis rollout planner (`RolloutPlanner`) to score candidate beams over a 2-step horizon with 6 stochastic particles. Candidate beams are selected via an auxiliary shortlist procedure that ranks beams by predicted utility, LoS probability, and reflection-path probability under configurable gating conditions. A LoS guard can optionally suppress the planner and fall back to reactive selection when the scene appears clear. All learned components are trained jointly on the same 48-episode dataset used for the predictor; training minimizes a composite loss including latent dynamics consistency, reward prediction, value prediction, and beam-gain ranking objectives.

### 1.4 Oracle (Upper Bound)

Oracle performs an exhaustive, noise-free evaluation of all 32 beams at each slot using the environment's internal state. It selects the beam that maximizes the true reward `r_t(a) = alpha * rate - beta * outage - gamma * switching_cost` with `measurement_noise=False`. This establishes an empirical upper bound on achievable performance given the codebook and reward structure, though it is not implementable in practice because it requires perfect knowledge of the propagation environment.

### 1.5 Regime-Aware Predictive Beam Control (ProposedV2)

Regime-Aware Predictive Beam Control combines a line-of-sight (LoS) guard with one-step predictive fallback. The guard evaluates at each slot whether the scene warrants predictive intervention; when it does not, the controller falls back to reactive beam selection. When the guard activates, the controller runs a learned predictor to score candidate beams, builds a shortlist combining local angle-based candidates and global predictor-favored candidates, and selects the highest-scoring beam under a multi-objective utility function that balances rate, outage risk, and switching cost. The controller also enforces a cooldown period after each guard activation to prevent rapid toggling. Section 2 describes each component in detail.

---

## 2. ProposedV2 Architecture

ProposedV2 has four functional layers: (i) observation-history buffering, (ii) LoS guard with cooldown, (iii) candidate shortlist construction, and (iv) multi-objective beam scoring. Figure 1 shows the decision flow; Algorithm 1 provides the pseudocode.

### 2.1 Observation-History Buffering

An 8-slot sliding window of observation-action pairs is maintained via a `HistoryBuffer`. At each slot, the buffer provides `(obs_seq, action_seq)` tensors of shape `(8, 8)` and `(8,)` respectively. This window is the input to the learned predictor whenever the LoS guard activates the predictive branch.

### 2.2 LoS Guard and Cooldown

The LoS guard decides at each slot whether to invoke the predictive fallback or remain in reactive mode. It uses a hard-trigger rule with five conditions, evaluated from the current observation vector `o_t`:

1. **LoS confidence low**: `1 - blocker_indicator < los_confidence_threshold` (default threshold: 0.60)
2. **Blockage risk elevated**: `blocker_indicator >= risk_threshold` (default: 0.25)
3. **Reflection activity**: `reflection_ratio >= reflection_threshold` (default: 0.20)
4. **Path spread**: `path_spread >= path_spread_threshold` (default: 0.20)
5. **Recent outage**: `last_outage > 0`
6. **Risk spike**: `risk_score_delta >= risk_spike_threshold` (default: 0.10)

The risk score is a conservative envelope over four observation channels:

```
risk_score = max(blocker_indicator, last_outage, 0.85 * reflection_ratio, 0.90 * path_spread)
```

If any trigger condition is satisfied, the guard activates the predictive fallback and sets a cooldown counter (`fallback_cooldown_steps`, default: 2). The cooldown keeps the fallback active for the specified number of subsequent slots, preventing rapid toggling between reactive and predictive modes during transient events. The cooldown decrements by 1 each slot; once it reaches zero, the guard re-evaluates the trigger conditions normally.

When the guard is inactive (no trigger and cooldown exhausted), the controller selects the reactive beam by the same rule as the Reactive baseline (Section 1.1).

### 2.3 Candidate Shortlist Construction

When the guard activates, candidate beams are assembled from two sources:

- **Local candidates** (default: 12 beams): Beams near the coarse angle estimate, selected via `env.candidate_actions_from_observation`, which picks the `local_candidate_count` beams closest to the coarse angle, with the spread widened proportionally to the path spread indicator.
- **Global candidates** (default: 6 beams): Top-k beams by predictor probability, added when the scene exhibits elevated blockage risk, reflection activity, or a recent outage. This ensures beams favored by the learned dynamics model are considered even when they lie far from the current angle estimate.

The union additionally includes the previous beam and the reactive beam to guarantee continuity. Duplicates are removed while preserving order. The total candidate count is capped at `local_candidate_count + global_topk_count + 2`, typically 18--20 beams out of the 32-beam codebook.

### 2.4 Multi-Objective Beam Scoring

Each candidate beam is scored under a weighted combination of five signals:

```
score(action) = predictive_weight * utility(action)
              + local_weight * angle_affinity(action)
              + prev_beam_bonus * uncertainty * prev_affinity(action)
              + reactive_bonus * reactive_affinity(action)
              + safety_bonus * safety_score(action)
              - outage_penalty * outage_prob(action)
              - switch_penalty * I[action != prev_beam]
              - reactive_distance_penalty * I[action != reactive_action]
```

where:

- **`utility(action)`**: A mixture of predictor probability and rate estimate for the candidate beam, blended per scene mode (the `predictor_mix` weight varies by whether the scene is classified as normal, blockage-dominant, reflection-dominant, or mixed). When the world model is available, a reward-rerank term from one-step reward prediction is blended in.
- **`angle_affinity(action)`**: Cosine-similarity-like affinity between the beam angle and the coarse angle estimate, in [0, 1].
- **`prev_affinity(action)`**: Circular proximity to the previous beam, scaled to [0, 1] by half the codebook size.
- **`reactive_affinity(action)`**: Circular proximity to the reactive beam choice.
- **`safety_score(action)`**: Softmax-normalized (1 - outage_prob) over the candidate set, rewarding low-outage beams.
- **`outage_prob(action)`**: Predicted outage probability for the candidate beam from the predictor's outage head.
- **`predictive_weight`**: Linearly interpolated between `min_predictive_weight` (0.55) and `max_predictive_weight` (0.90) by the current risk score. Higher risk increases reliance on learned utility.
- **`local_weight`**: `1 - predictive_weight`, ensuring angle information dominates in low-risk conditions.
- **`uncertainty`**: `1 - top_predictor_confidence`, increasing the previous-beam bonus when the predictor is uncertain.

The candidate with the highest score is provisionally selected. A reactive override check then compares the chosen beam against the reactive beam: if the score advantage is smaller than a regime-conditioned gap (`reactive_override_gap`, default: 0.08), the reactive beam is selected instead. This override prevents the predictor from forcing beam changes when its advantage over the simple reactive choice is marginal.

Additionally, a scene-mode-conditioned rate-preserving veto blocks the fallback selection if the rate regret (predicted rate loss vs. reactive) exceeds a threshold while the safety gain (outage reduction) falls below a minimum. In the default (evaluated) configuration, the veto thresholds are set permissively so that the veto rarely fires; the veto is a structural feature of the architecture but does not dominate decision-making in the reported results. The explicit rate-preserving veto variant tested in the ablation-adjacent experiments (Section VI-C) uses tighter thresholds and is documented as a failed extension.

### 2.5 Algorithm Pseudocode

```
Algorithm: Regime-Aware Predictive Beam Control (ProposedV2)
  Input: observation o_t (8-dim), environment env, buffer B, config cfg
  Output: beam action a_t

  // 1. Compute risk and evaluate guard
  risk = max(o_t[4], o_t[5], 0.85*o_t[6], 0.90*o_t[7])
  risk_delta = risk - prev_risk
  hard_trigger = (1-o_t[4] < los_conf_thresh) OR (o_t[4] >= risk_thresh)
              OR (o_t[6] >= refl_thresh) OR (o_t[7] >= path_thresh)
              OR (o_t[5] > 0) OR (risk_delta >= spike_thresh)
  if hard_trigger:
      cooldown = cfg.cooldown_steps
  use_fallback = hard_trigger OR (cooldown > 0)

  // 2. Reactive path
  if not use_fallback:
      angle = atan2(o_t[2], o_t[3])
      action = env.nearest_beam(angle)
      if cooldown > 0: cooldown -= 1
      prev_risk = risk
      return action

  // 3. Predictive fallback path
  cooldown -= 1
  pred_outputs = predictor(B.obs_window, B.action_window)
  candidates = local_candidates_from_angle(o_t, local_k)
             UNION global_topk_from_predictor(pred_outputs, global_k)
             UNION {env.prev_beam, reactive_action}

  for each a in candidates:
      score[a] = predictive_weight * utility(a, pred_outputs, scene_mode)
               + local_weight * angle_affinity(a, o_t)
               + prev_bonus * uncertainty * prev_affinity(a, env)
               + reactive_bonus * reactive_affinity(a, reactive_action)
               + safety_bonus * safety_score(a, pred_outputs)
               - outage_penalty * outage_prob(a, pred_outputs)
               - switch_penalty * I[a != prev_beam]
               - distance_penalty * I[a != reactive_action]

  chosen = argmax(score)
  if score[chosen] < score[reactive] + override_gap:
      chosen = reactive_action

  prev_risk = risk
  return chosen
```

---

## 3. Training Procedure (Summary)

The learned components (predictor, history encoder, and world model) are trained once on a fixed dataset of 48 episodes (9,600 slots) collected with a mixed behavior policy (35% oracle, 65% random) in the default environment configuration. No online data collection or policy-gradient training is used; the controller is constructed from frozen checkpoints at evaluation time.

- **One-Step Predictor**: 12 epochs, Adam optimizer (lr=1e-3), composite loss: cross-entropy + soft target KL + pairwise ranking loss, with optional risk reweighting (disabled by default, `alpha=0.0`).
- **World Model + History Encoder**: 15 epochs, Adam optimizer (lr=1e-3), composite loss: latent dynamics consistency (Gaussian KL), reward MSE, value smooth-L1, outage BCE, LoS BCE, path-type CE, beam-gain smooth-L1, and beam-gain ranking losses.

All models use a hidden dimension of 128, latent dimension of 64, 2 transformer layers with 4 heads, and dropout of 0.1. Training is performed on CPU. Checkpoints are loaded at evaluation time and held fixed across all evaluation seeds, sweep points, and ablation variants.

---

## 4. Ablation Variants

Two ablation variants are evaluated in Section IV-C to isolate the contribution of each core component:

- **No LoS Guard**: The LoS guard is disabled (`rollout_use_los_guard = False`). The predictive fallback is always active; every decision runs the full candidate-shortlist and scoring pipeline. This isolates the cost of removing the reactive-preserving guard.
- **No Predictive Fallback**: The predictive fallback mechanism is removed. The controller retains the guard structure (cooldown, risk tracking) but when the guard would activate, it continues to use the reactive beam selection rule rather than invoking the predictor. This isolates the marginal contribution of the predictor on top of the guarded control structure.

These ablation variants are distinct from the standalone Reactive baseline, which has no guard, no cooldown, and no predictor. The relationship between these four configurations is summarized in Table III.

---

## 5. What Is NOT Implemented or Claimed

The following extensions were prototyped during development but produced net regression and are **not part of the evaluated ProposedV2 controller**. They are documented in Section VI-C as negative results:

1. **Adaptive difficulty estimation** (`proposedv2_use_adaptive_difficulty = False`): An EMA-smoothed hardness score that interpolates between easy and hard parameter profiles. Not used in the main results.
2. **Rate-preserving fallback veto** (`proposedv2_rate_veto_enabled = False`): A tighter rate-regret threshold that blocks fallback decisions causing excessive rate loss. Not used in the main results; the scene-mode-conditioned veto in the default controller uses permissive thresholds.
3. **Tri-regime fallback gate** (`proposedv2_tri_regime_gate_enabled = False`): A three-regime (clear/medium/extreme) classifier with per-regime fallback policies. Not used in the main results.

All three are disabled by boolean flags in the default configuration. A reader who encounters these flags in the code package should understand them as deactivated development artifacts, not as components of the evaluated method.

---

## 6. Evidence and Interpretation Boundary

The controller description above reflects the implemented design. The empirical evaluation (Section IV) reports aggregate snapshot results over 5 seeds without per-seed variance or confidence intervals. Accordingly:

- The LoS guard is described through its trigger logic, but the paper does not claim that the individual trigger thresholds (e.g., `los_confidence_threshold = 0.60`) are calibrated or optimal. The threshold sweep (Section IV-E) shows insensitivity within a range but does not establish optimality.
- The switching notation `g_t`, `tau` from Section II-A is a conceptual abstraction of the multi-condition guard described here; the paper does not claim that a scalar `g_t` has been separately validated.
- The cooldown mechanism is described as a design feature; its behavioral effect (reduced toggling) is not validated through switching-trace analysis.
- All predictive components (predictor, world model, encoder) are evaluated as frozen checkpoints from a single training run per seed. Generalization to different environments, codebook sizes, or channel models is not characterized.
