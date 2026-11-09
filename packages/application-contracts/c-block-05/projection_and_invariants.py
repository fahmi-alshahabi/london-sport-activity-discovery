#!/usr/bin/env python3
"""
C-BLOCK-05 reference projector + executable release-blocking invariants.

AI-ASSISTED SCAFFOLD prepared from CLARENCE_ZHEN_JIN_TAN_SPECIALISED_WORK_PACKAGE.md
(sections 4.2, 4.3, 15.1, 15.2, 15.6) and its review (CA-1, CA-3). This is NOT evidence
that Clarence authored, read or accepted it. He must inspect it, correct it in his own
words, replace placeholders, and obtain non-author review (he cannot certify his own
contracts, WP 2.6).

Purpose: make the C-BLOCK-09 / CA-1 gates EXECUTABLE rather than aspirational. Given a
STAFF-COMPLETE ApplicationEnvelope, this module derives the public / staff / research
projections purely from the disclosure-class map (fail-closed), and checks the invariants
that must hold before any UI is built on top.

Stdlib only. Usage:
    python projection_and_invariants.py --seal fixtures/valid/<f>.json   # fill correct digest
    python projection_and_invariants.py                                  # run the battery
"""
from __future__ import annotations
import copy, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES_PATH = os.path.join(HERE, "disclosure-classes.json")
FIXTURES = os.path.join(HERE, "fixtures")

# ---- fixtures: expected outcome so the battery is self-checking -------------
# valid  -> every applicable invariant must PASS
# adversarial -> the named invariant must FAIL (i.e. detection works)
EXPECTATIONS = {
    "valid/discovery_supported.json":        ("valid", None),
    "valid/service_failure.json":            ("valid", None),
    "adversarial/unknown_rendered_as_no.json":   ("adversarial", "INV-NO-COLLAPSE"),
    "adversarial/staff_note_in_public.json":     ("adversarial", "INV-DISCLOSURE"),
    "adversarial/dropped_scope_qualifier.json":  ("adversarial", "INV-COVERAGE"),
    "adversarial/unverified_claim_present.json": ("adversarial", "INV-NO-UNVERIFIED"),
    "adversarial/client_sort_reorder.json":      ("adversarial", "INV-SLATE-ORDER"),
    "adversarial/tampered_public_digest.json":   ("adversarial", "INV-REPLAY"),
}

STAFF_SIGNATURES = re.compile(
    r"(lineage|receipt|superEvent|STAFF:|"
    r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b)"  # UK postcode
)

# ---------------------------------------------------------------------------
def load_classes():
    with open(CLASSES_PATH) as fh:
        c = json.load(fh)
    return c["fields"], c["planes"]

def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

DROP = object()

def project(node, fields, allowed, path=""):
    """Fail-closed projection: a leaf survives only if its declared class is allowed;
    an unlisted leaf is dropped from every plane."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            cp = f"{path}.{k}" if path else k
            pv = project(v, fields, allowed, cp)
            if pv is not DROP:
                out[k] = pv
        return out if out else DROP
    if isinstance(node, list):
        cp = f"{path}[]"
        out = []
        for item in node:
            pv = project(item, fields, allowed, cp)
            if pv is not DROP:
                out.append(pv)
        return out if out else DROP
    # leaf
    cls = fields.get(path)
    if cls is not None and cls in allowed:
        return node
    return DROP

def walk_leaves(node, fields, path=""):
    """Yield (parent, key, path, cls) for every scalar leaf, so callers can mutate."""
    if isinstance(node, dict):
        for k, v in list(node.items()):
            cp = f"{path}.{k}" if path else k
            if isinstance(v, (dict, list)):
                yield from walk_leaves(v, fields, cp)
            else:
                yield (node, k, cp, fields.get(cp))
    elif isinstance(node, list):
        cp = f"{path}[]"
        for item in node:
            if isinstance(item, (dict, list)):
                yield from walk_leaves(item, fields, cp)
            # scalars inside arrays are addressed at cp; mutation of those is not needed here

def decision_of(env):
    if env.get("action_kind") != "discovery_decision":
        return None
    return env.get("payload", {}).get("decision")

# ---- invariants -----------------------------------------------------------
def inv_disclosure(env, fields, planes):
    pub = project(env, fields, set(planes["public"]))
    if pub is DROP:
        pub = {}
    bad = []
    def scan(n, p=""):
        if isinstance(n, dict):
            for k, v in n.items():
                scan(v, f"{p}.{k}" if p else k)
        elif isinstance(n, list):
            for it in n:
                scan(it, f"{p}[]")
        elif isinstance(n, str) and not p.endswith("digest"):
            if STAFF_SIGNATURES.search(n):
                bad.append((p, n))
    scan(pub)
    return (not bad, f"staff signatures leaked into public plane: {bad}" if bad else "public plane clean")

def inv_noninterference(env, fields, planes):
    pub_allowed = set(planes["public"])
    base_pub = project(env, fields, pub_allowed)
    mutated = copy.deepcopy(env)
    changed = 0
    for parent, key, p, cls in walk_leaves(mutated, fields):
        if cls != "PUBLIC_SAFE":  # includes unlisted (None) and all staff/research
            v = parent[key]
            if isinstance(v, bool):
                parent[key] = not v
            elif isinstance(v, (int, float)):
                parent[key] = v + 1
            elif isinstance(v, str):
                parent[key] = v + "_MUTATED"
            else:
                parent[key] = "MUTATED"
            changed += 1
    mut_pub = project(mutated, fields, pub_allowed)
    ok = canonical(base_pub) == canonical(mut_pub)
    return (ok, f"public projection stable after mutating {changed} non-public leaves"
                if ok else "MUTATING non-public fields changed the public projection")

def inv_symmetry(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    pub = project(env, fields, set(planes["public"]))
    stf = project(env, fields, set(planes["staff"]))
    pd, sd = pub["payload"]["decision"], stf["payload"]["decision"]
    checks = {
        "terminal_decision": pd.get("terminal_decision") == sd.get("terminal_decision"),
        "scope_qualifier": pd.get("scope_qualifier") == sd.get("scope_qualifier"),
        "recommendation_action": pd.get("recommendation_action") == sd.get("recommendation_action"),
        "coverage_statement": pd.get("coverage_qualifier", {}).get("statement") == sd.get("coverage_qualifier", {}).get("statement"),
        "candidate_order": [(c["candidate_id"], c["rank"]) for c in pd.get("candidates", [])]
                            == [(c["candidate_id"], c["rank"]) for c in sd.get("candidates", [])],
        "vintage": pd.get("versions", {}).get("vintage") == sd.get("versions", {}).get("vintage"),
    }
    bad = [k for k, ok in checks.items() if not ok]
    return (not bad, "public/staff agree on shared decision fields" if not bad else f"asymmetry: {bad}")

def inv_replay(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    pub = project(env, fields, set(planes["public"]))
    pd = copy.deepcopy(pub["payload"]["decision"])
    stored = pd.pop("digest", None)
    recomputed = sha(pd)
    ok = stored == recomputed
    return (ok, "retained public payload digest replays" if ok
                else f"digest mismatch: stored={stored} recomputed={recomputed}")

def inv_no_unverified(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    leftover = [ (c.get("subject"), c.get("predicate")) for c in d.get("claims", [])
                 if c.get("verification") != "verified" ]
    return (not leftover, "only verified claims in renderable set"
                if not leftover else f"non-verified claims present in renderable claims[]: {leftover}")

def inv_no_collapse(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    # build predicate id -> state across top-level and candidate attributes
    states = {}
    for p in d.get("predicates", []):
        states[p["predicate_id"]] = p["evidence_state"]
    for c in d.get("candidates", []):
        for a in c.get("attributes", []):
            states[a["predicate_id"]] = a["evidence_state"]
    violations = []
    for cl in d.get("claims", []):
        if cl.get("claim_type") == "listing_attribute":
            st = states.get(cl.get("predicate"))
            if st in ("U", "B"):
                violations.append((cl.get("predicate"), st, cl.get("value")))
    return (not violations, "no definite claim over an U/B predicate"
                if not violations else f"COLLAPSE: definite listing_attribute claims over U/B predicates: {violations}")

def inv_coverage(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    if d.get("terminal_decision") == "bounded_non_match":
        stmt = d.get("coverage_qualifier", {}).get("statement")
        return (bool(stmt), "bounded_non_match carries coverage qualifier" if stmt
                    else "bounded_non_match WITHOUT coverage qualifier")
    return (True, "n/a (not a bounded_non_match)")

def inv_slate_order(env, fields, planes):
    d = decision_of(env)
    if d is None:
        return (True, "n/a (no decision)")
    cands = d.get("candidates", [])
    ranks = [c["rank"] for c in cands]
    order_ok = ranks == sorted(ranks) and ranks == list(range(1, len(ranks) + 1)) if cands else True
    if d.get("recommendation_action") == "authorised_slate":
        pools_ok = all(c["pool"] == "supported" for c in cands)
    else:
        pools_ok = True
    ok = order_ok and pools_ok
    return (ok, "certified order preserved; slate pools consistent" if ok
                else f"slate/order defect: array-order!=rank ({ranks}) or non-supported item in authorised_slate")

INVARIANTS = [
    ("INV-DISCLOSURE", inv_disclosure),
    ("INV-NONINTERFERENCE", inv_noninterference),
    ("INV-SYMMETRY", inv_symmetry),
    ("INV-REPLAY", inv_replay),
    ("INV-NO-UNVERIFIED", inv_no_unverified),
    ("INV-NO-COLLAPSE", inv_no_collapse),
    ("INV-COVERAGE", inv_coverage),
    ("INV-SLATE-ORDER", inv_slate_order),
]

# ---------------------------------------------------------------------------
def seal(path, fields, planes):
    with open(path) as fh:
        env = json.load(fh)
    d = decision_of(env)
    if d is None:
        print(f"  (no decision to seal in {path})"); return
    pub = project(env, fields, set(planes["public"]))
    pd = copy.deepcopy(pub["payload"]["decision"]); pd.pop("digest", None)
    env["payload"]["decision"]["digest"] = sha(pd)
    with open(path, "w") as fh:
        json.dump(env, fh, indent=2); fh.write("\n")
    print(f"  sealed {os.path.relpath(path, HERE)} -> {env['payload']['decision']['digest']}")

def run():
    fields, planes = load_classes()
    all_ok = True
    for rel, (kind, target) in EXPECTATIONS.items():
        fpath = os.path.join(FIXTURES, rel)
        if not os.path.exists(fpath):
            print(f"MISSING FIXTURE {rel}"); all_ok = False; continue
        with open(fpath) as fh:
            env = json.load(fh)
        results = {name: fn(env, fields, planes) for name, fn in INVARIANTS}
        failed = [n for n, (ok, _) in results.items() if not ok]
        if kind == "valid":
            ok = not failed
            verdict = "PASS" if ok else "UNEXPECTED FAIL: " + ", ".join(failed)
        else:
            ok = target in failed
            verdict = f"DETECTED {target}" if ok else f"MISSED {target} (failed={failed})"
        all_ok = all_ok and ok
        print(f"[{ 'OK ' if ok else 'BAD'}] {rel:44s} {verdict}")
        for n in (failed if kind == "valid" else [target]):
            if n and n in results:
                print(f"        - {n}: {results[n][1]}")
    print("\nRESULT:", "ALL EXPECTATIONS MET" if all_ok else "EXPECTATIONS NOT MET")
    return 0 if all_ok else 1

if __name__ == "__main__":
    fields, planes = load_classes()
    if len(sys.argv) >= 3 and sys.argv[1] == "--seal":
        for p in sys.argv[2:]:
            seal(p if os.path.isabs(p) else os.path.join(HERE, p), fields, planes)
    else:
        sys.exit(run())
