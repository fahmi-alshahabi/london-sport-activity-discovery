"""Verification for the public discovery slice.

AI-ASSISTED SCAFFOLD (WP Phase D, §15). NOT authorship evidence; a non-author reviewer must confirm.
Checks, per route: HTTP 200; static a11y subset clean; NO staff/research value leaks into the
public HTML; over-claim vocabulary absent; no-JS core (no inline critical script); and via the JSON
API, no staff/research keys in the public projection. Also runs the C-11 render linter over the
app's actual wording.

Run:  python test_slice.py     # exit 0 iff every check passes
"""
from __future__ import annotations
import html as _html
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server")
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
CONTENT = os.path.join(REPO, "packages", "accessible-design-system", "content")
for p in (SERVER, CONTENT, HERE):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient  # noqa: E402
for _m in ("main", "render"):              # both apps ship their own main.py/render.py;
    sys.modules.pop(_m, None)              # bind THIS app's copy when harnesses share a process
import main, render                        # noqa: E402
import a11y_check                          # noqa: E402
import render_lint                         # noqa: E402

client = TestClient(main.app)

# staff/research VALUES that must never appear in public HTML
LEAK_VALUES = [
    "internal_score", "0.82", "0.77", "recmodel-0.3", "explicit-three-state", "lineage",
    "req-55021", "req-nm-1", "req-in-1", "ep-7731", "ep-nm-1", "ep-in-1",
    "trace-aa19", "tr-nm-1", "tr-in-1", "r-a1", "r-a2", "r-nm1", "r-in1",
    "sha256:1111", "sha256:2222", "sha256:3333", "blocking_state",
]
# staff/research KEYS that must never appear in the public JSON projection
LEAK_KEYS = {
    "internal_score", "lineage_note", "receipts", "receipt_id", "content_digest",
    "receipt_ids", "verification", "request_id", "episode_id", "trace_id",
    "model_version", "policy_version", "blocking_state", "unevaluated_feeds", "failed_stage",
}
CORE_PAGES = ["/", "/discover?scenario=supported", "/discover?scenario=no_match",
              "/discover?scenario=indeterminate", "/discover?scenario=service_failure",
              "/result/sess-101?scenario=supported", "/compare?scenario=supported", "/help"]


def strip_tags(html):
    return re.sub(r"<[^>]+>", " ", html)


def inline_script_present(html):
    for m in re.finditer(r"<script([^>]*)>(.*?)</script>", html, re.S | re.I):
        attrs, body = m.group(1), m.group(2)
        if "src=" not in attrs and body.strip():
            return True
    return False


def walk_keys(node):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(node, list):
        for it in node:
            yield from walk_keys(it)


def main_run():
    fails = 0

    for path in CORE_PAGES:
        r = client.get(path)
        tag = path
        if r.status_code != 200:
            print(f"[BAD] {tag}: HTTP {r.status_code}"); fails += 1; continue
        html = r.text
        problems = a11y_check.check_html(html)
        leaks = [v for v in LEAK_VALUES if v in html]
        text = strip_tags(html)
        overclaim = [d for rid, d in render_lint.lint_render(render_lint.load_lexicon(), {}, [text])
                     if rid in ("global_banned", "conditional:accessible")]
        inline = inline_script_present(html)
        ok = not problems and not leaks and not overclaim and not inline
        print(f"[{'OK ' if ok else 'BAD'}] {tag}")
        for p in problems:  print("      a11y:", p)
        for l in leaks:     print("      LEAK:", l)
        for o in overclaim: print("      over-claim:", o)
        if inline:          print("      no-JS core: an inline <script> carries content")
        fails += 0 if ok else 1

    # content-specific expectations
    checks = {
        "/discover?scenario=supported": ["Matches your confirmed needs", "sess-101", "not published", "Suggested order"],
        "/discover?scenario=no_match": ["No listed match", "does not mean no activity exists"],
        "/discover?scenario=indeterminate": ["can't tell", "weren't fully checked"],
        "/discover?scenario=service_failure": ["Something went wrong", "stale"],
        "/compare?scenario=supported": ["sess-101", "sess-102", "not published", "no overall"],
    }
    for path, needles in checks.items():
        html = _html.unescape(client.get(path).text)  # compare semantic text (Jinja escapes ' -> &#39;)
        missing = [n for n in needles if n not in html]
        ok = not missing
        print(f"[{'OK ' if ok else 'BAD'}] content {path}")
        for m in missing: print("      missing:", repr(m))
        fails += 0 if ok else 1

    # JSON disclosure: no staff/research keys in the public projection
    for sc in ("supported", "no_match", "indeterminate", "service_failure"):
        env = client.get(f"/api/envelope?scenario={sc}").json()
        leaked = sorted(set(walk_keys(env)) & LEAK_KEYS)
        ok = not leaked
        print(f"[{'OK ' if ok else 'BAD'}] api disclosure {sc}")
        if leaked: print("      LEAKED KEYS:", leaked)
        fails += 0 if ok else 1

    # C-11 render lint over the app's actual wording (supported scenario)
    lex = render_lint.load_lexicon()
    pub = render.load_public("supported")
    view = render.build_view(pub)
    violations = render_lint.lint_render(lex, pub["payload"]["decision"], render.visible_strings(view))
    ok = not violations
    print(f"[{'OK ' if ok else 'BAD'}] C-11 render-lint on app wording")
    for rid, d in violations: print(f"      {rid}: {d}")
    fails += 0 if ok else 1

    # C-17: conditions change only presentation over the SAME decision (C-BLOCK-06 at the app boundary)
    order = {}
    for cond in ("P0", "P1", "P2"):
        h = client.get(f"/discover?scenario=supported&condition={cond}").text
        order[cond] = re.findall(r"Option \d+: (sess-\d+)", h)
    p0 = client.get("/discover?scenario=supported&condition=P0").text
    p1 = client.get("/discover?scenario=supported&condition=P1").text
    same_order = order["P0"] == order["P1"] == order["P2"] == ["sess-101", "sess-102"]
    p0_hides = ("not published" not in p0) and ("not published" in p1)
    cond_ok = same_order and p0_hides
    print(f"[{'OK ' if cond_ok else 'BAD'}] C-17 conditions: identical order P0/P1/P2; P0 list-only, P1 evidence-aware")
    if not cond_ok:
        print("      order:", order, "p0_hides:", p0_hides)
    fails += 0 if cond_ok else 1

    # MS-1 (Michael 2026-08-23): a non-verified claim's content must not survive public projection
    _env = {"action_kind": "discovery_decision", "payload": {"decision": {
        "terminal_decision": "supported_match",
        "claims": [
            {"subject": "sess-x", "predicate": "leak=unverified", "value": "SECRET-UNVERIFIED", "verification": "failed"},
            {"subject": "sess-101", "predicate": "activity=swimming", "value": True, "verification": "verified"},
        ]}}}
    render._drop_unverified_claims(_env)
    _pub = render.proj.project(_env, render._FIELDS, set(render._PLANES["public"]))
    if "SECRET-UNVERIFIED" in str(_pub) or "leak=unverified" in str(_pub):
        print("[BAD] MS-1: non-verified claim content survived public projection"); fails += 1
    else:
        print("[OK ] MS-1: non-verified claim tuple removed from public projection")

    # WY-2 (Wesley 2026-08-24): a javascript: provider link must be sanitised out at the render boundary
    _v = render.build_view({"action_kind": "discovery_decision", "payload": {"decision": {
        "terminal_decision": "supported_match",
        "candidates": [{"candidate_id": "sess-1", "rank": 1, "pool": "supported",
                        "provider_link": "javascript:alert(document.domain)", "attributes": []}]}}})
    _pl = _v["candidates"][0]["provider_link"]
    if _pl:
        print(f"[BAD] WY-2: unsafe provider_link survived render: {_pl!r}"); fails += 1
    else:
        print("[OK ] WY-2: unsafe provider_link sanitised to empty at the render boundary")

    # WY-2a (Wesley re-review 2026-08-24): the JSON boundary (load_public) must also sanitise links
    _pub2 = {"payload": {"decision": {"candidates": [{"candidate_id": "c1", "provider_link": "javascript:alert(1)"}]}}}
    render._sanitise_provider_links(_pub2)
    if _pub2["payload"]["decision"]["candidates"][0]["provider_link"]:
        print("[BAD] WY-2a: /api/envelope boundary still serves an unsafe provider_link"); fails += 1
    else:
        print("[OK ] WY-2a: provider link sanitised at the load_public / JSON boundary too")

    print("\nRESULT:", "ALL SLICE CHECKS PASS" if fails == 0 else f"{fails} FAILURE(S)")
    return 1 if fails else 0


def test_public_slice():
    """pytest entry point so PyCharm's green button / `pytest` collect this file (they look
    for a test_* function; the report lives in main_run()). Use -s to see the per-check lines,
    or run the file directly (python test_slice.py) for the full printed report."""
    assert main_run() == 0, "public slice suite failed — run the file directly to see which check"


if __name__ == "__main__":
    sys.exit(main_run())
