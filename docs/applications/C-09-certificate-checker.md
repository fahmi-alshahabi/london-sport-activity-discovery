# C-09 — Independent certificate checker

**Owner (proposed):** Clarence (implementation) · **Contract review:** Michael (Section 09) · **Non-author code review:** required, not Clarence (WP §2.6, §10.5)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Not frozen; not independently reviewed.
**Binds to:** `RATIFY-09-04` (production / reference / checker ownership), Section 09 outcome vocabulary. Builds on C-BLOCK-05 (`DecisionEnvelope`).

> **Authorship notice (WP §0).** AI-assisted scaffold prepared from
> `CLARENCE_ZHEN_JIN_TAN_SPECIALISED_WORK_PACKAGE.md` §10. Not evidence that Clarence authored,
> read or accepted it. He must inspect it, correct it in his own words, re-derive the expected
> outcomes himself, and obtain a non-author code review. **He cannot certify his own checker**
> (WP §2.6, §10.4).

## 1. Purpose (WP §10.1)

Michael's production interpreter emits a terminal decision **and** a compact certificate/witness.
Clarence implements a **deliberately small** checker that verifies the certificate *without trusting
the production implementation*. This is **limited technical independence**, not external
independence — its value is that a bug in production is caught by code that shares none of
production's logic.

## 2. Independence rules honoured (WP §10.4)

The reference checker (`packages/certificate-checker/certificate_checker.py`):

- imports nothing from any production/evidence module (stdlib only);
- never calls the production interpreter to decide the expected output;
- implements only the frozen certificate contract;
- takes expected values (versions, receipts, target query/decision digest, certifiable fragment)
  from a caller-supplied **manifest/store**, never re-derived from production code;
- fails **closed**: any exception during a check yields `FAIL_MALFORMED`, never an accidental `PASS`.

The test suite's expected outcomes are **hand-authored from the contract**, not read from a
production oracle. Disagreements between production, a reference interpreter and this checker are
recorded in `discrepancy-register.md` and **triaged, never resolved by editing the checker to make
production pass** (WP §10.4).

> Open contract question for the workshop (review **CA-2**): Michael owns both the artefact under
> test (production interpreter) *and* the contract that defines "correct" (claim contract).
> `RATIFY-09-04` must state whether the claim-contract author may also be the production-interpreter
> author, or whether that pairing must be split.

## 3. Contract

Input: a `Certificate` (`certificate.schema.json`) + a verification context
`{receipt_store, manifest, expected_query_id, expected_decision_digest}`. Output: exactly one
outcome from the WP §10.3 enum. Names are **PROPOSED** and bind to Section 09 — the checker must not
invent competing semantics (WP §10.3).

Outcomes: `PASS`, `FAIL_MALFORMED`, `FAIL_MISSING_WITNESS`, `FAIL_UNRESOLVED_RECEIPT`,
`FAIL_DIGEST_MISMATCH`, `FAIL_VERSION_MISMATCH`, `FAIL_ILLEGAL_ESCALATION`,
`FAIL_SCOPE_INCONSISTENCY`, `FAIL_UNSUPPORTED_FRAGMENT`.

Precedence (first failing check wins, so a single outcome is returned):
`MALFORMED → VERSION_MISMATCH → UNSUPPORTED_FRAGMENT → MISSING_WITNESS → UNRESOLVED_RECEIPT →
DIGEST_MISMATCH → ILLEGAL_ESCALATION → SCOPE_INCONSISTENCY → PASS`.

## 4. Negative-test matrix (WP §10.5) — all passing

| WP §10.5 case | Fixture | Outcome |
|---|---|---|
| missing witness | `_missing_witness` | `FAIL_MISSING_WITNESS` |
| truncated evidence path | `_truncated_path` | `FAIL_MISSING_WITNESS` |
| swapped receipt | `_swapped_receipt` | `FAIL_DIGEST_MISMATCH` |
| forged hash | `_forged_hash` | `FAIL_DIGEST_MISMATCH` |
| stale vintage | `_stale_vintage` | `FAIL_VERSION_MISMATCH` |
| incompatible schema/interpretation version | `_bad_version` | `FAIL_VERSION_MISMATCH` |
| `U`/`B` escalated to supported | `_escalation_ub` | `FAIL_ILLEGAL_ESCALATION` |
| scope qualifier dropped | `_dropped_scope` | `FAIL_SCOPE_INCONSISTENCY` |
| supported slate with ineligible candidate | `_ineligible_cand` | `FAIL_ILLEGAL_ESCALATION` |
| certificate for another query/candidate | `_wrong_target` | `FAIL_DIGEST_MISMATCH` |
| predicate outside certifiable fragment | `_unsupported_fragment` | `FAIL_UNSUPPORTED_FRAGMENT` |
| unresolved receipt | `_unresolved_receipt` | `FAIL_UNRESOLVED_RECEIPT` |
| duplicated/ambiguous identity | `_dup_identity` | `FAIL_MALFORMED` |

**Mutation testing (WP §10.5 "mutation of every checker decision branch"):** deleting any one of the
eight decision branches changes at least one negative outcome — **0 surviving mutants**. This is the
evidence that every branch is load-bearing and tested (a test that cannot fail is not evidence,
WP §17.3).

## 5. What must be agreed before this freezes

1. Exact outcome names and their meaning (`RATIFY-09-04`, Section 09) — the enum here is a proposal.
2. The exact certificate/witness shape Michael's production interpreter will emit (this
   `certificate.schema.json` is Clarence's *consumer* proposal; production must emit a compatible
   object).
3. What `decision_digest` is computed over, so "certificate for another decision" is detectable
   (must match C-BLOCK-05's `DecisionEnvelope.digest`).
4. The certifiable-predicate fragment (`RATIFY-09-03`): which `fragment_class` values may ever be
   certified.
5. CA-2 independence split (claim-contract author vs production-interpreter author).

## 6. Completion criteria (WP §10.5)

- [x] Checker implements only the frozen contract (stdlib; no production import).
- [x] Negative fixtures for every §10.5 case; each returns its exact code.
- [x] Mutation report: every decision branch killed (0 survivors).
- [ ] Contract confirmed with Michael / Section 09 (`RATIFY-09-04`); enum names ratified.
- [ ] **Non-author** code review recorded (not Clarence).
- [ ] Production / reference / checker discrepancy register populated once production emits certificates.

Until the last three are done this remains a proposed artefact, not completed assurance evidence.
