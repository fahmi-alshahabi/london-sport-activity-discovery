#!/usr/bin/env python3
"""
C-13 privacy / telemetry validator (WP §12.4/§12.5/§13.3, C-BLOCK-07).

AI-ASSISTED SCAFFOLD. NOT authorship evidence; controller/processor and lawful-basis determinations
are governance decisions (RATIFY-15-02/04), not Clarence's to issue.

Checks:
  1. the telemetry dictionary and the C-17 event schema describe EXACTLY the same fields (no
     undocumented field can be logged, and no documented field is missing from the contract);
  2. every field declares personal_data, a retention class and a minimisation note;
  3. transient-by-default, and personal-data fields default to transient/session only (minimisation);
  4. no forbidden concept (raw utterance / exact location / free text / access needs) is a field;
  5. the four information planes and the cross-plane join rule are present.

Run:  python validate_privacy.py
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DICT = json.load(open(os.path.join(HERE, "telemetry-dictionary.json")))
EVSCHEMA = json.load(open(os.path.join(REPO, "packages", "evaluation", "event-schema.json")))

FORBIDDEN_SUBSTR = ["utterance", "postcode", "lat", "lon", "free_text", "raw", "location", "address", "access_need"]
EXPECTED_PLANES = {"restricted_source", "public_service", "staff_ops", "approved_research"}
MINIMISED_DEFAULTS = {"transient", "session"}


def main():
    errs = []
    fields = DICT["fields"]
    schema_props = set(EVSCHEMA["properties"])
    dict_props = set(fields)

    # 1. parity
    missing = schema_props - dict_props
    extra = dict_props - schema_props
    if missing:
        errs.append(f"event fields not documented in the telemetry dictionary: {sorted(missing)}")
    if extra:
        errs.append(f"telemetry dictionary documents fields not in the event schema: {sorted(extra)}")

    # 2/3. per-field discipline
    classes = set(DICT["retention_classes"])
    for name, f in fields.items():
        if not isinstance(f.get("personal_data"), bool):
            errs.append(f"{name}: personal_data must be boolean")
        if f.get("retention_class_default") not in classes:
            errs.append(f"{name}: retention_class_default not in {sorted(classes)}")
        if not f.get("purpose") or not f.get("minimisation"):
            errs.append(f"{name}: missing purpose/minimisation")
        if f.get("personal_data") and f.get("retention_class_default") not in MINIMISED_DEFAULTS:
            errs.append(f"{name}: personal-data field must default to transient/session (minimisation), got {f.get('retention_class_default')}")

    if not DICT.get("transient_by_default"):
        errs.append("transient_by_default must be true")

    # 4. forbidden concepts must not be fields
    for name in schema_props | dict_props:
        if any(s in name.lower() for s in FORBIDDEN_SUBSTR):
            errs.append(f"forbidden concept exposed as a field: {name}")
    for fb in DICT.get("forbidden_fields", []):
        if fb in schema_props:
            errs.append(f"forbidden field present in event schema: {fb}")

    # 5. planes
    if set(DICT.get("planes", {})) != EXPECTED_PLANES:
        errs.append(f"planes must be exactly {sorted(EXPECTED_PLANES)}")
    if not DICT.get("cross_plane_join_rules"):
        errs.append("cross_plane_join_rules missing")

    if errs:
        print("PRIVACY MODEL INVALID:")
        for e in errs:
            print("  -", e)
        return 1
    pii = [n for n, f in fields.items() if f["personal_data"]]
    print("PRIVACY MODEL OK — dictionary matches the event schema exactly; transient-by-default.")
    print(f"  {len(fields)} fields; personal-data fields (transient/session only): {pii}")
    print(f"  planes: {sorted(DICT['planes'])}; forbidden concepts cannot be logged by construction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
