#!/usr/bin/env python3
"""
reducer_v0_1_1.py — the R1 evidence gate (D4_INPUT_CONTRACT_v0_1 §3), PROPOSED

SUPERSEDES reducer_v0_1.py (hash dac99905…). v0.1.1 changelog — from the
1 Sep adversarial review, defect proven on real data before fixing:
  * FIX (R1, honesty-critical): _norm was shallow — nested address blocks
    (locality, region, postcode, street) were invisible to the matcher, so
    querying a venue's OWN postcode returned bounded_non_match: a confident
    false non-match, exactly the "unjustified bounded non-match" loss class
    this project exists to prevent. _norm now recurses through nested dicts
    and lists, so the matcher sees the record's full text.
  * FIX (R2, hygiene): dead `if False else` construct removed from the
    selftest; regression cases for R1 added (own-postcode must satisfy).
  * CLASSIFIER UNCHANGED: the three-way logic and its precedence are
    byte-for-byte the contract's §3 semantics, as in v0.1.

Classification (frozen):
    supported_match          all constrained dimensions evidence-T AND satisfied
    bounded_non_match        >=1 constrained dimension evidence-T AND unsatisfied
    evidence_indeterminate   no T-dimension unsatisfied; >=1 constrained dim U
Precedence is order-free: a demonstrated failure beats an unknown.

HONESTY BOUNDARY:
  * Matchers are policy, not logic. v0.1.1 ships text containment over the
    record's FULL normalized text (URLs, identifiers and any markup included —
    it is a text-level predicate, not a semantic one) and ISO date-window
    containment. Field-aware or semantic matching is a ratification item —
    plug in as a new matcher, never edit the classifier.
  * bounded_non_match is a claim RELATIVE TO THE DECLARED PREDICATE ("the
    queried text does not occur anywhere in this record's supported value").
    A slate-level claim that "no matches exist" additionally requires the
    bounded-search argument, which is outside this reducer's scope.

Deterministic: no randomness, no wall-clock, no environment reads.
"""
import json, unicodedata

REDUCER_VERSION = "reducer-0.1.1-PROPOSED"
CONTRACT_REF = "D4_INPUT_CONTRACT_v0_1 §3"
SUPERSEDES = {"reducer_v0_1.py": "dac99905a80eb244de3831dc8b34680cf2079e6c0914332bd9587d99379bebf4"}

# --- evidence states from lineage (verbatim from b0-substrate v0.1) ---------
_T = {"ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL", "INHERITED"}
_U = {"SOURCE_ABSENT", "UNRESOLVABLE_PARENT_UNAVAILABLE"}


def evidence_state(record, field):
    """'T' | 'U' for one field of one S1 record (child-only absent => 'U')."""
    entry = (record.get("lineage") or {}).get(field)
    cls = entry.get("class") if isinstance(entry, dict) else entry
    if cls is None:
        return "U"
    if cls in _T:
        return "T"
    if cls in _U:
        return "U"
    raise ValueError(f"unknown lineage class {cls!r} for field {field!r}")


# --- v0.1.1 matchers (PROPOSED policy; text-level, deep, deterministic) -----
def _norm(x):
    """Lower-cased, accent-stripped, whitespace-collapsed text of a value,
    recursing through nested dicts (sorted by key) and lists — the record's
    full text, so absence of the queried text is never an artefact of depth."""
    if isinstance(x, dict):
        return " ".join(_norm(v) for _, v in sorted(x.items()))
    if isinstance(x, list):
        return " ".join(_norm(i) for i in x)
    s = unicodedata.normalize("NFKD", str(x))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def match_text(wanted):
    """Satisfied iff the normalized wanted string occurs anywhere in the
    value's full normalized text."""
    w = _norm(wanted)
    return lambda value: w in _norm(value)


def match_date_window(start_iso, end_iso):
    """Satisfied iff the value's date part lies in [start, end] (ISO compare)."""
    return lambda value: start_iso <= str(value)[:10] <= end_iso


# --- the frozen classifier (unchanged from v0.1) -----------------------------
def reduce_decision(record, constraints):
    """constraints: list of (field, predicate). Returns (decision, detail);
    detail maps each field to 'T:satisfied' | 'T:unsatisfied' | 'U'."""
    detail, saw_unsat, saw_u = {}, False, False
    for field, pred in constraints:
        st = evidence_state(record, field)
        if st == "U":
            detail[field] = "U"; saw_u = True
        else:
            ok = bool(pred(record["fields"][field]))
            detail[field] = "T:satisfied" if ok else "T:unsatisfied"
            saw_unsat = saw_unsat or not ok
    if saw_unsat:
        return "bounded_non_match", detail
    if saw_u:
        return "evidence_indeterminate", detail
    return "supported_match", detail


# --- self-test: hand-computed fixtures incl. the R1 regression --------------
def _selftest():
    L = lambda c: {"class": c, "rule": "test"}
    rec = {
        "fields": {
            "name": "Hydrohex Cardio",
            "location": {"name": "Mill House Leisure Centre",
                         "address": {"@type": "PostalAddress", "addressRegion": "Hartlepool",
                                     "postalCode": "TS24 8AR", "streetAddress": "Raby Road"}},
            "startDate": "2026-07-15T05:30:00+00:00"},
        "lineage": {"name": L("INHERITED"), "location": L("INHERITED"),
                    "activity": L("SOURCE_ABSENT"), "startDate": L("ON_CHILD")},
    }
    cases = [
        ([("location", match_text("mill house")),
          ("startDate", match_date_window("2026-07-01", "2026-07-31"))], "supported_match"),
        # R1 REGRESSION: nested-address values must be visible to the matcher
        ([("location", match_text("TS24 8AR"))], "supported_match"),
        ([("location", match_text("raby road"))], "supported_match"),
        ([("location", match_text("hartlepool"))], "supported_match"),
        # U dimension present, nothing contradicted -> indeterminate
        ([("location", match_text("mill house")), ("activity", match_text("yoga"))],
         "evidence_indeterminate"),
        # T-unsatisfied beats U -> bounded_non_match (token absent everywhere)
        ([("location", match_text("aquatics centre")), ("activity", match_text("yoga"))],
         "bounded_non_match"),
        # date outside window -> bounded_non_match
        ([("startDate", match_date_window("2026-08-01", "2026-08-31"))], "bounded_non_match"),
        # constrained child-only field absent (no lineage row) -> indeterminate
        ([("endDate", match_date_window("2026-07-01", "2026-07-31"))], "evidence_indeterminate"),
    ]
    for constraints, want in cases:
        got, detail = reduce_decision(rec, constraints)
        assert got == want, (want, got, detail)
    rec2 = {"fields": {}, "lineage": {"location": L("UNRESOLVABLE_PARENT_UNAVAILABLE")}}
    assert reduce_decision(rec2, [("location", match_text("x"))])[0] == "evidence_indeterminate"
    a = reduce_decision(rec, [("location", match_text("aquatics")), ("activity", match_text("yoga"))])[0]
    b = reduce_decision(rec, [("activity", match_text("yoga")), ("location", match_text("aquatics"))])[0]
    assert a == b == "bounded_non_match"
    print(json.dumps({"reducer": REDUCER_VERSION, "selftest": "ALL PASS",
                      "cases": len(cases) + 2, "supersedes": SUPERSEDES}))


if __name__ == "__main__":
    _selftest()
