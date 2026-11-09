"""View builders for the staff assurance workbench.

AI-ASSISTED SCAFFOLD (WP §8). NOT authorship evidence; Clarence corrects it in his own words and
obtains non-author review. Reuses the C-BLOCK-05 projector: staff panels render the STAFF projection
(receipts, why-not, mechanisms, aggregates) while public-state replay uses the PUBLIC projection —
the same terminal decision, authority-asymmetric views. Scenarios are shared with the public app so
both surfaces read one source.
"""
from __future__ import annotations
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(APP, "..", ".."))
CB05 = os.path.join(REPO, "packages", "application-contracts", "c-block-05")
SCEN = os.path.join(REPO, "apps", "public-discovery", "server", "scenarios")
SM_PATH = os.path.join(REPO, "packages", "staff-ia", "action-card-state-machine.json")

sys.path.insert(0, CB05)
import projection_and_invariants as proj  # noqa: E402

FIELDS, PLANES = proj.load_classes()
SCENARIOS = ("supported", "no_match", "indeterminate", "service_failure", "d4_live")  # d4_live: INTEGRATION TEST ONLY (branch clarence/d4-integration-test)


def load_env(scenario):
    return json.load(open(os.path.join(SCEN, scenario + ".json")))


def _project(env, plane):
    p = proj.project(env, FIELDS, set(PLANES[plane]))
    return {} if p is proj.DROP else p


def _decision(node):
    return (node.get("payload") or {}).get("decision", {})


def staff_view(env):
    s = _project(env, "staff")
    d = _decision(s)
    return {
        "action_kind": s.get("action_kind"),
        "terminal": d.get("terminal_decision"),
        "scope": d.get("scope_qualifier"),
        "recommendation": d.get("recommendation_action"),
        "coverage": d.get("coverage_qualifier", {}),
        "versions": d.get("versions", {}),
        "candidates": d.get("candidates", []),
        "why_not": d.get("why_not", []),
        "predicates": d.get("predicates", []),
        "digest": d.get("digest"),
    }


def replay(env):
    """Public-state replay (WP §8.1): recompute the digest of the retained public payload."""
    p = _project(env, "public")
    d = copy.deepcopy(_decision(p))
    stored = d.pop("digest", None)
    recomputed = proj.sha(d)
    return {"stored": stored, "recomputed": recomputed, "ok": stored == recomputed, "public_decision": d}


def failure_chain(env):
    d = _decision(_project(env, "staff"))
    cq = d.get("coverage_qualifier", {})
    steps = [{"stage": "acquisition",
              "detail": cq.get("statement", ""),
              "status": "complete" if cq.get("acquisition_complete") else "incomplete"}]
    for p in d.get("predicates", []):
        mech = f" ({p.get('mechanism')})" if p.get("mechanism") else ""
        steps.append({"stage": "reconstruction / evidence",
                      "detail": f"{p['predicate_id']} = {p['evidence_state']}{mech}",
                      "status": p["evidence_state"]})
    for w in d.get("why_not", []):
        steps.append({"stage": "gate (why-not)",
                      "detail": f"{w.get('predicate_id')} blocked by {w.get('blocking_state')}",
                      "status": w.get("blocking_state")})
    steps.append({"stage": "interface",
                  "detail": f"terminal={d.get('terminal_decision')}; recommendation={d.get('recommendation_action')}",
                  "status": "rendered"})
    return steps


def collection_health(env):
    d = _decision(_project(env, "staff"))
    cq, v = d.get("coverage_qualifier", {}), d.get("versions", {})
    return {"acquisition_complete": cq.get("acquisition_complete"),
            "unevaluated_feeds": cq.get("unevaluated_feeds"),
            "statement": cq.get("statement"),
            "vintage": v.get("vintage"), "corpus_version": v.get("corpus_version"),
            "interpretation_version": v.get("interpretation_version")}


def action_card(state="drafted"):
    sm = json.load(open(SM_PATH))
    allowed = [t for t in sm["transitions"] if t["from"] == state]
    return {"state": state, "allowed": allowed, "required_fields": sm["card_fields_required"], "gates": sm["gates"]}


def provenance(env, panel, permitted_action, permitted_wording):
    """The §8.2 binding block every staff panel must carry."""
    d = _decision(_project(env, "staff"))
    v, cq = d.get("versions", {}), d.get("coverage_qualifier", {})
    return {"panel": panel, "universe": "acquired London feeds (scenario)",
            "denominator_unevaluated_feeds": cq.get("unevaluated_feeds"),
            "vintage": v.get("vintage"), "corpus_version": v.get("corpus_version"),
            "interpretation_version": v.get("interpretation_version"),
            "access_role": "staff", "permitted_action": permitted_action,
            "permitted_wording": permitted_wording}


def bounded_scenario(env):
    """Bounded-scenario lab (WP §8.1): best/worst-case bounds only, no realised-gain wording."""
    d = _decision(_project(env, "staff"))
    flippable = [w for w in d.get("why_not", []) if w.get("blocking_state") in ("U", "B")]
    supported = sum(1 for c in d.get("candidates", []) if c.get("pool") == "supported")
    return {
        "hypothesis": "If the unknown or conflicting fields were resolved favourably",
        "unknown_or_conflict": [w.get("predicate_id") for w in flippable],
        "lower_bound": supported,
        "upper_bound": supported + len(flippable),
        "note": "Best/worst-case bounds only — missing values are unknown, so this is not a realised gain.",
    }


def recommender_assurance(env):
    """Recommender/AI assurance (WP §8.1): within the frozen risk/coverage envelope."""
    d = _decision(_project(env, "staff"))
    v = d.get("versions", {})
    return {
        "model_version": v.get("model_version"), "policy_version": v.get("policy_version"),
        "recommendation_action": d.get("recommendation_action"),
        "abstained": d.get("recommendation_action") == "model_abstained",
        "supported_count": sum(1 for c in d.get("candidates", []) if c.get("pool") == "supported"),
        "scope": d.get("scope_qualifier"),
        "note": "False-assurance and coverage rates are measured in Fahmi's evaluation, not asserted here.",
    }


def equity_audit(env):
    """Equity-relevant audit (WP §8.1/§8.3): contextual, never identity; no league tables."""
    s = _project(env, "staff")
    d = _decision(s)
    return {
        "coarsened_origin": (s.get("header") or {}).get("coarsened_origin"),
        "scope": d.get("scope_qualifier"),
        "unevaluated_feeds": (d.get("coverage_qualifier") or {}).get("unevaluated_feeds"),
        "note": "Contextual measures only (area/scope) — never identity; no borough or publisher league tables; bounded wording.",
    }


def release_incident(env):
    """Release / incident control (WP §8.1/§12.9/§12.10)."""
    h = _project(env, "staff").get("header") or {}
    return {
        "maturity": h.get("release_maturity_class"),
        "safety_gate_state": h.get("safety_gate_state"),
        "kill_switch": "available (stub — Wesley implements)",
        "rollback": "available (stub — Wesley implements)",
        "note": "An authorised person — not Clarence — records the maturity / residual-risk decision (WP §12.9).",
    }
