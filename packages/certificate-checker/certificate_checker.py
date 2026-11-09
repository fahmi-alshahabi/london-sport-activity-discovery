#!/usr/bin/env python3
"""
C-09 independent certificate checker (reference implementation).

AI-ASSISTED SCAFFOLD prepared from CLARENCE_ZHEN_JIN_TAN_SPECIALISED_WORK_PACKAGE.md
section 10. NOT evidence Clarence authored/accepted it; he must inspect it, correct it in his
own words, and obtain non-author review. He CANNOT certify his own checker (WP 2.6).

Independence (WP 10.4), enforced by construction here:
  - imports nothing from any production/evidence module (stdlib + jsonschema for runtime
    schema enforcement only — never a production interpreter);
  - never calls a production interpreter to decide the expected output;
  - implements only the frozen certificate contract;
  - expected values (versions, receipts, target query/decision, certifiable fragment) are
    supplied by the caller's manifest/store, never re-derived from production code.

The outcome vocabulary is the WP 10.3 enum and is PROPOSED pending RATIFY-09-04 / Section 09.
Do not rename to make production pass (WP 10.4); record disagreements in discrepancy-register.md.
"""
from __future__ import annotations
import json as _json
import os as _os

# --- WP 10.3 outcome enum (exact names ratified with Section 09) ------------
PASS = "PASS"
FAIL_MALFORMED = "FAIL_MALFORMED"
FAIL_MISSING_WITNESS = "FAIL_MISSING_WITNESS"
FAIL_UNRESOLVED_RECEIPT = "FAIL_UNRESOLVED_RECEIPT"
FAIL_DIGEST_MISMATCH = "FAIL_DIGEST_MISMATCH"
FAIL_VERSION_MISMATCH = "FAIL_VERSION_MISMATCH"
FAIL_ILLEGAL_ESCALATION = "FAIL_ILLEGAL_ESCALATION"
FAIL_SCOPE_INCONSISTENCY = "FAIL_SCOPE_INCONSISTENCY"
FAIL_UNSUPPORTED_FRAGMENT = "FAIL_UNSUPPORTED_FRAGMENT"

_EVIDENCE_STATES = {"T", "F", "U", "B"}
_GRADES = {"explicit", "schedule_derived", "specification_default"}
_TERMINALS = {"supported_match", "bounded_non_match", "evidence_indeterminate"}
_SCOPES = {"scope_complete", "scope_indeterminate"}
_ACTIONS = {"authorised_slate", "model_abstained", "deterministic_fallback", "browse_only"}
_POOLS = {"supported", "indeterminate", "excluded"}

# This checker's own identity. A certificate must name THIS checker; a caller cannot assert a
# different checker_version and have it trusted (MS-7, Michael 2026-08-23).
CHECKER_VERSION = "chk-1.0"

_SCHEMA_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "certificate.schema.json")


# --- individual checks: each returns a detail string if it FAILS, else None -
def _c_schema(cert, ctx):
    """MS-3: enforce the certificate JSON Schema at runtime, and structurally validate the
    verification context. A schema-invalid certificate can never reach PASS. Fail-closed if
    jsonschema is unavailable (cannot enforce -> cannot certify)."""
    try:
        import jsonschema
    except Exception as ex:
        return f"jsonschema not installed — cannot enforce the certificate schema (pip install jsonschema) ({ex})"
    try:
        with open(_SCHEMA_PATH) as fh:
            schema = _json.load(fh)
        errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(cert), key=lambda e: list(e.path))
        if errs:
            e = errs[0]
            loc = "/".join(str(p) for p in e.path) or "(root)"
            return f"certificate fails its JSON Schema at {loc}: {e.message}"
    except Exception as ex:
        return f"schema validation error: {ex!r}"
    if not isinstance(ctx, dict):
        return "context is not an object"
    if not isinstance(ctx.get("receipt_store"), dict):
        return "context.receipt_store missing or not an object"
    man = ctx.get("manifest")
    if not isinstance(man, dict):
        return "context.manifest missing or not an object"
    for k in ("compatible_release_root", "allowed_versions", "certifiable_fragment"):
        if k not in man:
            return f"context.manifest missing required key: {k}"
    for k in ("expected_query_id", "expected_decision_digest"):
        if k not in ctx:
            return f"context missing required key: {k}"
    return None
def _c_malformed(cert, ctx):
    if not isinstance(cert, dict):
        return "certificate is not an object"
    if cert.get("contract") != "Certificate":
        return "contract != 'Certificate'"
    for k in ("query_id", "decision_digest", "compatible_release_root",
              "claimed", "versions", "scope_witness",
              "predicate_witnesses", "candidate_witnesses", "state_transition"):
        if k not in cert:
            return f"missing required key: {k}"
    cl = cert["claimed"]
    if cl.get("terminal_decision") not in _TERMINALS: return "bad claimed.terminal_decision"
    if cl.get("scope_qualifier") not in _SCOPES: return "bad claimed.scope_qualifier"
    if cl.get("recommendation_action") not in _ACTIONS: return "bad claimed.recommendation_action"
    if not isinstance(cert["scope_witness"], dict) or not isinstance(cert["scope_witness"].get("evaluated_complete"), bool):
        return "bad scope_witness.evaluated_complete"
    pws = cert["predicate_witnesses"]
    if not isinstance(pws, list): return "predicate_witnesses not a list"
    seen_p = set()
    for pw in pws:
        if not isinstance(pw, dict): return "predicate_witness not an object"
        pid = pw.get("predicate_id")
        if not isinstance(pid, str): return "predicate_witness.predicate_id missing"
        if pid in seen_p: return f"duplicate/ambiguous predicate identity: {pid}"
        seen_p.add(pid)
        if pw.get("evidence_state") not in _EVIDENCE_STATES: return f"bad evidence_state for {pid}"
        if pw.get("grade") not in _GRADES: return f"bad grade for {pid}"
        if not isinstance(pw.get("fragment_class"), str): return f"missing fragment_class for {pid}"
        if not isinstance(pw.get("receipts"), list): return f"receipts not a list for {pid}"
        for r in pw["receipts"]:
            if not isinstance(r, dict) or "receipt_id" not in r or "content_digest" not in r:
                return f"malformed receipt on {pid}"
    cws = cert["candidate_witnesses"]
    if not isinstance(cws, list): return "candidate_witnesses not a list"
    seen_c = set()
    for cw in cws:
        cid = cw.get("candidate_id")
        if not isinstance(cid, str): return "candidate_witness.candidate_id missing"
        if cid in seen_c: return f"duplicate/ambiguous candidate identity: {cid}"
        seen_c.add(cid)
        if cw.get("pool") not in _POOLS: return f"bad pool for {cid}"
        if not isinstance(cw.get("rank"), int) or cw["rank"] < 1: return f"bad rank for {cid}"
        if not isinstance(cw.get("hard_predicate_ids"), list): return f"bad hard_predicate_ids for {cid}"
    return None


def _c_version(cert, ctx):
    # ORDERING (WY-3 / MS-3<->MS-7 interlock, Wesley + Michael): _c_schema MUST run before this check.
    # The schema requires all five version keys (additionalProperties:false), which is what stops a
    # certificate from OMITTING a version key to dodge the pin loop below (MS-7). Reordering CHECKS
    # would reintroduce the empty/partial allowed_versions fail-open — do not move _c_schema after this.
    man = ctx["manifest"]
    cv = cert.get("versions", {})
    # MS-7: the certificate must name THIS checker; never trust a caller-asserted checker version.
    if cv.get("checker_version") != CHECKER_VERSION:
        return f"certificate names checker_version {cv.get('checker_version')!r} but this checker is {CHECKER_VERSION!r}"
    if cert.get("compatible_release_root") != man.get("compatible_release_root"):
        return "compatible_release_root does not match the release manifest"
    allowed = man.get("allowed_versions", {})
    # WY-3 (Wesley 2026-08-24): an empty or partial allowed_versions map must NOT waive version
    # pinning (fail closed, as certifiable_fragment already does). Every declared version except this
    # checker's own identity must be pinned by the manifest and match.
    if not isinstance(allowed, dict) or not allowed:
        return "release manifest waives version pinning (allowed_versions is empty) — refusing to certify"
    for k in cv:
        if k == "checker_version":
            continue
        if k not in allowed:
            return f"version key {k!r} is not pinned by the release manifest (allowed_versions incomplete)"
        if cv.get(k) != allowed[k]:
            return f"version {k}={cv.get(k)!r} not compatible (manifest requires {allowed[k]!r})"
    return None


def _c_fragment(cert, ctx):
    allowed = set(ctx["manifest"].get("certifiable_fragment", []))
    for pw in cert["predicate_witnesses"]:
        if pw["fragment_class"] not in allowed:
            return f"predicate {pw['predicate_id']} uses fragment '{pw['fragment_class']}' outside the certifiable fragment"
    return None


def _c_missing_witness(cert, ctx):
    wit = {pw["predicate_id"] for pw in cert["predicate_witnesses"]}
    if cert["claimed"]["terminal_decision"] == "supported_match" and not cert["predicate_witnesses"]:
        return "supported_match with no predicate witnesses"
    for pw in cert["predicate_witnesses"]:
        if pw["evidence_state"] == "T" and not pw["receipts"]:
            return f"truncated evidence path: T witness {pw['predicate_id']} has no receipts"
    for cw in cert["candidate_witnesses"]:
        if cw["pool"] == "supported":
            for hp in cw["hard_predicate_ids"]:
                if hp not in wit:
                    return f"missing witness for hard predicate {hp} of supported candidate {cw['candidate_id']}"
    return None


def _c_unresolved(cert, ctx):
    store = ctx["receipt_store"]
    for pw in cert["predicate_witnesses"]:
        for r in pw["receipts"]:
            if r["receipt_id"] not in store:
                return f"receipt {r['receipt_id']} does not resolve in the receipt store"
    return None


def _c_digest(cert, ctx):
    if cert.get("query_id") != ctx["expected_query_id"]:
        return f"certificate is for another query ({cert.get('query_id')!r} != {ctx['expected_query_id']!r})"
    if cert.get("decision_digest") != ctx["expected_decision_digest"]:
        return "decision_digest does not match the expected DecisionEnvelope digest"
    store = ctx["receipt_store"]
    for pw in cert["predicate_witnesses"]:
        for r in pw["receipts"]:
            if store.get(r["receipt_id"]) != r["content_digest"]:
                return f"receipt {r['receipt_id']} digest mismatch (swapped/forged)"
    return None


def _c_escalation(cert, ctx):
    cl = cert["claimed"]
    states = {pw["predicate_id"]: pw["evidence_state"] for pw in cert["predicate_witnesses"]}
    if cl["terminal_decision"] == "supported_match":
        for pid, st in states.items():
            if st != "T":
                return f"supported_match but predicate {pid} is {st} (illegal U/B/F -> supported escalation)"
    if cl["recommendation_action"] == "authorised_slate":
        for cw in cert["candidate_witnesses"]:
            if cw["pool"] != "supported":
                return f"authorised_slate contains ineligible candidate {cw['candidate_id']} (pool={cw['pool']})"
            for hp in cw["hard_predicate_ids"]:
                if states.get(hp) != "T":
                    return f"slate candidate {cw['candidate_id']} rests on non-T predicate {hp}"
    return None


def _c_scope(cert, ctx):
    cl = cert["claimed"]
    sw = cert["scope_witness"]["evaluated_complete"]
    if cl["scope_qualifier"] == "scope_complete" and sw is False:
        return "scope_qualifier claims scope_complete but scope was not fully evaluated (dropped qualifier)"
    if cl["scope_qualifier"] == "scope_indeterminate" and sw is True:
        return "scope_qualifier claims scope_indeterminate but scope was fully evaluated"
    if cl["terminal_decision"] == "bounded_non_match":
        cq = cert.get("coverage_qualifier") or {}
        if not cq.get("statement"):
            return "bounded_non_match without a coverage qualifier"
    return None


_ALLOWED_DECISION_ACTIONS = {
    "supported_match": {"authorised_slate", "browse_only"},
    "bounded_non_match": {"deterministic_fallback", "browse_only"},
    "evidence_indeterminate": {"model_abstained", "deterministic_fallback", "browse_only"},
}


def _c_decision_consistency(cert, ctx):
    """MS-7: reject incompatible terminal_decision / recommendation_action combinations
    (e.g. an authorised_slate under a non-supported terminal decision)."""
    cl = cert["claimed"]
    td, act = cl["terminal_decision"], cl["recommendation_action"]
    allowed = _ALLOWED_DECISION_ACTIONS.get(td, set())
    if act not in allowed:
        return f"incompatible decision combination: {td} with {act} (allowed: {sorted(allowed)})"
    return None


def _c_transition(cert, ctx):
    """MS-6: the claimed state transition must be one the release manifest permits."""
    st = cert.get("state_transition") or {}
    frm, to = st.get("from_state"), st.get("to_state")
    allowed = ctx["manifest"].get("allowed_transitions")
    if allowed is None:
        return "manifest does not declare allowed_transitions; cannot verify the state transition"
    if not any(t.get("from_state") == frm and t.get("to_state") == to for t in allowed):
        return f"state transition {frm!r} -> {to!r} is not a permitted transition"
    return None


# Ordered precedence: the first failing check wins (WP 10.3 single outcome).
CHECKS = [
    (FAIL_MALFORMED, _c_schema),
    (FAIL_MALFORMED, _c_malformed),
    (FAIL_VERSION_MISMATCH, _c_version),
    (FAIL_UNSUPPORTED_FRAGMENT, _c_fragment),
    (FAIL_MISSING_WITNESS, _c_missing_witness),
    (FAIL_UNRESOLVED_RECEIPT, _c_unresolved),
    (FAIL_DIGEST_MISMATCH, _c_digest),
    (FAIL_ILLEGAL_ESCALATION, _c_escalation),
    (FAIL_MALFORMED, _c_decision_consistency),
    (FAIL_MALFORMED, _c_transition),
    (FAIL_SCOPE_INCONSISTENCY, _c_scope),
]


def _run_checks(cert, ctx, checks):
    """Run an explicit, ordered check list. INTERNAL ONLY — used by the mutation harness to
    prove each branch is load-bearing. Not for production use: it can be handed a reduced list.
    Fail-closed: an empty check set never certifies (MS-8), and any exception is FAIL_MALFORMED
    rather than an accidental PASS."""
    if not checks:
        return (FAIL_MALFORMED, "empty check set: refusing to certify without running the checks")
    for code, fn in checks:
        try:
            detail = fn(cert, ctx)
        except Exception as ex:  # fail closed
            return (FAIL_MALFORMED, f"exception in {code} check: {ex!r}")
        if detail:
            return (code, detail)
    return (PASS, "certificate verified against witness, receipts, versions and scope")


def check(cert, ctx):
    """Public entry point. ALWAYS runs the complete, ordered CHECKS — there is no caller
    override, so there is no bypass (MS-8, Michael 2026-08-23). Fail-closed throughout."""
    return _run_checks(cert, ctx, CHECKS)


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) >= 3:
        cert = json.load(open(sys.argv[1]))
        ctx = json.load(open(sys.argv[2]))
        outcome, detail = check(cert, ctx)
        print(outcome, "-", detail)
        sys.exit(0 if outcome == PASS else 2)
    print("usage: certificate_checker.py <certificate.json> <context.json>")
