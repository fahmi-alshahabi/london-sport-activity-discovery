# C-BLOCK-03 — provenance wording for independent review

**Authoring stream:** Clarence, prepared with AI assistance on 14 September 2026. **Status: PROPOSED / NOT APPROVED / NOT AUTHORISED TO RENDER.** Reviewer: Fahmi, subject to eligibility for the exact contract and wording versions. This document supplies the missing candidate wording; it does not satisfy §09-1(1)(b).

## 1. Exact review target

Candidate: `provenance_lexicon_candidate_20260914.json`.
SHA-256: `35dcd1cd7aefe0862269ddcb84b3893d2645541dada10683d72cc5d2dd18a2cc`.
The file's own review fields deliberately remain PENDING/null. The independent review result must be recorded separately against this immutable candidate hash and the real contract commit. Any subsequent change to wording or semantics requires review of the new version; do not rewrite the reviewed file to insert a self-certifying approval.

## 2. Proposed public wording — both values

| Contract value | Exact short label | Exact explanatory text |
|---|---|---|
| `on_record` | Source: this record. | The contributing value or values come from this record. This describes their source, not their evidence grade. |
| `inherited_from_parent` | Source: includes inheritance from a parent record. | At least one contributing value is inherited from a parent record. Other contributing values may come from this record. Inheritance does not reduce the evidence grade. |

The label is about the source of contributing values, not an independent verification of the real-world activity. Keep the existing approved strength/evidence-grade wording separate. In particular, a value inherited under the motion may retain `grade: explicit`; do not relabel it weaker, inferred, less certain, or lower quality merely because it is inherited. For an aggregate, “at least one” deliberately avoids claiming that every contributor came from the parent. [S03, §09-1(2),(7)]

## 3. Mapping and completeness

`ON_CHILD`, `CHILD_OVERRIDES`, `BOTH_EQUAL` → `on_record`.
`INHERITED` → `inherited_from_parent`.
An aggregate uses `inherited_from_parent` if any contributing value is inherited. U states carry no provenance value. These rules do not select a winner for unresolved conflicts, and the rendering layer must not manufacture lineage from a grade or from text. [S03, §09-1(1),(7)]

The **new provenance category only** has the exact completeness set:

```text
CANON[provenance] = {on_record, inherited_from_parent}
```

This is the logical completeness requirement, not a claim about the syntax or container type of the unseen production `CANON`. Both values must have approved labels and explanations in the real lexicon, without deleting existing categories. Unknown categories, unknown values and unapproved wording must not gain a guessed/default rendering.

## 4. Verify before projection and rendering

First establish the certified state and contributing values, then compute the distinct strength and provenance axes, then apply disclosure classification, then render only the approved surviving claim. A claim refused under §09-1(7) is dropped **whole before projection** and recorded as a named open item; never render it with a blank, missing or guessed grade. This drops the refused claim, not automatically the entire decision envelope or its legitimate indeterminate/coverage message. Do not log staff-only receipts, source spans or internal details into a public response. [S03, §09-1(7),(8); S05, disclosure]

For U states, “no value” is a semantic requirement. Whether the production schema represents absence by omission or another already-authorised encoding must be checked against that schema; this candidate does not invent a permissive null alternative.

## 5. Review criteria and independence

Fahmi should independently decide whether this exact candidate (a) separates strength from lineage, (b) accurately covers single and multiple contributors, (c) preserves explicit strength under inheritance, (d) provides no U/conflict laundering, (e) respects the public disclosure boundary, and (f) is complete for both values. Review includes whether “this record” has a sufficiently clear referent on each proposed display surface.

Fahmi must not draft, co-draft, suggest alternative phrases or provide a wording steer. He may independently accept or reject and record the defect and evidence supporting that judgement; Clarence authors any revision. Acceptance of the reviewer role alone neither approves this candidate nor closes CL-2, CL-4 or CL-10. [S03, 6.0]

## 6. Record required from the reviewer — not pre-completed

The separate review record must identify reviewer, eligibility for both exact artefacts, contract `file@full_commit`, candidate filename and hash, accept/reject decision, scope and findings, date/time with timezone, and any limits. `approved` must never be inferred from silence, a name, or an unsigned template. Match the accepted wording to the version actually used in the passing release battery.

## 7. Deadline and release rule

Independent approval is one gate, not the entire battery. All §09-1 conditions must be evidenced by **Tuesday 15 September 2026, 18:00 BST**. Otherwise clause (1)(c) supplies the post-submission fallback. The reference checks supplied with this pack are illustrative local tests, not the production checker, fixture seals, eight invariants or eleven mutation branches. [S03]
