# F-03 — origin frame and template-count rules

**Owner:** Fahmi Alshahabi · **Recorded:** 2026-09-03
**Recorded before authoring begins and before any vintage is opened.**

## 1. Origin sampling frame

All 33 London boroughs are eligible. Origins are drawn by seeded random
sampling from that frame; the seed is recorded and the frame is not edited
after authoring starts.

No supply floor is applied. Instead the data card carries a borough → located-item
count table for the DEV vintage, so that a structural non-match (no supply in the
borough) can be distinguished from a decided non-match at analysis time.

Amended from the LSOA/IMD frame on 2026-08-29: no LSOA or IMD file exists on any
branch, and `deprivation_tertile` fed only F-12 equity analysis, which is out of scope.

## 2. Template-count rule

q counts `task_template_id`, not task rows and not judgments.

H-P is estimative under CA-01.A9, so the count is not set by the power ceiling.
It is bounded above by the assessor-hours envelope and below by design coverage.

**Ceiling.** Judgments per assessor = templates × arms × 2 constructs
(usefulness and evidence-support; Q is not collected per 4.3). At 2–3 minutes per
judgment and a cap of 7 hours per assessor inside the 11–15 Sep window:
3 arms → ~28 templates; 4 arms → ~21.

**Floor.** 6 families and 7 defect mechanisms. A single pass over the mechanisms
costs 7 diagnostic templates, so nothing below ~13 exercises the design.

**Consequence, accepted in advance:** at this count no per-family claim is
available — roughly 4 templates per family. Per-family reporting is descoped.

Seven hours is the most I can ask of Clarence and Wesley inside 11–15 September, because both are writing their own reports in the same window and their own submissions are worth more to them than my judging.
## 3. Not covered

The arm count is not final until 4.2 ratifies the designation pair, and the DEV
vintage is not fixed until 2.1. Both change the numbers above, not the rules.

## SIGN-OFF — F-03 authoring rules

- **Claim ID:** F-03-rules
- **Artefacts checked:** `src/evaluation/task.schema.json`, `docs/evaluation/F-06-sizing-result.md`
  — branch `fahmi/proposal-v2-sections-6-7`, commit `e8caee3`
- **Outcome:** APPROVED
- - **Method:** Derived the floor from the six families and seven defect mechanisms in task.schema.json, and the ceiling from the assessor-hours envelope at two constructs; checked both against the F-06 sizing grid.
- **Not covered by this sign-off:** the arm count and DEV vintage, pending 4.2 and 2.1
- **Reference:** CA-01.A9
- **Signed:** Fahmi Alshahabi · 2026-09-03
