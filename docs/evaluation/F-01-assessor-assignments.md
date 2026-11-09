# F-01 — Assessor assignments and eligibility rulings

**Owner:** Fahmi Alshahabi · **Applies:** RATIFY-19-03, RATIFY-19-07
**Restated:** 2026-08-29 — arms are Clarence's P0/P1/P2 presentation conditions, which changes who is conflicted.

## Assignments

| Construct                | Assessor 1 | Assessor 2 | Arbiter              | Recused                                      |
| ------------------------ | ---------- | ---------- | -------------------- | -------------------------------------------- |
| Usefulness (U) — primary | Wesley     | Michael    | none — deferral only | Fahmi (C1); Clarence (C-a, authors the arms) |
| Relevance (Q)            | Clarence   | Wesley     | Michael              | Fahmi (C1)                                   |
| Evidence-support         | Clarence   | Wesley     | Fahmi                | Michael (C2)                                 |
| Locked-run custodian     | —          | —          | Michael              | Fahmi                                        |
| Non-author reproducer    | —          | —          | Michael              | Fahmi                                        |

## Sign-offs

### SIGN-OFF — OPEN-1, Wesley's eligibility to judge relevance

* **Claim ID:** OPEN-1
* **Artefacts checked:** docs/evaluation/eligibility-matrix-feasibility.md §3.2, docs/evaluation/codebook-v0.3.md §1 — branch `fahmi/proposal-v2-sections-6-7`, commit `f315976`
* **Method:** read eligibility-matrix §3.2 against codebook v0.3 §1 to check whether the blinding provision covers the ownership risk.
* **Outcome:** APPROVED WITH CONDITIONS — option 1a
* **Conditions:** Wesley owns retrieval and reranking, so this is accepted with that recorded, on the basis that blinding is by hidden condition labels per F-05 §1 and removing him would leave relevance with a single assessor and no agreement statistic.
* **Not covered:** This doesn't rule on whether `Q` is collected at all, which is pending Clarence's answer on whether P0/P1/P2 differ in ordering.
* **Reference:** RATIFY-19-03
* **Signed:** Fahmi Alshahabi · 2026-08-29

### SIGN-OFF — OPEN-2, alternate arbiter appointment

* **Claim ID:** OPEN-2
* **Artefacts checked:** docs/evaluation/eligibility-matrix-feasibility.md §2, this file's assignments table — branch `fahmi/proposal-v2-sections-6-7`, commit `4605587`
* **Method:** checked the eligibility matrix and assignments table for an alternate arbiter who is eligible for the constructs in question. Wesley is an assessor on all three constructs, so there is no item where he is eligible to arbitrate without already being a party to it.
* **Outcome:** APPROVED WITH CONDITIONS — option 2a
* **Conditions:** the alternate covers primary-arbiter unavailability by deferring the item, not arbitrating it; deferred items are reported as unresolved.
* **Not covered:** no threshold is set for how many deferrals the route can absorb before it stops being a real adjudication route.
* **Reference:** RATIFY-19-07
* **Signed:** Fahmi Alshahabi · 2026-08-29

### SIGN-OFF — Clarence's eligibility once P0/P1/P2 became the treatment

* **Claim ID:** C-a
* **Artefacts checked:** Michael's reply of 2026-08-29, docs/evaluation/estimand-registry.yaml §6, this file's assignments table — branch `fahmi/proposal-v2-sections-6-7`, commit `4605587`
* **Method:** read Michael's 2026-08-29 confirmation that the arms are Clarence's presentation conditions against the C2 recusal already applied to Michael for his own engine, to determine whether Clarence's authorship creates a conflict for usefulness.
* **Outcome:** APPROVED WITH CONDITIONS — Clarence recused from usefulness; Michael assesses it
* **Conditions:** recusal is scoped to usefulness only, because that's the construct carrying the primary; Michael assesses in his place.
* **Not covered:** Clarence still assesses relevance and evidence-support while authoring the arms; and Michael now holds five roles.
* **Reference:** RATIFY-19-07
* **Signed:** Fahmi Alshahabi · 2026-08-29

### SIGN-OFF — C6 consequence on the usefulness construct

* **Claim ID:** C6-usefulness
* **Artefacts checked:** this file's assignments table, standing constraint C6 — branch `fahmi/proposal-v2-sections-6-7`, commit `4605587`
* **Method:** checked the assignments table against C6 (two eligible assessors plus an adjudication route per locked construct) and found usefulness satisfies the first half and not the second.
* **Outcome:** REVIEWED — declared weakness, not a ruling
* **Conditions:** usefulness has two assessors, Wesley and Michael, and no arbiter, because Michael can't arbitrate what he assesses and everyone else is recused. Adjudication is deferral only, per 2a.
* **Not covered:** whether a confirmatory primary can rest on a construct with no adjudication route. Note the F-06 result of 29 Aug bears on this and isn't actioned yet.
* **Reference:** RATIFY-19-07
* **Signed:** Fahmi Alshahabi · 2026-08-29
