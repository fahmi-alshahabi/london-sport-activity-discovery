# F-02 RATIFY values — proposed values and justifications

**Prepared by:** Fahmi Alshahabi · 14 August 2026
**Purpose:** F-02 (estimand registry) carries every numeric threshold as a `RATIFY` placeholder, deliberately — none may be invented for apparent completeness. This memo proposes values *with justifications* so the ratification meeting can decide rather than stall. Nothing here is decided; every row needs a team decision, and two need the partner.
**Grounding:** Lakens (2017) on justifying equivalence and non-inferiority bounds (attested, matrix row 4); Bates et al. (2021) on risk-control validity conditions (row 3); Artstein & Poesio (2008) on agreement reporting (row 2); Westfall, Judd & Kenny (2014) on the item-sample power ceiling (row 1).
**Blocking:** F-06 (sizing simulation) cannot run, and the benchmark cannot freeze, until rows 1–3 below are decided.

---

## Why these can't just be chosen

Lakens (2017, pp. 359–360) sets an order of legitimacy for bounds: theory, practical importance, or cost–benefit reasoning first; the smallest effect the design can detect only as a **last resort**, because that states what the study *could* detect rather than what would *matter*. He explicitly warns against bounds chosen after seeing results, or numbers picked because they seem reasonable. Every proposal below therefore names its justification type, and where the honest answer is "only the partner knows," it says so.

---

## Row 1 — Q non-inferiority margin (ranking utility)

**The question:** how much ranking quality may the evidence-gated system lose against the strongest baseline before we stop calling it non-inferior?

**Proposal: (a) ask London Sport, with (c) as a pre-committed fallback.**

| | |
|---|---|
| Primary route | Put it to the partner as a service-level question: what reduction in result quality would still be acceptable in a referral or finder workflow? |
| Justification type | Practical importance — Lakens' first-choice category, and only the partner holds it |
| Fallback | If no partner answer by the freeze date, use the smallest margin the feasible design can detect at target power, and label it explicitly as a design-derived (last-resort) bound |
| Rationale (owner) | The partner is the only party who can define what loss in ranking quality is acceptable in practice; the pre-committed fallback means a slow reply cannot delay the freeze |

**Decision needed:** approve the partner question and the fallback rule, and set the date at which the fallback triggers.

## Row 2 — R_decision risk ceiling (unacceptable-decision rate among emitted decisions)

**The question:** what rate of unacceptable decisions is tolerable at the H-P risk gate?

**Proposal: (c) anchor to the baseline — our ceiling is the unacceptable-decision rate of the strongest eligible baseline (B0) — ratified by the team.**

| | |
|---|---|
| Justification type | Cost–benefit / empirical comparison rather than an invented absolute |
| Rationale (owner) | Anchoring to the current baseline means the ceiling reflects real performance rather than an arbitrary number we invented |
| Method note | The anchor is estimated on DEV only and frozen before locked evaluation; it is never re-derived after seeing locked results |
| Standing constraint | Per Bates et al. (2021) and CA-01.A4, whatever ceiling is chosen, the finite-sample guarantee is claimable only if the LTT/RCPS preconditions hold for our clustered, design-weighted calibration data. They do not hold automatically — see the open F-08 question below |

**Decision needed:** approve baseline anchoring, and confirm the team (not Fahmi alone) owns the final number — the work package explicitly reserves this.

## Row 3 — Ranking depth (F-02 discrepancy D-2, remainder)

**The question:** to what depth are results judged for relevance?

**Proposal: (a) match the depth Clarence's public interface actually displays**, read off the condition manifests rather than chosen independently.

| | |
|---|---|
| Justification type | Construct validity — judged depth should equal experienced depth |
| Rationale (owner) | We should evaluate the same number of results users actually see in the interface, not a ranking depth they never experience |
| Cost note | Depth drives assessor hours directly; the figure is an input to F-06 sizing |
| Action | Confirm the displayed depth with Clarence; if the interface is paginated or variable, freeze the first-screen depth |

**Decision needed:** confirm the number from the interface, and record it as resolving D-2 (the scale half was resolved by CB-D2, the 4-point relevance scale).

## Row 4 — U superiority margin (useful supported decision coverage)

**Status: not proposed here.** U is the H-P superiority quantity, and its margin is a practical-importance judgment of the same kind as Row 1 — how much additional useful coverage constitutes a real improvement for a practitioner. It should be sent to the partner in the same question as Row 1 rather than derived internally. If no answer arrives, the same last-resort fallback applies, declared as such.

## Row 5 — Unacceptable-decision condition (the non-evidence half of `L_decision`)

**Status: not proposed here — this is a definition, not a number.** Per CA-01.A2, `L_decision` = `L_evidence` OR an independently frozen unacceptable-decision condition. That condition must be written from partner/workflow meaning (what makes a recommendation genuinely bad for a Londoner, beyond being unsupported), and it cannot be back-filled from what the system happens to do. Proposed owner: drafted by Fahmi from partner materials, ratified by the team.

---

## Open question this memo surfaces (F-08)

Bates et al.'s guarantee assumes i.i.d. calibration data exchangeable with test data. Our calibration data are clustered (tasks nested in origins and publishers) and design-weighted, so the basic finite-sample guarantee does not automatically apply. The team must choose:

1. Find a grouped/clustered risk-control variant whose conditions our design satisfies; or
2. Report empirical risk–coverage curves with cluster-respecting uncertainty and **drop guarantee language entirely**, as CA-01.A4 prescribes.

This changes what F-08 is permitted to promise, so it should be decided at the same meeting.

## Decisions requested

1. Approve the Row 1 partner question + fallback rule, and set the fallback trigger date.
2. Approve Row 2 baseline anchoring; team ratifies the final ceiling.
3. Confirm Row 3 depth from Clarence's interface; record D-2 as resolved.
4. Agree that Rows 4 and 5 go to the partner / are drafted from partner materials rather than set internally.
5. Decide the F-08 route (1 or 2 above).
