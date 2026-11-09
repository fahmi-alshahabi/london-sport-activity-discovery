#!/usr/bin/env python3
"""
C-14 security validator (WP §12.8, §15.4).

AI-ASSISTED SCAFFOLD. NOT authorship evidence; a security/assurance reviewer signs residuals and
infrastructure controls are Wesley's (Section 16). Checks:
  1. the threat register covers the required §12.8 categories and has no orphan (control + evidence +
     owner + valid status on every threat);
  2. the sanitisers actually work (spreadsheet formula injection neutralised; javascript:/data: URLs
     blocked; HTML escaped);
  3. no obvious secret is committed (AKIA keys, private-key blocks, key = "long-value");
  4. every provider link in the shipped scenarios is an http(s) URL.

Run:  python validate_security.py
"""
from __future__ import annotations
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
REG = json.load(open(os.path.join(HERE, "threat-register.json")))
sys.path.insert(0, HERE)
import sanitize  # noqa: E402

REQUIRED = {
    "prompt_injection", "arbitrary_execution", "authorization", "disclosure",
    "receipt_forgery_version", "stale_replay", "unsafe_html_url", "spreadsheet_formula_injection",
    "dos_cost_abuse", "model_supply_chain_drift", "malicious_staff_action",
    "telemetry_reidentification", "deceptive_interface_automation_bias",
    "deletion_withdrawal_failure", "incident_concealment_unowned_residual",
}
SCAN_EXT = {".py", ".json", ".md", ".html", ".css", ".ts", ".tsx", ".txt", ".yml", ".yaml", ".ini", ".cfg", ".js"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "dist", "enhanced", ".venv"}
SKIP_FILES = {os.path.abspath(__file__)}
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9/\+_\-]{16,}['\"]"),
]


def check_register():
    errs = []
    allowed = set(REG["statuses_allowed"])
    ids = {t["id"] for t in REG["threats"]}
    for req in sorted(REQUIRED - ids):
        errs.append(f"threat register missing required category: {req}")
    for t in REG["threats"]:
        for k in ("threat", "control", "evidence", "owner"):
            if not t.get(k):
                errs.append(f"threat '{t.get('id','?')}' missing {k}")
        if t.get("status") not in allowed:
            errs.append(f"threat '{t.get('id','?')}' status not in {sorted(allowed)}")
    return errs


def check_sanitisers():
    errs = []
    cases = [("=1+1", "'=1+1"), ("+cmd", "'+cmd"), ("-2", "'-2"), ("@x", "'@x"), ("Tai Chi", "Tai Chi")]
    for raw, exp in cases:
        if sanitize.csv_field(raw) != exp:
            errs.append(f"csv_field({raw!r}) != {exp!r}")
    if sanitize.safe_url("javascript:alert(1)") != "":
        errs.append("safe_url did not block javascript:")
    if sanitize.safe_url("data:text/html,x") != "":
        errs.append("safe_url did not block data:")
    if sanitize.safe_url("https://example.org/x") != "https://example.org/x":
        errs.append("safe_url blocked a valid https URL")
    if sanitize.escape_html("<b>&\"") != "&lt;b&gt;&amp;&quot;":
        errs.append("escape_html incorrect")
    return errs


def secret_scan():
    hits = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in SCAN_EXT:
                continue
            path = os.path.join(root, fn)
            if os.path.abspath(path) in SKIP_FILES:
                continue
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for pat in SECRET_PATTERNS:
                if pat.search(text):
                    hits.append(os.path.relpath(path, REPO))
                    break
    return hits


def provider_link_scan():
    errs = []
    scen = os.path.join(REPO, "apps", "public-discovery", "server", "scenarios")
    for fn in os.listdir(scen):
        if not fn.endswith(".json"):
            continue
        env = json.load(open(os.path.join(scen, fn)))
        for c in (env.get("payload", {}).get("decision", {}) or {}).get("candidates", []):
            link = c.get("provider_link", "")
            if link and not sanitize.safe_url(link):
                errs.append(f"{fn}: unsafe provider_link {link}")
    return errs


def main():
    fails = 0
    for label, errs in [("threat register", check_register()),
                        ("sanitisers", check_sanitisers()),
                        ("provider links", provider_link_scan())]:
        print(f"[{'OK ' if not errs else 'BAD'}] {label}")
        for e in errs:
            print("   -", e)
        fails += len(errs)
    hits = secret_scan()
    print(f"[{'OK ' if not hits else 'BAD'}] secret scan ({'clean' if not hits else 'HITS'})")
    for h in hits:
        print("   - possible secret in", h)
    fails += len(hits)

    print("\nRESULT:", "SECURITY MODEL OK" if fails == 0 else f"{fails} PROBLEM(S)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
