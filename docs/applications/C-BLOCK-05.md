# C-BLOCK-05 — Frozen application contracts (`ApplicationEnvelope`, terminal `DecisionEnvelope`, projections, disclosure classes)

**Owner (proposed):** Clarence Zhen Jin Tan (conversational-UX & application-integration owner)
**Joint sign-off required:** Michael (evidence semantics) · Wesley (transport / versioning / auth)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Not frozen, not ratified, not independently reviewed.
**Binds to:** `RATIFY-14-04` (application/decision/disclosure schemas), `RATIFY-09-01/02/03/05` (evidence, grade, predicate-fragment, claim vocabulary).
**Version:** contracts `0.1.0-PROPOSED`.

> **Authorship notice (WP §0).** This is an AI-assisted coordination scaffold prepared from
> `CLARENCE_ZHEN_JIN_TAN_SPECIALISED_WORK_PACKAGE.md` (7 Aug 2026) and its review
> (7 Aug 2026). It is **not** evidence that Clarence authored, read, accepted or completed the
> work. Clarence must inspect it, correct it in his own words, complete his own primary-source
> reading, accept or amend every decision, work through his own branch, and obtain a scoped
> non-author review. He **cannot certify his own contracts** (WP §2.6).

---

## 1. Why this is the keystone (CA-3)

The review names `C-BLOCK-05` the **sequencing keystone**: "Phases D–H all build on those schemas,
so every other blocker and deliverable is downstream of it. Give it an explicit date and a named
joint owner with Michael and Wesley, ahead of the other thirteen" (CA-3). Section-8's conversational
assistant already *assumes* these schemas exist ("the claim contract and certifying verifier sit in
the reconstruction/evidence stream; conversational UX sits in the applications stream"). Until the
envelope, the terminal decision object, the projections and the disclosure classes are **machine
contracts with passing tests**, no UI logic (`C-05`), no staff workbench (`C-07`), no conversational
integration (`C-08`) and no experiment builds (`C-17`) can be built on solid ground.

**Definition of done for C-BLOCK-05** (WP Phase B exit): schemas validate; incompatible or unsafe
field combinations fail; example envelopes have stable content hashes; the release-blocking
invariants run and pass on valid fixtures and *catch* the adversarial ones; a named non-author
reviewer (not Clarence) has signed the contract.

## 2. What is in this contract bundle

| Artefact | Path | Role |
|---|---|---|
| `DecisionEnvelope` schema | `packages/application-contracts/c-block-05/decision-envelope.schema.json` | The **immutable terminal evidence decision**. The CA-1 referent. |
| `ApplicationEnvelope` schema | `packages/application-contracts/c-block-05/application-envelope.schema.json` | Versioned discriminated union (`action_kind`) the client consumes; embeds the `DecisionEnvelope`. |
| Disclosure classes | `packages/application-contracts/c-block-05/disclosure-classes.json` | Field → release-class map; single source of truth for projection. |
| Projector + invariants | `packages/application-contracts/c-block-05/projection_and_invariants.py` | Reference projector and the **executable** release gates. |
| Fixtures | `packages/application-contracts/c-block-05/fixtures/` | One valid golden envelope + adversarial envelopes seeding one defect each (WP §15.6). |

## 3. Canonical vocabulary carried by the contract (WP §4.2) — must not be collapsed

Atomic evidence states `T` / `F` / `U` / `B`. Terminal decisions `supported_match` /
`bounded_non_match` / `evidence_indeterminate`. Orthogonal `scope_qualifier`
(`scope_complete` / `scope_indeterminate`). Recommendation action `authorised_slate` /
`model_abstained` / `deterministic_fallback` / `browse_only`. The interface may **never** collapse
`U`→`F`, `B`→support, `model_abstained`→`evidence_indeterminate`, `service_failure`→"no results",
`scope_indeterminate`→`bounded_non_match`, or `browse_only`→`authorised_slate`. Each of these is
enforced by an invariant below and/or by the schema's `enum` + conditional `required`.

## 4. Disclosure classes and the projection rule (WP Phase B step 4)

Four field-level classes: `PUBLIC_SAFE`, `STAFF_AGGREGATE`, `STAFF_EVIDENCE`, `RESEARCH_RESTRICTED`.
The public/staff/research surfaces are **derived** from one staff-complete envelope by dropping any
field whose class is not permitted for the plane. Projection is **fail-closed**: a field with no
declared class is dropped from *every* plane until it is classified (this is what makes WP §15.2 —
"nested/free-text/link values are validated, not only top-level keys" — hold by construction).

The interface is a **one-way** simplifier: it may remove detail but may never add certainty, reorder
the certified slate, bypass abstention, or surface a staff-only value (WP §2, §7.3). "The interface
may never strengthen a claim."

## 5. Release-blocking invariants (executable — `projection_and_invariants.py`)

| Invariant | Guards | WP / C-BLOCK |
|---|---|---|
| `INV-DISCLOSURE` | public projection contains only `PUBLIC_SAFE` fields; content scan catches staff signatures smuggled into public strings | §15.2, C-BLOCK-09 |
| `INV-NONINTERFERENCE` | mutating **only** non-`PUBLIC_SAFE` fields leaves the public projection byte-identical | §15.2, C-BLOCK-09, **CA-1** |
| `INV-SYMMETRY` | public and staff agree on decision, scope, action, coverage statement, candidate id+order, vintage | §4.1 |
| `INV-REPLAY` | recomputed digest of the retained public payload equals the stored digest (semantic replay) | C-BLOCK-09 |
| `INV-NO-UNVERIFIED` | no claim with `verification ≠ verified` sits in the renderable set | C-BLOCK-10 |
| `INV-NO-COLLAPSE` | no definite `listing_attribute` claim over a `U`/`B` predicate | §4.2 |
| `INV-COVERAGE` | every `bounded_non_match` carries a non-empty coverage qualifier | C-BLOCK-08 |
| `INV-SLATE-ORDER` | array order equals certified `rank`; an `authorised_slate` contains only `supported` candidates | C-BLOCK-14 |

The adversarial fixtures (`unknown_rendered_as_no`, `staff_note_in_public`,
`dropped_scope_qualifier`, `unverified_claim_present`, `client_sort_reorder`,
`tampered_public_digest`) exist to prove each gate **fails** on the defect it targets — a gate that
cannot fail is not evidence (WP §17.3).

## 6. CA-1 — the `L_reliance` referent (highest-value review finding)

> The review's sharpest catch: unsafe reliance was defined against *displayed* evidence, but `P0`
> and `P1` differ **precisely in what is displayed**, so a system could score *safer by showing
> less* — inverting the construct.

**Disposition adopted here:** `L_reliance` binds to the **terminal `DecisionEnvelope` evidence
state**, which is identical across `P0`/`P1`/`P2` (and `W0`/`W1`/`W1-NA`) by design. The interface
condition changes only the *projection* of that fixed decision, never the decision itself; the
`digest` makes the shared referent auditable and replayable. Because the public projection is a
pure function of the staff-complete decision (`INV-NONINTERFERENCE`), the reliance construct is
measured against the same evidence regardless of how much any condition chooses to display.

**Ownership:** register as **`C-BLOCK-15` and `F-BLOCK-09`** with a **single named owner** shared
with Fahmi (neither work package owns it today). This document proposes the referent; it does not by
itself close the blocker — that needs the joint decision-log entry.

## 7. Reconciliation decision-table row (WP §3 required format)

```text
decision_id:          C-BLOCK-05
question:             What are the frozen machine contracts for ApplicationEnvelope, terminal
                      DecisionEnvelope, public/staff projections and field-level disclosure classes?
options_considered:   (a) prose-only contract in Section 14 [status quo — rejected: not testable];
                      (b) separate hand-maintained public and staff schemas [rejected: they drift and
                          cannot guarantee non-interference];
                      (c) ONE staff-complete schema + a fail-closed class-driven projection with
                          executable invariants [chosen].
chosen_option:        (c)
rationale:            A single source of truth with a derived public view makes evidence symmetry
                      and value-level non-interference provable (CA-1); fail-closed projection makes
                      WP 15.2 hold by construction; digests give semantic replay.
affected_contracts:   application-envelope.schema.json; decision-envelope.schema.json;
                      disclosure-classes.json; C-08 conversation; C-10 projection suite; C-17 builds.
owner:                Clarence (integration lead)
approver:             Michael (evidence semantics) + Wesley (transport/version/auth)  [PENDING]
date:                 <set at the contract workshop — CA-3 says give this the FIRST date>
decision_log_ref:     <bind to a real canonical decision-log ID before Phase C — see CA-4 pattern>
tests_required:       schema validation of all variants; INV-DISCLOSURE, INV-NONINTERFERENCE,
                      INV-SYMMETRY, INV-REPLAY, INV-NO-UNVERIFIED, INV-NO-COLLAPSE, INV-COVERAGE,
                      INV-SLATE-ORDER; stable example hashes.
fallback_if_unresolved: build nothing UI-shaped; deterministic template rendering only over the
                      DecisionEnvelope until the schemas freeze.
```

> No cell may be back-filled from memory after results are seen (WP §3).

## 8. What Clarence must agree with Michael and Wesley before writing any UI logic

**With Michael (evidence semantics / Section 09):**
1. Exact names and order of evidence states, grades and the closed `mechanism` list — the schema
   `enum`s here are proposals and must equal the ratified Section 09 vocabulary (WP §10.3 forbids
   inventing competing semantics).
2. The certifiable predicate fragment (`RATIFY-09-03`): which predicates may ever be `T`.
3. The claim-tuple vocabulary and the render obligation that only `verification == verified` renders
   (`RATIFY-09-05`, C-BLOCK-10).
4. Receipt/witness shape and the certificate-checker contract (feeds `C-09`; keep production ≠
   reference ≠ checker independence, and resolve CA-2: may the claim-contract author also author the
   production interpreter?).
5. What exactly the `digest` is computed over (this draft: canonical public payload minus `digest`).

**With Wesley (transport / Section 16):**
6. Version fields, compatibility rule and fail-closed behaviour on stale/incompatible releases.
7. Auth/role boundary that enforces the disclosure classes server-side (not hidden buttons).
8. Physical repository layout for `packages/` and `apps/` (WP §16 is a candidate, not permission to
   overwrite existing paths).

**Jointly (all three):** freeze the class of every field in `disclosure-classes.json`; agree that
the public surface is a *derived projection*, never a hand-authored second document.

## 9. Permitted wording this artefact licenses (WP §19.1)

> "The applications consume one certified evidence contract: a versioned `ApplicationEnvelope`
> whose terminal `DecisionEnvelope` carries the immutable evidence decision, scope qualifier,
> certified candidate slate, recommendation action, typed claims and receipts. Public and staff
> surfaces are permission-separated **projections** of that one decision; evidence symmetry and
> value-level non-interference are checked by executable gates."

Do **not** describe these as "two dashboards" novel by number, and do **not** call the projection
"secure/private/compliant" — those are Section 15 authority determinations, not Clarence's to issue
(WP §2.4, §19.3).

## 10. Status and next step

PROPOSED. Requires: (i) the contract workshop with Michael and Wesley (WP §21 action 8); (ii) a real
`decision_log_ref`; (iii) `C-BLOCK-15`/`F-BLOCK-09` opened jointly with Fahmi for CA-1; (iv) a
non-author reviewer of the contract (Michael for semantics, plus a non-author code reviewer for the
projector). Only then does it freeze and unblock Phases D–H.
