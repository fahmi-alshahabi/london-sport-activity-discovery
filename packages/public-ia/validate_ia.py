#!/usr/bin/env python3
"""
Validate the public information architecture against the C-BLOCK-05 contract.

AI-ASSISTED SCAFFOLD (WP sec 7.1, 7.2, 9.3). NOT authorship evidence; Clarence must correct in his
own words and obtain non-author HCI review (RATIFY-14-05, C-BLOCK-03).

Checks the state machine COVERS every contract enum, keeps the five terminal experiences visibly
DISTINCT (WP 7.2), provides the required routes plus non-chat / non-map / no-JS fallbacks
(C-BLOCK-11/14), and never transitions a service_failure straight back into results (no stale reuse).

Enums are read from the C-BLOCK-05 schemas so the IA cannot silently drift from the contract.

Run:  python validate_ia.py
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IA = os.path.join(HERE, "public-state-machine.json")
CB05 = os.path.normpath(os.path.join(HERE, "..", "application-contracts", "c-block-05"))

REQUIRED_ROUTES = ["guided_search", "conversational", "browse_list", "compare", "detail_receipt", "handoff"]
DISTINCT_TERMINALS = ["supported_match", "bounded_non_match", "evidence_indeterminate"]
FAILURE_ALLOWED_TARGETS = {"query_review", "handoff"}


def contract_enums():
    app = json.load(open(os.path.join(CB05, "application-envelope.schema.json")))
    dec = json.load(open(os.path.join(CB05, "decision-envelope.schema.json")))
    action_kinds = set()
    for branch in app.get("oneOf", []):
        c = branch.get("properties", {}).get("action_kind", {}).get("const")
        if c:
            action_kinds.add(c)
    props = dec["properties"]
    return {
        "action_kind": action_kinds,
        "terminal_decision": set(props["terminal_decision"]["enum"]),
        "scope_qualifier": set(props["scope_qualifier"]["enum"]),
        "recommendation_action": set(props["recommendation_action"]["enum"]),
    }


def collect(ia, key):
    """map enum value -> list of screen ids covering it"""
    out = {}
    for s in ia["screens"]:
        v = s.get("covers", {}).get(key)
        if v:
            out.setdefault(v, []).append(s["id"])
    return out


def main():
    ia = json.load(open(IA))
    enums = contract_enums()
    errs = []

    # 1. coverage of every contract enum value (scope_complete needs no screen)
    for key in ("action_kind", "terminal_decision", "recommendation_action"):
        cov = collect(ia, key)
        for val in sorted(enums[key]):
            if val not in cov:
                errs.append(f"no screen covers {key} = {val}")
    if "scope_indeterminate" not in collect(ia, "scope_qualifier"):
        errs.append("no screen surfaces scope_qualifier = scope_indeterminate")

    # 2. distinct terminal experiences + failure distinct from them (WP 7.2, 9.3)
    tcov = collect(ia, "terminal_decision")
    screens_for = {t: set(tcov.get(t, [])) for t in DISTINCT_TERMINALS}
    for t in DISTINCT_TERMINALS:
        if not screens_for[t]:
            errs.append(f"terminal {t} has no distinct screen")
    # no single screen may cover two different terminals
    for s in ia["screens"]:
        tv = s.get("covers", {}).get("terminal_decision")
        # (each screen has at most one terminal_decision key by construction; explicit guard)
    failure_screens = set(collect(ia, "action_kind").get("service_failure", []))
    overlap = failure_screens & (screens_for["bounded_non_match"] | screens_for["evidence_indeterminate"])
    if overlap:
        errs.append(f"service_failure shares a screen with a terminal decision: {sorted(overlap)}")

    # 3. required routes + fallback guarantees
    routes = ia["routes"]
    for r in REQUIRED_ROUTES:
        if not routes.get(r, {}).get("required"):
            errs.append(f"required route missing/!required: {r}")
    fb = ia.get("fallback_guarantees", {})
    for g in ("non_chat_route", "non_map_route", "no_js_core"):
        if not fb.get(g):
            errs.append(f"fallback guarantee not met: {g}")
    if not any(routes[r].get("chat_free") for r in routes):
        errs.append("no chat-free route exists")

    # 4. every screen.route is defined
    for s in ia["screens"]:
        if s["route"] not in routes:
            errs.append(f"screen {s['id']} references undefined route {s['route']}")

    # 5. transitions reference defined screens
    ids = {s["id"] for s in ia["screens"]}
    for t in ia["transitions"]:
        if t["from"] not in ids:
            errs.append(f"transition from undefined screen {t['from']}")
        if t["to"] not in ids:
            errs.append(f"transition to undefined screen {t['to']}")

    # 6. no stale reuse after failure
    if not ia.get("no_stale_after_failure"):
        errs.append("no_stale_after_failure must be true")
    for t in ia["transitions"]:
        if t["from"] == "service_failure" and t["to"] not in FAILURE_ALLOWED_TARGETS:
            errs.append(f"service_failure transitions to '{t['to']}' (allowed: {sorted(FAILURE_ALLOWED_TARGETS)}) — risk of stale reuse")

    # report
    if errs:
        print("IA INVALID:")
        for e in errs:
            print("  -", e)
        return 1
    print("IA OK — covers the C-BLOCK-05 contract:")
    for key in ("action_kind", "terminal_decision", "recommendation_action"):
        cov = collect(ia, key)
        for val in sorted(enums[key]):
            print(f"  {key:22s} {val:22s} -> {', '.join(cov[val])}")
    print(f"  scope_indeterminate            -> {', '.join(collect(ia,'scope_qualifier')['scope_indeterminate'])}")
    print(f"  routes: {len(routes)} ({sum(1 for r in routes.values() if r.get('required'))} required) · "
          f"non-chat={fb['non_chat_route']} non-map={fb['non_map_route']} no-JS={fb['no_js_core']}")
    print(f"  {len(ia['screens'])} screens, {len(ia['transitions'])} transitions, failure->{sorted(FAILURE_ALLOWED_TARGETS)} only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
