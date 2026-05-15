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

### 1. Method/Architecture Section (written, not yet integrated)
**Priority**: High — now reduced to Medium (content exists, integration pending)
**What's needed**: ~~A dedicated section between Evaluation Protocol and Experimental Results describing:~~ (content written in `method_section_v0.md`)
- [x] LoS guard architecture (input signals, confidence scoring, threshold logic)
- [x] World model structure (architecture, training objective, rollout procedure)
- [x] Predictive fallback mechanism (beam scoring, selection rule)
- [x] Full ProposedV2 algorithm pseudocode
- [x] All five evaluated methods defined: Reactive, One-Step Predictive, Belief-Aware Rollout, Oracle, ProposedV2
**Current status**: Standalone `method_section_v0.md` created in `15_full_paper_assembly/`. Covers all required content: 5 controller definitions with pseudocode, LoS guard with trigger logic, predictive fallback with scoring function, candidate shortlist construction, training summary, ablation variant descriptions, and explicit boundary against failed adaptive/veto/tri-regime variants. **Remaining work**: Integrate this section into `full_paper_draft_v0.md` (insert as Section III or IV, renumber downstream sections).
**Source material**: `method_section_v0.md`, `06_writing/section4_hybrid_controller_v0.md`, `baselines.py`, `model.py`, `planner.py`, `config.py`

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

### 4. Figures and Tables (assets found, manuscript integration pending)
**Priority**: Medium
**What's needed**: 
- Decide which candidate figures become the final main-paper figure set
- Add manuscript citations/captions for the selected figures
- Consolidate or remove the redundant V-C / V-D slice tables once their figure replacements are adopted
- Render final IEEE table environments for the retained numbered tables
**Current status**: Candidate assets now exist for the conceptual schematic, scene-sweep overview, observation-noise slice, blocker-density tradeoff, ablation, blockage-event timeline, latency/complexity comparison, and a qualitative return-outage regime map. `paper_figure_table_list.md` now tracks these assets and statuses. The manuscript itself still contains no figure citations.
**Source material**: `15_full_paper_assembly/paper_figure_table_list.md`, `15_full_paper_assembly/figure_table_restructuring_plan_v0.md`, `06_writing/figure_table_captions_v0.md`, `06_writing/figure_table_storyboard.md`

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

### 8. Unlabeled Section V Data Tables (missing cataloguing)
**Priority**: Medium
**What's needed**: Sections V-C (Observation Noise Spectrum) and V-D (Blocker Density) still contain embedded data tables that are not assigned table numbers and are not cross-referenced in prose. The V-F regime-boundary summary table is also embedded but unnumbered; if retained, it is the natural future `Table V`.
**Current status**: `paper_figure_table_list.md` now catalogs the V-C, V-D, and V-F table objects and flags the intended replacements. Section IV-D is now explicitly referenced as `Table IV`, so that specific gap is resolved. The remaining choice is whether V-C / V-D survive as numbered tables or are removed once the replacement figures are integrated.

## Sections Intentionally Omitted

- **Adaptive difficulty method**: Failed variant, relegated to Discussion Section VI-C.
- **Rate-preserving veto method**: Failed variant, relegated to Discussion Section VI-C.
- **Tri-regime gate method**: Failed variant, relegated to Discussion Section VI-C.
- **Formal proofs/regret bounds**: Not in evidence boundary. Section II provides conceptual notation only.
