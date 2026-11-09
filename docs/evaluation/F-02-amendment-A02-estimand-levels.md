# F-02 Amendment A-02 — Separate theoretical and empirical estimands; bind `U` to its operational definition

**Proposed by:** Fahmi Alshahabi · 15 August 2026
**Target:** `docs/evaluation/estimand-registry.yaml` — the `U` entry, and the registry schema generally.
**Status:** PROPOSED. Takes effect on team ratification.
**Source:** Lundberg, Johnson & Stewart (2021), *American Sociological Review* 86(3), 532–565, DOI 10.1177/00031224211004187 — attested, source-reading matrix row 8.

---

## Problem

Applying the Lundberg test to F-02: an estimand must name a theoretical quantity, then an empirical quantity defined over observable data with a specified unit and target population, with the link between them stated. Most F-02 entries name a unit, numerator, denominator and weighting. `U` does not fully separate the two levels, and is therefore partly defined by how it would be computed rather than by what it represents.

Concretely, the theoretical quantity behind `U` is something like *the proportion of tasks for which a Londoner could act on the answer*. What the study measures is *the proportion of tasks for which a trained assessor, applying the frozen codebook under masking, judges the response actionable*. These are not the same quantity. The second is a defensible proxy for the first, but the substitution is currently silent — which is precisely the failure Lundberg et al. describe.

A related gap: F-05 §2 already operationalises usefulness properly — evidence-grounded service rather than user satisfaction (PU1: the system is not permitted to be right by accident; PU2: honest failure can be useful; PU3: fluency and volume are not evidence), with worked cases U1–U4. F-02 does not reference it, so the registry appears to leave "useful" undefined when in fact the definition exists in another committed artifact.

## Proposed change

**1. Add two fields to every estimand entry in the registry schema:**

```yaml
theoretical_estimand: >
  The quantity of interest, stated in terms of the world rather than the
  measurement procedure.
empirical_estimand: >
  The observable quantity actually estimated: unit-level quantity, target
  population/universe, and the measurement route that produces it.
construct_gap: >
  What is lost or assumed in substituting the empirical for the
  theoretical estimand. Stated, not resolved.
```

**2. Apply them to `U`:**

```yaml
U:
  name: useful_supported_decision_coverage
  theoretical_estimand: >
    The proportion of tasks in the declared universe for which a person
    with the stated need could act on the system's answer.
  empirical_estimand: >
    The design-weighted proportion of tasks in the intention-to-evaluate
    task universe for which independent masked assessors, applying the
    frozen F-05 codebook (§2, PU1-PU3), judge the response USEFUL —
    i.e. evidence-grounded and actionable against the task's stated need.
  operational_definition: docs/evaluation/codebook.md §2 (CB-D1; PU1-PU3; U1-U4)
  construct_gap: >
    Assessor judgment under a codebook is a proxy for a Londoner's ability
    to act. The substitution assumes the codebook's notion of actionability
    tracks real-world actionability for the population of interest; this is
    assumed, not demonstrated, and no participant-based validation is in
    scope unless the ethics route is approved. Declared in the limitations
    section of the report.
  unit: task
  role: H-P_superiority_quantity
  # ... existing fields unchanged
```

**3. Sweep the remaining entries.** `K`, `Q`, `R_evidence`, `R_decision`, `H_evidence` and `H_decision` are reviewed against the same test before freeze; where the theoretical and empirical levels coincide (as they largely do for the risk quantities, which are defined over emitted decisions rather than over a latent world quantity), that is recorded explicitly rather than left implicit.

## Rationale

Stating the gap does not close it, and is not meant to. The value is that it becomes visible to reviewers and to us: the report can then claim what the study measured, and separately discuss how far that stands in for what was wanted. The alternative — treating the assessor-judged quantity as if it simply were the real-world quantity — is the specific error Lundberg et al. identify, and it would be caught at the claim audit rather than corrected now.

Binding `U` to F-05 also removes a live inconsistency: the registry and the codebook currently define usefulness independently, with no reference between them, so a future edit to either could silently diverge.

## Interaction with existing decisions

- No change to `U`'s unit, denominator, weighting or role in H-P.
- No change to the superiority margin, which remains RATIFY (see RATIFY-values memo, Row 4).
- Complements A-01 (bulk/tail ESS split); the two are independent.
- Supports the SAP's estimand-conformance check, which currently has no defined criterion for what conformance means; the theoretical/empirical/gap triple gives it one.

---
*Change log: A-02 proposed 15 Aug 2026.*
