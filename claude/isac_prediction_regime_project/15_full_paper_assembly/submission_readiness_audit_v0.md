# Submission-Readiness Structural Audit v0

**Audited file:** `15_full_paper_assembly/full_paper_draft_v0.md`
**Date:** 2026-05-14
**Scope:** Structural, consistency, claim-boundary, and overclaiming audit. No content rewrite.

---

## Executive Verdict: **Almost Ready — with 5 blocking issues**

The draft has a coherent narrative backbone: regime-dependent framing → problem formulation → protocol → results → regime analysis → limitations → conclusion. Numbers are internally consistent across all sections. The claim boundary is well-documented and the paper transparently reports both wins (11/16 return) and losses (5/16). However, five blocking issues must be resolved before submission. None require new experiments or number changes.

---

## Top 5 Blocking Issues

### B1. Three baseline methods are undefined

**Severity:** Blocker — a reviewer cannot evaluate the main comparison table.

One-Step Predictive, Belief-Aware Rollout, and Oracle appear in Table I (Section IV-A) without any prior definition. The paper never explains:
- What predictive model One-Step Predictive uses
- What belief representation and rollout horizon Belief-Aware Rollout uses
- How Oracle accesses the optimal beam (perfect CSI? genie? exhaustive search?)

**Fix:** Add a short subsection in Section III (or a new Method section) defining all five evaluated methods with enough detail that a reader can interpret Table I.

### B2. Missing dedicated Method/Architecture section

**Severity:** Blocker — IEEE reviewers expect a standalone method section.

The current draft embeds partial controller description in Section II-A (conceptual switching notation only) and Section III-A (behavioral description only). A reader cannot answer:
- What inputs does the LoS guard consume?
- How is the confidence score computed?
- What is the predictor architecture? The world model architecture?
- How does the predictive fallback select among candidate beams?
- What is the training procedure?

Already flagged in `missing_sections_checklist.md` item 1. This is the single largest structural gap.

**Fix:** Insert a section between III (Evaluation Protocol) and IV (Experimental Results) covering LoS guard, predictor, world model, and fallback beam selection. Source material exists in `06_writing/section4_hybrid_controller_v0.md`.

### B3. Overclaiming language at 9 locations

**Severity:** Blocker — these sentences claim more confidence than the aggregate, no-variance evidence supports. Exact violations and suggested replacements:

#### B3.1 "robust" (3 instances)

| # | Location | Quoted Sentence | Suggested Replacement |
|---|---|---|---|
| 1 | IV-E, line 190 | "the method is **robust** to threshold choice within a reasonable range" | "the method is relatively insensitive to threshold choice within the tested range" |
| 2 | V-A, line 196 | "Outage and beam success are **robust** across all regimes (16/16 wins each)" | "Outage and beam success favor ProposedV2 at all 16 sweep points" |
| 3 | V-B, Medium-Risk, "largest return advantages" context — close call but OK since qualified with specific numbers | — | — |

#### B3.2 "confirms" (2 instances)

| # | Location | Quoted Sentence | Issue |
|---|---|---|---|
| 4 | IV-C, line 169 | "This **confirms** the LoS guard is the single most critical component for preserving throughput." | Ablation shows direction and magnitude, not mechanism confirmation. |
| 5 | IV-D, line 187 | "The fallback trigger rate of 90.9% **confirms** the LoS guard correctly activates the predictive mechanism around blockage onset events." | Correlation (high trigger rate during blockage) does not confirm causation. No false-positive rate reported. |

**Suggested replacements:**
- B3.1#1: "the method is relatively insensitive to threshold choice within the tested range"
- B3.1#2: "Outage and beam success favor ProposedV2 at all 16 sweep points"
- B3.2#1: "This indicates the LoS guard is the single most critical component for preserving throughput"
- B3.2#2: "The fallback trigger rate of 90.9% is consistent with the LoS guard activating the predictive mechanism around blockage onset events"

#### B3.3 "outperforms" / performance-ordering language (2 instances)

| # | Location | Quoted Sentence | Issue |
|---|---|---|---|
| 6 | IV-B, line 156 | "ProposedV2 **outperforms** Reactive most clearly at moderate-to-high observation noise" | "Outperforms" asserts verified superiority ordering without variance data. |
| 7 | V-A, line 196 | "return and rate advantages are regime-dependent (11/16 and 6/16 wins respectively)" | Acceptable — "wins" is tied to directional comparison at sweep points. |

**Suggested replacement for B3.3#1:**
"ProposedV2 shows the largest return advantages over Reactive at moderate-to-high observation noise"

#### B3.4 "dramatically" / intensifier language (1 instance)

| # | Location | Quoted Sentence | Suggested Replacement |
|---|---|---|---|
| 8 | V-C, line 217 | "the gap **widens dramatically**: ProposedV2 return is +18.1% over Reactive" | "the gap widens substantially: ProposedV2 return is +18.1% over Reactive" |

#### B3.5 "consistent" (1 instance)

| # | Location | Quoted Sentence | Suggested Replacement |
|---|---|---|---|
| 9 | V-D, line 228 | "ProposedV2 **maintains a consistent return advantage** (+0.05 to +0.08)" | "ProposedV2 shows a return advantage at each of these three density points (+0.05 to +0.08)" |

### B4. Section V data tables are unlabeled and uncatalogued

**Severity:** Blocker — paper inventory is incomplete.

Sections V-C (Observation Noise Spectrum) and V-D (Blocker Density) each contain full data tables rendered inline. These tables are not:
- Assigned table numbers (Table VI? Table VII?)
- Cross-referenced in the prose ("Table X shows...")
- Listed in `paper_figure_table_list.md`

Additionally, Section IV-D embeds a data table that is never explicitly referenced as "Table IV" in the surrounding prose.

**Fix:** Either (a) assign these as Tables VI and VII and update `paper_figure_table_list.md`, or (b) fold the data into the existing sweep summary (Table II) since they are subset extractions, and remove the redundant tables. Option (b) is preferred — the noise and density tables are vertical slices of Table II and don't carry new data.

### B5. No Related Work section

**Severity:** Blocker — IEEE desk reject without literature positioning.

Already flagged as missing_sections_checklist.md item 2. The current Introduction paragraph 2 has a single sentence about predictive beamforming literature framing. A full Related Work section is needed covering at minimum: predictive beamforming, reactive baselines, hybrid/gated architectures, and regime-aware beam management.

**Fix:** Insert after Introduction (before Problem Formulation) or after Problem Formulation (before Evaluation Protocol). IEEE conventions vary.

---

## Top 5 Non-Blocking Polish Issues

### P1. Evidence-strength annotations in prose body

Section IV-A labels outage as "(strongest claim)" and beam success as "(strong claim)." These are authorial meta-commentary that belong in a separate evidence-strength table (already exists in `paper_claim_boundary_final.md`), not in results prose. A reviewer may find this unusual.

### P2. Naming inconsistency: "ProposedV2" vs. "Regime-Aware Predictive Beam Control"

The paper introduces the method as "Regime-Aware Predictive Beam Control (ProposedV2)" in the Abstract and Introduction, but most of the Results and Regime Analysis sections use bare "ProposedV2." This is understandable for brevity but the first use in each major section should restate the full name.

### P3. Regime taxonomy thresholds are uncalibrated

Section V-B defines Clear/Medium/Extreme regimes with specific numeric thresholds (blockage indicator < 0.20, reflection ratio < 0.15, risk score > 0.65, etc.). These thresholds are presented as definitions but their provenance is never explained. A reviewer will ask: are these tuned, set a priori, or computed from data? Either state they are illustrative/descriptive, or cite the source.

### P4. Conclusion restates abstract numbers verbatim

The Conclusion (Section VII, line 294) restates the same 32%, 7.0%, 16/16, 11/16 statistics that appeared in the Abstract and Introduction. The Conclusion should synthesize rather than re-report. The second half (lines 296) does this well — the diagnostic-rather-than-triumphant framing is strong. Consider compressing the first half.

### P5. Evidence Boundary section partially duplicates Appendix

The final "Evidence Boundary" paragraph (line 351) and the Appendix "Claim Boundary" (line 298) overlap significantly. They serve different purposes (boundary = scope of conditions; claim = scope of assertions) but the distinction is subtle. Consider merging into a single "Evidence and Claim Boundary" appendix, or clarifying the relationship between the two.

---

## Claim-Boundary Violations (detailed)

All violations are covered in B3 above. In summary:

| Type | Count | Severity |
|---|---|---|
| "robust" (implies statistical reliability) | 2 | Must fix |
| "confirms" (implies mechanism validation) | 2 | Must fix |
| "outperforms" (implies verified ordering) | 1 | Must fix |
| "dramatically" (intensifier) | 1 | Should fix |
| "consistent" (implies reliability) | 1 | Should fix |

No violations of the explicit DO NOT CLAIM list (universal superiority, SOTA, optimal gating, real-world performance, computational efficiency, real-time feasibility, consistent rate advantage).

---

## Figure/Table Consistency Check

| Element | In Paper Text | In `paper_figure_table_list.md` | Status |
|---|---|---|---|
| Table I (Main comparison) | Referenced: "Table I reports..." | Listed as Table I | OK |
| Table II (Scene sweep) | Referenced: "Table II summarizes..." | Listed as Table II | OK |
| Table III (Ablation) | Referenced: "Table III reports..." | Listed as Table III | OK |
| Table IV (Blockage recovery) | **Not referenced in prose** | Listed as Table IV | **Gap** |
| Table V (Regime boundaries) | Referenced only by location | Listed as Table V | OK |
| Section V-C noise table | **Embedded, no number** | **Not listed** | **Gap** |
| Section V-D density table | **Embedded, no number** | **Not listed** | **Gap** |
| Figure 1 (Return diff) | Not referenced in prose | Listed, "Not rendered" | Expected |
| Figure 2 (Outage vs noise) | Not referenced in prose | Listed, "Not rendered" | Expected |
| Figure 3 (Density impact) | Not referenced in prose | Listed, "Not rendered" | Expected |

**Corrective action needed on paper_figure_table_list.md:**
1. Add entries for the Section V-C (Observation Noise Spectrum) and V-D (Blocker Density) tables.
2. Note that Table IV is not cross-referenced in prose.
3. Consider whether V-C and V-D tables should be collapsed into Table II since they are subset extractions.

---

## Section-by-Section Consistency Notes

### Abstract ↔ Introduction
**Consistent.** Numbers match. Both frame the contribution as regime-dependent. Both disclaim universal superiority. ✓

### Abstract ↔ Results (IV)
**Consistent.** All four aggregate metrics match between Abstract and Table I. 16/16 sweep point claim matches Section IV-B. ✓

### Abstract ↔ Conclusion (VII)
**Consistent.** Same numbers, same framing. Conclusion adds the "diagnostic rather than triumphant" positioning that the Abstract implies but doesn't state explicitly. ✓

### Problem Formulation (II) ↔ Results (IV)
**Minor tension.** Section II defines the switching score g_t and threshold tau as "conceptual notation." The results never operationalize g_t — no switching score distributions, no tau sensitivity shown (the threshold sweep in IV-E sweeps three hyperparameters but doesn't map them to the g_t/tau formalism). The paper would benefit from connecting the formal notation to the actual implementation.

### Problem Formulation (II) ↔ Regime Analysis (V)
**Minor tension.** Section II-B introduces regime variable d as "an organizing variable attached to sampled conditions." Section V-B operationalizes d with specific numeric thresholds. These thresholds (blockage indicator < 0.20, etc.) appear to come from the internal controller logic but are never connected back to the sampled dimensions in II-B.

### Evaluation Protocol (III) ↔ Results (IV)
**Consistent.** The 5 seeds × 4 episodes × 200 slots protocol matches what's reported. Metrics defined in III-B match Table I columns. ✓

### Evaluation Protocol (III) ↔ Regime Analysis (V)
**Minor gap.** Section III-C lists four sampled dimensions. Section V analyzes all four. But Section V also introduces a three-regime taxonomy (Clear/Medium/Extreme) that is not previewed in Section III. This is fine structurally but the reader may wonder how the taxonomy relates to the sampling.

### Discussion (VI) ↔ Results (IV)
**Consistent.** Failure regimes match between IV-B and VI-B. Ablation conclusions match between IV-C and VI-A. Negative result numbers match between VI-C and the claim boundary. ✓

### Discussion (VI) ↔ Conclusion (VII)
**Consistent.** Both emphasize regime-dependence and disclaim universal superiority. ✓

---

## Missing Sections Checklist Accuracy

`missing_sections_checklist.md` is **mostly accurate but needs two updates:**

### Update 1: Add undefined baselines to Method section gap
Item 1 (Method/Architecture) should also note that One-Step Predictive, Belief-Aware Rollout, and Oracle are referenced in Table I but never defined anywhere in the paper text. A reader encountering these names has no description of what they are.

### Update 2: Add unlabeled tables gap
A new item should be added under "Sections Requiring Future Completion" noting that the paper contains two unlabeled data tables (Sections V-C and V-D) and one unreferenced table (Section IV-D). These need either numbering or consolidation.

These two updates will be applied to `missing_sections_checklist.md` as part of this audit.

---

## Contribution Statement Assessment

Despite the no-variance limitation, the paper has a **clear, defensible contribution statement** (Introduction, paragraph 5, line 19):

1. **Problem formulation**: Evidence-bounded predictive decision framing → well-scoped, philosophical contribution
2. **Empirical analysis**: Regime-oriented comparison across 4 difficulty dimensions → methodological contribution
3. **Evaluation framing**: Multi-metric rate-reliability-alignment tradeoff → diagnostic contribution

These are credible claims that do not require variance data. The paper correctly positions itself as a "how to think about this problem" contribution rather than a "we beat benchmark X" contribution. The Conclusion reinforces this scope. ✓

---

## Recommended Next Task

**Write the missing Method/Architecture section.** This is the single highest-leverage task that resolves blocking issues B1 (undefined baselines), B2 (missing method section), and partially addresses P3 (uncalibrated regime thresholds).

Specific actions:
1. Read source material: `06_writing/section4_hybrid_controller_v0.md`, `04_code/repo_inventory.md`, `claude/isac_uploaded_repo/repo/model.py`, `claude/isac_uploaded_repo/repo/planner.py`
2. Draft a new Section III (or insert as Section IV, renumbering subsequent sections) covering:
   - LoS guard: inputs, confidence scoring, threshold logic
   - World model: architecture sketch, training objective, rollout procedure
   - Predictive fallback: beam scoring, candidate generation, selection rule
   - All five evaluated methods: Reactive, ProposedV2, One-Step Predictive, Belief-Aware Rollout, Oracle — each with a 2-3 sentence definition
3. Update all section number references downstream
4. Commit as: "Add method section with baseline definitions"
