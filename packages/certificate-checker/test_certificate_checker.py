#!/usr/bin/env python3
"""
C-09 checker test + mutation suite.

AI-ASSISTED SCAFFOLD (WP section 10.5). Expected outcomes below are HAND-AUTHORED from the
certificate contract, NOT taken from a production oracle (WP 10.4: "do not call the production
interpreter to determine expected output"). Clarence must re-derive and own these himself, and a
non-author reviewer must sign the checker before it is complete (WP 10.5).

Run:  python test_certificate_checker.py    # exits 0 iff every negative test hits its exact code
                                            # and no checker branch survives mutation.
"""
from __future__ import annotations
import copy
import certificate_checker as C


def hx(ch):
    return "sha256:" + ch * 64


def golden():
    """A valid certificate + verification context that must return PASS."""
    cert = {
        "contract": "Certificate",
        "schema_version": "0.1.0",
        "query_id": "q-croydon-swim-stepfree",
        "decision_digest": hx("d"),
        "claimed": {
            "terminal_decision": "supported_match",
            "scope_qualifier": "scope_complete",
            "recommendation_action": "authorised_slate",
        },
        "versions": {
            "corpus_version": "H1-2026-06-30",
            "interpretation_version": "interp-1.2",
            "schema_version": "0.1.0",
            "verifier_version": "ver-1.0",
            "checker_version": "chk-1.0",
        },
        "compatible_release_root": hx("e"),
        "scope_witness": {"evaluated_complete": True},
        "predicate_witnesses": [
            {"predicate_id": "activity=swimming", "evidence_state": "T", "grade": "explicit",
             "fragment_class": "activity", "receipts": [{"receipt_id": "r-a1", "content_digest": hx("1")}]},
            {"predicate_id": "access=step_free", "evidence_state": "T", "grade": "explicit",
             "fragment_class": "access", "receipts": [{"receipt_id": "r-a2", "content_digest": hx("2")}]},
        ],
        "candidate_witnesses": [
            {"candidate_id": "sess-101", "rank": 1, "pool": "supported",
             "hard_predicate_ids": ["activity=swimming", "access=step_free"]},
            {"candidate_id": "sess-102", "rank": 2, "pool": "supported",
             "hard_predicate_ids": ["activity=swimming", "access=step_free"]},
        ],
        "state_transition": {"from_state": "query_review", "to_state": "discovery_decision"},
    }
    ctx = {
        "receipt_store": {"r-a1": hx("1"), "r-a2": hx("2")},
        "manifest": {
            "compatible_release_root": hx("e"),
            "allowed_versions": {
                "corpus_version": "H1-2026-06-30",
                "interpretation_version": "interp-1.2",
                "schema_version": "0.1.0",
                "verifier_version": "ver-1.0",
                "checker_version": "chk-1.0",
            },
            "certifiable_fragment": ["activity", "access", "geo"],
            "allowed_transitions": [
                {"from_state": "query_review", "to_state": "discovery_decision"},
                {"from_state": "query_review", "to_state": "clarify"},
                {"from_state": "clarify", "to_state": "discovery_decision"},
            ],
        },
        "expected_query_id": "q-croydon-swim-stepfree",
        "expected_decision_digest": hx("d"),
    }
    return cert, ctx


# --- negative cases: (name, WP-10.5 label, mutate(cert,ctx), expected_code) ----
def _missing_witness(c, x):      del c["predicate_witnesses"][1]           # drop access witness
def _truncated_path(c, x):       c["predicate_witnesses"][0]["receipts"] = []
def _swapped_receipt(c, x):      x["receipt_store"]["r-a1"] = hx("9")      # id resolves, wrong content
def _forged_hash(c, x):          c["predicate_witnesses"][0]["receipts"][0]["content_digest"] = hx("8")
def _stale_vintage(c, x):        c["versions"]["corpus_version"] = "H1-2026-06-29"
def _bad_version(c, x):          c["versions"]["interpretation_version"] = "interp-1.1"
def _escalation_ub(c, x):        c["predicate_witnesses"][0]["evidence_state"] = "U"
def _dropped_scope(c, x):        c["scope_witness"]["evaluated_complete"] = False
def _ineligible_cand(c, x):      c["candidate_witnesses"][1]["pool"] = "indeterminate"
def _wrong_target(c, x):         c["query_id"] = "q-some-other-query"
def _unsupported_fragment(c, x): c["predicate_witnesses"][0]["fragment_class"] = "free_text_guess"
def _unresolved_receipt(c, x):   c["predicate_witnesses"][0]["receipts"].append({"receipt_id": "r-nope", "content_digest": hx("1")})
def _dup_identity(c, x):         c["predicate_witnesses"].append(copy.deepcopy(c["predicate_witnesses"][0]))
def _schema_extra_field(c, x):   c["surprise_field"] = "unexpected"                             # additionalProperties:false (MS-3)
def _incompatible_decision(c, x): c["claimed"]["terminal_decision"] = "evidence_indeterminate"  # slate under non-supported (MS-7)
def _bad_transition(c, x):       c["state_transition"]["to_state"] = "results_leak"             # not a permitted transition (MS-6)
def _caller_asserted_checker(c, x):                                                             # MS-7 checker version
    c["versions"]["checker_version"] = "chk-9.9"; x["manifest"]["allowed_versions"]["checker_version"] = "chk-9.9"
def _empty_allowed_versions(c, x): x["manifest"]["allowed_versions"] = {}                        # WY-3 fail-open
def _unpinned_version_key(c, x):   x["manifest"]["allowed_versions"].pop("corpus_version", None)  # WY-3 partial pin

NEGATIVES = [
    ("missing_witness",      "missing witness",                       _missing_witness,      C.FAIL_MISSING_WITNESS),
    ("truncated_path",       "truncated evidence path",               _truncated_path,       C.FAIL_MISSING_WITNESS),
    ("swapped_receipt",      "swapped receipt",                       _swapped_receipt,      C.FAIL_DIGEST_MISMATCH),
    ("forged_hash",          "forged hash",                           _forged_hash,          C.FAIL_DIGEST_MISMATCH),
    ("stale_vintage",        "stale vintage",                         _stale_vintage,        C.FAIL_VERSION_MISMATCH),
    ("incompatible_version", "incompatible schema/interp version",    _bad_version,          C.FAIL_VERSION_MISMATCH),
    ("escalation_ub",        "U or B escalated to supported",         _escalation_ub,        C.FAIL_ILLEGAL_ESCALATION),
    ("dropped_scope",        "scope qualifier dropped",               _dropped_scope,        C.FAIL_SCOPE_INCONSISTENCY),
    ("ineligible_candidate", "supported slate w/ ineligible candidate", _ineligible_cand,    C.FAIL_ILLEGAL_ESCALATION),
    ("wrong_target",         "certificate for another query",         _wrong_target,         C.FAIL_DIGEST_MISMATCH),
    ("unsupported_fragment", "predicate outside certifiable fragment", _unsupported_fragment, C.FAIL_UNSUPPORTED_FRAGMENT),
    ("unresolved_receipt",   "unresolved receipt",                    _unresolved_receipt,   C.FAIL_UNRESOLVED_RECEIPT),
    ("dup_identity",         "duplicated/ambiguous identity",         _dup_identity,         C.FAIL_MALFORMED),
    ("schema_extra_field",   "certificate violates its JSON Schema",   _schema_extra_field,   C.FAIL_MALFORMED),
    ("incompatible_decision","incompatible decision combination",      _incompatible_decision, C.FAIL_MALFORMED),
    ("bad_transition",       "impermissible state transition",         _bad_transition,       C.FAIL_MALFORMED),
    ("caller_asserted_checker","caller-asserted checker version",       _caller_asserted_checker, C.FAIL_VERSION_MISMATCH),
    ("empty_allowed_versions", "empty allowed_versions waives pinning",  _empty_allowed_versions,  C.FAIL_VERSION_MISMATCH),
    ("unpinned_version_key",   "partial allowed_versions (unpinned key)", _unpinned_version_key,   C.FAIL_VERSION_MISMATCH),
]


def build(mutate):
    c, x = golden()
    mutate(c, x)
    return c, x


def run():
    failures = 0

    # 1) golden must PASS
    c, x = golden()
    out, detail = C.check(c, x)
    ok = out == C.PASS
    failures += (not ok)
    print(f"[{'OK ' if ok else 'BAD'}] golden -> {out}")

    # MS-8 (Michael 2026-08-23): the public API must not allow a bypass with an empty check set
    try:
        C.check(c, x, [])  # type: ignore[call-arg]
        print("[BAD] check() accepted a checks override (MS-8 bypass OPEN)"); failures += 1
    except TypeError:
        print("[OK ] check() has no bypass parameter (MS-8)")
    if C._run_checks(c, x, [])[0] != C.FAIL_MALFORMED:
        print("[BAD] _run_checks([]) did not fail closed (MS-8)"); failures += 1
    else:
        print("[OK ] _run_checks([]) fails closed -> FAIL_MALFORMED (MS-8)")

    # 2) each negative must hit its exact code
    print("\n-- negative cases (WP 10.5) --")
    baseline = {}
    for name, label, mut, expected in NEGATIVES:
        c, x = build(mut)
        out, detail = C.check(c, x)
        baseline[name] = out
        ok = out == expected
        failures += (not ok)
        print(f"[{'OK ' if ok else 'BAD'}] {name:22s} {label:38s} -> {out}"
              + ("" if ok else f"  EXPECTED {expected}"))

    # 3) mutation testing: removing any single checker branch must change >=1 negative outcome
    print("\n-- mutation testing (branch deletion) --")
    survivors = []
    for i, (code, _) in enumerate(C.CHECKS):
        mutant = C.CHECKS[:i] + C.CHECKS[i + 1:]
        changed = False
        for name, label, mut, expected in NEGATIVES:
            c, x = build(mut)
            if C._run_checks(c, x, mutant)[0] != baseline[name]:
                changed = True
                break
        status = "killed" if changed else "SURVIVED"
        if not changed:
            survivors.append(code)
        print(f"[{'OK ' if changed else 'BAD'}] drop {code:26s} -> {status}")
    failures += len(survivors)

    print("\nRESULT:", "ALL CHECKER TESTS PASS" if failures == 0
          else f"{failures} FAILURE(S)" + (f"; surviving mutants: {survivors}" if survivors else ""))
    return 1 if failures else 0


def test_certificate_checker():
    """pytest entry point so PyCharm's green button / `pytest` collect this file
    (they look for a test_* function; the full report lives in run()). Passes when the
    golden certificate PASSes, every negative case returns its expected FAIL_* code, and
    no checker branch survives mutation. Run with -s to see the per-case lines, or run the
    file directly (python test_certificate_checker.py) for the full printed report."""
    assert run() == 0, "checker suite failed — run the file directly to see which case"


if __name__ == "__main__":
    import sys
    sys.exit(run())
