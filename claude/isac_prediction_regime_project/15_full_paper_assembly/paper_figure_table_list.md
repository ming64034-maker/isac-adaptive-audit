# Paper Figure and Table List

## Metadata Basis

- Manuscript source checked: `claude/isac_prediction_regime_project/15_full_paper_assembly/full_paper_draft_v0.md`
- Planning source checked: `claude/isac_prediction_regime_project/15_full_paper_assembly/figure_table_restructuring_plan_v0.md`
- `fig*_spec_v0.md` files found in `15_full_paper_assembly/`: none
- Candidate figure assets found in repo: `15_full_paper_assembly/figures/figure1_problem_controller_schematic.svg`, `figure2_return_difference_across_sweep_dimensions.svg`, `figure3_outage_vs_observation_noise.svg`, `figure4_blocker_density_return_outage_tradeoff.svg`
- Candidate external assets supplied by user:
  - `/Users/cccwm/Downloads/fig_ablation_v1.svg`
  - `/Users/cccwm/Downloads/fig_event_timeline_v1.svg`
  - `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg`
  - `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png`
  - `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 02_01_34.png`

## 1. Current Manuscript Inventory

### Figures currently present in `full_paper_draft_v0.md`

- None. The markdown draft currently contains no embedded figures and no explicit `Figure 1`, `Figure 2`, ... prose references.

### Tables currently present in `full_paper_draft_v0.md`

| Manuscript object | Section | Reference status in prose | Role |
|---|---|---|---|
| Table I | IV-A | Explicitly referenced | Main method comparison |
| Table II | IV-B | Explicitly referenced | 16-point scene sweep |
| Table III | IV-C | Explicitly referenced | Ablation study |
| Table IV | IV-D | Explicitly referenced | Blockage-event recovery summary |
| Unnumbered table | V-C | Embedded only | Observation-noise slice; duplicated from Table II values |
| Unnumbered table | V-D | Embedded only | Blocker-density slice; duplicated from Table II values |
| Unnumbered table | V-F | Embedded only | Regime-boundary synthesis; natural candidate for future `Table V` if kept |

## 2. Planned Main-Paper Figures and Candidate Assets

| Planned figure | Intended placement | Status | Candidate asset(s) | Notes |
|---|---|---|---|---|
| Figure 1. Dynamic-blockage ISAC scenario schematic + controller schematic / flow diagram (combined conceptual figure) | Section II or Section III-D | existing | `15_full_paper_assembly/figures/figure1_problem_controller_schematic.svg`; `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png` | Current candidate already combines environment schematic and LoS-guard flow logic in one figure, which is compatible with the restructuring plan. |
| Figure 2. Scene-sweep overview figure | Section IV-B | existing | `15_full_paper_assembly/figures/figure2_return_difference_across_sweep_dimensions.svg` | Existing repo figure corresponds to the restructuring-plan replacement for the dense sweep table. |
| Figure 3. Ablation visualization | Section IV-C | existing | `/Users/cccwm/Downloads/fig_ablation_v1.svg` | Candidate replacement for the current Table III-heavy presentation. |
| Figure 4. Blockage-event timeline | Section IV-D | requires event-level data | `/Users/cccwm/Downloads/fig_event_timeline_v1.svg` | Candidate artifact exists, but manuscript use should remain contingent on confirmed per-slot trace provenance. |
| Figure 5(a). Observation-noise spectrum | Section V-C | existing | `15_full_paper_assembly/figures/figure3_outage_vs_observation_noise.svg` | Can be used as panel (a) of the restructuring-plan regime-detail figure. |
| Figure 5(b). Blocker-density return-outage tradeoff | Section V-D | existing | `15_full_paper_assembly/figures/figure4_blocker_density_return_outage_tradeoff.svg` | Can be used as panel (b) of the restructuring-plan regime-detail figure. |
| Figure 6. Latency/complexity comparison | End of Section IV-A or appendix | existing | `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg` | Matches the optional appendix-first figure proposed in the restructuring plan. |

## 3. Additional Candidate Figure

| Candidate figure | Intended placement | Status | Candidate asset(s) | Notes |
|---|---|---|---|---|
| Return-outage regime map | Section V-B or appendix | needs redraw | `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 02_01_34.png` | Current candidate is explicitly qualitative/illustrative. If kept, it should be redrawn from the existing sweep values and labeled conservatively. |

## 4. Table Retention / Replacement Plan

| Current table object | Keep in main paper? | Replacement / follow-up |
|---|---|---|
| Table I | Yes | Keep as the headline numeric comparison table. |
| Table II | Probably appendix after figure integration | Replace main-paper role with Figure 2 scene-sweep overview. |
| Table III | Probably appendix after figure integration | Replace main-paper role with Figure 3 ablation visualization. |
| Table IV | Appendix fallback if event timeline is adopted | Figure 4 is the stronger narrative object, but Table IV remains the safe aggregate fallback. |
| V-C unnumbered slice table | No, if Figure 5 is adopted | Fold into Figure 5(a) or appendix detail only. |
| V-D unnumbered slice table | No, if Figure 5 is adopted | Fold into Figure 5(b) or appendix detail only. |
| V-F unnumbered synthesis table | Yes, likely as future `Table V` | Best current candidate for the manuscript's next numbered table after Table IV. |

## 5. Figure/Table Inconsistencies to Track

- `full_paper_draft_v0.md` currently cites `Table I` through `Table IV` only; it does not yet cite any figures.
- The previous metadata assumption that `Figure 1`, `Figure 2`, and `Figure 3` were already referenced in the manuscript was incorrect.
- The V-C observation-noise table and V-D blocker-density table still exist as embedded unnumbered tables even though the restructuring plan recommends replacing them with figures.
- The V-F regime-boundary summary table is present in the draft body but still unnumbered; if retained, it is the natural future `Table V`.
- The blockage-event timeline is the only planned figure whose manuscript use still depends on confirmed event-level trace support.

## 6. Recommended Evidence Flow After Figure Integration

1. Use the existing combined conceptual schematic as the first figure before results.
2. Use the existing scene-sweep overview figure to replace the main-paper role of the dense sweep table.
3. Use the ablation SVG and the existing noise/density figures as the next quantitative visual layer.
4. Treat the blockage-event timeline as conditional on verified trace provenance.
5. Keep the latency/complexity figure appendix-first unless page budget remains.
