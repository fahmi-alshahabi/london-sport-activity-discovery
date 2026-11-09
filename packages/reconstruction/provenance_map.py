#!/usr/bin/env python3
"""
provenance_map.py — the §09-1 clause (1) projection: S1 lineage class -> provenance locus,
plus reference implementations of the clause (7) aggregation rules.

ONE TABLE, IMPORTED, NEVER RE-IMPLEMENTED. This module exists so that Michael's pack generator
(lineage_pack_v0_2_0.py) and Wesley's D4 envelope assembly project the SAME lineage classes to
the SAME provenance values. Wesley's stated risk for the three-way change was "three people
building inconsistent parts"; the way to make that impossible for this mapping is for both
consumers to import it. The same discipline the pack generator applies to the R1 gate
("the reducer is imported, never re-implemented").

WHAT IT MAPS. The S1 engine (v0.3.1, frozen) emits, per record and governed field,
record["lineage"][field]["class"] in {ON_CHILD, CHILD_OVERRIDES, BOTH_EQUAL, INHERITED,
SOURCE_ABSENT, UNRESOLVABLE_PARENT_UNAVAILABLE}. The B0 substrate's CLASS_MAP projects those six
classes to (evidence_state, mechanism, lineage_grade). This module projects the same six classes
to the provenance locus the DecisionEnvelope target specification (C-BLOCK-05 v0.2, §5) declares:

    ON_CHILD, CHILD_OVERRIDES, BOTH_EQUAL  -> on_record
    INHERITED                              -> inherited_from_parent
    SOURCE_ABSENT, UNRESOLVABLE_PARENT_UNAVAILABLE -> (absent)   [U states carry no value]

The engine does NOT change for any of this. Provenance is a consumer-side projection of a class
the engine already emits; nothing here re-opens byte-identity verification of any engine output.

WHAT IT DOES NOT DO. It does not decide the §09-1 motion. It is PROPOSED and is safe to build
against under either outcome of that motion (post-submission execution, or branch-now with a
fallback date), because nothing that imports it is merged to main by this module's existence.

Fail-closed: an unknown lineage class raises, it is never mapped to a default.

Provenance: Michael's stream, 13 Sep 2026, AI-assisted; PROPOSED pending non-author review.
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path

PROVENANCE_MAP_VERSION = "provenance-map-0.1-PROPOSED"

ON_RECORD = "on_record"
INHERITED_FROM_PARENT = "inherited_from_parent"
PROVENANCE_VALUES = (ON_RECORD, INHERITED_FROM_PARENT)

# --- §09-1 clause (1): lineage class -> provenance locus ------------------------------------------
LINEAGE_TO_PROVENANCE = {
    "ON_CHILD":        ON_RECORD,
    "CHILD_OVERRIDES": ON_RECORD,               # child value wins; locus is the record
    "BOTH_EQUAL":      ON_RECORD,               # attested both sides; the record is sufficient
    "INHERITED":       INHERITED_FROM_PARENT,
    "SOURCE_ABSENT":   None,                    # U state — no value, no locus
    "UNRESOLVABLE_PARENT_UNAVAILABLE": None,    # U state
}
# The pack generator's synthetic label for a child-only field with no lineage row (U state).
ABSENT_CHILD_ONLY_FIELD = "ABSENT_CHILD_ONLY_FIELD"

# --- §09-1 clause (2): the pack's lineage grade -> the envelope's strength grade -------------------
# v0.1 packs wrote grade 'inherited' for INHERITED rows. Under clause (2) an inherited value keeps
# grade 'explicit' (it was published, on the parent) and the inheritance fact travels as provenance.
LINEAGE_GRADE_TO_STRENGTH = {"explicit": "explicit", "inherited": "explicit", None: None}

# The envelope's strength enum (target spec §1; unchanged by §09-1). Unordered — see claim_grade().
ENVELOPE_GRADES = ("explicit", "schedule_derived", "specification_default")

# Verbatim copy of the B0 CLASS_MAP domain, cross-checked at import when B0 is importable.
_B0_CLASS_MAP_DOMAIN = ("ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL", "INHERITED",
                        "SOURCE_ABSENT", "UNRESOLVABLE_PARENT_UNAVAILABLE")
_B0_T_CLASSES = ("ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL", "INHERITED")


class ProvenanceMapError(ValueError):
    """Raised, never swallowed: an unknown lineage class, or an aggregation the rules refuse."""


class AggregationRefused(ProvenanceMapError):
    """§09-1 clause 7(ii): non-explicit contributors disagree; the claim is refused, not guessed."""


def provenance_of(lineage_class):
    """Lineage class -> 'on_record' | 'inherited_from_parent' | None (U states carry no value).

    None (no lineage row: a child-only field absent on the child) and the pack generator's
    ABSENT_CHILD_ONLY_FIELD label are U states and map to None. Anything else unknown raises.
    """
    if lineage_class is None or lineage_class == ABSENT_CHILD_ONLY_FIELD:
        return None
    try:
        return LINEAGE_TO_PROVENANCE[lineage_class]
    except KeyError:
        raise ProvenanceMapError(f"unknown lineage class {lineage_class!r} — refusing to map (fail-closed)")


def strength_of(lineage_grade):
    """B0/pack lineage grade ('explicit' | 'inherited' | None) -> envelope strength grade."""
    try:
        return LINEAGE_GRADE_TO_STRENGTH[lineage_grade]
    except KeyError:
        raise ProvenanceMapError(f"unknown lineage grade {lineage_grade!r} — refusing to map (fail-closed)")


# --- §09-1 clause (7): aggregation over a claim's contributing values ------------------------------
def claim_provenance(contributing):
    """7(i). inherited_from_parent if ANY contributing value is inherited; on_record if all located
    values are on-record; None if no contributing value is located. Binary — no ordering needed."""
    located = [p for p in contributing if p is not None]
    for p in located:
        if p not in PROVENANCE_VALUES:
            raise ProvenanceMapError(f"unknown provenance value {p!r}")
    if not located:
        return None
    return INHERITED_FROM_PARENT if INHERITED_FROM_PARENT in located else ON_RECORD


def claim_grade(contributing):
    """7(ii). 'explicit' ONLY IF EVERY contributing grade is explicit (unanimity for the positive
    claim — the same rule reduce_decision applies to supported_match). If the non-explicit
    contributors all agree, the claim carries that shared value. If they disagree, the claim is
    REFUSED (AggregationRefused), never downgraded by guess: nothing in the contract orders
    schedule_derived against specification_default, so no 'weakest' exists to pick.

    None entries (no grade: a U contributor in the pack's convention) are ignored; a claim with no
    graded contributor returns None."""
    graded = [g for g in contributing if g is not None]
    for g in graded:
        if g not in ENVELOPE_GRADES:
            raise ProvenanceMapError(f"unknown envelope grade {g!r}")
    if not graded:
        return None
    non_explicit = {g for g in graded if g != "explicit"}
    if not non_explicit:
        return "explicit"
    if len(non_explicit) == 1:
        return non_explicit.pop()
    raise AggregationRefused(
        f"contributing grades disagree {sorted(non_explicit)}: no order is declared over the grade enum, "
        f"so the claim is refused rather than downgraded by guess (§09-1 clause 7(ii)); record as a named open item")


# --- integrity: this table and B0's must be one table -----------------------------------------------
def crosscheck_b0():
    """If the B0 substrate is importable, our domain must equal its CLASS_MAP domain and our T/U split
    must equal its evidence_state split. Returns a typed report string; raises on disagreement."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import b0_evidence_substrate_v0_1 as b0
    except ImportError:
        try:
            import b0_evidence_substrate_v0_1_1 as b0
        except ImportError:
            return "b0 substrate not importable here — domain taken as copied (verbatim, 13 Sep 2026)"
    dom = tuple(b0.CLASS_MAP.keys())
    if set(dom) != set(LINEAGE_TO_PROVENANCE):
        raise ProvenanceMapError(f"domain differs from B0 CLASS_MAP: {sorted(set(dom) ^ set(LINEAGE_TO_PROVENANCE))}")
    for cls, (state, _mech, grade) in b0.CLASS_MAP.items():
        want_located = state == "T"
        if (LINEAGE_TO_PROVENANCE[cls] is not None) != want_located:
            raise ProvenanceMapError(f"{cls}: B0 evidence_state {state} but provenance {LINEAGE_TO_PROVENANCE[cls]!r}")
        if strength_of(grade) != ("explicit" if want_located else None):
            raise ProvenanceMapError(f"{cls}: B0 grade {grade!r} projects to {strength_of(grade)!r}")
    return f"domain and T/U split cross-checked equal to {getattr(b0, 'ENGINE_VERSION', 'B0 substrate')}"


# --- totality over a real corpus: from the frozen engine's own counters ----------------------------
def totality_report(corpus_rollup_path):
    """Read corpus_rollup.json's field_lineage counters ('<field>:<CLASS>': n) and report whether every
    class the engine emitted over the corpus is in this map's domain. This is a corpus-wide statement
    made from the engine's own counters, not from a sample of records."""
    r = json.loads(Path(corpus_rollup_path).read_text(encoding="utf-8"))
    fl = r.get("field_lineage")
    if not isinstance(fl, dict) or not fl:
        raise ProvenanceMapError("corpus_rollup.json carries no field_lineage counters")
    by_class, by_field, unmapped = collections.Counter(), collections.defaultdict(dict), {}
    for k, n in fl.items():
        field, cls = k.split(":", 1)
        by_class[cls] += n
        by_field[field][cls] = n
        if cls not in LINEAGE_TO_PROVENANCE:
            unmapped[cls] = unmapped.get(cls, 0) + n
    by_prov = collections.Counter()
    for cls, n in by_class.items():
        by_prov[LINEAGE_TO_PROVENANCE.get(cls, "UNMAPPED") or "absent (U)"] += n
    fields_total = {f: sum(v.values()) for f, v in by_field.items()}
    return {
        "engine": r.get("engine"), "policy": r.get("policy"), "snapshot": r.get("snapshot"),
        "provenance_map": PROVENANCE_MAP_VERSION,
        "records": (r.get("totals") or {}).get("resolution:RESOLVED", 0) + (r.get("totals") or {}).get("resolution:PARENT_NOT_IN_SAMPLE", 0),
        "governed_fields": sorted(by_field), "field_totals_equal": len(set(fields_total.values())) == 1,
        "assignments_total": sum(by_class.values()),
        "classes_observed": dict(sorted(by_class.items(), key=lambda kv: -kv[1])),
        "classes_unmapped": unmapped,
        "map_is_total_over_corpus": not unmapped,
        "by_provenance": dict(by_prov),
    }


# --- self-test ----------------------------------------------------------------------------------------
def selftest():
    results = []
    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))
    # clause (1): the six classes, exact values
    check("ON_CHILD/CHILD_OVERRIDES/BOTH_EQUAL -> on_record",
          all(provenance_of(c) == ON_RECORD for c in ("ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL")))
    check("INHERITED -> inherited_from_parent", provenance_of("INHERITED") == INHERITED_FROM_PARENT)
    check("U classes carry no value (None)",
          provenance_of("SOURCE_ABSENT") is None and provenance_of("UNRESOLVABLE_PARENT_UNAVAILABLE") is None
          and provenance_of(None) is None and provenance_of(ABSENT_CHILD_ONLY_FIELD) is None)
    check("domain is exactly the six B0 classes", set(LINEAGE_TO_PROVENANCE) == set(_B0_CLASS_MAP_DOMAIN))
    check("located classes are exactly B0's T classes",
          {c for c, p in LINEAGE_TO_PROVENANCE.items() if p is not None} == set(_B0_T_CLASSES))
    def raises(fn, exc):
        try:
            fn()
        except exc:
            return True
        return False
    check("unknown class refused (fail-closed), not defaulted", raises(lambda: provenance_of("PARENT_WINS"), ProvenanceMapError))
    # clause (2): strength projection
    check("strength: explicit->explicit, inherited->explicit, None->None",
          strength_of("explicit") == "explicit" and strength_of("inherited") == "explicit" and strength_of(None) is None)
    check("unknown lineage grade refused", raises(lambda: strength_of("schedule_derived"), ProvenanceMapError))
    # clause 7(i)
    check("7(i): any inherited -> inherited_from_parent", claim_provenance([ON_RECORD, INHERITED_FROM_PARENT, None]) == INHERITED_FROM_PARENT)
    check("7(i): all on_record -> on_record", claim_provenance([ON_RECORD, None, ON_RECORD]) == ON_RECORD)
    check("7(i): nothing located -> None", claim_provenance([None, None]) is None and claim_provenance([]) is None)
    check("7(i): unknown value refused", raises(lambda: claim_provenance(["published"]), ProvenanceMapError))
    # clause 7(ii)
    check("7(ii): explicit only if every contributor is explicit", claim_grade(["explicit", "explicit", None]) == "explicit")
    check("7(ii): one non-explicit contributor -> claim carries it, never explicit",
          claim_grade(["explicit", "schedule_derived"]) == "schedule_derived"
          and claim_grade(["specification_default", "explicit", "explicit"]) == "specification_default")
    check("7(ii): agreeing non-explicit contributors -> that value",
          claim_grade(["schedule_derived", "schedule_derived", "explicit"]) == "schedule_derived")
    check("7(ii): DISAGREEING non-explicit contributors -> REFUSED, not a guess",
          raises(lambda: claim_grade(["schedule_derived", "specification_default", "explicit"]), AggregationRefused))
    check("7(ii): no graded contributor -> None", claim_grade([None, None]) is None)
    check("7(ii): unknown grade refused ('inherited' is not an envelope grade — clause 5)",
          raises(lambda: claim_grade(["inherited"]), ProvenanceMapError))
    # the analogy that was withdrawn: the rules are NOT 'weakest wins' — there is no order to appeal to
    check("no order is declared over the envelope grades (tuple, unordered by contract)", isinstance(ENVELOPE_GRADES, tuple) and len(set(ENVELOPE_GRADES)) == 3)
    # B0 cross-check (typed report either way; raises on disagreement)
    try:
        rep = crosscheck_b0(); check("B0 cross-check: " + rep, True)
    except ProvenanceMapError as e:
        check("B0 cross-check", False, str(e))
    width = max(len(n) for n, _, _ in results)
    for n, ok, det in results:
        print(("OK   " if ok else "FAIL ") + n.ljust(width) + ("" if ok or not det else "   <- " + det))
    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"\nSELFTEST: {n_ok}/{len(results)} checks pass — " + ("ALL PASS" if n_ok == len(results) else "STOP: failures above"))
    return 0 if n_ok == len(results) else 1


def main():
    ap = argparse.ArgumentParser(description="§09-1 provenance map: self-test, or totality check over a corpus_rollup.json")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--corpus-check", metavar="corpus_rollup.json")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.corpus_check:
        rep = totality_report(a.corpus_check)
        print(json.dumps(rep, indent=1))
        sys.exit(0 if rep["map_is_total_over_corpus"] else 13)
    ap.error("--selftest or --corpus-check required")


if __name__ == "__main__":
    main()
