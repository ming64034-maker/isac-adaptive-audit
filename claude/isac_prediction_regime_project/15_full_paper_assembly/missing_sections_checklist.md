# Missing Sections Checklist

## Sections Present in Draft

- [x] Abstract
- [x] I. Introduction
- [x] II. Problem Formulation
- [x] III. Evaluation Protocol
- [x] IV. Experimental Results (A--E)
- [x] V. Regime Analysis (A--F)
- [x] VI. Discussion and Limitations (A--D)
- [x] VII. Conclusion
- [x] Appendix: Claim Boundary
- [x] References (placeholder)
- [x] Evidence Boundary statement

## Sections Requiring Future Completion

### 1. Method/Architecture Section (missing)
**Priority**: High
**What's needed**: A dedicated section between Evaluation Protocol and Experimental Results describing:
- LoS guard architecture (input signals, confidence scoring, threshold logic)
- World model structure (architecture, training objective, rollout procedure)
- Predictive fallback mechanism (beam scoring, selection rule)
- Full ProposedV2 algorithm pseudocode
**Current status**: Partial method description embedded in Problem Formulation (Section II-A) and Evaluation Protocol. Insufficient for an IEEE paper; reviewers will expect a standalone Method section.
**Source material**: `06_writing/section4_hybrid_controller_v0.md`, `04_code/repo_inventory.md`

### 2. Related Work section (missing)
**Priority**: High
**What's needed**: Standard IEEE related work covering:
- Predictive beamforming (next-step beam/angle/channel prediction)
- Reactive beam selection baselines
- Hybrid/gated control architectures
- Regime-aware or context-adaptive beam management
- Differentiated positioning statement
**Current status**: Brief literature framing in Introduction paragraph 2. Needs full section.
**Source material**: `06_writing/paper_outline.md`, `00_brief/project_brief.md`

### 3. References (placeholder only)
**Priority**: High
**What's needed**: Complete bibliography with ~20--35 entries.
**Current status**: Placeholder line only.

### 4. Figures and Tables (cross-reference only)
**Priority**: Medium
**What's needed**: 
- Figure 1: Return difference vs Reactive across sweep dimensions
- Figure 2: Outage probability vs observation noise
- Figure 3: Blocker density impact on rate-outage tradeoff
- Actual rendered table environments for Tables I--V
**Current status**: Data tables present in markdown; figures referenced but not generated.
**Source material**: `06_writing/figure_table_captions_v0.md`, `06_writing/figure_table_storyboard.md`

### 5. Statistical Reporting (missing)
**Priority**: Medium
**What's needed**: Per-seed mean and standard deviation for all metrics. Confidence intervals or sign-consistency checks.
**Current status**: Aggregate-only reporting over 5 seeds. Section III notes this limitation.

### 6. Event-Level Mechanism Validation (missing)
**Priority**: Low
**What's needed**: Switching traces, fallback trigger analysis per regime, case studies of correct vs. incorrect fallback decisions.
**Current status**: Only blockage event recovery analysis (Section IV-D) with 40 events. No per-decision mechanism validation.

### 7. Computational Complexity Analysis (missing)
**Priority**: Low
**What's needed**: FLOP counts, memory requirements, training wall-clock time, inference throughput bounds.
**Current status**: Only latency measured in simulator (0.29 ms). No complexity analysis.

## Sections Intentionally Omitted

- **Adaptive difficulty method**: Failed variant, relegated to Discussion Section VI-C.
- **Rate-preserving veto method**: Failed variant, relegated to Discussion Section VI-C.
- **Tri-regime gate method**: Failed variant, relegated to Discussion Section VI-C.
- **Formal proofs/regret bounds**: Not in evidence boundary. Section II provides conceptual notation only.
