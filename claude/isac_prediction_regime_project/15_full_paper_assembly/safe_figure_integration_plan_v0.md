# Safe Figure Integration Plan v0

**Scope:** plan only.  
**Do not edit yet:** `claude/isac_prediction_regime_project/15_full_paper_assembly/full_paper_draft_v0.md`  
**Goal:** integrate only evidence-safe figures into the main manuscript, consistent with the claim boundary and the figure readiness audit.

## Guardrails

- Do not imply statistical significance or uncertainty quantification that is not present.
- Do not use event-level figures as mechanism proof unless their logged data source is located and documented.
- Do not imply deployment performance, hardware validation, or real-time feasibility.
- Do not introduce any new results beyond the values already present in the manuscript tables.

## 1. Exact Figure Files Currently Available in the Repo

### Vector figure sources in the repo

- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure1_problem_controller_schematic.svg`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure2_return_difference_across_sweep_dimensions.svg`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure3_outage_vs_observation_noise.svg`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure4_blocker_density_return_outage_tradeoff.svg`

### Preview PNGs in the repo

- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/rendered_png/figure1_problem_controller_schematic.png`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/rendered_png/figure2_return_difference_across_sweep_dimensions.png`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/rendered_png/figure3_outage_vs_observation_noise.png`
- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/rendered_png/figure4_blocker_density_return_outage_tradeoff.png`

### Supporting script in the repo

- `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/redraw_figures_2_4.py`

### Figure spec files

- No `fig*_spec_v0.md` files are currently present in `15_full_paper_assembly/`.

## 2. Figures Currently Outside the Repo

These files exist only outside the repo at the moment:

- `/Users/cccwm/Downloads/fig_ablation_v1.svg`
- `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg`
- `/Users/cccwm/Downloads/fig_event_timeline_v1.svg`
- `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png`
- `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 02_01_34.png`

### External image-to-slot mapping

The previously shared new images can be mapped to the planned figure slots as follows:

- `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png`
  - corresponds to **Figure 1** scenario/controller concept
  - use as a redraw reference or fallback candidate only after copying into the repo
- `/Users/cccwm/Downloads/fig_ablation_v1.svg`
  - corresponds to **Figure 3** ablation visualization
  - this is the strongest current external main-text candidate
- `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg`
  - corresponds to **Appendix Figure A1** latency/complexity comparison
- `/Users/cccwm/Downloads/fig_event_timeline_v1.svg`
  - corresponds to the currently excluded blockage-event timeline
  - do not integrate unless the event-level trace source is documented
- `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 02_01_34.png`
  - corresponds to the currently excluded return-outage regime-map concept
  - do not integrate into the main text in its current illustrative form

### Recommended copy targets if later approved

- Ablation figure:
  - copy to `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure3_ablation_visualization.svg`
- Optional latency/complexity figure:
  - copy to `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/appendix_figure_latency_complexity.svg`
- Excluded blockage-event timeline:
  - copy only if trace provenance is documented, then use `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/appendix_figure_blockage_event_timeline.svg`
- Optional Fig. 1 concept-art reference:
  - if needed as a redraw reference only, copy to `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/reference_figure1_scenario_concept.png`
- Excluded regime-map concept:
  - if needed as a redraw reference only, copy to `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/reference_regime_map_concept.png`

Do not copy any of these files yet unless explicitly instructed.

## 3. Safe Main-Text Figure Set and Proposed Numbering

Use only the readiness-audit-safe set in the main paper:

1. **Figure 1**: Dynamic-blockage ISAC scenario / controller schematic
   - Asset status: repo-tracked but needs redraw/readability cleanup
   - Planned source: `figures/figure1_problem_controller_schematic.svg`
   - External reference that can be placed in this slot later if copied and cleaned: `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png`
2. **Figure 2**: Sweep `Δreturn` figure across the 16 sampled scene slices
   - Planned source: `figures/figure2_return_difference_across_sweep_dimensions.svg`
3. **Figure 3**: Ablation visualization
   - Planned source: external only for now
   - Candidate source: `/Users/cccwm/Downloads/fig_ablation_v1.svg`
4. **Figure 4**: Blocker-density return-outage tradeoff
   - Planned source: `figures/figure4_blocker_density_return_outage_tradeoff.svg`

### Optional / appendix

- **Appendix Figure A1**: latency/complexity comparison
  - Candidate source: `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg`

### Exclude for now

- Blockage-event timeline
- Return-outage regime map
- Observation-noise figure in its current form

## 4. Proposed Insertion Points in `full_paper_draft_v0.md`

### Figure 1

- **Section:** `III-D. Environment and Sensing Abstraction`
- **Insertion point:** immediately after the paragraph ending at line 170
- **Reason:** this is the safest place to ground the environment and sensing abstraction before results begin

### Figure 2

- **Section:** `IV-B. Scene Sweep: Regime-Dependent Performance`
- **Insertion point:** immediately after the Table II block ending at line 223, before the aggregate sweep statistics at line 225
- **Reason:** the figure can become the main visual summary of regime dependence without requiring immediate removal of Table II

### Figure 3

- **Section:** `IV-C. Ablation Study`
- **Insertion point:** immediately after the Table III block ending at line 245, before the ablation interpretation text at line 247
- **Reason:** the figure can visually summarize the component tradeoff before the prose explanation

### Figure 4

- **Section:** `V-D. Blocker Density and Predictability Limits`
- **Insertion point:** immediately after the density table block ending at line 304, before the interpretation paragraph at line 306
- **Reason:** this is the cleanest place to replace the slice table’s explanatory burden with a visual tradeoff view

## 5. Caption Drafts for the Safe Main-Text Figures

### Figure 1 caption draft

`Dynamic-blockage ISAC beam-control setting and selective predictive-control schematic. A transmitter selects beams from a finite codebook under moving blockers, partial observability, and reflection-assisted propagation; compact sensing cues are used to decide when reactive selection is sufficient and when guarded predictive fallback is activated. The diagram is schematic only and does not represent a hardware-validated sensing stack or waveform pipeline.`

### Figure 2 caption draft

`Aggregate return difference across the 16 sampled sweep points, computed as ProposedV2 minus Reactive. Positive values indicate higher aggregate return for ProposedV2. The figure summarizes sampled conditions only and should be read alongside the manuscript's outage results, which favor ProposedV2 at all 16 sweep points.`

### Figure 3 caption draft

`Ablation summary for the two core ProposedV2 components. Removing the LoS guard causes the largest aggregate return drop, while removing predictive fallback weakens the outage advantage and lowers return more modestly. Values are aggregate results from the manuscript ablation table and do not include variance estimates.`

### Figure 4 caption draft

`Blocker-density slice viewed through aggregate return and outage. ProposedV2 remains lower-outage at all four sampled density settings, but the return advantage disappears and becomes negative at the highest-density slice (`d=3`). The figure summarizes only the sampled density settings used in the manuscript tables.`

## 6. Tables That Become Redundant or Less Necessary After Figure Integration

### Clearly redundant or mostly redundant

- **Table III** (`IV-C` ablation table)
  - Once Figure 3 is integrated, Table III becomes largely redundant in the main text.
  - Recommended later action: move Table III to appendix or compress to a brief numeric appendix reference.

- **V-D unnumbered density slice table**
  - Once Figure 4 is integrated, the current density slice table becomes redundant in the main text.
  - Recommended later action: remove it from the main text or move it to appendix if exact numbers must remain visible.

### Partially redundant

- **Table II** (`IV-B` scene sweep summary)
  - Figure 2 reduces its visual burden, but Table II still contains exact return and outage values that the `Δreturn` figure does not fully replace.
  - Recommended later action: keep Table II during the first conservative figure insertion pass, then decide in a separate layout pass whether to move it to appendix.

### Not made redundant by the safe main-text set

- **Table I** should remain in the main text.
- **Table IV** should remain in the main text unless a data-backed event timeline is later approved.
- **V-C observation-noise slice table** is not yet displaced, because the current observation-noise figure is not approved for safe main-text use.
- **V-F regime-boundary summary table** is also still useful unless a later synthesis rewrite changes the section structure.

## 7. Page-Budget Warning for 8-Page IEEE Format

Adding four main-text figures without removing tables will likely overfill an 8-page IEEE conference layout.

The main risks are:

- keeping Table II and adding Figure 2
- keeping Table III and adding Figure 3
- keeping the V-D slice table and adding Figure 4
- adding a large conceptual Figure 1 before results

Conservative page-budget implication:

- Figure 1 is likely to consume at least one single-column block and possibly more if redrawn with large labels.
- Figure 2 is strongest as a double-column figure.
- Figure 3 may fit in one column if compact, but could expand to two.
- Figure 4 likely wants at least a single-column footprint and may read better at larger width.

Safe planning conclusion:

- Do not integrate all four figures and keep all current tables unchanged in the same manuscript pass if the target remains 8 pages.
- The first safe integration pass should insert figure citations/captions conservatively and leave table-removal decisions for an immediate follow-up layout pass.

## 8. Main-Text Integration Sequence

Use this sequence when figure insertion actually begins:

1. Insert Figure 1 only if the redrawn schematic is readable and stripped of over-detailed implementation labels. The previously shared scenario/controller image can serve as the corresponding visual reference for this slot after it is copied into the repo and normalized.
2. Insert Figure 2 as the first quantitative main-text figure.
3. Insert Figure 3 only after the ablation asset is copied into the repo and tracked there.
4. Insert Figure 4 as the safe regime-detail figure.
5. Keep the latency/complexity figure out of the main text.
6. Keep the blockage-event timeline excluded unless a logged event source is documented first.

## 9. Exact Next Single Task

Redraw and simplify `claude/isac_prediction_regime_project/15_full_paper_assembly/figures/figure1_problem_controller_schematic.svg` into a main-text-safe Figure 1 asset that removes embedded caption text, dense implementation labels, and any unsupported mechanism cues.
