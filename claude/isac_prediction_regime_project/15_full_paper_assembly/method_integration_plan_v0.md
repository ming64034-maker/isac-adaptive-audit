# Method Integration Plan v0

**Source:** `method_section_v0.md` (205 lines, standalone)
**Target:** `full_paper_draft_v0.md` (353 lines)
**Date:** 2026-05-14

---

## 1. Recommended Insertion Point

Insert the Method section **between current Section III (Evaluation Protocol) and current Section IV (Experimental Results).**

**Rationale:** The paper's logical flow is: define the decision problem (II) → define how we evaluate (III) → define what we evaluate (IV, new Method) → report what happened (V, results) → analyze why (VI, regime analysis) → discuss limitations (VII). The Method section bridges "here is the evaluation framework" and "here are the results" by answering "here are the controllers being evaluated."

### Before (current)
```
I.   Introduction
II.  Problem Formulation        (A, B, C)
III. Evaluation Protocol        (A, B, C, D)
IV.  Experimental Results       (A, B, C, D, E)   ← no method section
V.   Regime Analysis            (A, B, C, D, E, F)
VI.  Discussion and Limitations (A, B, C, D)
VII. Conclusion
```

### After (proposed)
```
I.   Introduction
II.  Problem Formulation        (A, B, C)
III. Evaluation Protocol        (A, B, C, D)
IV.  Method: Regime-Aware Predictive Beam Control   ← NEW (from method_section_v0.md)
V.   Experimental Results       (A, B, C, D, E)    ← was IV
VI.  Regime Analysis            (A, B, C, D, E, F)  ← was V
VII. Discussion and Limitations (A, B, C, D)        ← was VI
VIII.Conclusion                                       ← was VII
```

---

## 2. Proposed New Section Numbering

| Current Section | New Section | Change |
|---|---|---|
| I. Introduction | I. Introduction | None |
| II. Problem Formulation | II. Problem Formulation | None |
| III. Evaluation Protocol | III. Evaluation Protocol | None |
| *(does not exist)* | **IV. Method** | **Added** |
| IV. Experimental Results | V. Experimental Results | +1 |
| V. Regime Analysis | VI. Regime Analysis | +1 |
| VI. Discussion and Limitations | VII. Discussion and Limitations | +1 |
| VII. Conclusion | VIII. Conclusion | +1 |
| Appendix | Appendix | None |
| Evidence Boundary | Evidence Boundary | None |

Method section internal numbering converts from `1., 2., ...` to `A., B., ...` to match IEEE subsection convention:
- 1. Evaluated Controllers → IV-A
- 2. ProposedV2 Architecture → IV-B
- 3. Training Procedure → IV-C
- 4. Ablation Variants → IV-D
- 5. What Is NOT Implemented → IV-E
- 6. Evidence and Interpretation Boundary → IV-F

---

## 3. Downstream Cross-References to Renumber

All section references in the current draft that point to Sections IV, V, VI, or VII must increment by 1.

| File Location | Current Text | Must Become | Type |
|---|---|---|---|
| `full_paper_draft_v0.md` line 196 | `Section IV-B` | `Section V-B` | Prose cross-ref |
| `full_paper_draft_v0.md` line 266 | `Section IV-E` | `Section V-E` | Prose cross-ref |
| Section headers IV through VII | `## IV.`, `## V.`, etc. | `## V.`, `## VI.`, etc. | Heading levels |
| Subsections IV-A through IV-E | `### A.`, etc. (under IV) | `### A.`, etc. (under V) | Inherits from parent |
| Subsections V-A through V-F | `### A.`, etc. (under V) | `### A.`, etc. (under VI) | Inherits from parent |
| Subsections VI-A through VI-D | `### A.`, etc. (under VI) | `### A.`, etc. (under VII) | Inherits from parent |
| Method section self-refs | `Section 2`, `Section 1.1`, etc. | `Section IV-B`, `Section IV-A.1`, etc. | Internal renumbering |
| `paper_figure_table_list.md` | Section IV-A, IV-B, etc. | Section V-A, V-B, etc. | Table cross-ref |
| `missing_sections_checklist.md` | IV, V, VI, VII | V, VI, VII, VIII | Section names |
| `submission_readiness_audit_v0.md` | IV-E, V-A, etc. | V-E, VI-A, etc. | Audit line refs |

---

## 4. Redundant Content to Remove or Shorten

### 4.1 Section III-A (line 78): Controller definitions

**Current text (lines 78):**
> "Reactive denotes the baseline controller that selects beams from currently available information without an explicit predictive fallback step. ProposedV2 denotes the hybrid controller that behaves reactively in easier conditions and activates a one-step predictive fallback by design in harder conditions."

**Action: Shorten.** Replace with a cross-reference to the new Method section:
> "The five evaluated controllers are defined in Section IV. The headline comparison is between Reactive (the primary baseline) and Regime-Aware Predictive Beam Control (ProposedV2)."

This is a 2-line change. The original text is 2 sentences that become redundant once Section IV provides full definitions with pseudocode.

### 4.2 Section II-A (lines 39-50): Switching notation

**Action: Keep as-is.** The mathematical notation (`pi_R`, `pi_H`, `pi_P`, `g_t`, `tau`) serves the Problem Formulation's conceptual purpose. The Method section (line 3) says "The notation follows Section II" and references this framing. The two sections are complementary: Section II says *what the switching logic expresses mathematically*, Section IV says *how it is implemented*. No change needed.

### 4.3 Abstract (line 5): Method description

**Action: No change.** The Abstract's one-sentence description of the controller ("a hybrid controller that combines a line-of-sight guard with one-step predictive fallback") is appropriately brief and does not duplicate the method section's detail.

---

## 5. Figure/Table Cross-Reference Impacts

| Artifact | Impact | Action |
|---|---|---|
| Table I--V (paper body) | None — tables are referenced by Roman numeral, not section number | No change |
| Figure 1 (paper_figure_table_list.md) | Listed as "Location: Section IV-B" | Update to "Section V-B" |
| Figure 2 (paper_figure_table_list.md) | Listed as "Location: Section V-C" | Update to "Section VI-C" |
| Figure 3 (paper_figure_table_list.md) | Listed as "Location: Section V-D" | Update to "Section VI-D" |
| Method section Figure 1 ref | "Figure 1 shows the decision flow" | Figure not yet rendered; label is aspirational. Keep as-is until figure generation task. |

The `paper_figure_table_list.md` file needs a separate maintenance pass after integration — not part of this task.

---

## 6. Integration Procedure (Step-by-Step)

1. **Open `full_paper_draft_v0.md`.**
2. **Locate the insertion point:** After the line `## III. Evaluation Protocol` block ends and before `## IV. Experimental Results` begins (between line 95 and line 96).
3. **Insert `method_section_v0.md` content** with these adaptations:
   - Change `# Method: Regime-Aware Predictive Beam Control` → `## IV. Method: Regime-Aware Predictive Beam Control`
   - Change `## 1.` → `### A.`
   - Change `## 2.` → `### B.`
   - Change `## 3.` → `### C.`
   - Change `## 4.` → `### D.`
   - Change `## 5.` → `### E.`
   - Change `## 6.` → `### F.`
   - Internal subsection numbering (`### 1.1`, `### 2.1`, etc.) → (`#### 1)`, `#### 1)`, etc. or leave as-is since markdown renders them correctly)
   - Update self-references: `Section 2` → `Section IV-B`, `Section 1.1` → `Section IV-A.1`
4. **Renumber downstream section headers:**
   - `## IV. Experimental Results` → `## V. Experimental Results`
   - `## V. Regime Analysis` → `## VI. Regime Analysis`
   - `## VI. Discussion and Limitations` → `## VII. Discussion and Limitations`
   - `## VII. Conclusion` → `## VIII. Conclusion`
5. **Update cross-references in prose:**
   - Line 196: `Section IV-B` → `Section V-B`
   - Line 266: `Section IV-E` → `Section V-E`
6. **Shorten Section III-A (line 78):** Replace the two-sentence controller definition with the cross-reference version from Section 4.1 above.
7. **Verify:** Read the full draft end-to-end. Confirm all section numbers in prose match the actual headers. Confirm no orphan cross-references.

---

## 7. Risk Checklist for Claim-Boundary Violations

| Risk | Mitigation |
|---|---|
| Method section introduces "confirms" or "proves" language | `method_section_v0.md` already passed overclaiming grep. Re-verify after integration edits. |
| Method section claims optimal thresholds | Already addressed: method_section_v0.md Section 6 says thresholds are not claimed as calibrated or optimal. |
| Method section mentions failed variants outside Section VI-C | Method section Section 5 (new IV-E) correctly isolates adaptive/veto/tri-regime. Verify no leakage during integration. |
| Integration edits accidentally change numeric values | No numeric values are touched during renumbering or cross-reference updates. |
| Section III-A shortening loses necessary context | The new text retains the key framing ("Reactive is the primary baseline, ProposedV2 is the proposed method") and defers details to Section IV. |
| Cross-reference to non-existent section | Verify every `Section X-Y` reference in prose points to an actual header after renumbering. |

---

## 8. Files Requiring Follow-Up After Integration

These files contain stale section numbers and should be updated in separate tasks:

| File | What's Stale | Priority |
|---|---|---|
| `paper_figure_table_list.md` | Section locations for Figures 1-3, Tables I-V | Low (non-blocking, internal tracking) |
| `submission_readiness_audit_v0.md` | Line references to `IV-E`, `V-A`, etc. | Low (audit is historical record) |
| `missing_sections_checklist.md` | Section names IV--VII need +1 shift | Low (cosmetic, doesn't affect completeness tracking) |

---

## 9. Exact Next Single Task

**Execute the integration.** Apply steps 1--7 from Section 6 above directly to `full_paper_draft_v0.md`.

Deliverables:
- Modified `full_paper_draft_v0.md` with Method section inserted and all downstream renumbering applied
- Updated `paper_figure_table_list.md` (section location fields only)
- Commit message: "Integrate method section into full paper draft"

Do not change any other files. Do not add new content beyond what is in `method_section_v0.md`. Do not modify numeric results.
