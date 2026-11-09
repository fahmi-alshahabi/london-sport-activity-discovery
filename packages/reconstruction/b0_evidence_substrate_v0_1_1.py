#!/usr/bin/env python3
"""
B0 evidence substrate v0.1.1 (PROPOSED) — the L_evidence component of the baseline
unacceptable-decision rate, computed from S1 records. Successor to v0.1 (sha256 f7713fd6…),
whose per-dimension figures it reproduces exactly (same classify(), same CLASS_MAP).

New in v0.1.1
  * --selftest: hand-computed fixture (records with known lineage classes and location
    shapes) => expected exposures, mechanism splits, the illustrative joint, the location
    detail, receipt binding, determinism, and the cross-validation path.
  * Built-in cross-validation. When the run directory carries the S1 engine's own
    corpus_rollup.json, every per-dimension exposure computed here record-by-record is
    recomputed INDEPENDENTLY from the engine's aggregate field_lineage counters (a code path
    that never reads a record) and the two must agree to six decimals; a disagreement is a
    defect and the run fails closed (exit 14). This is the check memo 53 performed by hand on
    3 Sep, now executed by the tool on every run.
  * Data-card second quantity: within supported (T) locations, the share that actually carry
    coordinates (schema.org GeoCoordinates latitude+longitude, numeric) and the share carrying
    a postal code, split by mechanism (explicit vs inherited). A "located venue" evidence
    state T says a location VALUE exists; whether it can place the session on a map is this
    separate, reported quantity. Nothing about the evidence mapping changes.

Scope and honesty boundary (unchanged, carried into every output):
  * Unit is the CANDIDATE (reconstructed ScheduledSession record), never the task. The
    task-weighted B0 anchor (ratify-values memo Row 2) follows mechanically once the task
    universe, design weights and the Row-5 unacceptable-decision condition are ratified.
  * L_decision = L_evidence OR the Row-5 condition (CA-01.A2). Only the L_evidence half is
    computed; every rate is therefore a LOWER-BOUND component of the full rate.
  * Evidence states derive 1:1 from the S1 engine's own lineage classes — no reinterpretation.
    F is not producible from catalogue absence; B has no producing class at this stage.

Deterministic: no randomness, no wall-clock, sorted iteration throughout.
Provenance: Michael's stream, 5 Sep 2026, AI-assisted; PROPOSED pending review.
"""
import argparse, hashlib, io, json, shutil, sys, tempfile
from collections import Counter, OrderedDict
from pathlib import Path

ENGINE_VERSION = "b0-evidence-substrate-0.1.1-PROPOSED"
SUPERSEDES = {"b0_evidence_substrate_v0_1.py": "f7713fd6ea9661a0b737fb1454214e19dd834ce09f2d7b88d4f73b9f49200827"}
REGISTRY_REF = "F-02 v0.1.0-provisional (CA-01.A2 losses; primary_unit_rule)"
LINEAGE_PACK_REF = "lineage-pack v0.1 predicate naming"

PREDICATES = [
    ("has-located-venue",          "location",             "inheritable"),
    ("has-start-datetime",         "startDate",            "child_only"),
    ("has-activity-classification","activity",             "inheritable"),
    ("has-name",                   "name",                 "inheritable"),
    ("has-organizer",              "organizer",            "inheritable"),
    ("has-offer-information",      "offers",               "inheritable"),
    ("has-booking-url",            "url",                  "inheritable"),
    ("has-attendee-instructions",  "attendeeInstructions", "inheritable"),
]
CLASS_MAP = {
    "ON_CHILD":       ("T", "explicit_on_child",              "explicit"),
    "CHILD_OVERRIDES":("T", "explicit_on_child_overriding",   "explicit"),
    "BOTH_EQUAL":     ("T", "attested_on_both_sides",         "explicit"),
    "INHERITED":      ("T", "standards_permitted_inheritance","inherited"),
    "SOURCE_ABSENT":  ("U", "absent_on_child_and_resolved_parent", None),
    "UNRESOLVABLE_PARENT_UNAVAILABLE":
                      ("U", "parent_outside_sample",          None),
}
CHILD_ONLY_ABSENT = ("U", "absent_child_only_field", None)
ILLUSTRATIVE_CORE = ["has-located-venue", "has-start-datetime", "has-activity-classification"]
T_CLASSES = [c for c, v in CLASS_MAP.items() if v[0] == "T"]
U_CLASSES = [c for c, v in CLASS_MAP.items() if v[0] == "U"]

sha = lambda b: hashlib.sha256(b).hexdigest()


def classify(rec):
    """Yield (predicate_id, state, mechanism) for one record. Unchanged from v0.1."""
    lin = rec.get("lineage", {})
    for pid, field, kind in PREDICATES:
        entry = lin.get(field)
        cls = entry.get("class") if isinstance(entry, dict) else entry
        if cls is None:
            if kind == "child_only":
                yield pid, *CHILD_ONLY_ABSENT[:2]
            else:
                raise ValueError(f"record {rec.get('item_id')}: no lineage for governed field '{field}'")
        else:
            if cls not in CLASS_MAP:
                raise ValueError(f"unknown lineage class '{cls}' for field '{field}'")
            st, mech, _ = CLASS_MAP[cls]
            yield pid, st, mech


def _num(x):
    if isinstance(x, bool): return None
    if isinstance(x, (int, float)): return float(x)
    if isinstance(x, str):
        try: return float(x.strip())
        except ValueError: return None
    return None


def location_shape(value):
    """(coordinate_bearing, postcode_bearing, coords_unparseable) for one supported location value."""
    if not isinstance(value, dict):
        return False, False, False
    geo = value.get("geo")
    lat = lon = None
    if isinstance(geo, dict):
        lat, lon = _num(geo.get("latitude")), _num(geo.get("longitude"))
        unparseable = ("latitude" in geo or "longitude" in geo) and (lat is None or lon is None)
    else:
        lat, lon = _num(value.get("latitude")), _num(value.get("longitude"))     # flattened variant
        unparseable = ("latitude" in value or "longitude" in value) and (lat is None or lon is None)
    coords = lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180
    addr = value.get("address")
    pc = None
    if isinstance(addr, dict):
        pc = addr.get("postalCode")
    elif isinstance(addr, list):
        pc = next((a.get("postalCode") for a in addr if isinstance(a, dict) and a.get("postalCode")), None)
    if pc is None:
        pc = value.get("postalCode")
    postcode = isinstance(pc, str) and bool(pc.strip())
    return coords, postcode, bool(unparseable)


def process_records(lines):
    n = 0
    resolution = Counter()
    per_pred = {pid: Counter() for pid, _, _ in PREDICATES}
    overrides = Counter()
    joint_all_T = 0
    loc = Counter()      # (grade, key) -> n ; keys: total, coordinate_bearing, postcode_bearing, coords_unparseable
    for ln in lines:
        if not ln.strip():
            continue
        rec = json.loads(ln)
        n += 1
        resolution[rec.get("parent_resolution", "?")] += 1
        states = {}
        for pid, st, mech in classify(rec):
            per_pred[pid][(st, mech)] += 1
            states[pid] = st
        lin = rec.get("lineage", {})
        for fld, e in lin.items():
            if isinstance(e, dict) and e.get("class") == "CHILD_OVERRIDES":
                overrides[fld] += 1
        if states["has-located-venue"] == "T":
            grade = CLASS_MAP[lin["location"]["class"]][2]
            c, p, u = location_shape(rec.get("fields", {}).get("location"))
            loc[(grade, "total")] += 1
            if c: loc[(grade, "coordinate_bearing")] += 1
            if p: loc[(grade, "postcode_bearing")] += 1
            if u: loc[(grade, "coords_unparseable")] += 1
        if all(states[p] == "T" for p in ILLUSTRATIVE_CORE):
            joint_all_T += 1
    return n, resolution, per_pred, overrides, joint_all_T, loc


def process_provider(path):
    with open(path, encoding="utf-8") as f:
        return process_records(f)


def location_detail(loc):
    out = OrderedDict()
    grades = ["explicit", "inherited"]
    tot_all = sum(loc[(g, "total")] for g in grades)
    for g in grades + ["all_supported"]:
        if g == "all_supported":
            t = tot_all; c = sum(loc[(x, "coordinate_bearing")] for x in grades)
            p = sum(loc[(x, "postcode_bearing")] for x in grades); u = sum(loc[(x, "coords_unparseable")] for x in grades)
        else:
            t, c, p, u = loc[(g, "total")], loc[(g, "coordinate_bearing")], loc[(g, "postcode_bearing")], loc[(g, "coords_unparseable")]
        out[g] = OrderedDict([("supported_locations", t), ("coordinate_bearing", c),
                              ("coordinate_bearing_share", round(c / t, 6) if t else None),
                              ("postcode_bearing", p), ("postcode_bearing_share", round(p / t, 6) if t else None),
                              ("coords_present_but_unparseable", u)])
    out["_definition"] = ("Within candidates whose has-located-venue state is T: coordinate_bearing = location value "
                          "carries numeric GeoCoordinates latitude AND longitude within range; postcode_bearing = a "
                          "non-empty address postalCode. Grade follows the lineage class (explicit: ON_CHILD / "
                          "CHILD_OVERRIDES / BOTH_EQUAL; inherited: INHERITED). Evidence states are NOT changed by this.")
    return out


def summarise(name, n, resolution, per_pred, overrides, joint_all_T, loc):
    preds = OrderedDict()
    for pid, field, kind in PREDICATES:
        c = per_pred[pid]
        supported = sum(v for (st, _), v in c.items() if st == "T")
        indeterminate = sum(v for (st, _), v in c.items() if st == "U")
        preds[pid] = OrderedDict([
            ("field", field),
            ("supported_T", supported),
            ("indeterminate_U", indeterminate),
            ("unsupported_implication_exposure", round(indeterminate / n, 6) if n else None),
            ("by_mechanism", OrderedDict((f"{st}:{mech}", c[(st, mech)]) for (st, mech) in sorted(c)))])
    return OrderedDict([
        ("provider", name),
        ("unit", "candidate"),
        ("candidates_total", n),
        ("parent_resolution", OrderedDict(sorted(resolution.items()))),
        ("predicates", preds),
        ("parent_value_divergence_CHILD_OVERRIDES", OrderedDict(sorted(overrides.items()))),
        ("illustrative_core_slate", OrderedDict([
            ("predicates", ILLUSTRATIVE_CORE),
            ("all_supported", joint_all_T),
            ("at_least_one_U", n - joint_all_T),
            ("exposure", round((n - joint_all_T) / n, 6) if n else None),
            ("status", "ILLUSTRATIVE_PENDING_RATIFY(Row-5, universe, weights)")])),
        ("location_detail", location_detail(loc)),
    ])


def cross_validate(rollup, s1_rollup):
    """Recompute every per-dimension exposure from the S1 engine's field_lineage counters
    (aggregate, never touching a record) and compare to the per-record figures."""
    fl = s1_rollup.get("field_lineage", {})
    n_rec = rollup["candidates_total"]
    rows, agree, n_checked = OrderedDict(), True, 0
    for pid, field, kind in PREDICATES:
        rec = rollup["predicates"][pid]["unsupported_implication_exposure"]
        if kind != "inheritable":
            # the S1 engine emits field_lineage counters for the governed (inheritable) fields only;
            # child-only fields have no aggregate counter, so there is nothing independent to compare
            rows[pid] = OrderedDict([("per_record", rec), ("from_s1_counters", None), ("agree_6dp", None),
                                     ("status", "not_counter_checkable(child-only field: engine emits inheritable-field counters only)")])
            continue
        tot = sum(fl.get(f"{field}:{c}", 0) for c in list(T_CLASSES) + list(U_CLASSES))
        u = sum(fl.get(f"{field}:{c}", 0) for c in U_CLASSES)
        ind = round(u / tot, 6) if tot else None
        ok = (tot == n_rec) and (ind == rec)
        agree &= ok; n_checked += 1
        rows[pid] = OrderedDict([("per_record", rec), ("from_s1_counters", ind), ("counter_total", tot),
                                 ("record_total", n_rec), ("agree_6dp", ok)])
    return OrderedDict([("status", "AGREE_TO_6DP" if agree else "DISAGREE"),
                        ("dimensions_checked", n_checked),
                        ("method", "per-record classification vs S1 corpus_rollup.field_lineage aggregate counters "
                                   "(independent code paths) for every inheritable dimension; must agree to six decimals. "
                                   "Child-only dimensions carry no engine counter and are reported as not checkable."),
                        ("dimensions", rows)])


def run(run_dir, out_dir, snapshot, s1_rollup_path=None):
    run_p = Path(run_dir)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    record_files = sorted(run_p.glob("*/s1_records.jsonl"))
    if not record_files:
        sys.exit(f"no */s1_records.jsonl under {run_p}")
    input_hashes, provider_summaries = OrderedDict(), OrderedDict()
    roll_n = 0; roll_res = Counter(); roll_joint = 0; roll_loc = Counter()
    roll_pred = {pid: Counter() for pid, _, _ in PREDICATES}
    roll_overrides = Counter()
    for rf in record_files:
        prov = rf.parent.name
        input_hashes[f"{prov}/s1_records.jsonl"] = sha(rf.read_bytes())
        n, resolution, per_pred, overrides, joint, loc = process_provider(rf)
        provider_summaries[prov] = summarise(prov, n, resolution, per_pred, overrides, joint, loc)
        roll_n += n; roll_res.update(resolution); roll_joint += joint; roll_loc.update(loc)
        for pid in roll_pred: roll_pred[pid].update(per_pred[pid])
        roll_overrides.update(overrides)
    rollup = summarise("ALL_PROVIDERS", roll_n, roll_res, roll_pred, roll_overrides, roll_joint, roll_loc)

    s1_path = Path(s1_rollup_path) if s1_rollup_path else run_p / "corpus_rollup.json"
    if s1_path.is_file():
        s1_rollup = json.loads(s1_path.read_text(encoding="utf-8"))
        input_hashes[s1_path.name + " (S1 engine rollup)"] = sha(s1_path.read_bytes())
        xval = cross_validate(rollup, s1_rollup)
        xval["s1_engine"] = s1_rollup.get("engine")
    else:
        xval = OrderedDict([("status", "S1_ROLLUP_NOT_FOUND"),
                            ("method", "no corpus_rollup.json in the run directory; pass --s1-rollup to enable")])

    envelope = OrderedDict([
        ("engine", ENGINE_VERSION), ("supersedes", SUPERSEDES),
        ("registry_ref", REGISTRY_REF), ("predicate_naming", LINEAGE_PACK_REF),
        ("snapshot", snapshot), ("unit", "candidate"),
        ("what_this_is", "L_evidence-component substrate of the baseline unacceptable-decision rate: "
         "per-candidate evidence states derived 1:1 from S1 lineage classes; exposure = share of candidates on "
         "which a definitive constraint-implying emission would rest on indeterminate (U) evidence for that dimension."),
        ("what_this_is_not", OrderedDict([
            ("task_weighted_B0", "PENDING: task universe, design weights and the Row-5 unacceptable-decision "
             "condition are RATIFY items and are not invented here (F-02; ratify-values memo Rows 2 & 5)"),
            ("F_and_B_states", "F not producible from catalogue absence; no producing class for B at this stage "
             "— stated, not suppressed"),
            ("bounded_non_match_clause", "emission-behaviour-dependent; out of candidate-marginal scope"),
        ])),
        ("relation_to_anchor", "lower-bound component: L_decision = L_evidence OR Row-5 condition, so the full B0 "
         "rate >= any task-weighting of these exposures over emitted slates"),
        ("class_map", {k: {"state": v[0], "mechanism": v[1], "grade": v[2]} for k, v in sorted(CLASS_MAP.items())}),
        ("cross_validation", xval),
        ("rollup", rollup),
        ("providers", provider_summaries),
    ])
    (out / "b0_substrate_rollup.json").write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    receipt = OrderedDict([
        ("engine_sha256", sha(Path(__file__).read_bytes())), ("engine", ENGINE_VERSION), ("supersedes", SUPERSEDES),
        ("snapshot", snapshot), ("inputs", input_hashes),
        ("cross_validation", xval["status"]),
        ("outputs", {"b0_substrate_rollup.json": sha((out / "b0_substrate_rollup.json").read_bytes())}),
        ("deterministic", True), ("seed", None),
    ])
    (out / "B0_SUBSTRATE_RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    report = {"providers": len(provider_summaries), "candidates": roll_n,
              "core_slate_exposure": rollup["illustrative_core_slate"]["exposure"],
              "per_dimension_exposure": {p: rollup["predicates"][p]["unsupported_implication_exposure"] for p, _, _ in PREDICATES},
              "location_detail": {g: rollup["location_detail"][g] for g in ("explicit", "inherited", "all_supported")},
              "cross_validation": xval["status"]}
    print(json.dumps(report, indent=1))
    if xval["status"] == "DISAGREE":
        print("CROSS-VALIDATION DISAGREEMENT: per-record and S1-counter exposures differ — treat as a defect "
              "(see cross_validation.dimensions in the rollup). [exit 14]", file=sys.stderr)
        raise SystemExit(14)
    return envelope, receipt


# ---------------- self-test ----------------------------------------------------------------------
def _rec(i, res, classes, location=None, start=True):
    L = lambda c: {"class": c, "rule": "M06-INHERITANCE-v0.2-UNRATIFIED:test"}
    lin = {f: L(classes.get(f, "SOURCE_ABSENT" if res == "RESOLVED" else "UNRESOLVABLE_PARENT_UNAVAILABLE"))
           for f in ["name", "location", "organizer", "activity", "category", "offers", "url", "attendeeInstructions", "level", "ageRange"]}
    fields = {}
    if start:
        lin["startDate"] = {"class": "ON_CHILD", "rule": "M06:child-only"}; fields["startDate"] = "2026-09-01T18:00:00+01:00"
    if location is not None:
        fields["location"] = location
    for f, c in classes.items():
        if CLASS_MAP[c][0] == "T" and f not in fields:
            fields[f] = f"{f}-value"
    return {"item_id": f"r{i}", "@id": f"https://t.test/s/{i}", "type": "ScheduledSession", "parent_resolution": res,
            "fields": fields, "lineage": lin}


def selftest():
    results = []
    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))
    GEO = lambda lat, lon, pc=None: {"@type": "Place", "name": "V", "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon},
                                     **({"address": {"@type": "PostalAddress", "postalCode": pc}} if pc else {})}
    recs = [
        _rec(1, "RESOLVED", {"location": "INHERITED", "activity": "INHERITED", "name": "BOTH_EQUAL"}, GEO(51.5, -0.1, "E1 6AN")),
        _rec(2, "RESOLVED", {"location": "INHERITED", "name": "INHERITED"}, {"@type": "Place", "name": "No coords", "address": {"postalCode": "SE1 7PB"}}),
        _rec(3, "RESOLVED", {"location": "ON_CHILD", "activity": "ON_CHILD"}, GEO("51.4", "-0.2")),
        _rec(4, "RESOLVED", {"location": "CHILD_OVERRIDES", "activity": "SOURCE_ABSENT"}, GEO("abc", -0.2)),
        _rec(5, "PARENT_NOT_IN_SAMPLE", {}, None),
        _rec(6, "NO_SUPEREVENT", {"location": "ON_CHILD"}, {"@type": "Place", "name": "Bare"}),
        _rec(7, "RESOLVED", {"location": "INHERITED", "activity": "INHERITED"}, GEO(51.6, -0.3), start=False),
        _rec(8, "RESOLVED", {"activity": "INHERITED"}, None),
    ]
    n, resolution, per_pred, overrides, joint, loc = process_records([json.dumps(r) for r in recs])
    s = summarise("T", n, resolution, per_pred, overrides, joint, loc)
    P = s["predicates"]
    check("8 candidates; resolution 6/1/1", n == 8 and resolution == {"RESOLVED": 6, "PARENT_NOT_IN_SAMPLE": 1, "NO_SUPEREVENT": 1})
    check("location: T 6 (r1,r2,r3,r4,r6,r7), U 2 (r5 unresolvable, r8 absent) -> exposure 0.25",
          P["has-located-venue"]["supported_T"] == 6 and P["has-located-venue"]["indeterminate_U"] == 2
          and P["has-located-venue"]["unsupported_implication_exposure"] == 0.25, json.dumps(P["has-located-venue"]))
    check("location mechanisms: inherited 3, explicit_on_child 2, overriding 1, parent_outside_sample 1, absent-on-both 1",
          P["has-located-venue"]["by_mechanism"] == {"T:explicit_on_child": 2, "T:explicit_on_child_overriding": 1,
                                                     "T:standards_permitted_inheritance": 3, "U:absent_on_child_and_resolved_parent": 1,
                                                     "U:parent_outside_sample": 1}, json.dumps(P["has-located-venue"]["by_mechanism"]))
    check("startDate: child-only absent on r7 -> U 1, exposure 0.125, mechanism absent_child_only_field",
          P["has-start-datetime"]["indeterminate_U"] == 1 and P["has-start-datetime"]["unsupported_implication_exposure"] == 0.125
          and P["has-start-datetime"]["by_mechanism"].get("U:absent_child_only_field") == 1)
    check("activity: T 4 (r1,r3,r7,r8), U 4 -> exposure 0.5", P["has-activity-classification"]["supported_T"] == 4
          and P["has-activity-classification"]["unsupported_implication_exposure"] == 0.5)
    check("joint core slate: all-T only r1, r3 (r7 lacks startDate) -> at_least_one_U 6, exposure 0.75",
          s["illustrative_core_slate"]["all_supported"] == 2 and s["illustrative_core_slate"]["exposure"] == 0.75)
    check("CHILD_OVERRIDES divergence counted per field (location 1)", s["parent_value_divergence_CHILD_OVERRIDES"] == {"location": 1})
    ld = s["location_detail"]
    check("location detail — inherited: 3 supported, 2 coordinate-bearing (r1, r7), 2 postcode-bearing (r1, r2)",
          ld["inherited"]["supported_locations"] == 3 and ld["inherited"]["coordinate_bearing"] == 2
          and ld["inherited"]["postcode_bearing"] == 2 and ld["inherited"]["coordinate_bearing_share"] == round(2 / 3, 6), json.dumps(ld["inherited"]))
    check("location detail — explicit: 3 supported (r3 string coords OK, r4 unparseable, r6 bare) -> 1 coordinate-bearing, 1 unparseable",
          ld["explicit"]["supported_locations"] == 3 and ld["explicit"]["coordinate_bearing"] == 1
          and ld["explicit"]["coords_present_but_unparseable"] == 1 and ld["explicit"]["postcode_bearing"] == 0, json.dumps(ld["explicit"]))
    check("location detail — all_supported: 6 / 3 coordinate-bearing (0.5)", ld["all_supported"]["supported_locations"] == 6
          and ld["all_supported"]["coordinate_bearing_share"] == 0.5)
    check("location_shape: out-of-range coordinates are not coordinate-bearing", location_shape(GEO(95.0, 0.0))[0] is False
          and location_shape(GEO(51.0, -0.1))[0] is True)
    # engine-contract violation: inheritable field without a lineage row must raise
    bad = json.loads(json.dumps(recs[0])); bad["lineage"].pop("offers")
    try:
        list(classify(bad)); raised = False
    except ValueError:
        raised = True
    check("missing lineage row on a governed field raises (engine contract)", raised)

    # run-dir mode: two providers, S1 rollup counters consistent -> AGREE; then a tampered counter -> exit 14
    tmp = Path(tempfile.mkdtemp(prefix="b0_selftest_"))
    try:
        import contextlib
        (tmp / "run" / "Prov_A").mkdir(parents=True); (tmp / "run" / "Prov_B").mkdir(parents=True)
        (tmp / "run" / "Prov_A" / "s1_records.jsonl").write_text("\n".join(json.dumps(r) for r in recs[:5]) + "\n", encoding="utf-8")
        (tmp / "run" / "Prov_B" / "s1_records.jsonl").write_text("\n".join(json.dumps(r) for r in recs[5:]) + "\n", encoding="utf-8")
        fl = Counter()                     # mirror the engine: counters for the governed inheritable fields only
        for r in recs:
            for f, e in r["lineage"].items():
                if f != "startDate":
                    fl[f"{f}:{e['class']}"] += 1
        (tmp / "run" / "corpus_rollup.json").write_text(json.dumps({"engine": "s1-engine-test", "field_lineage": dict(fl)}), encoding="utf-8")
        outs = []
        for k in (1, 2):
            with contextlib.redirect_stdout(io.StringIO()):
                env, rec = run(tmp / "run", tmp / f"out{k}", "FIXTURE")
            outs.append((env, rec))
        env, rec = outs[0]
        check("run-dir: rollup candidates 8 over 2 providers; per-dimension exposures equal the in-memory computation",
              env["rollup"]["candidates_total"] == 8 and env["rollup"]["predicates"] == P)
        xd = env["cross_validation"]["dimensions"]
        check("cross-validation against S1 counters: AGREE_TO_6DP on the 7 inheritable dimensions; startDate reported not counter-checkable",
              env["cross_validation"]["status"] == "AGREE_TO_6DP" and env["cross_validation"]["dimensions_checked"] == 7
              and all(v["agree_6dp"] for k, v in xd.items() if k != "has-start-datetime")
              and xd["has-start-datetime"]["agree_6dp"] is None and "not_counter_checkable" in xd["has-start-datetime"]["status"]
              and rec["cross_validation"] == "AGREE_TO_6DP", json.dumps(env["cross_validation"]))
        check("receipt binds inputs (2 record files + S1 rollup) and the output rollup",
              len(rec["inputs"]) == 3 and rec["outputs"]["b0_substrate_rollup.json"] == sha((tmp / "out1" / "b0_substrate_rollup.json").read_bytes()))
        check("determinism: two runs byte-identical (rollup + receipt)",
              (tmp / "out1" / "b0_substrate_rollup.json").read_bytes() == (tmp / "out2" / "b0_substrate_rollup.json").read_bytes()
              and (tmp / "out1" / "B0_SUBSTRATE_RECEIPT.json").read_bytes() == (tmp / "out2" / "B0_SUBSTRATE_RECEIPT.json").read_bytes())
        fl2 = dict(fl); fl2["location:INHERITED"] -= 1; fl2["location:SOURCE_ABSENT"] += 1
        (tmp / "run" / "corpus_rollup.json").write_text(json.dumps({"engine": "s1-engine-test", "field_lineage": fl2}), encoding="utf-8")
        code = None
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                run(tmp / "run", tmp / "out3", "FIXTURE")
        except SystemExit as e:
            code = e.code
        env3 = json.loads((tmp / "out3" / "b0_substrate_rollup.json").read_text(encoding="utf-8"))
        check("tampered S1 counter: DISAGREE recorded on exactly the location dimension and the run fails closed (exit 14)",
              code == 14 and env3["cross_validation"]["status"] == "DISAGREE"
              and [k for k, v in env3["cross_validation"]["dimensions"].items() if v["agree_6dp"] is False] == ["has-located-venue"])
        (tmp / "run" / "corpus_rollup.json").unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            env4, _ = run(tmp / "run", tmp / "out4", "FIXTURE")
        check("no S1 rollup present: status S1_ROLLUP_NOT_FOUND, run still completes", env4["cross_validation"]["status"] == "S1_ROLLUP_NOT_FOUND")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    width = max(len(n_) for n_, _, _ in results)
    for n_, ok, det in results:
        print(("OK   " if ok else "FAIL ") + n_.ljust(width) + ("" if ok or not det else "   <- " + det))
    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"\nSELFTEST: {n_ok}/{len(results)} checks pass — " + ("ALL PASS" if n_ok == len(results) else "STOP: failures above"))
    return 0 if n_ok == len(results) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", help="S1 run dir containing <Provider>/s1_records.jsonl (and corpus_rollup.json for cross-validation)")
    ap.add_argument("--out", default="b0_substrate_out")
    ap.add_argument("--snapshot")
    ap.add_argument("--s1-rollup", help="path to the S1 engine's corpus_rollup.json if not inside --run-dir")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if not (args.run_dir and args.snapshot):
        ap.error("--run-dir and --snapshot are required (or --selftest)")
    run(args.run_dir, args.out, args.snapshot, args.s1_rollup)


if __name__ == "__main__":
    main()
