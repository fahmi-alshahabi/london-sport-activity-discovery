#!/usr/bin/env python3
"""
lineage_pack_v0_1.py — generator for LINEAGE PACK v0.1 (PROPOSED)

A lineage pack makes ONE decision over ONE slate fully auditable: for every predicate the
decision used it records the evidence state, the value relied on, the served RPDE page that
value came from (feed, page index, sha256 of the served bytes), and the receipts that bind
those pages and files to the engine run. It is generated — never hand-written — from:

    an S1/S1b engine v0.3.1+ run directory   (s1_records.jsonl, s1_parent_provenance.jsonl,
                                              MASTER_RECEIPT.json per run)
    a query file                             (query_id, constraints, slate; see QUERY FORMAT)
    optionally Wesley's pages.csv            (then every cited page is checked against the
                                              acquisition ledger, fail-closed on mismatch)

Decisions come from reducer_v0_1_1.reduce_decision (the R1 gate; D4_INPUT_CONTRACT §3) —
this file never re-implements the classifier. Evidence states come from the S1 lineage class
through the B0 substrate's CLASS_MAP (copied verbatim below and cross-checked at import when
the substrate is importable). The pack validates against lineage_pack_schema_v0_1.json before
it is written (built-in stdlib validator covering the subset of JSON Schema the schema uses).

QUERY FORMAT (JSON):
  {"query_id": "Q-…", "task_ref": "optional pointer", "vintage_label": "V2026-08-27-DEV",
   "constraints": [{"predicate_id": "has-located-venue", "matcher": "text", "value": "mill house"},
                   {"predicate_id": "has-start-datetime", "matcher": "date_window",
                    "start": "2026-08-27", "end": "2026-09-23"}],
   "slate": [{"candidate_id": "<record @id or item_id>", "provider": "Active Hartlepool"}, …]}
  Slate order is rank order. provider may be omitted (all providers in the run are searched;
  an id found in two providers fails closed).

Terminal decision over the slate: supported_match if any candidate is supported; else
evidence_indeterminate if any is indeterminate; else bounded_non_match (all candidates
bounded); no_candidates for an empty slate. NOTE the honesty boundary carried in limits[]:
a slate-level "no matches exist" additionally needs the bounded-search argument, which is
outside this pack.

Deterministic: same run directory + same query => byte-identical pack. No wall-clock, no
randomness, sorted iteration throughout. Every failure is typed and fails closed (exit 13).

Provenance: Michael's stream, 5 Sep 2026, AI-assisted; PROPOSED pending review.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, shutil, sys, tempfile
from pathlib import Path

PACK_SCHEMA_ID = "lineage-pack-0.1-PROPOSED"
SUPERSEDES_GENERATOR = {"lineage_pack_v0_1.py": "2ab75237cb5b48b9d4fa683bf28da87dc7ae41c2e79c5911b499922c241ab70e"}
GENERATOR_VERSION = "lineage-pack-generator-0.1.1-PROPOSED"
MIN_ENGINE = ("s1-engine-0.3.1-PROPOSED",)          # runs whose records carry page provenance + sidecar
SCHEMA_FILE = "lineage_pack_schema_v0_1.json"

# Predicate naming — verbatim from b0_evidence_substrate_v0_1.py (LINEAGE_PACK_REF)
PREDICATES = {
    "has-located-venue": ("location", "inheritable"),
    "has-start-datetime": ("startDate", "child_only"),
    "has-activity-classification": ("activity", "inheritable"),
    "has-name": ("name", "inheritable"),
    "has-organizer": ("organizer", "inheritable"),
    "has-offer-information": ("offers", "inheritable"),
    "has-booking-url": ("url", "inheritable"),
    "has-attendee-instructions": ("attendeeInstructions", "inheritable"),
}
# S1 lineage class -> (evidence_state, mechanism, grade) — verbatim from b0_evidence_substrate_v0_1.py
CLASS_MAP = {
    "ON_CHILD":        ("T", "explicit_on_child",               "explicit"),
    "CHILD_OVERRIDES": ("T", "explicit_on_child_overriding",    "explicit"),
    "BOTH_EQUAL":      ("T", "attested_on_both_sides",          "explicit"),
    "INHERITED":       ("T", "standards_permitted_inheritance", "inherited"),
    "SOURCE_ABSENT":   ("U", "absent_on_child_and_resolved_parent", None),
    "UNRESOLVABLE_PARENT_UNAVAILABLE": ("U", "parent_outside_sample", None),
}
CHILD_ONLY_ABSENT = ("U", "absent_child_only_field", None)
DIGEST_RULE = ("sha256 of canonical JSON of "
               "{query_id, constraints, slate: [candidate_id…], decisions: [[candidate_id, decision, detail]…]}. "
               "CANONICAL JSON is json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False) "
               "encoded UTF-8 — ensure_ascii is False, pinned: a non-ASCII venue name digests differently under True. "
               "CONSTRUCTION ORDER: 'slate' and 'decisions' follow the candidates array order as serialised in this "
               "pack, never a re-sort by candidate_id or by rank. "
               "RANK IS NOT DIGESTED: rank is positional (candidates[i].rank == i+1) and is excluded from the digested "
               "object, so a pack whose rank values were altered without reordering the array still reproduces its "
               "digest — a verifier MUST assert the rank invariant separately. "
               "Provenance is excluded, so identical decisions over identical records digest identically. "
               "Digest reproduction establishes integrity, not validity.")

sha = lambda b: hashlib.sha256(b).hexdigest()
canon = lambda obj: json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
pdir_name = lambda prov: re.sub(r"[^A-Za-z0-9_-]+", "_", prov)[:60]     # the engine's directory rule


def die(msg, code=13):
    print(f"LINEAGE PACK REFUSED (fail-closed): {msg} [exit {code}]", file=sys.stderr)
    raise SystemExit(code)


def _import_reducer():
    try:
        import reducer_v0_1_1 as r
    except ImportError:
        here = Path(__file__).resolve().parent
        sys.path.insert(0, str(here))
        try:
            import reducer_v0_1_1 as r
        except ImportError:
            die("reducer_v0_1_1.py must sit next to this file (the R1 gate is imported, never re-implemented)")
    return r


def _crosscheck_b0():
    """If the B0 substrate is importable, its CLASS_MAP/PREDICATES must equal ours (typed report)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import b0_evidence_substrate_v0_1 as b0
    except ImportError:
        return "b0_evidence_substrate_v0_1 not importable here — CLASS_MAP taken as copied (verbatim, 1 Sep 2026)"
    same_map = b0.CLASS_MAP == CLASS_MAP and tuple(b0.CHILD_ONLY_ABSENT) == CHILD_ONLY_ABSENT
    same_pred = {p: (f, k) for p, f, k in b0.PREDICATES} == PREDICATES
    if not (same_map and same_pred):
        die("CLASS_MAP/PREDICATES differ from b0_evidence_substrate_v0_1.py — the evidence mapping must be one table")
    return "CLASS_MAP and PREDICATES cross-checked equal to b0_evidence_substrate_v0_1.py"


# ---------------- minimal JSON Schema validator (stdlib; the subset the schema uses) ------------
def validate(instance, schema, root=None, path="$"):
    root = root if root is not None else schema
    errs = []
    if "$ref" in schema:
        ref = schema["$ref"]
        assert ref.startswith("#/"), ref
        target = root
        for part in ref[2:].split("/"):
            target = target[part]
        merged = {k: v for k, v in schema.items() if k != "$ref"}
        errs += validate(instance, target, root, path)
        schema = merged
        if not schema:
            return errs
    if "anyOf" in schema:
        branches = [validate(instance, sub, root, path) for sub in schema["anyOf"]]
        if not any(not b for b in branches):
            errs.append(f"{path}: matches none of anyOf ({'; '.join(e for b in branches for e in b[:1])})")
    if "const" in schema and instance != schema["const"]:
        errs.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        tmap = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float),
                "boolean": bool, "null": type(None)}
        ok = False
        for t in types:
            if t == "integer" and isinstance(instance, bool): continue
            if t == "number" and isinstance(instance, bool): continue
            if isinstance(instance, tmap[t]): ok = True
        if not ok:
            errs.append(f"{path}: type {type(instance).__name__} not in {types}")
            return errs
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append(f"{path}: {instance!r} does not match {schema['pattern']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: {instance} < minimum {schema['minimum']}")
    if isinstance(instance, dict):
        for k in schema.get("required", []):
            if k not in instance:
                errs.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errs += validate(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: additional property '{k}' not allowed")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errs.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, it in enumerate(instance):
                errs += validate(it, schema["items"], root, f"{path}[{i}]")
    return errs


# ---------------- run directory access (receipt-bound) ------------------------------------------
class Run:
    def __init__(self, run_dir: Path):
        self.dir = Path(run_dir)
        mr = self.dir / "MASTER_RECEIPT.json"
        if not mr.is_file():
            die(f"no MASTER_RECEIPT.json in {run_dir}")
        self.master_bytes = mr.read_bytes()
        self.master = json.loads(self.master_bytes)
        eng = self.master.get("engine", "")
        if eng not in MIN_ENGINE and not eng.startswith("s1-engine-0.3.") and not eng.startswith("s1-engine-0.4"):
            die(f"run engine '{eng}' lacks page provenance + parent sidecar; need one of {MIN_ENGINE} or later")
        if eng == "s1-engine-0.3-PROPOSED":
            die("run engine v0.3 has no s1_parent_provenance.jsonl sidecar; re-run with v0.3.1+")
        self.per_provider = self.master["outputs"]["per_provider"]
        self._records, self._parents = {}, {}

    def providers(self):
        return sorted(self.per_provider)

    def _load(self, prov):
        if prov in self._records:
            return
        if prov not in self.per_provider:
            die(f"provider '{prov}' not in MASTER_RECEIPT per_provider")
        d = self.dir / pdir_name(prov)
        for fn in ("s1_records.jsonl", "s1_parent_provenance.jsonl"):
            if not (d / fn).is_file():
                die(f"{prov}/{fn} is not in the run directory (a summaries-only copy cannot generate packs; "
                    f"point --run-dir at the full run whose receipt lists this file)")
        rb = (d / "s1_records.jsonl").read_bytes()
        pb = (d / "s1_parent_provenance.jsonl").read_bytes()
        want = self.per_provider[prov]
        if sha(rb) != want["records_sha256"]:
            die(f"{prov}/s1_records.jsonl bytes differ from MASTER_RECEIPT (got {sha(rb)[:12]}, receipt {want['records_sha256'][:12]})")
        if sha(pb) != want.get("parent_provenance_sha256"):
            die(f"{prov}/s1_parent_provenance.jsonl bytes differ from MASTER_RECEIPT")
        by_atid, by_item = {}, {}
        for line in rb.decode("utf-8").splitlines():
            r = json.loads(line)
            by_item[r["item_id"]] = r
            if r.get("@id"):
                if r["@id"] in by_atid:
                    die(f"{prov}: duplicate @id in records: {r['@id']}")
                by_atid[r["@id"]] = r
        parents = {}
        for line in pb.decode("utf-8").splitlines():
            p = json.loads(line)
            parents[p["@id"]] = p
        self._records[prov] = (by_atid, by_item, sha(rb))
        self._parents[prov] = (parents, sha(pb))

    def find(self, candidate_id, prov=None):
        provs = [prov] if prov else self.providers()
        hits = []
        for p in provs:
            self._load(p)
            by_atid, by_item, _ = self._records[p]
            r = by_atid.get(candidate_id) or by_item.get(candidate_id)
            if r is not None:
                hits.append((p, r))
        if not hits:
            die(f"candidate '{candidate_id}' not found in {'provider ' + prov if prov else 'any provider of the run'}")
        if len(hits) > 1:
            die(f"candidate '{candidate_id}' found in {len(hits)} providers — pass 'provider' in the slate")
        return hits[0]

    def parent(self, prov, parent_atid):
        self._load(prov)
        p = self._parents[prov][0].get(parent_atid)
        if p is None:
            die(f"{prov}: parent {parent_atid} cited by a lineage row is absent from s1_parent_provenance.jsonl")
        return p

    def file_receipts(self, provs):
        out = []
        for p in sorted(provs):
            self._load(p)
            out.append({"provider": p, "file": f"{pdir_name(p)}/s1_records.jsonl", "sha256": self._records[p][2],
                        "bound_to_master_receipt": True})
            out.append({"provider": p, "file": f"{pdir_name(p)}/s1_parent_provenance.jsonl", "sha256": self._parents[p][1],
                        "bound_to_master_receipt": True})
        return out


# ---------------- pack construction -------------------------------------------------------------
def _source(role, prov_dict, item_at_id=None):
    return {"role": role, "item": prov_dict.get("rpde_id"), "item_at_id": item_at_id,
            "kind": prov_dict.get("kind"), "source_feed": prov_dict.get("source_feed"),
            "rpde_modified": prov_dict.get("modified"), "page_index": prov_dict.get("page_index"),
            "page_sha256": prov_dict.get("page_sha256"), "page_license": prov_dict.get("page_license")}


def build_constraints(query, reducer):
    cons, spec = [], []
    for c in query.get("constraints", []):
        pid = c.get("predicate_id")
        if pid not in PREDICATES:
            die(f"unknown predicate_id {pid!r}; allowed: {sorted(PREDICATES)}")
        field, _ = PREDICATES[pid]
        m = c.get("matcher")
        if m == "text":
            if not isinstance(c.get("value"), str) or not c["value"].strip():
                die(f"text matcher for {pid} needs a non-empty 'value'")
            pred = reducer.match_text(c["value"])
            spec.append({"predicate_id": pid, "field": field, "matcher": "text", "value": c["value"]})
        elif m == "date_window":
            s, e = c.get("start"), c.get("end")
            if not (isinstance(s, str) and isinstance(e, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)
                    and re.fullmatch(r"\d{4}-\d{2}-\d{2}", e) and s <= e):
                die(f"date_window matcher for {pid} needs ISO 'start' <= 'end'")
            pred = reducer.match_date_window(s, e)
            spec.append({"predicate_id": pid, "field": field, "matcher": "date_window", "start": s, "end": e})
        else:
            die(f"unknown matcher {m!r} for {pid}; allowed: text, date_window")
        cons.append((field, pred))
    if not cons:
        die("query has no constraints")
    return cons, spec


def candidate_entry(run, prov, rec, rank, cons, spec, detail, decision):
    pool = {"supported_match": "supported", "evidence_indeterminate": "indeterminate",
            "bounded_non_match": "non_match"}[decision]
    child_prov = rec.get("provenance") or {}
    parent_atid = rec.get("parent_@id")
    evidence, lineage = [], []
    for c in spec:
        field, pid = c["field"], c["predicate_id"]
        row = (rec.get("lineage") or {}).get(field)
        cls = row.get("class") if isinstance(row, dict) else None
        if cls is None:
            state, mech, grade = CHILD_ONLY_ABSENT
            cls_label, rule = "ABSENT_CHILD_ONLY_FIELD", "M06:child-only (absent => no lineage row)"
        else:
            if cls not in CLASS_MAP:
                die(f"unknown lineage class {cls!r} on {rec.get('item_id')}.{field}")
            state, mech, grade = CLASS_MAP[cls]
            cls_label, rule = cls, row.get("rule", "")
        evidence.append({"predicate_id": pid, "field": field, "evidence_state": state, "lineage_class": cls_label,
                         "grade": grade, "mechanism": mech, "verdict": detail[field]})
        value = rec["fields"].get(field) if state == "T" else None
        entry = {"predicate_id": pid, "field": field, "value": value, "rule": rule, "source": None,
                 "json_path": f"$.data.{field}"}
        if cls_label in ("ON_CHILD", "CHILD_OVERRIDES", "BOTH_EQUAL"):
            entry["source"] = _source("child", child_prov, rec.get("@id"))
            if cls_label in ("CHILD_OVERRIDES", "BOTH_EQUAL"):
                pp = run.parent(prov, parent_atid)
                key = "overridden_source" if cls_label == "CHILD_OVERRIDES" else "corroborating_source"
                entry[key] = _source("parent", pp, parent_atid)
                entry["json_path"] += (" [child value; parent value differs — overridden by rule]" if cls_label == "CHILD_OVERRIDES"
                                       else " [same value attested on child and parent]")
        elif cls_label == "INHERITED":
            pp = run.parent(prov, row.get("parent_@id") or parent_atid)
            entry["source"] = _source("parent", pp, row.get("parent_@id") or parent_atid)
            entry["json_path"] += " [inherited whole-value from SessionSeries parent]"
        elif cls_label == "SOURCE_ABSENT":
            entry["json_path"] += " (absent on child AND resolved parent)"
        elif cls_label == "UNRESOLVABLE_PARENT_UNAVAILABLE":
            entry["json_path"] += f" (absent on child; parent {rec.get('parent_resolution')})"
        else:   # ABSENT_CHILD_ONLY_FIELD
            entry["json_path"] += " (child-only field absent on child)"
        lineage.append(entry)
    return {"candidate_id": rec.get("@id") or rec["item_id"], "item_id": rec["item_id"], "provider": prov,
            "rank": rank, "pool": pool, "decision": decision, "detail": detail,
            "parent_resolution": rec.get("parent_resolution"), "parent_id": parent_atid,
            "evidence": evidence, "lineage": lineage}


def page_receipts(cands, pages_csv, master):
    cited = {}
    for c in cands:
        for l in c["lineage"]:
            for key in ("source", "corroborating_source", "overridden_source"):
                s = l.get(key)
                if s:
                    cited[(s["source_feed"], s["page_index"])] = s["page_sha256"]
    ledger = {"status": "not_supplied"}
    status = "ledger_not_checked"
    if pages_csv:
        pb = Path(pages_csv).read_bytes()
        ledger = {"status": "checked_against_pages_csv", "pages_csv_sha256": sha(pb),
                  "matches_master_receipt": sha(pb) == master.get("pages_csv_sha256")}
        if not ledger["matches_master_receipt"]:
            die("supplied pages.csv is not the ledger the run was verified against (sha differs from MASTER_RECEIPT)")
        expected = {}
        with io.StringIO(pb.decode("utf-8-sig")) as f:
            for row in csv.DictReader(f):
                h = (row.get("sha256") or "").strip().lower()
                if h:
                    expected[(row["feed_id"], int(float(row["page_index"])))] = h
        for (feed, idx), h in sorted(cited.items()):
            if expected.get((feed, idx)) != h:
                die(f"cited page {feed}#{idx} sha {h[:12]} is not the ledger's value {str(expected.get((feed, idx)))[:12]}")
        status = "ledger_bound"
    pages = [{"source_feed": f, "page_index": i, "page_sha256": h, "ledger_status": status}
             for (f, i), h in sorted(cited.items())]
    return pages, ledger


def build_pack(run: Run, query: dict, pages_csv=None, reducer=None):
    reducer = reducer or _import_reducer()
    qid = query.get("query_id")
    if not isinstance(qid, str) or not qid.strip():
        die("query_id missing")
    vintage_label = query.get("vintage_label")
    if not isinstance(vintage_label, str) or not vintage_label.strip():
        die("vintage_label missing from query (e.g. 'V2026-08-27-DEV'); the pack never guesses a vintage role")
    cons, spec = build_constraints(query, reducer)
    slate = query.get("slate")
    if not isinstance(slate, list):
        die("slate must be a list (may be empty)")
    cands, decisions, provs = [], [], set()
    for rank, s in enumerate(slate, 1):
        cid, prov = s.get("candidate_id"), s.get("provider")
        if not isinstance(cid, str) or not cid:
            die(f"slate[{rank - 1}] has no candidate_id")
        prov_found, rec = run.find(cid, prov)
        decision, detail = reducer.reduce_decision(rec, cons)
        cands.append(candidate_entry(run, prov_found, rec, rank, cons, spec, detail, decision))
        decisions.append([cands[-1]["candidate_id"], decision, detail])
        provs.add(prov_found)
    pools = {"supported": sum(c["pool"] == "supported" for c in cands),
             "indeterminate": sum(c["pool"] == "indeterminate" for c in cands),
             "non_match": sum(c["pool"] == "non_match" for c in cands)}
    terminal = ("no_candidates" if not cands else "supported_match" if pools["supported"] else
                "evidence_indeterminate" if pools["indeterminate"] else "bounded_non_match")
    digest = sha(canon({"query_id": qid, "constraints": spec, "slate": [c["candidate_id"] for c in cands],
                        "decisions": decisions}))
    pages, ledger = page_receipts(cands, pages_csv, run.master)
    rules = {e["rule"] for c in cands for e in c["lineage"]}
    limits = [
        "matchers are policy, not logic: 'text' is deep text containment over the record's full normalised value "
        "(not semantic); 'date_window' is ISO date containment (reducer v0.1.1)",
        "bounded_non_match is relative to the declared predicate; a slate-level 'no matches exist' claim additionally "
        "requires the bounded-search argument, which is outside this pack",
        "unit = candidate record (S1); schedule-derived occurrences (S1b) are not candidates in pack v0.1",
        f"vintage label '{vintage_label}' is caller-supplied from the F-04 role table; the pack does not infer roles",
        "digest reproduction establishes INTEGRITY, not VALIDITY: it shows the decisions were not altered, not that "
        "they were correct. Format invariants are not covered by the digest and must be checked separately — "
        "beginning with candidates[i].rank == i+1, which a rank-tampered pack violates while still reproducing "
        "its digest",
    ]
    if any("UNRATIFIED" in r for r in rules):
        limits.append("inheritance under an UNRATIFIED candidate policy (rule strings carry the label) — "
                      "usable for development judgment only until ratified")
    if ledger["status"] == "not_supplied":
        limits.append("page receipts are hash-bound to the run only; pass --pages-csv to bind them to the "
                      "acquisition ledger as well")
    if pools["indeterminate"] and not pools["supported"]:
        limits.append("terminal evidence_indeterminate: at least one constrained dimension is U on every "
                      "non-refuted candidate — abstention is the honest output, not a ranking")
    pack = {
        "_status": f"LINEAGE PACK v0.1 — PROPOSED; generated by {GENERATOR_VERSION} from engine "
                   f"{run.master.get('engine')}; policy {run.master.get('policy')}",
        "pack_schema": PACK_SCHEMA_ID,
        "decision_ref": {"query_id": qid, "task_ref": query.get("task_ref"), "terminal_decision": terminal,
                         "decision_digest": digest, "digest_rule": DIGEST_RULE, "slate_size": len(cands), "pools": pools},
        "query": {"query_id": qid, "task_ref": query.get("task_ref"), "constraints": spec},
        "candidates": cands,
        "receipts": {"master_receipt_sha256": sha(run.master_bytes), "engine_sha256": run.master.get("engine_sha256"),
                     "pages": pages, "files": run.file_receipts(provs), "ledger": ledger},
        "versions": {"corpus_vintage": vintage_label, "snapshot": run.master.get("snapshot"),
                     "engine": run.master.get("engine"), "policy": run.master.get("policy"),
                     "interpretation": run.master.get("interpretation"),
                     "reducer": getattr(reducer, "REDUCER_VERSION", "unknown"),
                     "b0_class_map": "b0-evidence-substrate-0.1-PROPOSED CLASS_MAP (verbatim copy, cross-checked when importable)",
                     "s1b_parameters": run.master.get("s1b_parameters"), "seed": None},
        "limits": limits,
    }
    ranks = [c["rank"] for c in pack["candidates"]]
    if ranks != list(range(1, len(ranks) + 1)):
        die(f"rank invariant violated (generator defect): expected 1..{len(ranks)}, got {ranks}")
    schema = json.loads((Path(__file__).resolve().parent / SCHEMA_FILE).read_text(encoding="utf-8"))
    errs = validate(pack, schema)
    if errs:
        die("generated pack fails its own schema (generator defect): " + "; ".join(errs[:5]))
    return pack


def write_pack(pack, out_path):
    b = (json.dumps(pack, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    Path(out_path).write_bytes(b)
    return sha(b)


# ---------------- self-test (fixture engine run, no inputs) ---------------------------------------
def selftest():
    import contextlib
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import s1_engine_v0_3_1 as eng
    except ImportError:
        die("selftest needs s1_engine_v0_3_1.py next to this file")
    reducer = _import_reducer()
    results = []
    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))
    tmp = Path(tempfile.mkdtemp(prefix="lineage_pack_selftest_"))
    try:
        zpath, pcsv, ledger, terms, page_bytes = eng.build_fixture(tmp / "fixture")
        a = argparse.Namespace(zip=str(zpath), pages_csv=str(pcsv), ledger=str(ledger), terminals=str(terms),
                               snapshot="2026-08-27", zip_sha256=None, continue_on_mismatch=False, parents=[], children=[],
                               out=str(tmp / "run"), horizon_days=28, horizon_status=eng.HORIZON_STATUS_DEFAULT, vintage_date=None)
        with contextlib.redirect_stdout(io.StringIO()):
            eng.run(a)
        run = Run(tmp / "run")
        base = {"vintage_label": "FIXTURE-DEV", "task_ref": "selftest"}
        q_sup = {**base, "query_id": "Q-sup", "constraints": [
            {"predicate_id": "has-located-venue", "matcher": "text", "value": "hall"},
            {"predicate_id": "has-start-datetime", "matcher": "date_window", "start": "2026-09-01", "end": "2026-09-30"}],
            "slate": [{"candidate_id": "https://x.test/session/1", "provider": "Fixture Prov"}]}
        p1 = build_pack(run, q_sup, str(pcsv), reducer)
        c = p1["candidates"][0]
        check("supported: terminal supported_match, pool supported", p1["decision_ref"]["terminal_decision"] == "supported_match" and c["pool"] == "supported")
        loc = next(l for l in c["lineage"] if l["field"] == "location")
        check("INHERITED location binds to the PARENT's served page (A on page 1) + parent role",
              loc["source"]["role"] == "parent" and loc["source"]["page_index"] == 1
              and loc["source"]["page_sha256"] == sha(page_bytes[("fix-sessionseries", 1)]) and loc["source"]["item_at_id"] == "https://x.test/series/A"
              and loc["value"] == {"@type": "Place", "name": "Hall"}, json.dumps(loc))
        sd = next(l for l in c["lineage"] if l["field"] == "startDate")
        check("ON_CHILD startDate binds to the CHILD's served page (page 0)",
              sd["source"]["role"] == "child" and sd["source"]["page_index"] == 0 and sd["source"]["page_sha256"] == sha(page_bytes[("fix-scheduledsession", 0)]))
        ev = {e["field"]: e for e in c["evidence"]}
        check("evidence rows: location T/inherited/standards_permitted_inheritance; startDate T/explicit",
              ev["location"]["grade"] == "inherited" and ev["location"]["mechanism"] == "standards_permitted_inheritance"
              and ev["startDate"]["grade"] == "explicit" and ev["startDate"]["verdict"] == "T:satisfied")
        check("page receipts: both cited pages ledger_bound against pages.csv; ledger sha matches MASTER_RECEIPT",
              len(p1["receipts"]["pages"]) == 2 and all(p["ledger_status"] == "ledger_bound" for p in p1["receipts"]["pages"])
              and p1["receipts"]["ledger"]["matches_master_receipt"] is True)
        check("file receipts: records + sidecar for the provider, bound to MASTER_RECEIPT",
              {f["file"] for f in p1["receipts"]["files"]} == {"Fixture_Prov/s1_records.jsonl", "Fixture_Prov/s1_parent_provenance.jsonl"})
        # indeterminate: activity is SOURCE_ABSENT on c1 (A has no activity)
        q_ind = {**q_sup, "query_id": "Q-ind", "constraints": q_sup["constraints"] + [{"predicate_id": "has-activity-classification", "matcher": "text", "value": "yoga"}]}
        p2 = build_pack(run, q_ind, str(pcsv), reducer)
        act = next(e for e in p2["candidates"][0]["evidence"] if e["field"] == "activity")
        actl = next(l for l in p2["candidates"][0]["lineage"] if l["field"] == "activity")
        check("indeterminate: activity U / SOURCE_ABSENT / no source / value null; terminal evidence_indeterminate + abstention limit",
              p2["decision_ref"]["terminal_decision"] == "evidence_indeterminate" and act["evidence_state"] == "U"
              and act["lineage_class"] == "SOURCE_ABSENT" and actl["source"] is None and actl["value"] is None
              and any("abstention" in l for l in p2["limits"]))
        # non-match: venue text absent everywhere on c1
        q_non = {**q_sup, "query_id": "Q-non", "constraints": [{"predicate_id": "has-located-venue", "matcher": "text", "value": "aquatics centre"}]}
        p3 = build_pack(run, q_non, str(pcsv), reducer)
        check("non-match: bounded_non_match with T:unsatisfied verdict", p3["decision_ref"]["terminal_decision"] == "bounded_non_match"
              and p3["candidates"][0]["evidence"][0]["verdict"] == "T:unsatisfied")
        # unresolvable parent: c4 -> location U via UNRESOLVABLE_PARENT_UNAVAILABLE
        q_unr = {**q_sup, "query_id": "Q-unr", "constraints": [{"predicate_id": "has-located-venue", "matcher": "text", "value": "hall"}],
                 "slate": [{"candidate_id": "c4"}]}
        p4 = build_pack(run, q_unr, None, reducer)
        e4 = p4["candidates"][0]["evidence"][0]
        check("unresolvable parent: U / UNRESOLVABLE_PARENT_UNAVAILABLE / parent_outside_sample; found by item_id without provider",
              e4["evidence_state"] == "U" and e4["lineage_class"] == "UNRESOLVABLE_PARENT_UNAVAILABLE" and e4["mechanism"] == "parent_outside_sample"
              and p4["candidates"][0]["parent_resolution"] == "PARENT_NOT_IN_SAMPLE")
        check("no pages.csv: page receipts ledger_not_checked and the limit says so",
              all(p["ledger_status"] == "ledger_not_checked" for p in p4["receipts"]["pages"]) and any("--pages-csv" in l for l in p4["limits"]))
        # child overrides: c3 has its own name -> CHILD_OVERRIDES with overridden parent source
        q_ov = {**q_sup, "query_id": "Q-ov", "constraints": [{"predicate_id": "has-name", "matcher": "text", "value": "own name"}],
                "slate": [{"candidate_id": "c3", "provider": "Fixture Prov"}]}
        p5 = build_pack(run, q_ov, str(pcsv), reducer)
        l5 = p5["candidates"][0]["lineage"][0]
        check("CHILD_OVERRIDES: child source + overridden parent source both bound to pages",
              l5["source"]["role"] == "child" and l5.get("overridden_source", {}).get("role") == "parent"
              and l5["overridden_source"]["page_index"] == 1 and p5["decision_ref"]["terminal_decision"] == "supported_match")
        # child-only absent field: endDate on c1 has no lineage row -> ABSENT_CHILD_ONLY_FIELD is not a predicate in v0.1 (only startDate is child-only);
        # multi-candidate slate: c1 supported + c4 indeterminate -> terminal supported, pools 1/1/0, ranks preserved
        q_multi = {**q_sup, "query_id": "Q-multi", "slate": [{"candidate_id": "c4", "provider": "Fixture Prov"}, {"candidate_id": "https://x.test/session/1", "provider": "Fixture Prov"}]}
        p6 = build_pack(run, q_multi, str(pcsv), reducer)
        check("multi-candidate slate: pools supported 1 / indeterminate 1; terminal supported_match; ranks 1,2 preserved",
              p6["decision_ref"]["pools"] == {"supported": 1, "indeterminate": 1, "non_match": 0}
              and p6["decision_ref"]["terminal_decision"] == "supported_match" and [c["rank"] for c in p6["candidates"]] == [1, 2])
        q_empty = {**q_sup, "query_id": "Q-empty", "slate": []}
        p7 = build_pack(run, q_empty, str(pcsv), reducer)
        check("empty slate: terminal no_candidates, digest still defined", p7["decision_ref"]["terminal_decision"] == "no_candidates" and len(p7["decision_ref"]["decision_digest"]) == 64)
        # determinism + digest stability
        s1 = write_pack(build_pack(Run(tmp / "run"), q_multi, str(pcsv), reducer), tmp / "p_a.json")
        s2 = write_pack(build_pack(Run(tmp / "run"), q_multi, str(pcsv), reducer), tmp / "p_b.json")
        check("determinism: same run + same query -> byte-identical pack", s1 == s2)
        check("digest excludes provenance: digest identical across the two builds and differs between queries",
              p6["decision_ref"]["decision_digest"] == json.loads((tmp / "p_b.json").read_text())["decision_ref"]["decision_digest"]
              and p1["decision_ref"]["decision_digest"] != p2["decision_ref"]["decision_digest"])
        # schema validation of every pack + a deliberately broken pack
        schema = json.loads((Path(__file__).resolve().parent / SCHEMA_FILE).read_text(encoding="utf-8"))
        check("all packs validate against lineage_pack_schema_v0_1.json", all(not validate(p, schema) for p in (p1, p2, p3, p4, p5, p6, p7)))
        broken = json.loads(json.dumps(p1)); broken["candidates"][0]["pool"] = "maybe"; broken["extra"] = 1
        errs = validate(broken, schema)
        check("validator catches an out-of-enum pool and an additional property", len(errs) == 2 and any("enum" in e for e in errs) and any("additional" in e for e in errs), json.dumps(errs))
        # fail-closed paths
        def refused(fn):
            try:
                with contextlib.redirect_stderr(io.StringIO()):
                    fn()
            except SystemExit as e:
                return e.code == 13
            return False
        check("refuses unknown predicate / matcher / missing vintage label",
              refused(lambda: build_pack(run, {**q_sup, "constraints": [{"predicate_id": "has-colour", "matcher": "text", "value": "x"}]}, None, reducer))
              and refused(lambda: build_pack(run, {**q_sup, "constraints": [{"predicate_id": "has-name", "matcher": "regex", "value": "x"}]}, None, reducer))
              and refused(lambda: build_pack(run, {k: v for k, v in q_sup.items() if k != "vintage_label"}, None, reducer)))
        check("refuses an unknown candidate id", refused(lambda: build_pack(run, {**q_sup, "slate": [{"candidate_id": "nope"}]}, None, reducer)))
        # tamper the records file -> refused (bytes differ from MASTER_RECEIPT)
        shutil.copytree(tmp / "run", tmp / "run_t")
        rp = tmp / "run_t" / "Fixture_Prov" / "s1_records.jsonl"
        rp.write_bytes(rp.read_bytes().replace(b"Yoga v2", b"Yoga v9"))
        check("tampered records file: refused (hash differs from MASTER_RECEIPT)", refused(lambda: build_pack(Run(tmp / "run_t"), q_sup, None, reducer)))
        # tamper pages.csv -> refused (not the ledger the run verified against)
        pc = tmp / "pages_t.csv"; pc.write_text(pcsv.read_text().replace("0", "1", 1))
        check("foreign pages.csv: refused (sha differs from MASTER_RECEIPT)", refused(lambda: build_pack(run, q_sup, str(pc), reducer)))
        check("engine gate: a v0.2.2-style receipt is refused",
              refused(lambda: (lambda d: (d.mkdir(), (d / "MASTER_RECEIPT.json").write_text(json.dumps({"engine": "s1-engine-0.2.2-PROPOSED", "outputs": {"per_provider": {}}})), Run(d)))(tmp / "old")))
        check("b0 cross-check", _crosscheck_b0().startswith("CLASS_MAP and PREDICATES cross-checked") or "not importable" in _crosscheck_b0())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    width = max(len(n) for n, _, _ in results)
    for n, ok, det in results:
        print(("OK   " if ok else "FAIL ") + n.ljust(width) + ("" if ok or not det else "   <- " + det))
    n_ok = sum(1 for _, ok, _ in results if ok)
    print(f"\nSELFTEST: {n_ok}/{len(results)} checks pass — " + ("ALL PASS" if n_ok == len(results) else "STOP: failures above"))
    return 0 if n_ok == len(results) else 1


def main():
    ap = argparse.ArgumentParser(description="Generate a lineage pack v0.1 from an S1 v0.3.1+ run and a query file.")
    ap.add_argument("--run-dir"); ap.add_argument("--query"); ap.add_argument("--out")
    ap.add_argument("--pages-csv", help="Wesley's pages.csv for the run's snapshot: binds every cited page to the acquisition ledger")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.run_dir and a.query and a.out):
        ap.error("--run-dir, --query and --out are required (or --selftest)")
    print(_crosscheck_b0(), file=sys.stderr)
    query = json.loads(Path(a.query).read_text(encoding="utf-8"))
    pack = build_pack(Run(a.run_dir), query, a.pages_csv)
    digest = write_pack(pack, a.out)
    print(json.dumps({"pack": a.out, "pack_sha256": digest, "query_id": pack["decision_ref"]["query_id"],
                      "terminal_decision": pack["decision_ref"]["terminal_decision"],
                      "decision_digest": pack["decision_ref"]["decision_digest"],
                      "pools": pack["decision_ref"]["pools"], "pages_cited": len(pack["receipts"]["pages"]),
                      "ledger": pack["receipts"]["ledger"]["status"]}, indent=1))


if __name__ == "__main__":
    main()
