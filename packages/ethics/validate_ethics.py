#!/usr/bin/env python3
"""
C-15 ethics / responsible-AI validator (WP §12.2/§12.3/§12.6/§12.7/§12.9/§12.10).

AI-ASSISTED SCAFFOLD. NOT authorship evidence; the Bristol PGT ethics route decides (RATIFY-15-03).

Checks:
  1. every activity has a default position, a gate and a fallback (no orphan activity);
  2. every human-participant activity REQUIRES an ethics route, and a global no-study fallback exists;
  3. the prohibited-use register covers the required WP §12.3 categories;
  4. maturity states are exactly the canonical four and declared non-compensatory;
  5. responsible-AI interaction requirements and intended-use are present.

Run:  python validate_ethics.py
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, "ethics-activity-matrix.json")))

CANONICAL_MATURITY = ["research_demonstration", "public_safe_demonstration", "staff_shadow_mode", "controlled_partner_pilot"]
REQUIRED_PROHIBITIONS = [
    ["clinical", "diagnosis"], ["eligibility"], ["booking", "payment", "referral"],
    ["sensitive"], ["profiling"], ["surveillance"], ["league table"],
    ["automatic acceptance"], ["reuse"],
]


def main():
    errs = []

    acts = M.get("activity_matrix", [])
    if not acts:
        errs.append("activity_matrix is empty")
    for a in acts:
        for k in ("activity", "default_position", "gate", "fallback"):
            if not a.get(k):
                errs.append(f"activity '{a.get('activity','?')}' missing {k}")
        if not isinstance(a.get("human_participant"), bool) or not isinstance(a.get("requires_ethics_route"), bool):
            errs.append(f"activity '{a.get('activity','?')}' must set human_participant and requires_ethics_route booleans")
        if a.get("human_participant") and not a.get("requires_ethics_route"):
            errs.append(f"activity '{a.get('activity','?')}' is human-participant but does not require an ethics route")

    if not M.get("no_study_fallback"):
        errs.append("a global no_study_fallback is required (WP §13.5)")

    proh = " ; ".join(M.get("prohibited_use", [])).lower()
    for group in REQUIRED_PROHIBITIONS:
        if not any(term in proh for term in group):
            errs.append(f"prohibited_use missing a required category (any of {group})")

    if M.get("maturity_states") != CANONICAL_MATURITY:
        errs.append(f"maturity_states must be exactly {CANONICAL_MATURITY}")
    if not M.get("non_compensatory"):
        errs.append("non_compensatory statement required (WP §12.9)")

    if len(M.get("responsible_ai_requirements", [])) < 8:
        errs.append("responsible_ai_requirements looks incomplete (expected the WP §12.7 set)")
    if not M.get("intended_use"):
        errs.append("intended_use register missing")

    if errs:
        print("ETHICS MODEL INVALID:")
        for e in errs:
            print("  -", e)
        return 1
    hp = [a["activity"] for a in acts if a["human_participant"]]
    print("ETHICS MODEL OK — every activity gated with a fallback; human-participant activities require an ethics route.")
    print(f"  {len(acts)} activities; human-participant (ethics-gated): {len(hp)}")
    print(f"  prohibited-use categories covered; maturity states non-compensatory; {len(M['responsible_ai_requirements'])} responsible-AI requirements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
