"""
Benchmark task linter.

Validates task files against task.schema.json and, more importantly, against
the CROSS-TASK invariants the schema cannot express on its own - above all the
F-07 PD-6 leakage rule: every task sharing a task_template_id must land in the
same split. A violation there silently contaminates the confirmatory run.

Usage:
    python lint_tasks.py tasks/                 # lint a directory of .json files
    python lint_tasks.py tasks/ --schema task.schema.json

Exit code 0 = clean, 1 = violations found (so CI can gate on it).

Scope: structure only. This never inspects task quality, difficulty or wording -
those are authorship questions, gated on RATIFY-19-06.

Author: Fahmi Alshahabi (evaluation stream)
Status: v0.1 - scaffolding permitted under CA-01 Part 3.4.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False


# ---------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------

def load_tasks(path):
    """Load every .json file under path. Returns (tasks, load_errors)."""
    tasks, errors = [], []
    files = sorted(Path(path).rglob("*.json"))
    if not files:
        errors.append(f"no .json files found under {path}")
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{f}: invalid JSON - {e}")
            continue
        for item in (data if isinstance(data, list) else [data]):
            item["_source_file"] = str(f)
            tasks.append(item)
    return tasks, errors


# ---------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------

def validate_schema(tasks, schema_path):
    """Per-task structural validation. Returns a list of violation strings."""
    if not HAVE_JSONSCHEMA:
        return ["jsonschema not installed - schema checks SKIPPED "
                "(pip install jsonschema). Cross-task checks still ran."]
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    violations = []
    for t in tasks:
        payload = {k: v for k, v in t.items() if k != "_source_file"}
        for err in sorted(validator.iter_errors(payload), key=lambda e: e.path):
            where = ".".join(str(p) for p in err.path) or "(root)"
            tid = t.get("task_id", "?")
            violations.append(f"{tid} [{where}]: {err.message}")
    return violations


# ---------------------------------------------------------------------
# Cross-task invariants - the part the schema cannot check
# ---------------------------------------------------------------------

def check_unique_ids(tasks):
    seen, violations = defaultdict(list), []
    for t in tasks:
        seen[t.get("task_id")].append(t.get("_source_file"))
    for tid, files in seen.items():
        if len(files) > 1:
            violations.append(f"duplicate task_id {tid} in: {', '.join(files)}")
    return violations


def check_template_split_integrity(tasks):
    """
    F-07 PD-6, the critical one: a task_template_id must not span splits.
    If it does, a DEV paraphrase of a LOCKED task exists and the
    confirmatory run is contaminated.
    """
    by_template = defaultdict(set)
    for t in tasks:
        tt, sp = t.get("task_template_id"), t.get("split")
        if tt and sp:
            by_template[tt].add(sp)
    return [
        f"LEAKAGE: template {tt} spans splits {sorted(splits)} "
        f"- all tasks sharing a template must be in one split (F-07 PD-6)"
        for tt, splits in by_template.items() if len(splits) > 1
    ]


def check_paraphrase_grouping(tasks):
    """A paraphrase must share its parent's template id, and the parent must exist."""
    by_id = {t.get("task_id"): t for t in tasks}
    violations = []
    for t in tasks:
        parent_id = t.get("paraphrase_of")
        if not parent_id:
            continue
        parent = by_id.get(parent_id)
        if parent is None:
            violations.append(
                f"{t.get('task_id')}: paraphrase_of {parent_id} which does not exist")
        elif parent.get("task_template_id") != t.get("task_template_id"):
            violations.append(
                f"{t.get('task_id')}: paraphrase of {parent_id} but template ids "
                f"differ ({t.get('task_template_id')} vs "
                f"{parent.get('task_template_id')}) - breaks leakage grouping")
    return violations


def check_hard_constraint_present(tasks):
    """Every task needs at least one hard constraint, or the gate has nothing to evaluate."""
    return [
        f"{t.get('task_id')}: no hard constraint - the evidence gate would have "
        f"nothing to evaluate"
        for t in tasks
        if not any(c.get("hardness") == "hard" for c in t.get("constraints", []))
    ]


# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------

def summarise(tasks):
    counts = {
        "total": len(tasks),
        "templates": len({t.get("task_template_id") for t in tasks}),
        "by_split": defaultdict(int),
        "by_family": defaultdict(int),
        "by_suite": defaultdict(int),
    }
    for t in tasks:
        counts["by_split"][t.get("split", "?")] += 1
        counts["by_family"][t.get("family", "?")] += 1
        counts["by_suite"][t.get("suite", "?")] += 1
    return counts


def main():
    ap = argparse.ArgumentParser(description="Lint benchmark task files.")
    ap.add_argument("path", help="directory containing task .json files")
    ap.add_argument("--schema", default="task.schema.json")
    args = ap.parse_args()

    tasks, load_errors = load_tasks(args.path)

    violations = []
    violations += load_errors
    if tasks:
        violations += validate_schema(tasks, args.schema)
        violations += check_unique_ids(tasks)
        violations += check_template_split_integrity(tasks)
        violations += check_paraphrase_grouping(tasks)
        violations += check_hard_constraint_present(tasks)

    if tasks:
        s = summarise(tasks)
        print(f"Tasks: {s['total']}   Templates: {s['templates']}")
        print(f"  by split:  {dict(s['by_split'])}")
        print(f"  by suite:  {dict(s['by_suite'])}")
        print(f"  by family: {dict(s['by_family'])}")
        print()

    if violations:
        print(f"FAIL - {len(violations)} issue(s):\n")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print("PASS - all structural and cross-task checks clean.")
    sys.exit(0)


if __name__ == "__main__":
    main()
