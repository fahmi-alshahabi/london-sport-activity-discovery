#!/usr/bin/env python3
"""
C-16 executable assurance case (WP §12.1).

AI-ASSISTED SCAFFOLD. NOT authorship evidence. Builds the claim -> harm -> control -> test ->
reviewer -> residual -> authority graph, DETECTS orphans (a missing use/harm/control/test/reviewer/
authority blocks the affected maturity state), and — the point — RUNS each linked check so the graph
shows which claims are currently evidenced by passing tests. Reviewer and authority gates are human
and remain PENDING; an authorised person (not Clarence) records the maturity decision (WP §12.9).

Exit 0 iff the graph is well-formed (no orphans) AND every linked executable test passes. Pending
human gates are reported and block the per-claim maturity verdict, but do not fail the build.

Run:  python validate_assurance.py
"""
from __future__ import annotations
import json, os, shlex, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(HERE, "assurance-case.json")
OUT = os.path.join(HERE, "assurance-case.md")


def detect_orphans(claim, registry):
    o = []
    if not claim.get("statement") or not claim.get("permitted_wording"):
        o.append("claim")
    if not claim.get("affected_party") or not claim.get("harm"):
        o.append("harm")
    controls = claim.get("controls", [])
    if not controls or any(not c.get("owner") for c in controls):
        o.append("control")
    tids = claim.get("test_ids", [])
    if not tids or any(t not in registry for t in tids):
        o.append("test")
    if not (claim.get("reviewer") or {}).get("scope"):
        o.append("reviewer")
    if not (claim.get("authority") or {}).get("decision"):
        o.append("authority")
    return o


def run_test(tid, spec):
    cmd = spec["command"]
    try:
        r = subprocess.run(shlex.split(cmd), cwd=REPO, capture_output=True, text=True, timeout=180)
        out = r.stdout + r.stderr
        ok = r.returncode == 0 and spec.get("expect", "") in out
        return ok, ("pass" if ok else f"FAIL (rc={r.returncode})")
    except Exception as ex:
        return False, f"ERROR {ex!r}"


def render(model, results, verdicts):
    L = ["# C-16 — Executable assurance case\n",
         "> **GENERATED** — edit `assurance-case.json`, then run `python validate_assurance.py`.\n",
         "> **AI-ASSISTED SCAFFOLD (WP §12.1).** Executable tests are run live below. Reviewer and "
         "authority gates are human and PENDING; an authorised person — not Clarence — records the "
         "maturity decision (WP §12.9).\n",
         f"**Status:** {model['status']} · **Maturity target:** {model['maturity_target']} · "
         f"**{len(model['claims'])} claims**\n",
         "## Linked test results (live)\n",
         "| Test | Result | Command |",
         "|------|--------|---------|"]
    for tid, spec in model["test_registry"].items():
        ok, detail = results[tid]
        L.append(f"| `{tid}` | {'✅ ' + detail if ok else '❌ ' + detail} | `{spec['command']}` |")
    L.append("\n## Claims → controls → evidence → maturity\n")
    for c in model["claims"]:
        v = verdicts[c["id"]]
        L.append(f"### {c['id']} — {c['statement']}")
        L.append(f"*Permitted wording:* {c['permitted_wording']}")
        L.append(f"- **Affected / harm:** {c['affected_party']} — {c['harm']}")
        L.append("- **Controls:** " + "; ".join(f"{k['id']} ({k['owner']})" for k in c["controls"]))
        L.append("- **Evidence (tests):** " + ", ".join(
            f"{t} {'✅' if results[t][0] else '❌'}" for t in c["test_ids"]))
        L.append(f"- **Reviewer:** {c['reviewer']['scope']} — {c['reviewer']['status']}")
        L.append(f"- **Authority:** {c['authority']['decision']} — {c['authority']['status']}")
        L.append(f"- **Residual risk:** {c['residual_risk']}")
        L.append(f"- **Maturity verdict:** {v['verdict']}"
                 + ("" if not v["blockers"] else "  — blocked on: " + "; ".join(v["blockers"])))
        L.append("")
    return "\n".join(L) + "\n"


def main():
    model = json.load(open(SRC))
    registry = model["test_registry"]

    # run each referenced test once
    referenced = sorted({t for c in model["claims"] for t in c.get("test_ids", []) if t in registry})
    results = {tid: run_test(tid, registry[tid]) for tid in registry}  # run all; report all

    fails = 0
    verdicts = {}
    print("== linked tests ==")
    for tid in registry:
        ok, detail = results[tid]
        used = " " if tid in referenced else " (unreferenced)"
        print(f"[{'OK ' if ok else 'BAD'}] {tid}{used}: {detail}")
        fails += 0 if ok else 1

    print("\n== claims ==")
    for c in model["claims"]:
        orphans = detect_orphans(c, registry)
        failing = [t for t in c["test_ids"] if not results.get(t, (False,))[0]]
        blockers = []
        if orphans:
            blockers.append("orphan:" + ",".join(orphans))
        if failing:
            blockers.append("failing evidence:" + ",".join(failing))
        if c["reviewer"]["status"] != "done":
            blockers.append("non-author review pending")
        if c["authority"]["status"] != "done":
            blockers.append("authority decision pending")
        # orphans and failing evidence FAIL the build; human gates only block the verdict
        fails += len(orphans) + (1 if failing else 0)
        verdict = f"AUTHORISED ({model['maturity_target']})" if not blockers else "BLOCKED"
        verdicts[c["id"]] = {"verdict": verdict, "blockers": blockers}
        graph_ok = not orphans and not failing
        print(f"[{'OK ' if graph_ok else 'BAD'}] {c['id']}: graph sound & evidence "
              f"{'green' if not failing else 'RED'}; verdict={verdict}"
              + ("" if not blockers else f" (blocked: {'; '.join(blockers)})"))

    with open(OUT, "w") as fh:
        fh.write(render(model, results, verdicts))

    authorised = sum(1 for v in verdicts.values() if not v["blockers"])
    pending = len(verdicts) - authorised
    print(f"\nGraph: {'SOUND — all linked evidence green' if fails == 0 else f'{fails} PROBLEM(S)'}")
    print(f"Maturity: {authorised} authorised, {pending} awaiting human review/authority "
          f"(expected at this stage). Rendered -> {os.path.relpath(OUT, REPO)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
