"""Verification for the staff assurance slice (WP §8, C-06/C-07).

AI-ASSISTED SCAFFOLD. NOT authorship evidence; a non-author reviewer must confirm. Checks:
role gating (403 without role); evidence symmetry (staff & public agree on the shared decision);
authority asymmetry (staff-only fields present in staff, ABSENT in public); public-state replay;
value-level non-interference at the boundary; action-card no-skip; a11y; and no RESEARCH_RESTRICTED
identity leaking into the staff view.

Run:  python test_staff.py     # exit 0 iff all checks pass
"""
from __future__ import annotations
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server")
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
CB05 = os.path.join(REPO, "packages", "application-contracts", "c-block-05")
PUBAPP = os.path.join(REPO, "apps", "public-discovery")
for p in (SERVER, CB05, PUBAPP, HERE):
    sys.path.insert(0, p)

from fastapi.testclient import TestClient  # noqa: E402
for _m in ("main", "render"):              # both apps ship their own main.py/render.py;
    sys.modules.pop(_m, None)              # bind THIS app's copy when harnesses share a process
import main, render                        # noqa: E402
import projection_and_invariants as proj   # noqa: E402
import a11y_check                          # noqa: E402

client = TestClient(main.app)
ROLE = {"x-staff-role": "analyst"}
STAFF_ROUTES = ["/", "/replay?scenario=supported", "/failure-chain?scenario=indeterminate",
                "/collection-health?scenario=indeterminate", "/action-card?state=drafted",
                "/bounded-scenario?scenario=indeterminate", "/recommender-assurance?scenario=supported",
                "/equity-audit?scenario=indeterminate", "/release-incident?scenario=supported"]
RESEARCH_TOKENS = ["ep-7731", "trace-aa19", "ep-in-1", "tr-in-1", "ep-nm-1", "tr-nm-1"]


def run():
    fails = 0

    # 1. role gate
    for path in STAFF_ROUTES:
        no = client.get(path)
        yes = client.get(path, headers=ROLE)
        ok = no.status_code == 403 and yes.status_code == 200
        print(f"[{'OK ' if ok else 'BAD'}] role-gate {path}  (no-role={no.status_code}, role={yes.status_code})")
        fails += 0 if ok else 1

    # 1b. dev-only ?role= query param also opens (still 403 without any role)
    qp_ok = (client.get("/replay?scenario=supported&role=analyst").status_code == 200
             and client.get("/replay?scenario=supported").status_code == 403)
    print(f"[{'OK ' if qp_ok else 'BAD'}] dev ?role= param opens; still 403 without any role")
    fails += 0 if qp_ok else 1

    # 2. a11y on staff pages (with role) + forbidden page
    pages = {p: client.get(p, headers=ROLE).text for p in STAFF_ROUTES}
    pages["/(forbidden)"] = client.get("/").text
    for label, html in pages.items():
        problems = a11y_check.check_html(html)
        leaked = [t for t in RESEARCH_TOKENS if t in html]
        ok = not problems and not leaked
        print(f"[{'OK ' if ok else 'BAD'}] a11y+research-leak {label}")
        for pr in problems: print("      a11y:", pr)
        for lk in leaked:   print("      RESEARCH LEAK:", lk)
        fails += 0 if ok else 1

    # 3. evidence symmetry + authority asymmetry
    for sc in ("supported", "no_match", "indeterminate"):
        env = render.load_env(sc)
        sv = render.staff_view(env)
        pub_dec = render.replay(env)["public_decision"]
        sym = (sv["terminal"] == pub_dec.get("terminal_decision")
               and sv["scope"] == pub_dec.get("scope_qualifier")
               and sv["recommendation"] == pub_dec.get("recommendation_action")
               and sv["versions"].get("vintage") == pub_dec.get("versions", {}).get("vintage")
               and [(c["candidate_id"], c["rank"]) for c in sv["candidates"]]
                   == [(c["candidate_id"], c["rank"]) for c in pub_dec.get("candidates", [])])
        print(f"[{'OK ' if sym else 'BAD'}] evidence-symmetry {sc}")
        fails += 0 if sym else 1

    # staff-only fields present in staff, ABSENT in public
    env = render.load_env("supported")
    sv = render.staff_view(env); pub = render.replay(env)["public_decision"]
    staff_has_score = any("internal_score" in c for c in sv["candidates"])
    public_no_score = all("internal_score" not in c for c in pub.get("candidates", []))
    staff_has_modelver = "model_version" in sv["versions"]
    public_no_modelver = "model_version" not in pub.get("versions", {})
    aa = staff_has_score and public_no_score and staff_has_modelver and public_no_modelver
    print(f"[{'OK ' if aa else 'BAD'}] authority-asymmetry (internal_score & model_version staff-only)")
    fails += 0 if aa else 1

    envn = render.load_env("no_match")
    svn = render.staff_view(envn); pubn = render.replay(envn)["public_decision"]
    staff_whynot = svn["why_not"] and "blocking_state" in svn["why_not"][0]
    public_whynot_clean = all("blocking_state" not in w for w in pubn.get("why_not", []))
    wn = bool(staff_whynot) and public_whynot_clean
    print(f"[{'OK ' if wn else 'BAD'}] why-not detail staff-only (blocking_state hidden from public)")
    fails += 0 if wn else 1

    # 4. public-state replay
    for sc in ("supported", "no_match", "indeterminate"):
        r = render.replay(render.load_env(sc))
        print(f"[{'OK ' if r['ok'] else 'BAD'}] public-state replay {sc}")
        fails += 0 if r["ok"] else 1

    # 5. value-level non-interference at the boundary (reuse C-BLOCK-05 invariant)
    for sc in ("supported", "no_match", "indeterminate"):
        ok, _ = proj.inv_noninterference(render.load_env(sc), proj.load_classes()[0], proj.load_classes()[1])
        print(f"[{'OK ' if ok else 'BAD'}] non-interference {sc}")
        fails += 0 if ok else 1

    # 6. action-card no-skip
    drafted = {t["to"] for t in render.action_card("drafted")["allowed"]}
    investigated = {t["to"] for t in render.action_card("investigated")["allowed"]}
    approved = render.action_card("approved_for_route")["allowed"]
    send = next((t for t in approved if t["to"] == "sent_by_authorised_role"), None)
    noskip = ("approved_for_route" not in drafted and "sent_by_authorised_role" not in drafted
              and "sent_by_authorised_role" not in investigated
              and send is not None and send.get("requires_authorised_role"))
    print(f"[{'OK ' if noskip else 'BAD'}] action-card no-skip (review+approval+authorised-role enforced)")
    fails += 0 if noskip else 1

    # 6b. new workspaces render honest wording (WP §8.1/§8.3)
    ea = client.get("/equity-audit?scenario=indeterminate", headers=ROLE).text
    ri = client.get("/release-incident?scenario=supported", headers=ROLE).text
    ra = client.get("/recommender-assurance?scenario=supported", headers=ROLE).text
    bs = client.get("/bounded-scenario?scenario=indeterminate", headers=ROLE).text
    ws_ok = ("identity" in ea and "league table" in ea            # contextual, not identity; no league tables
             and "research_demonstration" in ri                    # maturity surfaced
             and "recmodel-0.3" in ra                              # staff sees model version
             and "not a realised gain" in bs)                      # bounded, no realised-gain
    print(f"[{'OK ' if ws_ok else 'BAD'}] staff workspaces render honest wording")
    fails += 0 if ws_ok else 1

    # 7. per-role authorisation on action-card transitions (WP §8.3, §8.5)
    def perform(frm, to, role):
        return client.get(f"/action-card/perform?frm={frm}&to={to}", headers={"x-staff-role": role}).status_code
    matrix = [
        ("investigated", "drafted", "analyst", 200),
        ("drafted", "independently_reviewed", "analyst", 403),
        ("drafted", "independently_reviewed", "assurance", 200),
        ("approved_for_route", "sent_by_authorised_role", "analyst", 403),
        ("approved_for_route", "sent_by_authorised_role", "assurance", 403),
        ("approved_for_route", "sent_by_authorised_role", "authoriser", 200),
    ]
    for frm, to, role, exp in matrix:
        got = perform(frm, to, role)
        ok = got == exp
        print(f"[{'OK ' if ok else 'BAD'}] role {role:9s} {frm} -> {to} = {got} (expect {exp})")
        fails += 0 if ok else 1

    # WY-1 (Wesley 2026-08-24): the perform endpoint enforces the state machine — an unmodelled
    # (frm,to) pair is refused, so an analyst cannot be told it may "send".
    r = client.get("/action-card/perform",
                   params={"frm": "observed", "to": "sent_by_authorised_role"}, headers={"x-staff-role": "analyst"})
    wy1 = r.status_code == 403
    print(f"[{'OK ' if wy1 else 'BAD'}] WY-1 unmodelled transition refused (analyst observed->sent_by_authorised_role = {r.status_code}, expect 403)")
    fails += 0 if wy1 else 1

    print("\nRESULT:", "ALL STAFF SLICE CHECKS PASS" if fails == 0 else f"{fails} FAILURE(S)")
    return 1 if fails else 0


def test_staff_slice():
    """pytest entry point so PyCharm's green button / `pytest` collect this file (they look
    for a test_* function; the report lives in run()). Use -s to see the per-check lines, or
    run the file directly (python test_staff.py) for the full printed report."""
    assert run() == 0, "staff slice suite failed — run the file directly to see which check"


if __name__ == "__main__":
    sys.exit(run())
