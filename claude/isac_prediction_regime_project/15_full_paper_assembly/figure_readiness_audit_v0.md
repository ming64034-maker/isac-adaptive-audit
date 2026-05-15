# Figure Readiness Audit v0

**Audited manuscript:** `claude/isac_prediction_regime_project/15_full_paper_assembly/full_paper_draft_v0.md`  
**Audited metadata:** `claude/isac_prediction_regime_project/15_full_paper_assembly/paper_figure_table_list.md`  
**Audited figure assets:** repo figures under `15_full_paper_assembly/figures/` plus current external candidates in `/Users/cccwm/Downloads/`

## Overall Verdict

The current figure set is promising but not uniformly manuscript-ready. Three figures are close to main-text use because they are already tied cleanly to existing manuscript tables: the sweep `Δreturn` figure, the blocker-density return-outage tradeoff figure, and the ablation figure. Two figures are conceptually useful but need redraw to avoid over-detailed or mixed-metric presentation: the Fig. 1 scenario/controller schematic and the observation-noise figure. The blockage-event timeline is unsafe unless its per-slot trace provenance is confirmed, and the latency/complexity figure should remain appendix-only because it mixes measured latency with qualitative algorithm labels. The planned return-outage regime map is currently illustrative rather than data-backed and should not be treated as a quantitative manuscript figure in its current form.

One global manuscript issue remains: `full_paper_draft_v0.md` still contains no figure citations, so even the strongest candidates are not yet integrated into the paper body.

## Summary Table

| Figure | Current asset(s) | Status | Basis | Evidence-boundary warning in caption? | Recommended placement |
|---|---|---|---|---|---|
| Fig. 1 scenario/controller schematic | `figures/figure1_problem_controller_schematic.svg`; `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 01_49_33 (1).png` | needs redraw | illustrative only | Yes | Main text, near Section III-D |
| Sweep `Δreturn` figure | `figures/figure2_return_difference_across_sweep_dimensions.svg` | ready | existing data | Yes | Main text, Section IV-B |
| Observation-noise figure | `figures/figure3_outage_vs_observation_noise.svg` | needs redraw | existing data | Yes | Main text only if redrawn as part of Section V-C |
| Blocker-density return-outage tradeoff | `figures/figure4_blocker_density_return_outage_tradeoff.svg` | ready | existing data | Yes | Main text, Section V-D |
| Ablation figure | `/Users/cccwm/Downloads/fig_ablation_v1.svg` | ready | existing data | Yes | Main text, Section IV-C |
| Blockage-event timeline | `/Users/cccwm/Downloads/fig_event_timeline_v1.svg` | unsafe unless data-backed | requires additional logs or confirmed logged traces | Yes | Appendix if provenance is confirmed |
| Latency/complexity figure | `/Users/cccwm/Downloads/fig_latency_complexity_v1.svg` | appendix only | mixed: existing latency data + qualitative logic | Yes | Appendix |
| Return-outage regime map | `/Users/cccwm/Downloads/ChatGPT Image 2026年5月15日 02_01_34.png` | needs redraw | illustrative only | Yes | Appendix unless rebuilt from exact table values |

## Figure-by-Figure Audit

### 1. Fig. 1 Scenario / Controller Schematic

**Status:** `needs redraw`

**IEEE suitability:** Conceptually useful, but the current repo figure is too dense for manuscript use. It embeds figure-number text inside the artwork, uses very small internal labels, and includes implementation-specific module names and trigger details that exceed what the current paper text cleanly defines.

**Basis:** Illustrative only. This figure is derived from the environment and controller description, not from measured data.

**Evidence-boundary warning:** Yes. The caption should explicitly say the figure is a schematic, not to scale, and not a hardware-validated sensing pipeline.

**Risk assessment:** High risk of implying unsupported mechanism if the figure shows exact trigger formulas, cooldown logic, or predictor-module details more strongly than the manuscript text justifies. It can also overstate sensing realism if it looks like a deployed ISAC stack rather than a simulation abstraction.

**Label / number match:** No table-number matching is needed, but the current repo figure mentions `OneStepPredictor`, risk formulas, and internal states that are not yet cleanly cross-defined in the manuscript. The user-supplied scenario image is visually cleaner, but it would still need one unified caption and style.

**Required fixes:**
- Use one final vector figure rather than a mix of repo flowchart and external concept art.
- Remove any embedded `Figure 1.` caption text from inside the artwork.
- Reduce internal text density; keep only the beam-control setting, sensing cues, LoS guard, reactive branch, and predictive-fallback branch.
- Avoid exact trigger formulas or threshold-looking annotations inside the final main-text figure.

**Recommended caption:**  
`Dynamic-blockage ISAC beam-control setting and selective predictive-control schematic. A transmitter selects beams from a finite codebook under moving blockers, partial observability, and reflection-assisted propagation; compact sensing cues are used to decide when reactive selection is sufficient and when guarded predictive fallback is activated. The diagram is schematic only and does not represent a hardware-validated sensing stack or waveform pipeline.`

**Recommended placement:** Main text, immediately after the environment / sensing abstraction in Section III-D.

### 2. Sweep `Δreturn` Figure

**Status:** `ready`

**IEEE suitability:** Suitable for main-text use. The figure is visually clean, directly tied to the manuscript's main regime-dependence story, and numerically aligned with the 16 rows of Table II.

**Basis:** Existing data from Table II in `full_paper_draft_v0.md` lines 208--223.

**Evidence-boundary warning:** Yes. The caption should say these are aggregate differences at sampled sweep points and that no variance bars are shown.

**Risk assessment:** Moderate risk of over-emphasizing return alone if the caption does not also remind the reader that outage favors ProposedV2 at all 16 points. Low risk of implying significance if the figure is presented explicitly as a sampled sweep summary.

**Label / number match:** Yes. The displayed deltas match Table II:
- Blocker density: `+0.065`, `+0.048`, `+0.081`, `-0.109`
- Observation noise: `-0.189`, `-0.155`, `+0.098`, `+0.676`
- Blocker speed: `+0.054`, `+0.137`, `+0.020`, `-0.047`
- Reflection strength: `-0.012`, `+0.030`, `+0.137`, `+0.170`

**Required fixes:**
- Keep the y-axis label explicit as `Δ return (ProposedV2 - Reactive)`.
- Ensure the caption notes that positive bars indicate higher aggregate return for ProposedV2.
- Use manuscript-consistent dimension names and value formatting.

**Recommended caption:**  
`Aggregate return difference across the 16 sampled sweep points, computed as ProposedV2 minus Reactive. Positive values indicate higher aggregate return for ProposedV2. The figure summarizes sampled conditions only and should be read alongside the manuscript's outage results, which favor ProposedV2 at all 16 sweep points.`

**Recommended placement:** Main text, Section IV-B.

### 3. Observation-Noise Figure

**Status:** `needs redraw`

**IEEE suitability:** Close, but not fully ready in its current form. The plotted values are correct for outage, but the figure annotates a `return crossover ~0.03-0.04` even though return itself is not shown. That mixed-metric annotation makes the current figure harder to defend cleanly.

**Basis:** Existing data from the Section V-C observation-noise table, lines 290--293, plus the return discussion in line 295.

**Evidence-boundary warning:** Yes. The caption should say this is a sampled observation-noise slice with aggregate values only.

**Risk assessment:** Moderate risk of implying stronger mechanism than supported, because the visual combines outage curves with a return crossover band. That can invite the reader to infer a more exact transition point than the current evidence warrants.

**Label / number match:** Partial match. The outage curves match the manuscript table exactly:
- ProposedV2 outage: `0.046`, `0.053`, `0.071`, `0.086`
- Reactive outage: `0.050`, `0.057`, `0.099`, `0.178`
But the displayed crossover annotation refers to return values from the same table, not to the plotted outage series.

**Required fixes:**
- Either redraw as a two-panel figure showing both return and outage, or remove the return-crossover band from the current outage-only plot.
- Keep the title metric-specific.
- State in the caption whether the crossover is directly shown or only inferred from the corresponding return table.

**Recommended caption:**  
`Observation-noise slice across four sampled settings. ProposedV2 maintains lower outage than Reactive across the sampled range, while the manuscript's corresponding return values transition from Reactive-favoring at very low noise to ProposedV2-favoring at moderate noise. The figure shows aggregate sampled values only and does not provide variance estimates.`

**Recommended placement:** Main text only if redrawn cleanly; otherwise keep as supporting material for Section V-C.

### 4. Blocker-Density Return-Outage Tradeoff

**Status:** `ready`

**IEEE suitability:** Suitable for manuscript use. This is the cleanest current regime-detail figure because it directly visualizes the dissociation emphasized in Section V-D: ProposedV2 remains lower-outage across density points while the return advantage flips negative at the highest density.

**Basis:** Existing data from Table II rows 208--211 and the Section V-D density table rows 301--304.

**Evidence-boundary warning:** Yes. The caption should say this is a sampled density slice and not a full regime map.

**Risk assessment:** Low-to-moderate risk. The figure is data-backed, but the caption should avoid implying a dense or universal tradeoff surface. It is a four-point sampled slice.

**Label / number match:** Yes. The plotted pairs align with the manuscript density slice:
- ProposedV2: `(0.055, 5.153)`, `(0.074, 4.825)`, `(0.084, 4.687)`, `(0.101, 4.258)`
- Reactive: `(0.071, 5.088)`, `(0.101, 4.777)`, `(0.120, 4.607)`, `(0.145, 4.367)`

**Required fixes:**
- Keep the axis labels explicit as `Outage probability` and `Aggregate return`.
- Ensure the density labels `d=0...3` are defined in the caption.
- Keep the `return flips at d=3` note descriptive rather than causal.

**Recommended caption:**  
`Blocker-density slice viewed through aggregate return and outage. ProposedV2 remains lower-outage at all four sampled density settings, but the return advantage disappears and becomes negative at the highest-density slice (`d=3`). The figure summarizes only the sampled density settings used in the manuscript tables.`

**Recommended placement:** Main text, Section V-D.

### 5. Ablation Figure

**Status:** `ready`

**IEEE suitability:** Suitable for main-text use as a compact replacement for the full ablation table. The current two-panel design makes the return/outage tradeoff legible without overwhelming the reader.

**Basis:** Existing data from Table III, lines 242--245.

**Evidence-boundary warning:** Yes. A brief aggregate-only warning is still appropriate because the figure visually sharpens the ablation ordering without variance information.

**Risk assessment:** Moderate risk of unsupported mechanism if the caption says the figure proves why the method works. It should stay at the level already supported in the text: removing the LoS guard causes the largest return collapse, while removing predictive fallback weakens the reliability advantage.

**Label / number match:** Yes. The current values align with Table III:
- Return: `4.881`, `3.988`, `4.798`, `4.744`
- Outage: `0.072`, `0.039`, `0.083`, `0.106`
- Delta-return annotations: `-0.893`, `-0.083`, `-0.137 vs. Full`

**Required fixes:**
- Keep variant names manuscript-consistent: `ProposedV2 (Full)`, `No LoS Guard`, `No Predictive Fallback`, `Reactive`.
- Remove any in-figure wording that reads like argument rather than label; the hatched `baseline` annotation is optional and can be simplified.
- Make sure the caption does not overclaim mechanism confirmation.

**Recommended caption:**  
`Ablation summary for the two core ProposedV2 components. Removing the LoS guard causes the largest aggregate return drop, while removing predictive fallback weakens the outage advantage and lowers return more modestly. Values are aggregate results from the manuscript ablation table and do not include variance estimates.`

**Recommended placement:** Main text, Section IV-C.

### 6. Blockage-Event Timeline

**Status:** `unsafe unless data-backed`

**IEEE suitability:** Not suitable for manuscript use unless the plotted traces can be tied to actual logged per-slot event data from the evaluated runs. The current figure looks plausible and well designed, but the manuscript does not yet document trace provenance.

**Basis:** Requires additional logs or explicit confirmation that the figure was generated from existing per-slot traces. It should not be treated as a pure illustration if it carries exact time-series values and threshold crossings.

**Evidence-boundary warning:** Yes. This figure absolutely needs a representative-example warning in the caption.

**Risk assessment:** High risk of unsupported mechanism and cherry-picking. The current panels could easily be read as proof that ProposedV2 anticipates blockage onset correctly in general, or that the guard score is causally validated, neither of which is established by the aggregate paper.

**Label / number match:** No direct one-to-one match with Table IV. Table IV reports aggregate recovery and trigger statistics across 40 events; the timeline would show one or a few representative events instead. It must not be presented as if it numerically verifies the `1.86` vs `2.03` slot averages by itself.

**Required fixes:**
- Confirm the exact source log file or trace provenance before use.
- State that the figure is representative and not a new aggregate result.
- Avoid language like `correct anticipation` or `validated guard mechanism`.
- If provenance is not available, exclude the figure rather than leaving it as a plausible-looking illustration.

**Recommended caption:**  
`Representative logged blockage event comparing ProposedV2 and Reactive around blockage onset. ProposedV2 activates guarded fallback near the transition and returns to a stable-rate regime in fewer slots in this example. The figure is an event-level illustration from logged traces and should not be interpreted as a statistical or universal mechanism claim.`

**Recommended placement:** Appendix if provenance is confirmed; otherwise do not include.

### 7. Latency / Complexity Figure

**Status:** `appendix only`

**IEEE suitability:** Usable as supporting material, but not ideal for the main text. The left side is data-backed and aligns with Table I, while the right side is qualitative algorithm-description material. That mixed evidentiary status is acceptable in an appendix but distracts from the paper's main empirical contribution if promoted to the core results section.

**Basis:** Mixed. Measured latency values come from Table I; the `current observation`, `one-step inference`, `guard + fallback`, `stochastic rollout`, and `state access` labels are qualitative descriptors rather than measured complexity results.

**Evidence-boundary warning:** Yes. The caption should explicitly mention the simplified simulator and say that the qualitative logic labels are contextual, not deployment-time complexity certification.

**Risk assessment:** Moderate-to-high risk of implying real-time feasibility or a validated complexity analysis if used too prominently. It can also sharpen the current prose gap that `One-Step Predictive` and `Oracle` are not yet well defined in the manuscript body.

**Label / number match:** Yes for latency values:
- Reactive: `0.003 ms`
- One-Step Predictive: `0.266 ms`
- ProposedV2: `0.286 ms`
- Belief Rollout: `0.815 ms`
- Oracle: `1.568 ms`
These align with Table I lines 180--184.

**Required fixes:**
- Keep the figure title tied to `planning latency in the simplified simulator`.
- Treat the right-side logic labels as qualitative annotations, not a formal complexity chart.
- Avoid claiming deployment feasibility or hardware-time guarantees.

**Recommended caption:**  
`Per-decision planning latency in the simplified simulator for the evaluated controllers. ProposedV2 increases latency relative to Reactive but remains below the rollout-based comparator under the current setup. The qualitative labels on the right provide algorithmic context only and do not constitute a deployment-time or asymptotic complexity proof.`

**Recommended placement:** Appendix.

### 8. Return-Outage Regime Map

**Status:** `needs redraw`

**IEEE suitability:** Not suitable in its current form as a manuscript evidence figure. The current candidate is explicitly qualitative and illustrative, and the manuscript itself warns against treating the regime variable as a dense quantified map.

**Basis:** Illustrative only in its current state.

**Evidence-boundary warning:** Yes. A strong warning is required if any version of this figure is kept.

**Risk assessment:** High risk of overstating quantification. The shaded `preferred region`, letter-coded points, and curved arrows encourage the reader to interpret the figure as a precise regime map, which the manuscript explicitly does not claim to have established.

**Label / number match:** Weak. The figure gestures toward the sweep dimensions (`D`, `N`, `S`, `R`), but it does not serve as a clean one-to-one visualization of Table II or the V-C / V-D slice tables in its current form.

**Required fixes:**
- If retained, rebuild it directly from exact sampled Table II values.
- State clearly that it is a sampled qualitative summary, not a continuous regime surface.
- Consider omitting it entirely if the sweep `Δreturn` figure and blocker-density tradeoff already carry the regime story sufficiently.

**Recommended caption:**  
`Illustrative summary of how sampled sweep slices move in aggregate return-outage space relative to Reactive. The figure is a qualitative synthesis of the sampled manuscript results rather than a dense statistical regime map, and it should not be interpreted as evidence of a continuous boundary or universally preferred region.`

**Recommended placement:** Appendix unless rebuilt directly from exact manuscript values and explicitly framed as qualitative.

## Priority Recommendation

If only a small manuscript-safe figure set is needed next, the best main-text sequence is:

1. Fig. 1 scenario/controller schematic after redraw  
2. Sweep `Δreturn` figure in Section IV-B  
3. Ablation figure in Section IV-C  
4. Blocker-density return-outage tradeoff in Section V-D  

Keep the latency/complexity figure in the appendix, and do not use the blockage-event timeline until its trace provenance is confirmed.
