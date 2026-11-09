"""FastAPI staff assurance workbench — role-gated SSR.

AI-ASSISTED SCAFFOLD (WP §8, C-06/C-07). NOT authorship evidence. Role gating here is a STUB for the
demonstration: real authentication/IAM/break-glass is Wesley's (Section 16, C-BLOCK-04). Server-side
enforcement is the point — a missing/invalid role returns 403, never partial staff content. Maturity:
research_demonstration (C-BLOCK-12).
"""
from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

try:
    from . import render
except ImportError:
    import render

HERE = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(HERE, "templates"))

app = FastAPI(title="LS OpenActive — staff assurance (restricted, research demonstration)")
app.mount("/static", StaticFiles(directory=os.path.join(HERE, "static")), name="static")

# Role -> capabilities (PROPOSED; ratify with Wesley/partner, RATIFY-15-06). Demonstrates WP §8.3:
# access is not granted "merely because the user is staff" — capabilities differ per role, and
# independent review / approval / sending are separated (WP §8.5).
ROLE_CAPABILITIES = {
    "analyst":    {"view", "triage", "draft"},
    "assurance":  {"view", "triage", "draft", "review", "approve"},
    "authoriser": {"view", "send"},
}
ALLOWED_ROLES = set(ROLE_CAPABILITIES)

# Which capability each action-card transition requires.
TRANSITION_CAPABILITY = {
    ("observed", "investigated"): "triage",
    ("investigated", "drafted"): "draft",
    ("drafted", "independently_reviewed"): "review",
    ("drafted", "returned_for_more_evidence"): "review",
    ("independently_reviewed", "approved_for_route"): "approve",
    ("independently_reviewed", "rejected"): "approve",
    ("approved_for_route", "sent_by_authorised_role"): "send",
    ("approved_for_route", "hold"): "approve",
    ("sent_by_authorised_role", "monitored"): "send",
    ("monitored", "closed_or_withdrawn"): "approve",
    ("returned_for_more_evidence", "investigated"): "triage",
    ("hold", "approved_for_route"): "approve",
    ("hold", "withdrawn"): "approve",
    ("rejected", "closed_or_withdrawn"): "approve",
    ("withdrawn", "closed_or_withdrawn"): "approve",
}


_DENY = "__deny__"  # sentinel capability no role holds; default-deny for unmodelled transitions (WY-1)


def _cap_for(frm, to):
    # WY-1 (Wesley 2026-08-24): an unmodelled transition must grant NO capability, not "view" (which
    # every role holds). Fail closed.
    return TRANSITION_CAPABILITY.get((frm, to), _DENY)


def _can(role, capability):
    return capability in ROLE_CAPABILITIES.get(role, set())


def _role(request: Request):
    # Real access is IAM-controlled (Wesley, Section 16, C-BLOCK-04). For LOCAL DEMO viewing only,
    # a ?role= query param is accepted in addition to the header — still 403 without either, so the
    # server-side gate and its test are unchanged. Remove when real auth lands.
    r = request.headers.get("x-staff-role") or request.query_params.get("role")
    return r if r in ALLOWED_ROLES else None


def _forbidden(request: Request):
    return templates.TemplateResponse(request, "forbidden.html", {}, status_code=403)


def _pick(scenario: str) -> str:
    return scenario if scenario in render.SCENARIOS else "supported"


@app.get("/", response_class=HTMLResponse)
def workbench(request: Request):
    role = _role(request)
    if not role:
        return _forbidden(request)
    return templates.TemplateResponse(request, "workbench.html",
                                      {"role": role, "scenarios": render.SCENARIOS})


@app.get("/replay", response_class=HTMLResponse)
def replay(request: Request, scenario: str = "supported"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "replay.html", {
        "role": role, "scenario": sc, "r": render.replay(env),
        "prov": render.provenance(env, "Public-state replay", "inspect only",
                                  "State whether the retained public payload replays to the same digest."),
    })


@app.get("/failure-chain", response_class=HTMLResponse)
def failure_chain(request: Request, scenario: str = "supported"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "failure_chain.html", {
        "role": role, "scenario": sc, "steps": render.failure_chain(env),
        "prov": render.provenance(env, "Failure-chain explorer", "diagnose only",
                                  "Describe where a public outcome became limited; no realised-gain wording."),
    })


@app.get("/collection-health", response_class=HTMLResponse)
def collection_health(request: Request, scenario: str = "supported"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "collection_health.html", {
        "role": role, "scenario": sc, "h": render.collection_health(env),
        "prov": render.provenance(env, "Collection / vintage health", "inspect only",
                                  "Report denominators and freshness; provision is a lower bound."),
    })


@app.get("/action-card", response_class=HTMLResponse)
def action_card(request: Request, state: str = "drafted"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    card = render.action_card(state)
    for t in card["allowed"]:
        t["capability"] = _cap_for(state, t["to"])
        t["permitted"] = _can(role, t["capability"])
    card["capabilities"] = sorted(ROLE_CAPABILITIES.get(role, []))
    return templates.TemplateResponse(request, "action_card.html", {"role": role, "card": card})


@app.get("/action-card/perform", response_class=HTMLResponse)
def action_card_perform(request: Request, frm: str, to: str):
    role = _role(request)
    if not role:
        return _forbidden(request)
    cap = _cap_for(frm, to)
    ctx = {"role": role, "frm": frm, "to": to, "capability": cap}
    # WY-1: the endpoint — not just the offered UI transitions — enforces the state machine. Reject any
    # request asserting an unmodelled (frm,to) pair, and any role lacking the capability.
    if (frm, to) not in TRANSITION_CAPABILITY or not _can(role, cap):
        return templates.TemplateResponse(request, "not_permitted.html", ctx, status_code=403)
    return templates.TemplateResponse(request, "performed.html", ctx)


@app.get("/bounded-scenario", response_class=HTMLResponse)
def bounded_scenario(request: Request, scenario: str = "indeterminate"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "bounded_scenario.html", {
        "role": role, "scenario": sc, "b": render.bounded_scenario(env),
        "prov": render.provenance(env, "Bounded scenario laboratory", "inspect only",
                                  "Best/worst-case bounds only; no realised-gain wording."),
    })


@app.get("/recommender-assurance", response_class=HTMLResponse)
def recommender_assurance(request: Request, scenario: str = "supported"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "recommender_assurance.html", {
        "role": role, "scenario": sc, "r": render.recommender_assurance(env),
        "prov": render.provenance(env, "Recommender / AI assurance", "inspect only",
                                  "Model/policy vintage and coverage; rates measured by Fahmi, not asserted."),
    })


@app.get("/equity-audit", response_class=HTMLResponse)
def equity_audit(request: Request, scenario: str = "indeterminate"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "equity_audit.html", {
        "role": role, "scenario": sc, "e": render.equity_audit(env),
        "prov": render.provenance(env, "Equity-relevant audit", "inspect only",
                                  "Contextual (area/scope) not identity; no league tables; bounded wording."),
    })


@app.get("/release-incident", response_class=HTMLResponse)
def release_incident(request: Request, scenario: str = "supported"):
    role = _role(request)
    if not role:
        return _forbidden(request)
    sc = _pick(scenario)
    env = render.load_env(sc)
    return templates.TemplateResponse(request, "release_incident.html", {
        "role": role, "scenario": sc, "x": render.release_incident(env),
        "prov": render.provenance(env, "Release / incident control", "inspect only",
                                  "Maturity state and controls; the authority records the decision."),
    })


@app.get("/help", response_class=HTMLResponse)
def help_page(request: Request):
    # Help/guidance carries no evidence, so it is available without a role (consistent help, 3.2.6).
    return templates.TemplateResponse(request, "help.html", {"role": _role(request)})
