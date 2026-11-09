# F-BLOCK-09 Decision Record

**Decision ID:** F-BLOCK-09 (joint with C-BLOCK-15)
**Status:** DRAFT — authored fields complete; institutional approval pending ratification.
**Authored:** 18 August 2026

> **Authorship notice.** The structure of this record derives from an AI-assisted coordination
> scaffold prepared from the current project artefacts. It is not evidence that Fahmi authored,
> read, accepted or completed the work.
> Decisions, rationale and authored fields in this record are mine.

## Status

-   **Owner:** Fahmi Alshahabi
-   **Joint reviewer:** Clarence (PENDING)
-   **Date:** PENDING
-   **Decision log:** PENDING

> This is the decision record derived from the structural scaffold.
> Institutional approval fields remain pending until ratification.

------------------------------------------------------------------------

## 1. Decision

### Question

What is the referent of `L_reliance`, where does it sit within the
frozen loss vocabulary, and how are P2 query-repair episodes handled?

### Referent

**Decision:** ACCEPT.

`L_reliance` is judged against the **terminal DecisionEnvelope evidence
state**, identical across P0, P1, P2, W0, W1 and W1-NA by design and
enforced through `INV-NONINTERFERENCE`.

### Chosen option

**(a) Third distinct application-layer loss**

Rejected options:

-   **(b)** Rejected because a human reliance action is not a system
    emission, so it should not be folded into `L_decision`.
-   **(c)** Rejected because treating reliance only as an outcome
    removes any bounded application-layer construct for unsafe reliance.

------------------------------------------------------------------------

## 2. Rationale

Reliance is a human action taken in response to a rendered decision rather than a
system emission, so it does not belong inside `L_decision`. Introducing `L_reliance`
is an explicit amendment recorded in this decision record instead of silent protocol
drift, preserving the frozen loss vocabulary through documented governance.
`L_reliance` never enters H-P, H-E, H-G or CAL-RISK, and every reliance quantity is
treated as estimative rather than confirmatory.

------------------------------------------------------------------------

## 3. P2 query-repair rule

**Decision:** Repaired episodes are excluded from the reliance
estimand.

Rule:

-   Episodes where conversational repair changes the interpreted query
    resolve a different terminal DecisionEnvelope.
-   Those episodes are excluded from the reliance estimand.
-   Their frequency is reported separately with uncertainty.
-   The exclusion is declared before outcome adjudication and is never
    outcome-dependent.

### Operational test

Use digest inequality as the mechanical screen: if the opening-query digest and the
terminal digest differ, the episode is automatically classified as repaired. Only the
digest-equal residual proceeds to blinded human adjudication to determine whether the
interpreted query genuinely changed or whether both queries resolve to the same
terminal DecisionEnvelope. Digest equality is evidence for that decision, not the
definition, because different interpreted queries may legitimately produce the same
terminal envelope.

**Dependency:** the opening-query digest is not yet present in `event-schema.json`;
until that contract is implemented, stage-one screening is not operational. Raised
with Clarence for the C-BLOCK-05 contract workshop.

### Inference boundary

Excluding repaired episodes means the P2 contrast under-tests conversational repair.
This exclusion is a declared inference boundary rather than a hidden confound, and the
repair rate is reported separately with uncertainty. With additional assessor
resources, the preferred design is two estimands: one for unrepaired same-envelope
episodes and one analysing repaired episodes independently.

------------------------------------------------------------------------

## 4. Ethics status

**Decision:** DEFINED BUT UNMEASURED without an approved participant
route.

If no ethics-approved human study exists, the reliance claim is withheld
entirely.

------------------------------------------------------------------------

## 5. Ownership

| Responsibility | Owner |
|---|---|
| Loss definition | Fahmi Alshahabi |
| Estimand | Fahmi Alshahabi |
| Sampling & adjudication | Fahmi Alshahabi |
| Analysis | Fahmi Alshahabi |
| Schema & invariant implementation | Clarence |

### Independence basis

Under the work package independence rule (§2.4), a component owner cannot judge
outputs where ownership defeats blinding. Clarence owns the application
implementation, so the loss definition, estimand and adjudicated scoring remain under
my ownership while implementation remains separate.

------------------------------------------------------------------------

## 5b. Permitted and prohibited claims

**Prohibited (candidates compiled from work package §22 and C-17 §5 — accept, strike or extend):**

- No human-effectiveness, usability or actionability claim absent an approved participant route.
- No deployment, adoption or organisational-effectiveness claim.
- No inference about Londoner behaviour, attendance or health outcomes.
- No demographic-fairness claim.
- No confirmatory wording of any kind — `L_reliance` is estimative by construction.
- No claim that a condition is safer on the basis of displaying less; the shared referent exists
  precisely to make that unstatable.

**Permitted:**

Reliance loss rate over unrepaired episodes within the declared task universe, at the
stated acquisition vintage, under the frozen design weights. Between-condition
contrasts are estimative and conditional on the shared terminal DecisionEnvelope
referent. No claim extends beyond the episodes adjudicated in this benchmark.

## 5c. Reading disposition

My definition uses the same failure conditions as misuse/disuse, but it does not adopt
the Lee & See (2004) or Parasuraman & Riley (1997) framing as a load-bearing
theoretical construct. Those sources are therefore not load-bearing for F-BLOCK-09.
Recorded as a decision, not an omission.

Date: 18 August 2026

------------------------------------------------------------------------

## 6. Affected artefacts

-   `docs/evaluation/estimand-registry.yaml`
-   `docs/evaluation/F-BLOCK-09-decision.md`
-   **CA-02** (recommended new amendment)
-   `F-13` application evaluation
-   `C-BLOCK-15`

------------------------------------------------------------------------

## 7. Required tests

-   `INV-NONINTERFERENCE`
-   Paired identical-digest fixture across P0/P1/P2
-   Exclusion-order gate: fails if any episode's repair status carries an
    adjudication timestamp later than its reliance adjudication timestamp, or if
    repair status is absent for any P2 episode entering the estimand.

------------------------------------------------------------------------

## Fallback

If unresolved or ethics approval is unavailable, **report no reliance
result**.

---

---

## Appended — 2026-09-13: F-09 outcome

FACT — the inputs landed. Michael delivered
`FAHMI_S1_S1B_B0_DELIVERY_20260910.zip` on 2026-09-10, 334,597 bytes, sha256
`9ea2525e880bc73c02bcfe3c34d388e6868365804e27a1c6943330cabe159f50`.

FACT — verified independently, not accepted on assertion. All six member hashes
re-checked against `SHA256SUMS.txt` (6/6 OK). The S1b occurrence total was
recounted directly from the per-provider JSONL rather than from the delivered
summaries: 8,034 across 66 providers, of which Open Sessions 6,597, Playwaze 964,
Bookwhen 473. This matches the delivered figure by a route independent of the
summaries, so a single parsing error could not have produced a false match.

FACT — the fallback was NOT triggered. Michael's 27 August fallback applied only
if S1/S1b failed to land by 2026-09-10 23:59. They landed. F-09 is therefore not
a specification-plus-synthetic-dry-run; the real corpus-wide outputs exist and
are frozen.

FACT — the B0 rate splits. The evidence half (`L_evidence`) is delivered and
cross-validated to 6 dp on seven inheritable dimensions; `has-start-datetime` is
child-only and reports `not_counter_checkable`. The baseline
unacceptable-decision rate is not delivered and cannot be: the rollup's own
fields give `status = ILLUSTRATIVE_PENDING_RATIFY(Row-5, universe, weights)` and
`relation_to_anchor = "L_decision = L_evidence OR Row-5 condition"`. Row 5 has no
meaning, so the disjunction has an undefined operand. The number does not exist
to be computed. No interim figure was requested or offered, per F-02's rule that
an anchor for a risk ceiling must not be invented.

OUTCOME. The required S1/S1b inputs were delivered by Michael on 10 September and
independently verified, so the delivery dependency was satisfied. The evaluation
that was meant to consume those inputs was never executed. The real corpus-wide
outputs exist and are frozen; no evaluation result was produced from them.

NOTED — finding carried from Michael, 2026-09-10, and attributed to him. The
39.36% B0 anchor is a two-point mixture rather than a spread. Of 66 providers
only 33 contribute candidates; of those 33, 27 sit at exactly 1.0 and hold
275,015 records, while Better (239,944, e=0.0026) and Playwaze (184,512,
e=0.0035) are 57.6% of the corpus at effectively zero. 94.8% of the exposed mass
comes from providers at exactly 1.0. The figure is therefore a
provider-composition statistic and must be recomputed, never rescaled, under a
London universe.
