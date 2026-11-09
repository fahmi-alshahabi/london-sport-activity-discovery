#!/usr/bin/env python3
"""
Validate the evaluation condition manifest (C-17) and prove the C-BLOCK-06 guarantee.

AI-ASSISTED SCAFFOLD (WP §13). NOT authorship evidence; Fahmi owns the estimands, Clarence the
frozen builds. Checks:
  1. every condition has its required fields and the declared capability relationships hold
     (P0 no evidence comms; P1 adds evidence comms; P2 = P1 + conversation; W1-NA = W1 - nl_assistant);
  2. SHARED BACKEND (C-BLOCK-06): for each task, every condition in a surface family resolves the
     IDENTICAL terminal DecisionEnvelope (projected-digest equality) — so an interface effect cannot
     be confounded with a backend difference. L_reliance binds to that shared decision (CA-1);
  3. a deliberately confounded binding (P2 pointed at a different scenario) is DETECTED;
  4. the telemetry event schema validates a sample and, by additionalProperties:false, cannot carry
     raw utterances / exact location / free text (WP §13.3, C-BLOCK-07).

Run:  python validate_conditions.py
"""
from __future__ import annotations
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
CB05 = os.path.join(REPO, "packages", "application-contracts", "c-block-05")
SCEN = os.path.join(REPO, "apps", "public-discovery", "server", "scenarios")
MAN = json.load(open(os.path.join(HERE, "condition-manifest.json")))
EVSCHEMA = os.path.join(HERE, "event-schema.json")

sys.path.insert(0, CB05)
import projection_and_invariants as proj  # noqa: E402
FIELDS, PLANES = proj.load_classes()

PLANE_FOR = {"public": "public", "staff": "staff"}
FORBIDDEN_KEY_SUBSTR = ["utterance", "postcode", "lat", "lon", "free_text", "raw", "location", "address"]


def _decision_digest(scenario, plane):
    env = json.load(open(os.path.join(SCEN, scenario + ".json")))
    p = proj.project(env, FIELDS, set(PLANES[plane]))
    d = copy.deepcopy(p["payload"]["decision"])
    d.pop("digest", None)
    return proj.sha(d)


def _eff_scenario(cond_id, task, overrides):
    ov = overrides.get(cond_id, {}) if isinstance(overrides.get(cond_id), dict) else {}
    return ov.get(task["task_id"], task["scenario"])


def check_family(surface, cond_ids, overrides):
    errs = []
    plane = PLANE_FOR[surface]
    for task in MAN["tasks"]:
        digs = {cid: _decision_digest(_eff_scenario(cid, task, overrides), plane) for cid in cond_ids}
        if len(set(digs.values())) != 1:
            errs.append(f"{surface}: task {task['task_id']} decision differs across {cond_ids}: {digs}")
    return errs


def check_capabilities():
    errs = []
    pub = {c["id"]: c["capabilities"] for c in MAN["public_conditions"]}
    stf = {c["id"]: c["capabilities"] for c in MAN["staff_conditions"]}
    if pub["P0"] != {"evidence_communication": False, "conversation": False}:
        errs.append("P0 must have no evidence communication and no conversation")
    if pub["P1"] != {"evidence_communication": True, "conversation": False}:
        errs.append("P1 must add evidence communication only")
    if pub["P2"] != {**pub["P1"], "conversation": True}:
        errs.append("P2 must equal P1 plus conversation only")
    if not (stf["W1"]["workbench"] and stf["W1"]["nl_assistant"]):
        errs.append("W1 must be the full workbench with the NL assistant")
    if stf["W1-NA"] != {**stf["W1"], "nl_assistant": False}:
        errs.append("W1-NA must equal W1 without the NL assistant")
    if stf["W0"]["workbench"]:
        errs.append("W0 must be a non-workbench control")
    return errs


def check_event_schema():
    # Fail CLEANLY, never with an uncaught crash: report the exact remedy instead of
    # stopping the run with no RESULT line.
    try:
        import jsonschema
    except Exception as ex:
        return [f"jsonschema not installed — run: pip install -U jsonschema  ({ex})"]
    try:
        Validator = jsonschema.Draft202012Validator
    except Exception:
        return ["jsonschema too old (no Draft202012Validator) — run: pip install -U jsonschema"]
    errs = []
    try:
        schema = json.load(open(EVSCHEMA))
        Validator.check_schema(schema)
        # allowed property names must not include a forbidden concept
        for name in schema["properties"]:
            if any(s in name.lower() for s in FORBIDDEN_KEY_SUBSTR):
                errs.append(f"event schema exposes a forbidden field: {name}")
        good = {
            "event_name": "slate_shown", "event_schema_version": "0.1.0", "condition_id": "P1",
            "task_id": "T-swim-croydon", "episode_id": "eph-xyz", "application_release_id": "app-0.1.0",
            "envelope_digest": "sha256:" + "d" * 64, "route": "guided_search",
            "state_before": "query_review", "authorised_action": "render_slate", "state_after": "results",
            "duration_ms": 812, "error_or_fallback_code": None, "purpose": "research",
            "retention_class": "transient",
        }
        v = jsonschema.Draft202012Validator(schema)
        ge = list(v.iter_errors(good))
        if ge:
            errs.append(f"valid sample event rejected: {ge[0].message}")
        bad = {**good, "raw_utterance": "cheap swimming near me"}
        if not list(v.iter_errors(bad)):
            errs.append("event schema ACCEPTED a raw_utterance field (should be rejected)")
    except Exception as ex:
        errs.append(f"event-schema validation error: {ex!r}")
    return errs


def _task_vintage(scenario):
    env = json.load(open(os.path.join(SCEN, scenario + ".json")))
    p = proj.project(env, FIELDS, set(PLANES["public"]))
    return (((p.get("payload") or {}).get("decision") or {}).get("versions") or {}).get("vintage")


def main():
    fails = 0
    empty = {}

    print("== capability relationships ==")
    ce = check_capabilities()
    print("OK" if not ce else "FAIL"); [print("  -", e) for e in ce]; fails += len(ce)

    print("\n== shared backend per family (C-BLOCK-06) ==")
    for surface, cond_ids in MAN["families"].items():
        e = check_family(surface, cond_ids, empty)
        print(f"[{'OK ' if not e else 'BAD'}] {surface} family {cond_ids}: identical decision per task")
        [print("  -", x) for x in e]; fails += len(e)

    print("\n== confound is detected (negative) ==")
    confound = {"P2": {"T-swim-croydon": "no_match"}}
    e = check_family("public", MAN["families"]["public"], confound)
    detected = bool(e)
    print(f"[{'OK ' if detected else 'BAD'}] confounded P2 binding detected")
    fails += 0 if detected else 1

    print("\n== telemetry event schema (§13.3) ==")
    ee = check_event_schema()
    print("OK — validates sample; rejects raw fields by construction" if not ee else "FAIL")
    [print("  -", e) for e in ee]; fails += len(ee)

    print("\n== task-set completeness (Fahmi review 2026-08) ==")
    tasks = MAN["tasks"]
    fv = MAN.get("frozen_vintage")
    role = MAN.get("task_set_role", "demonstration")
    minb = (MAN.get("benchmark_requirements") or {}).get("min_tasks_for_benchmark", 20)

    # R2: origin + publisher recorded (PD-6 leakage splits / CAL-RISK clustering)
    miss = [t["task_id"] for t in tasks if not t.get("origin") or not t.get("publisher")]
    print(f"[{'OK ' if not miss else 'BAD'}] every task records origin + publisher (PD-6 / CAL-RISK)")
    for m in miss:
        print("  - missing origin/publisher:", m)
    fails += len(miss)

    # R4: single frozen vintage — nothing runs two conditions at different vintages
    badv = [(t["task_id"], _task_vintage(t["scenario"])) for t in tasks if _task_vintage(t["scenario"]) != fv]
    print(f"[{'OK ' if not badv else 'BAD'}] all tasks bound to frozen_vintage {fv}")
    for tid, v in badv:
        print(f"  - {tid} -> {v}")
    fails += len(badv)

    # R3: query-repair minting — a repaired task references a distinct existing base (F-BLOCK-09)
    ids = {t["task_id"] for t in tasks}
    badr = [t["task_id"] for t in tasks
            if t.get("repair_of") and (t["repair_of"] not in ids or t["repair_of"] == t["task_id"])]
    print(f"[{'OK ' if not badr else 'BAD'}] repaired tasks reference a distinct existing base (F-BLOCK-09)")
    for r in badr:
        print("  - bad repair_of:", r)
    fails += len(badr)

    # R1: task-set role vs benchmark minimum (demo fixtures are fine; a benchmark must meet the floor)
    if role == "benchmark" and len(tasks) < minb:
        print(f"[BAD] benchmark task set needs >= {minb} tasks; has {len(tasks)}")
        fails += 1
    else:
        extra = "benchmark" if role == "benchmark" else f"demonstration fixtures; benchmark requires >= {minb}"
        print(f"[OK ] task-set role = {role}: {len(tasks)} tasks ({extra})")

    print("\nRESULT:", "ALL CONDITION CHECKS PASS" if fails == 0 else f"{fails} FAILURE(S)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
