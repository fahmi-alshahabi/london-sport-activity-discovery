#!/usr/bin/env python3
"""Envelope assembly for the D4 seam — Clarence's side of the handoff.

Takes what Wesley's d4_handoff.py emits (candidates in $defs/candidate shape, why_not entries,
and his coverage statement) and assembles a complete DecisionEnvelope: the twelve required
top-level fields, the metadata blocks, and the digest.

WHAT THIS IS
    An executable demonstration that the specified seam closes. It assembles against the
    PROPOSED v0.2 schema, validates, computes the digest by the identical canonical form
    INV-REPLAY uses, and runs the invariant battery over the result.

WHAT THIS IS NOT
    An execution of §09-1. It does not modify decision-envelope.schema.json (still
    0.1.0-PROPOSED), does not touch disclosure-classes.json, and does not re-seal any fixture.
    The frozen contract and its eleven sealed fixtures are untouched and still pass.

    Executing §09-1 remains scheduled post-submission by the ratification record of 13 Sep and
    gated on RATIFY-14-02 — the non-author HCI/content reviewer is still unnamed (CL-2, CL-4,
    CL-10 all read name: null), so `provenance` has no approved user-facing wording and a valid
    envelope carrying it still cannot render that field.

Run:  python3 assemble_envelope_v0_2.py
"""
from __future__ import annotations
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import projection_and_invariants as P          # the frozen projector — reused, not reimplemented

FROZEN   = os.path.join(HERE, "decision-envelope.schema.json")
PROPOSED = os.path.join(HERE, "PROPOSED-decision-envelope.v0.2.schema.json")

# Wesley's verdict vocabulary -> the slate rule (Michael's generator, lineage_pack_v0_1 l.400)
def terminal_from_verdicts(verdicts):
    if not verdicts:                              return "no_candidates"
    if "supported_match" in verdicts:             return "supported_match"
    if "evidence_indeterminate" in verdicts:      return "evidence_indeterminate"
    return "bounded_non_match"

_ACTION = {
    "supported_match":        "authorised_slate",
    "evidence_indeterminate": "model_abstained",
    "bounded_non_match":      "deterministic_fallback",
    "no_candidates":          "deterministic_fallback",
}


def assemble(candidates, why_not, coverage_statement, verdicts, identity, versions,
             scope_qualifier="scope_complete", acquisition_complete=True, unevaluated_feeds=0):
    """Assemble the envelope. `candidates` and `why_not` arrive in Wesley's emitted shape."""
    terminal = terminal_from_verdicts(verdicts)

    # predicates[] is the union of the constrained predicates across the slate, deduplicated by id.
    seen, predicates = set(), []
    for c in candidates:
        for a in c.get("attributes") or []:
            if a["predicate_id"] not in seen:
                seen.add(a["predicate_id"]); predicates.append(copy.deepcopy(a))

    decision = {
        "contract":             "DecisionEnvelope",
        "schema_version":       "0.2.0-PROPOSED",
        "identity":             identity,
        "versions":             versions,
        "terminal_decision":    terminal,
        "scope_qualifier":      scope_qualifier,
        "coverage_qualifier":   {"acquisition_complete": acquisition_complete,
                                 "statement": coverage_statement,
                                 "unevaluated_feeds": unevaluated_feeds},
        "recommendation_action": _ACTION[terminal],
        "predicates":           predicates,
        "candidates":           candidates,
        "claims":               [],
    }
    if why_not:
        decision["why_not"] = why_not

    env = {"action_kind": "discovery_decision",   # decision_of() gates on this exact value
           "header": {"release_maturity_class": "research_demonstration"},
           "payload": {"decision": decision}}

    # Digest: identical canonical form to INV-REPLAY — project to public, drop the digest key,
    # sha over the remainder. Computed on the PUBLIC projection, which is what is retained.
    fields, planes = P.load_classes()
    pub = P.project(env, fields, set(planes["public"]))
    pd = copy.deepcopy(pub["payload"]["decision"]); pd.pop("digest", None)
    decision["digest"] = P.sha(pd)
    return env


# ------------------------------------------------------------------ demonstration
def _demo_input():
    """Representative of what d4_handoff.build_candidates returns for an activity query.
       Provenance is mixed on purpose: activity is 58.8% inherited where present (Wesley,
       15 Sep), so a real activity-query slate carries both loci."""
    def pred(pid, state, grade, prov=None, mech=None):
        p = {"predicate_id": pid, "evidence_state": state, "grade": grade}
        if mech:  p["mechanism"] = mech
        if prov:  p["provenance"] = prov
        return p
    candidates = [
        {"candidate_id": "https://better-admin.org.uk/api/openactive/better/scheduled-sessions/activity:89760737",
         "rank": 1, "pool": "supported",
         "attributes": [pred("activity", "T", "explicit", "inherited_from_parent"),
                        pred("startDate", "T", "explicit", "on_record"),
                        pred("offers", "U", "specification_default", mech="source_absence")]},
        {"candidate_id": "https://better-admin.org.uk/api/openactive/better/scheduled-sessions/activity:89760738",
         "rank": 2, "pool": "supported",
         "attributes": [pred("activity", "T", "explicit", "on_record"),
                        pred("startDate", "T", "explicit", "on_record"),
                        pred("offers", "U", "specification_default", mech="source_absence")]},
    ]
    why_not = [{"predicate_id": "location", "blocking_state": "F",
                "relaxation_suggestion": "Widen the area or try a different activity."}]
    return candidates, why_not, ["supported_match", "supported_match"]


def _cases():
    """Three terminal states, so every gate is exercised somewhere. A single supported_match
       leaves INV-COVERAGE permanently n/a, which is not a pass — it is an untested gate."""
    cands, why_not, _ = _demo_input()
    return [("supported_match",        cands,  [],      ["supported_match", "supported_match"]),
            ("bounded_non_match",      [],     why_not, ["bounded_non_match"]),
            ("evidence_indeterminate", [],     why_not, ["evidence_indeterminate"])]


def main():
    candidates, why_not, verdicts = _demo_input()
    coverage = ("Of the 5 candidates retrieved from a corpus of 724,361 searchable records "
                "(737,227 total, 33 providers, no provider skipped), none outside the returned "
                "slate was evaluated. A bounded non-match means no retrieved candidate satisfied "
                "the constraints, not that no matching activity exists.")
    identity = {"episode_id": "ep-d4-001", "turn_id": 1,
                "request_id": "req-d4-001", "trace_id": "trace-d4-001"}
    versions = {"corpus_version": "V2026-08-27-DEV", "interpretation_version": "interp-1.2",
                "verifier_version": "ver-1.0", "vintage": "2026-08-27"}

    env = assemble(candidates, why_not, coverage, verdicts, identity, versions)
    d = env["payload"]["decision"]

    print("== assembled envelope ==")
    for k in ("contract", "schema_version", "terminal_decision", "scope_qualifier",
              "recommendation_action"):
        print(f"   {k:22}: {d[k]}")
    print(f"   {'candidates':22}: {len(d['candidates'])}  predicates: {len(d['predicates'])}"
          f"  why_not: {len(d.get('why_not') or [])}")
    print(f"   {'digest':22}: {d['digest']}")
    print(f"   provenance loci carried: "
          f"{sorted({a.get('provenance') for c in d['candidates'] for a in c['attributes'] if a.get('provenance')})}")

    print("\n== schema validation ==")
    try:
        import jsonschema
        for label, path in (("frozen  v0.1", FROZEN), ("proposed v0.2", PROPOSED)):
            s = json.load(open(path))
            errs = list(jsonschema.Draft202012Validator(s).iter_errors(d))
            verdict = "VALID" if not errs else f"{len(errs)} error(s): {errs[0].message[:72]}"
            print(f"   {label}: {verdict}")
        print("   (v0.1 rejecting it is CORRECT — the frozen contract has no provenance leaf)")
    except ImportError:
        print("   jsonschema unavailable")

    print("\n== invariant battery over the assembled envelope ==")
    fields, planes = P.load_classes()
    results = {n: fn(env, fields, planes) for n, fn in P.INVARIANTS}
    for n, (ok, detail) in results.items():
        print(f"   [{'OK ' if ok else 'BAD'}] {n:22} {detail[:60]}")
    # Every gate must be exercised by at least one terminal state — a gate that is n/a in all
    # cases has tested nothing. (First run of this script printed "all invariants hold" with six
    # of eight n/a, because action_kind was wrong and decision_of() returned None.)
    print("\n== all three terminal states, so every gate fires somewhere ==")
    fired = {n: False for n, _ in P.INVARIANTS}
    for label, cs, wn, vs in _cases():
        e = assemble(cs, wn, coverage, vs, identity, versions)
        r = {n: fn(e, fields, planes) for n, fn in P.INVARIANTS}
        bad = [n for n, (ok, _) in r.items() if not ok]
        for n, (_, det) in r.items():
            if "n/a" not in det: fired[n] = True
        print(f"   {label:24} -> {'all hold' if not bad else 'FAILED: ' + ','.join(bad)}")
    never = [n for n, f in fired.items() if not f]
    print(f"   gates exercised: {sum(fired.values())}/8"
          + (f"   NEVER FIRED: {', '.join(never)}" if never else ""))

    failed = [n for n, (ok, _) in results.items() if not ok] + never
    # A battery that reports n/a on most gates has not tested anything. The first run of this
    # script printed "all invariants hold" while six of eight were n/a because action_kind was
    # wrong and decision_of() returned None. Refuse that outcome rather than report it as a pass.
    print(f"\nRESULT: {'all 8 invariants exercised and hold' if not failed else 'FAILED: ' + ', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
