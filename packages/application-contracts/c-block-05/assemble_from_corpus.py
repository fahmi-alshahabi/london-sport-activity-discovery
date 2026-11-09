#!/usr/bin/env python3
"""Assemble a DecisionEnvelope from REAL corpus records — reproducible on your machine.

Reads records straight out of Wesley's corpus zip, gates them with Michael's real reducer, and
assembles the envelope with assemble_envelope_v0_2.assemble(). Validates against both schemas and
runs the full invariant battery.

USAGE
    python3 assemble_from_corpus.py <corpus.zip> [--provider Oxford_University] [--match "bike doctor"]
                                    [--n 8] [--out envelope.json]

    e.g.  python3 assemble_from_corpus.py ~/Downloads/WESLEY_S1_CORPUS_V2026-08-27_20260911.zip

REQUIREMENTS
    reducer_v0_1_1.py must be importable — put Michael's copy (sha 2d543be3…, 7,348 B) beside this
    file, or pass its folder on PYTHONPATH.

STAND-IN, DECLARED
    Michael's provenance_map.py was never delivered to this stream. The lineage -> provenance and
    lineage -> grade mappings below are implemented from the target spec §5 and are MINE, not his.
    The records, the lineage classes and the reducer are real. If his module arrives, delete the
    two functions and import his — the output should be identical, and if it is not, that is a
    finding worth recording.

NOT an execution of §09-1. Writes nothing into the frozen contract, touches no fixture.
"""
from __future__ import annotations
import argparse, io, json, os, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import projection_and_invariants as P
import assemble_envelope_v0_2 as A

try:
    from reducer_v0_1_1 import reduce_decision, match_text
except ImportError:
    sys.exit("reducer_v0_1_1.py not importable — put Michael's copy beside this file (see docstring).")

# ---- STAND-IN for Michael's provenance_map (target spec §5) -------------------
_ON_RECORD = {"ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL"}
_T_CLASSES = _ON_RECORD | {"INHERITED"}

def provenance_of(cls):
    if cls in _ON_RECORD:  return "on_record"
    if cls == "INHERITED": return "inherited_from_parent"
    return None                                   # U states carry no locus

def strength_of(cls):
    return "explicit" if cls in _T_CLASSES else "specification_default"
# ------------------------------------------------------------------------------


def build_predicate(record, field):
    row = (record.get("lineage") or {}).get(field)
    cls = row.get("class") if isinstance(row, dict) else None
    state = "T" if cls in _T_CLASSES else "U"
    p = {"predicate_id": field, "evidence_state": state, "grade": strength_of(cls)}
    if state == "U":
        p["mechanism"] = "source_absence"
    prov = provenance_of(cls)
    if prov and state in ("T", "F"):
        p["provenance"] = prov
    return p


def load_records(zip_path, provider, n):
    z = zipfile.ZipFile(zip_path)
    name = f"{provider}/s1_records.jsonl"
    if name not in z.namelist():
        opts = sorted({e.split("/")[0] for e in z.namelist() if e.endswith("s1_records.jsonl")})
        sys.exit(f"provider {provider!r} not in the zip. Available: {', '.join(opts[:12])} ...")
    out = []
    with z.open(name) as fh:
        for i, line in enumerate(io.TextIOWrapper(fh, "utf8")):
            if i >= n: break
            out.append(json.loads(line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("--provider", default="Oxford_University")
    ap.add_argument("--match", default="bike doctor", help="substring matched against the name field")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    records = load_records(a.zip, a.provider, a.n)
    print(f"== {len(records)} real records from {a.provider} ==")

    constraints = [("name", match_text(a.match)), ("startDate", lambda v: True)]
    cands, verdicts, why_not, rank = [], [], [], 0
    seen_blockers = set()
    for rec in records:
        decision, detail = reduce_decision(rec, constraints)
        verdicts.append(decision)
        if decision == "bounded_non_match":
            for field, v in detail.items():
                if v == "T:unsatisfied" and field not in seen_blockers:   # dedupe
                    seen_blockers.add(field)
                    why_not.append({"predicate_id": field, "blocking_state": "F",
                                    "relaxation_suggestion": f"Try a different {field}, or widen the search."})
            continue
        rank += 1
        cands.append({
            "candidate_id": rec["@id"], "rank": rank,
            "pool": {"supported_match": "supported",
                     "evidence_indeterminate": "indeterminate"}[decision],
            "attributes": [build_predicate(rec, f) for f, _ in constraints],
        })

    counts = {v: verdicts.count(v) for v in sorted(set(verdicts))}
    print(f"   verdicts   : {counts}")
    print(f"   candidates : {len(cands)}   why_not: {len(why_not)}")

    coverage = (f"Of {len(records)} records gated from {a.provider} in corpus V2026-08-27, none "
                f"outside this set was evaluated. A bounded non-match means no gated candidate "
                f"satisfied the constraints, not that no matching activity exists.")
    env = A.assemble(cands, why_not, coverage, verdicts,
                     {"episode_id": "ep-corpus-001", "turn_id": 1,
                      "request_id": "req-corpus-001", "trace_id": "tr-corpus-001"},
                     {"corpus_version": "V2026-08-27-DEV", "interpretation_version": "interp-1.2",
                      "verifier_version": "ver-1.0", "vintage": "2026-08-27"})
    d = env["payload"]["decision"]

    print(f"\n   terminal   : {d['terminal_decision']}   action: {d['recommendation_action']}")
    print(f"   digest     : {d['digest']}")
    loci = sorted({x.get("provenance") for c in d["candidates"] for x in c["attributes"]
                   if x.get("provenance")})
    print(f"   provenance : {loci}")
    if d["candidates"]:
        print(f"   rank 1     : {d['candidates'][0]['candidate_id']}")

    print("\n== schema validation ==")
    try:
        import jsonschema
        for label, path in (("frozen  v0.1", A.FROZEN), ("proposed v0.2", A.PROPOSED)):
            errs = list(jsonschema.Draft202012Validator(json.load(open(path))).iter_errors(d))
            print(f"   {label}: {'VALID' if not errs else str(len(errs)) + ' error(s): ' + errs[0].message[:60]}")
    except ImportError:
        print("   jsonschema unavailable — pip install jsonschema --break-system-packages")

    print("\n== invariants ==")
    fields, planes = P.load_classes()
    res = {n: fn(env, fields, planes) for n, fn in P.INVARIANTS}
    for n, (ok, det) in res.items():
        print(f"   [{'OK ' if ok else 'BAD'}] {n:22} {det[:54]}")
    bad = [n for n, (ok, _) in res.items() if not ok]

    out = a.out or os.path.join(HERE, "envelope_from_corpus.json")
    json.dump(env, open(out, "w"), indent=2)
    print(f"\n   written: {out}")
    print("RESULT:", "all invariants hold" if not bad else "FAILED: " + ", ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
