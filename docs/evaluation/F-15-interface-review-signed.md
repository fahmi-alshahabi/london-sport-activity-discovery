# F-15 — Interface review: public discovery and staff assurance

**Reviewer:** Fahmi Alshahabi (non-author, evaluation stream)
**Author of artefacts under review:** Clarence Zhen Jin Tan
**Reviewed:** `apps/public-discovery`, `apps/staff-assurance`, `packages/application-contracts/c-block-05`
**Branch:** `clarence/c-block-05` · **Review date:** 18 August 2026
**Basis:** work package §4.2 canonical vocabulary; §22 prohibited claims; C-BLOCK-05 §3 collapse
prohibitions; the eight executable invariants.

**Verdict: CONFIRMED WITH AMENDMENTS.** The rendered interfaces honour the evidence semantics on
every outcome I was able to exercise. Three findings, none blocking. The two `major` findings are
about what cannot currently be tested and what the public projection does not distinguish, not
about a semantics failure.

> Independent non-author review under Section 19. It does not approve or ratify. Findings are
> numbered; the author accepts, amends or contests each one.

---

## 1. What I ran

All observations below are mine, made on 18 August 2026 against the branch state above.

| Suite | Result |
|---|---|
| `apps/public-discovery/test_slice.py` | 19 checks, ALL PASS |
| `packages/application-contracts/c-block-05/projection_and_invariants.py` | 2 valid fixtures pass; 6 adversarial fixtures each DETECTED by their seeded invariant |
| `apps/staff-assurance/test_staff.py` | 41 checks, ALL PASS |

I then exercised the running applications in a browser: four public scenarios, the detail and help
pages, and three staff panels under the `analyst` role.

---

## 2. Collapse prohibitions (§4.2 / C-BLOCK-05 §3)

| # | Prohibition | Result | Observed |
|---|---|---|---|
| 1.1 | `U` → `F` | **PASS** | Unpublished price renders as "not published (assumed from the standard's default)", never as "no" or "free". Detail page states: fields shown as "not published" are missing from the source, not a "no". |
| 1.2 | `B` → support | **NOT TESTABLE** | No conflicting-evidence scenario exists. See F15-2. |
| 1.3 | `model_abstained` → `evidence_indeterminate` | **PASS (staff plane)** | Failure-chain explorer shows `terminal=evidence_indeterminate; recommendation=model_abstained` as distinct values on the same row. Not exercisable from the public app. |
| 1.4 | `service_failure` → "no results" | **PASS** | Renders "Something went wrong — a component didn't respond. We will not show a stale or made-up result in its place." Next step declared as deterministic fallback. |
| 1.5 | `scope_indeterminate` → `bounded_non_match` | **PASS** | Coverage is stated as its own qualifier: 2 of 6 Croydon feeds timed out on 2026-06-30, results may be incomplete. |
| 1.6 | `browse_only` → `authorised_slate` | **NOT TESTABLE** | No browse-only scenario. See F15-2. |

## 3. Claim discipline (§22)

| # | Check | Result | Observed |
|---|---|---|---|
| 2.1 | "No listed match" ≠ "no activity exists" | **PASS** | The no-match screen names the corpus searched (4 Havering feeds, vintage 2026-06-30) and states that nothing matched in the data checked. The disclaimer also appears in the footer of every page. |
| 2.2 | Capacity never inferred | **PASS** | No capacity or spaces-available language anywhere in the public app. |
| 2.3 | Bookability never inferred | **PASS** | Detail page: nothing here is a guarantee of availability or booking. Footer states the service is not a booking, payment or referral service. |
| 2.4 | No population or coverage claim | **PASS** | Help page frames the service as finding *published* activities and showing what the data can and cannot confirm. |
| 2.5 | Vintage visible | **PASS** | Data vintage 2026-06-30 shown on results and detail pages; condition label shown alongside it. |

## 4. Staff assurance

| # | Check | Result | Observed |
|---|---|---|---|
| 3.1 | Disclosure classes hold | **PASS** | `internal_score` and `model_version` staff-only; why-not `blocking_state` hidden from public; role gate returns 403 without a role on all nine staff routes. |
| 3.2 | Provenance legible | **PASS** | Every panel carries a provenance block: universe, unevaluated-feeds denominator, vintage, corpus/interpretation version, access role, permitted action, permitted wording. The failure-chain explorer traces acquisition → reconstruction/evidence → gate → interface with a status per stage. |
| 3.3 | Indeterminacy survives to staff | **PASS** | Evidence-symmetry holds on all three scenarios; staff and public agree on the shared decision. Authority is asymmetric, evidence is not. |
| 3.4 | No unverified claim; workflow cannot be skipped | **PASS** | Action-card workflow enforces independent review before approval and an authorised role before send. An `assurance` role cannot self-authorise a route. |

## 5. Conditions and measurement (evaluation-stream relevance)

| # | Check | Result | Observed |
|---|---|---|---|
| 4.1 | P0/P1/P2 distinguishable | **PASS** | Results page labels the active condition ("Condition P1 — evidence-aware interface"). |
| 4.2 | Ordering identical across conditions | **PASS** | `test_slice.py` asserts identical order across P0/P1/P2, with P0 list-only and P1 evidence-aware. |
| 4.3 | Terminal decision shared across conditions | **PASS** | INV-NONINTERFERENCE passes on all scenarios; staff replay confirms stored and recomputed digests identical. |
| 4.4 | Denominator visible | **PASS** | Unevaluated-feeds denominator exposed in the staff provenance block (0 on supported, 2 on indeterminate). |
| 4.5 | Opening-query envelope not captured | **CONFIRMED ABSENT** | No opening-query digest in `event-schema.json` or in any rendered panel. Confirms the F-BLOCK-09 dependency raised for the C-BLOCK-05 contract workshop. |

## 6. Findings

| ID | Severity | Finding | Evidence | Proposed disposition |
|---|---|---|---|---|
| **F15-1** | major | The public projection does not distinguish coverage-incompleteness from evidence-unknown. The `indeterminate` screen is an evidence decision whose entire explanatory box is a coverage story (2 of 6 feeds timed out). A public user cannot tell whether a field was unpublished or whether coverage was incomplete. **The information exists** — the staff failure-chain separates `acquisition: incomplete` from `access=step_free = U (source_absence)` — so this is a projection and wording issue, not a semantics failure. | Public `indeterminate` screen vs staff failure-chain explorer, same scenario | Distinguish the two in public wording, or state explicitly that the public plane merges them by design |
| **F15-2** | major | Three collapse prohibitions cannot be exercised. Only four scenarios exist (`supported`, `no_match`, `indeterminate`, `service_failure`); there is no conflicting-evidence (`B`), `model_abstained` or `browse_only` scenario in the public app. Separately, INV-NONINTERFERENCE and INV-SYMMETRY have no adversarial fixture — they run on valid envelopes but nothing demonstrates they *catch* a defect. INV-NONINTERFERENCE is the gate the `L_reliance` shared referent depends on. | Scenario directory listing; fixture-to-invariant map in `projection_and_invariants.py` | Add scenarios for `B`, `model_abstained`, `browse_only`; add adversarial fixtures for INV-NONINTERFERENCE and INV-SYMMETRY |
| **F15-3** | minor | The price row reads "not published" with basis "assumed from the standard's default". If nothing was published, nothing was assumed; if a default was applied, something was inferred and the state may not be a pure `U`. Price is exactly the field where an inferred default could be read as a confirmed fact. | Detail page, `sess-101`, scenario `supported` | Clarify the wording or the state mapping |

## 7. Reproducibility

| Item | Observation |
|---|---|
| Public app | `uvicorn server.main:app --app-dir apps/public-discovery --reload --reload-dir apps/public-discovery` — started clean, no errors |
| Staff app | Same pattern with `apps/staff-assurance`. Browser access requires the dev `?role=` parameter; the documented `curl -H` example does not work in PowerShell, where `curl` aliases to `Invoke-WebRequest` |
| Setup | `pip install fastapi jinja2 httpx uvicorn` was sufficient. No undocumented steps |
| Minor | `test_slice.py` and `test_staff.py` emit a StarletteDeprecationWarning: `httpx` with `starlette.testclient` is deprecated. Not a failure; will break on a future Starlette version |
| Minor | `/static/enhanced/enhance.js` returns 404 on the results page. The no-JS core is unaffected, but the progressive-enhancement bundle is not built or not served |
| Version reviewed | `clarence/c-block-05`, 18 August 2026 |

## 8. Confirmed as written

The typed-outcome separation is real in the rendered pages, not only in the schema: four distinct
screens with distinct headings, distinct explanations and distinct next actions. The C-11 lexicon
holds under render-lint. The footer disclaimer appears on every page rather than only where
convenient. Evidence symmetry with authority asymmetry is the right shape — staff get more
authority, not different facts — and the action-card gates enforce it in the state machine rather
than in guidance. The provenance block exceeds what §3.2 asked for, and exposing the
unevaluated-feeds denominator in the interface is a genuine contribution to measurability.

The adversarial fixtures deserve specific credit: each of the six seeds one defect and each is
caught by the invariant it targets. Gates that cannot fail are not evidence; these can and do.

## 9. Reviewer statement

I reviewed the running applications and the contract test suites on 18 August 2026 as a non-author
under Section 19. I did not author, modify or contribute to the code under review. The
observations recorded above are my own.

**Signed:** Fahmi Alshahabi **Date:** 18 August 2026
