#!/usr/bin/env python3
"""
Validate the action-card workflow (WP §8.5): no step may skip independent review or approval, and
sending requires an authorised role.

AI-ASSISTED SCAFFOLD. NOT authorship evidence; Section 18 owner + partner route confirm it.

Run:  python validate_action_cards.py     # exit 0 iff the workflow enforces the gates
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.join(HERE, "action-card-state-machine.json")


def main():
    m = json.load(open(SM))
    states = set(m["canonical_states"]) | set(m["side_states"])
    trans = m["transitions"]
    errs = []

    # every canonical state present in the linear spine
    for s in ["observed", "investigated", "drafted", "independently_reviewed",
              "approved_for_route", "sent_by_authorised_role", "monitored", "closed_or_withdrawn"]:
        if s not in states:
            errs.append(f"missing canonical state: {s}")

    # transitions reference defined states
    for t in trans:
        if t["from"] not in states:
            errs.append(f"transition from undefined state {t['from']}")
        if t["to"] not in states:
            errs.append(f"transition to undefined state {t['to']}")

    incoming = {}
    for t in trans:
        incoming.setdefault(t["to"], []).append(t)

    # GATE 1: every transition INTO approved_for_route must come from independently_reviewed
    for t in incoming.get("approved_for_route", []):
        if t["from"] not in ("independently_reviewed", "hold"):
            errs.append(f"approval reached from '{t['from']}' — must pass independently_reviewed (no-skip)")
    if not any(t["from"] == "independently_reviewed" for t in incoming.get("approved_for_route", [])):
        errs.append("no path independently_reviewed -> approved_for_route")

    # GATE 2: the review transition and the approval transition require non-author review
    for t in trans:
        if t["to"] == "independently_reviewed" and t["from"] == "drafted" and not t.get("requires_non_author_review"):
            errs.append("drafted -> independently_reviewed must set requires_non_author_review")
        if t["from"] == "independently_reviewed" and t["to"] == "approved_for_route" and not t.get("requires_non_author_review"):
            errs.append("independently_reviewed -> approved_for_route must set requires_non_author_review")

    # GATE 3: every transition INTO sent must come from approved_for_route AND require an authorised role
    for t in incoming.get("sent_by_authorised_role", []):
        if t["from"] != "approved_for_route":
            errs.append(f"send reached from '{t['from']}' — must be approved_for_route first")
        if not t.get("requires_authorised_role"):
            errs.append("send transition must set requires_authorised_role")

    # GATE 4: no direct skip edges (drafted/investigated/observed -> approved/sent)
    SKIP = {("drafted", "approved_for_route"), ("drafted", "sent_by_authorised_role"),
            ("investigated", "approved_for_route"), ("investigated", "sent_by_authorised_role"),
            ("observed", "sent_by_authorised_role")}
    for t in trans:
        if (t["from"], t["to"]) in SKIP:
            errs.append(f"illegal skip transition {t['from']} -> {t['to']}")

    # GATE 5: correction token only creates 'observed' and cannot mutate/contact
    ct = m.get("correction_token", {})
    if ct.get("creates") != "observed":
        errs.append("correction_token must only create 'observed'")
    if ct.get("may_mutate_evidence") or ct.get("may_contact_publisher"):
        errs.append("correction_token must not mutate evidence or contact a publisher")

    if errs:
        print("ACTION-CARD WORKFLOW INVALID:")
        for e in errs:
            print("  -", e)
        return 1
    print("ACTION-CARD WORKFLOW OK: independent review + approval + authorised-role gates enforced; no skip paths.")
    print(f"  canonical states: {len(m['canonical_states'])}, side states: {len(m['side_states'])}, transitions: {len(trans)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
