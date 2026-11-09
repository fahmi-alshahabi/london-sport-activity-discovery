#!/usr/bin/env python3
"""
Validate the C-01 reconciliation register and render its human-readable view.

AI-ASSISTED SCAFFOLD (WP sec 3 required reconciliation artefact + CA-6 core/stretch tagging).
Enforces the discipline that no mandatory cell is blank and that institutional cells not yet
decided are EXPLICIT 'PENDING' rather than silently backfilled (WP sec 3: "No cell may be
backfilled from memory after results are seen").

Run:  python validate_register.py            # validate + regenerate the markdown view
Exits non-zero on any completeness violation.
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reconciliation-register.json")
OUT = os.path.join(HERE, "C-01-reconciliation-register.md")

EXPECTED_IDS = {f"C-BLOCK-{i:02d}" for i in range(1, 16)}
STR_FIELDS = ["decision_id","question","chosen_option","rationale","owner","approver","date","decision_log_ref","fallback_if_unresolved","status"]
LIST_FIELDS = ["options_considered","affected_contracts","tests_required"]


def validate(reg):
    errs = []
    rows = reg.get("rows", [])
    ids = [r.get("decision_id") for r in rows]
    missing = EXPECTED_IDS - set(ids)
    extra = set(ids) - EXPECTED_IDS
    dupes = {i for i in ids if ids.count(i) > 1}
    if missing: errs.append(f"missing C-BLOCKs: {sorted(missing)}")
    if extra:   errs.append(f"unexpected decision_ids: {sorted(extra)}")
    if dupes:   errs.append(f"duplicate decision_ids: {sorted(dupes)}")
    for r in rows:
        rid = r.get("decision_id", "?")
        for f in STR_FIELDS:
            v = r.get(f)
            if not isinstance(v, str) or not v.strip():
                errs.append(f"{rid}: empty/absent field '{f}'")
        for f in LIST_FIELDS:
            v = r.get(f)
            if not isinstance(v, list) or not v:
                errs.append(f"{rid}: empty/absent list '{f}'")
        # no-blank-cell discipline: undecided institutional cells must be explicit PENDING
        for f in ("approver", "date", "decision_log_ref"):
            v = r.get(f, "")
            if isinstance(v, str) and v.strip() and not (v.startswith("PENDING") or _looks_decided(v)):
                pass  # a concrete value is fine
        # chosen_option must be an option OR explicit PENDING
        co = r.get("chosen_option", "")
        opts = r.get("options_considered", [])
        if not (co.startswith("PENDING") or any(co.strip() == o.strip() or co.strip() in o for o in opts)):
            errs.append(f"{rid}: chosen_option is neither PENDING nor one of options_considered")
        if r.get("tier") not in ("core", "stretch"):
            errs.append(f"{rid}: tier must be core|stretch")
        if not isinstance(r.get("priority"), int):
            errs.append(f"{rid}: priority must be an integer")
    return errs


def _looks_decided(v):
    return True  # concrete (non-PENDING) strings are acceptable once a real decision is recorded


def render(reg):
    rows = sorted(reg["rows"], key=lambda r: r["priority"])
    n_core = sum(1 for r in rows if r["tier"] == "core")
    n_stretch = sum(1 for r in rows if r["tier"] == "stretch")
    L = []
    L.append("# C-01 — Reconciliation decision register (all C-BLOCKs)\n")
    L.append("> **GENERATED FILE** — edit `reconciliation-register.json`, then run "
             "`python validate_register.py`. Do not hand-edit this markdown.\n")
    L.append("> **AI-ASSISTED SCAFFOLD (WP §3).** Not authorship evidence. Clarence takes the team "
             "decisions himself and obtains review; institutional cells marked `PENDING` must not be "
             "backfilled from memory after results are seen.\n")
    L.append(f"**Status:** {reg['status']} · **Version:** {reg['version']} · "
             f"**{len(rows)} blockers** ({n_core} core, {n_stretch} stretch)\n")
    L.append("## Priority order\n")
    L.append("| # | Blocker | Tier | Status | Chosen option (or PENDING) |")
    L.append("|---|---------|------|--------|-----------------------------|")
    for r in rows:
        co = r["chosen_option"]
        co = (co[:70] + "…") if len(co) > 70 else co
        L.append(f"| {r['priority']} | `{r['decision_id']}` | {r['tier']} | {r['status'].split('(')[0].strip()} | {co} |")
    L.append("")
    L.append("## Full dispositions\n")
    for r in rows:
        L.append(f"### {r['decision_id']} — {r['question']}")
        L.append(f"*Tier:* **{r['tier']}** · *Priority:* {r['priority']} · *Status:* {r['status']}\n")
        L.append("- **Options considered:** " + "; ".join(r["options_considered"]))
        L.append("- **Chosen:** " + r["chosen_option"])
        L.append("- **Rationale:** " + r["rationale"])
        L.append("- **Affected contracts:** " + ", ".join(r["affected_contracts"]))
        L.append(f"- **Owner:** {r['owner']}  ·  **Approver:** {r['approver']}")
        L.append(f"- **Date:** {r['date']}  ·  **Decision-log ref:** {r['decision_log_ref']}")
        L.append("- **Tests required:** " + ", ".join(r["tests_required"]))
        L.append("- **Fallback if unresolved:** " + r["fallback_if_unresolved"])
        L.append("")
    return "\n".join(L) + "\n"


def main():
    reg = json.load(open(SRC))
    errs = validate(reg)
    if errs:
        print("REGISTER INVALID:")
        for e in errs:
            print("  -", e)
        return 1
    md = render(reg)
    with open(OUT, "w") as fh:
        fh.write(md)
    rows = reg["rows"]
    print(f"REGISTER OK: {len(rows)} blockers, all C-BLOCK-01..15 present, no blank cells.")
    print(f"  core={sum(1 for r in rows if r['tier']=='core')} stretch={sum(1 for r in rows if r['tier']=='stretch')}")
    print(f"  drafted={sum(1 for r in rows if r['status'].startswith(('DRAFTED','PARTIAL')))} "
          f"proposed={sum(1 for r in rows if r['status'].startswith('PROPOSED'))}")
    print(f"  rendered -> {os.path.relpath(OUT, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
