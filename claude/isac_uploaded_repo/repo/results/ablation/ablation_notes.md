# Ablation Notes

- BeliefAwareRollout_V1 disables beam-gain use, LoS guard, auxiliary shortlist, and global fallback at inference. It reuses the available Model v2 checkpoint, so it is an inference-side V1 proxy rather than a separately trained no-ranking checkpoint.
- ProposedV2_NoLoSGuard widens the fallback thresholds enough that predictive fallback is active for most timesteps. Treat it as an almost always-on fallback stress test, not as a pure one-line removal of the LoS confidence check.
- Skipped: no separate checkpoint trained with beam_gain_pairwise_rank_loss_weight=0 is present. The current ProposedV2Policy uses the one-step predictor for fallback, so pairwise ranking affects the BeliefAwareRollout model path rather than this policy directly.
