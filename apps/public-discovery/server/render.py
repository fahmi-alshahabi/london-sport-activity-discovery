"""View-model builder for the public discovery slice.

AI-ASSISTED SCAFFOLD (WP Phase D). NOT authorship evidence; Clarence corrects it in his own words
and obtains non-author review. It reuses the C-BLOCK-05 projector and the C-11 wording lexicon so
the UI can only ever show the PUBLIC projection, worded from the approved lexicon — never a staff
field, never an over-claim.
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(APP, "..", ".."))
CB05 = os.path.join(REPO, "packages", "application-contracts", "c-block-05")
CONTENT = os.path.join(REPO, "packages", "accessible-design-system", "content")
SCEN = os.path.join(HERE, "scenarios")

SEC = os.path.join(REPO, "packages", "security")
sys.path.insert(0, CB05)
sys.path.insert(0, SEC)
import projection_and_invariants as proj  # noqa: E402
from sanitize import safe_url              # noqa: E402  (WY-2: sanitise provider links at the render boundary)

_FIELDS, _PLANES = proj.load_classes()
_LEX = json.load(open(os.path.join(CONTENT, "evidence-language.json")))

SCENARIOS = ("supported", "no_match", "indeterminate", "service_failure", "d4_live")  # d4_live: INTEGRATION TEST ONLY (branch clarence/d4-integration-test)

# Evaluation conditions (C-17): P0/P1/P2 change only PRESENTATION over the same decision (C-BLOCK-06).
EVAL_MANIFEST = os.path.join(REPO, "packages", "evaluation", "condition-manifest.json")
try:
    _COND_CAPS = {c["id"]: c["capabilities"] for c in json.load(open(EVAL_MANIFEST)).get("public_conditions", [])}
except Exception:
    _COND_CAPS = {}


def condition_caps(cid):
    return _COND_CAPS.get(cid, {"evidence_communication": True, "conversation": False})


UNMAPPED = []  # (category, value) seen with no approved wording — asserted empty by the tests


def phrase(cat, val, default=""):
    """Approved wording only. An unmapped value is DROPPED, never echoed to the user.

    DEFECT FIXED 9 Sep 2026 (found from Michael's verified pack data). The old fallback was
    `return default or (val or "")`, and since every call site passes the default `""` — which is
    falsy — an unmapped value fell through to the RAW INTERNAL TOKEN. Demonstrated on the real
    (evidence_state, grade) pairs the evidence engine emits:

        ("T", "explicit")  -> "confirmed published by the provider"     (worded)
        ("T", "inherited") -> "confirmed inherited"   <-- raw enum on a PUBLIC surface
        ("U", None)        -> "not published"                            (safe: guarded)

    `inherited` has no entry in evidence-language.json, so the one mechanism that exists to keep
    unapproved wording off the public surface was emitting the internal vocabulary instead. Note
    the severity is the opposite way round from first reading: the null grade is SAFE (the
    `if a.get("grade")` guard catches it); the non-null unmapped value is the leak, because it
    passes the truthiness guard and then falls through here.

    Dropping is the correct fail-closed behaviour and is inside the claim boundary: public
    simplification may REMOVE detail, it may never ADD certainty (WP §19.3). Emitting an
    unapproved token is not simplification. Unmapped values are recorded so a silent drop cannot
    hide the gap.

    NOT FIXED HERE, deliberately: approved wording for `inherited` is content. It needs Clarence's
    own words and non-author HCI/content review (C-BLOCK-03), not a value invented by the code
    that found the gap.
    """
    if val is None or val == "":
        return default
    e = _LEX.get(cat, {}).get(val)
    if e and e.get("approved"):
        return e["approved"][0]
    if (cat, val) not in UNMAPPED:
        UNMAPPED.append((cat, val))
    return default


def _drop_unverified_claims(env):
    """MS-1 (Michael 2026-08-23): a claim whose verification is not 'verified' must have its ENTIRE
    tuple removed before public projection. The verification field is staff-only, so field-class
    projection alone would strip 'verification' yet leave the unverified subject/predicate/value
    visible to the public. Reject the whole tuple instead."""
    dec = (env.get("payload") or {}).get("decision")
    if isinstance(dec, dict) and isinstance(dec.get("claims"), list):
        dec["claims"] = [c for c in dec["claims"] if c.get("verification") == "verified"]


def _sanitise_provider_links(pub):
    """WY-2a (Wesley re-review 2026-08-24): sanitise provider links at the load_public / JSON boundary,
    so /api/envelope (which returns load_public directly) cannot serve a javascript: URL — not only the
    build_view HTML path."""
    dec = (pub.get("payload") or {}).get("decision") or {}
    for c in dec.get("candidates", []):
        if isinstance(c, dict) and "provider_link" in c:
            c["provider_link"] = safe_url(c.get("provider_link", ""))


def load_public(scenario):
    """Load the staff-complete scenario envelope and return ONLY its public projection. Non-verified
    claim tuples are removed entirely first (MS-1); provider links are sanitised here so the JSON
    boundary is covered too, not only build_view (WY-2a)."""
    env = json.load(open(os.path.join(SCEN, scenario + ".json")))
    _drop_unverified_claims(env)
    pub = proj.project(env, _FIELDS, set(_PLANES["public"]))
    if pub is proj.DROP:
        return {}
    _sanitise_provider_links(pub)
    return pub


def build_view(pub):
    v = {
        "action_kind": pub.get("action_kind"),
        "maturity": (pub.get("header") or {}).get("release_maturity_class"),
    }
    if v["action_kind"] == "service_failure":
        p = pub.get("payload", {})
        # failed_stage is STAFF_AGGREGATE (F1): dropped by the public projection, never named to
        # users. The public failure page shows only the generic message + the safe next step.
        v["safe_next"] = p.get("safe_next")
        return v
    d = (pub.get("payload") or {}).get("decision", {})
    v["terminal"] = d.get("terminal_decision")
    v["terminal_text"] = phrase("terminal_decision", d.get("terminal_decision"))
    v["recommendation"] = d.get("recommendation_action")
    v["recommendation_text"] = phrase("recommendation_action", d.get("recommendation_action"))
    v["scope"] = d.get("scope_qualifier")
    v["scope_notice"] = phrase("scope_qualifier", "scope_indeterminate") if d.get("scope_qualifier") == "scope_indeterminate" else ""
    v["coverage"] = (d.get("coverage_qualifier") or {}).get("statement", "")
    v["vintage"] = (d.get("versions") or {}).get("vintage", "")
    cands = []
    for c in d.get("candidates", []):
        attrs = []
        for a in c.get("attributes", []):
            state_text = phrase("evidence_state", a["evidence_state"])
            if not state_text:
                # Fail closed: an evidence state with no approved wording cannot be described
                # honestly, so the attribute is not rendered at all rather than shown with an
                # empty or raw qualifier. The gap is recorded in UNMAPPED by phrase().
                continue
            attrs.append({
                "id": a["predicate_id"],
                "state": a["evidence_state"],
                "state_text": state_text,
                "grade_text": phrase("grade", a.get("grade")) if a.get("grade") else "",
            })
        cands.append({
            "id": c["candidate_id"], "rank": c["rank"], "pool": c["pool"],
            "provider_link": safe_url(c.get("provider_link", "")), "attributes": attrs,
        })
    v["candidates"] = cands
    return v


def compare_matrix(view):
    """Compare grid over the SAME certified candidates: predicates as rows, candidates as columns.
    Preserves unknown/conflict wording; invents no composite winner (WP §7.3)."""
    cands = view.get("candidates", [])
    pids = []
    for c in cands:
        for a in c["attributes"]:
            if a["id"] not in pids:
                pids.append(a["id"])
    header = [{"id": c["id"], "rank": c["rank"]} for c in cands]
    rows = []
    for p in pids:
        cells = []
        for c in cands:
            cells.append(next((a["state_text"] for a in c["attributes"] if a["id"] == p), "not published"))
        rows.append({"predicate": p, "cells": cells})
    return {"candidates": header, "rows": rows}


def visible_strings(view):
    """Flatten the human-facing strings a page shows, for the C-11 render linter."""
    out = [view.get("terminal_text", ""), view.get("recommendation_text", ""),
           view.get("scope_notice", ""), view.get("coverage", "")]
    for c in view.get("candidates", []):
        for a in c["attributes"]:
            out.append(f"{a['id']}: {a['state_text']} {a['grade_text']}")
    return [s for s in out if s]
