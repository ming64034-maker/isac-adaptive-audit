# Integration Decision — Rate-Preserving Fallback Veto v2

## Decision: **REJECT** (Do not integrate into ProposedV2)

## Rationale

Per the decision rules:

> 如果 main comparison return 下降，reject。

The main comparison return dropped from 4.8808 (conservative veto, essentially identical to no-veto baseline of 4.8809) to 4.8545 (aggressive veto).

| Threshold | Main Return | Δ vs Baseline | Veto Fire Rate |
|---|---|---|---|
| No veto (baseline) | 4.8809 | — | — |
| 0.04/0.015 (conservative) | 4.8808 | -0.0001 | 0.45% |
| 0.012/0.012 (aggressive) | 4.8545 | **-0.0264** | 2.94% |

The aggressive veto is too blunt: it improves failure-point returns by 0.027–0.048 but degrades the average return by 0.026, indicating it blocks beneficial fallback decisions in easy/medium regimes.

## What Worked

- All 3 failure points showed **measurable improvement** (14–30% deficit reduction)
- Outage advantage over Reactive was preserved at all 3 points
- The veto mechanism itself is sound: when a fallback decision has high rate regret AND low safety gain, blocking it is the right call

## What Didn't Work

- The same thresholds applied uniformly across all regimes caused over-vetoing in easy scenarios
- Veto fire rate of 2.94% is too high for scenarios where the predictor is reliable (e.g., blocker_density=0.0, obs_noise=0.0)
- The net effect is negative: gains at failure points are offset by losses in easy regimes

## Recommended Path Forward

### Option A: Regime-Adaptive Thresholds (preferred)

Instead of fixed thresholds, make them depend on the adaptive difficulty signal already in the codebase (`_adaptive_profile()`):

- **Easy regime**: `rate_regret_threshold = 0.04`, `min_safety_gain = 0.03` (rarely veto — trust the predictor)
- **Hard regime**: `rate_regret_threshold = 0.008`, `min_safety_gain = 0.008` (aggressively veto — predictor is unreliable)

This would require ~20 lines of code change and a `proposedv2_use_adaptive_veto` flag.

### Option B: Single Compromise Threshold

Try an intermediate value (e.g., `0.02/0.02`) to see if there is a sweet spot that helps failure points without hurting the average. The failure-point deficit reduction from conservative (0.45% fire rate) to aggressive (2.94% fire rate) suggests improvement is monotonic in fire rate — so an intermediate threshold may capture partial benefit with less average-return damage.

### Option C: Abandon Veto, Fix Root Cause

The return deficit at failure points is not fundamentally about fallback decisions being wrong. It is about the predictor overestimating its own accuracy in hard regimes. Instead of patching with veto logic, improve the predictor's uncertainty calibration or the world model's rollout quality in high-noise/high-density regimes.

## Verdict

The rate-preserving fallback veto is a **correctly-motivated mechanism with positive directional evidence** but the uniform-threshold implementation causes net regression. Do not merge in current form. Option A (regime-adaptive thresholds) is the most promising follow-up.
