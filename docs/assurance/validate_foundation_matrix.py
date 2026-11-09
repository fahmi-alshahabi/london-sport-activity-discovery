#!/usr/bin/env python3
"""
K7 foundation-matrix validator + reading-log renderer (WP §18.1/§18.3, CA-5).

Checks that the reading register is structurally sound and enforces the WP §18.3
discipline, then renders a human-readable reading log and reports attestation
progress. Stdlib only.

Usage:
    python validate_foundation_matrix.py          # validate + render, report progress
    python validate_foundation_matrix.py --strict  # also FAIL unless every load-bearing
                                                    # source is fully attested

Structural/semantic errors exit non-zero. Un-read sources are NOT an error by default
(reading is Clarence's ongoing task); --strict makes full attestation a hard gate.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "foundation-matrix.json")
OUT = os.path.join(HERE, "reading-log.md")

REQUIRED_SOURCE_KEYS = [
    "source_id", "theme", "citation_as_given", "full_citation_proposed",
    "supports", "load_bearing", "priority", "attestation",
]
REQUIRED_ATTEST_KEYS = [
    "publication_status_version", "database_or_authority", "version_of_record",
    "date_accessed", "sections_pages_read", "claim_supported",
    "exact_limit_or_non_claim", "clarence_independent_verdict",
    "new_finding_or_correction", "reviewer", "personally_read",
]
# Fields that must be non-empty once a source is marked personally_read=true.
ATTEST_ON_READ = [
    "date_accessed", "sections_pages_read", "claim_supported",
    "exact_limit_or_non_claim", "clarence_independent_verdict",
]


def load():
    with open(MATRIX, encoding="utf-8") as fh:
        return json.load(fh)


def vor(attest):
    v = attest.get("version_of_record") or {}
    return (v.get("doi") or "").strip(), bool(v.get("verified"))


def is_attested(src):
    a = src["attestation"]
    doi, verified = vor(a)
    return (
        bool(a.get("personally_read"))
        and doi != ""
        and verified
        and (a.get("clarence_independent_verdict") or "").strip() != ""
    )


def validate(data):
    errors, warnings = [], []

    if not isinstance(data.get("sources"), list) or not data["sources"]:
        errors.append("no 'sources' array")
        return errors, warnings
    if "meta" not in data:
        warnings.append("no 'meta' block")

    seen = set()
    for i, src in enumerate(data["sources"]):
        sid = src.get("source_id", f"<index {i}>")
        for k in REQUIRED_SOURCE_KEYS:
            if k not in src:
                errors.append(f"{sid}: missing key '{k}'")
        if sid in seen:
            errors.append(f"{sid}: duplicate source_id")
        seen.add(sid)

        if "attestation" not in src:
            continue
        a = src["attestation"]
        for k in REQUIRED_ATTEST_KEYS:
            if k not in a:
                errors.append(f"{sid}: attestation missing '{k}'")
        if "version_of_record" in a:
            v = a["version_of_record"]
            if not isinstance(v, dict) or "doi" not in v or "verified" not in v:
                errors.append(f"{sid}: version_of_record needs 'doi' and 'verified'")

        if src.get("load_bearing") and not src.get("supports"):
            errors.append(f"{sid}: load_bearing but no 'supports' claim bound (CA-5 is per-claim)")

        # Discipline: cannot mark read without completing the record.
        if a.get("personally_read"):
            missing = [k for k in ATTEST_ON_READ if not (a.get(k) or "").strip()]
            if missing:
                errors.append(
                    f"{sid}: personally_read=true but incomplete record — fill: {', '.join(missing)}"
                )
            doi, verified = vor(a)
            if not doi or not verified:
                errors.append(
                    f"{sid}: personally_read=true but version of record not verified "
                    f"(set version_of_record.doi and verified=true)"
                )

        # WP §18.3 preprint rule.
        status = (a.get("publication_status_version") or "").lower()
        if src.get("load_bearing") and ("preprint" in status or "arxiv" in status):
            if not a.get("no_archival_vor_exists"):
                errors.append(
                    f"{sid}: load-bearing preprint — cite the version of record, or set "
                    f"attestation.no_archival_vor_exists=true only if you confirmed none exists (§18.3)"
                )

        # Nudge to de-cluster unnamed sources.
        if "[IDENTIFY]" in (src.get("full_citation_proposed") or ""):
            warnings.append(f"{sid}: still a theme cluster — identify the specific source (CA-5)")

    return errors, warnings


def render(data):
    sources = data["sources"]
    lb = [s for s in sources if s.get("load_bearing")]
    attested = [s for s in lb if is_attested(s)]
    n_att, n_lb = len(attested), len(lb)

    def status_icon(s):
        a = s["attestation"]
        if is_attested(s):
            return "✅ attested"
        if a.get("personally_read"):
            return "⚠ incomplete"
        return "◻ to read"

    lines = []
    lines.append("# Reading log — K7 foundation matrix (CA-5)\n")
    lines.append("> **GENERATED FILE** — edit `foundation-matrix.json`, then run "
                 "`python validate_foundation_matrix.py`. Do not hand-edit this markdown.\n")
    meta = data.get("meta", {})
    if meta.get("authorship_notice"):
        lines.append(f"> **Authorship notice.** {meta['authorship_notice']}\n")
    lines.append(f"**K7 attestation: {n_att}/{n_lb} load-bearing sources attested.** "
                 f"A source is attested only when you have personally read it, recorded a verified "
                 f"version-of-record DOI, and written your own verdict (WP §18.3).\n")

    unread_high = [s for s in lb if s.get("priority") == "high" and not is_attested(s)]
    if unread_high:
        lines.append("**Read these first (high priority, not yet attested):** "
                     + ", ".join(f"{s['source_id']} {s['citation_as_given']}" for s in unread_high) + "\n")

    themes = []
    for s in sources:
        if s["theme"] not in themes:
            themes.append(s["theme"])

    for theme in themes:
        lines.append(f"\n## {theme}\n")
        lines.append("| ID | Source (verify against version of record) | Priority | Supports | VoR DOI | Status |")
        lines.append("|----|------|----------|----------|---------|--------|")
        for s in [x for x in sources if x["theme"] == theme]:
            doi, _ = vor(s["attestation"])
            lines.append(
                f"| {s['source_id']} | {s['citation_as_given']} | {s.get('priority','')} | "
                f"{', '.join(s.get('supports', []))} | {doi or '—'} | {status_icon(s)} |"
            )

    lines.append("\n---\n")
    lines.append("**How to complete a row:** read the primary source; in `foundation-matrix.json` set "
                 "that source's `attestation.personally_read=true`, fill `version_of_record.doi` + set "
                 "`verified=true`, and complete `date_accessed`, `sections_pages_read`, `claim_supported`, "
                 "`exact_limit_or_non_claim` and — in your own words — `clarence_independent_verdict`. "
                 "Re-run the validator; the row flips to ✅ and the counter advances.\n")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return n_att, n_lb


def main():
    strict = "--strict" in sys.argv
    data = load()
    errors, warnings = validate(data)

    for w in warnings:
        print(f"[warn] {w}")
    if errors:
        print("\nFOUNDATION MATRIX INVALID:")
        for e in errors:
            print(f"  [FAIL] {e}")
        sys.exit(1)

    n_att, n_lb = render(data)
    print(f"FOUNDATION MATRIX OK: {len(data['sources'])} sources, structure sound.")
    print(f"K7 attestation: {n_att}/{n_lb} load-bearing sources attested "
          f"({'complete' if n_att == n_lb else 'PENDING — Clarence to read'}).")
    print(f"Rendered {os.path.relpath(OUT, HERE)}")

    if strict and n_att < n_lb:
        print("[strict] FAIL: not every load-bearing source is attested.")
        sys.exit(2)


if __name__ == "__main__":
    main()
