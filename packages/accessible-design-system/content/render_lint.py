#!/usr/bin/env python3
"""
C-11 evidence-language linter.

AI-ASSISTED SCAFFOLD (WP sec 7.3, 9.3, 11, 19.3). NOT authorship evidence; Clarence must correct
the wording rules in his own words and obtain a non-author HCI/content review (C-BLOCK-03).

Two jobs:
  1. completeness  -- every canonical contract enum value has approved wording in the lexicon;
  2. render lint   -- given the PUBLIC-projected DecisionEnvelope + the user-facing strings a
                      surface would show, flag over-claiming / state-collapse / hidden-scope wording.

The render lint reuses the C-BLOCK-05 projector so it inspects the real public surface, not a guess.

Run:  python render_lint.py     # completeness + compliant render (pass) + bad render + adversarial (flagged)
"""
from __future__ import annotations
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEXICON = os.path.join(HERE, "evidence-language.json")
CB05 = os.path.normpath(os.path.join(HERE, "..", "..", "application-contracts", "c-block-05"))

# Canonical enum vocabulary (WP 4.2) the lexicon must fully cover.
CANON = {
    "evidence_state": ["T", "F", "U", "B"],
    "grade": ["explicit", "schedule_derived", "specification_default"],
    "terminal_decision": ["supported_match", "bounded_non_match", "evidence_indeterminate"],
    "scope_qualifier": ["scope_complete", "scope_indeterminate"],
    "recommendation_action": ["authorised_slate", "model_abstained", "deterministic_fallback", "browse_only"],
}
U_VALUE_NEGATIVES = ["free", "none", "inaccessible", "unavailable", "£0", "no cost"]


def load_lexicon():
    with open(LEXICON) as fh:
        return json.load(fh)


def _has(text, term):
    """word-boundary match for single words; substring for phrases."""
    t = text.lower()
    term = term.lower()
    if " " in term or any(c in term for c in "£0123456789"):
        return term in t
    return re.search(r"\b" + re.escape(term) + r"\b", t) is not None


def lint_completeness(lex):
    v = []
    for cat, values in CANON.items():
        block = lex.get(cat, {})
        for val in values:
            entry = block.get(val)
            if not entry or not entry.get("approved"):
                v.append(f"lexicon missing approved wording for {cat}.{val}")
    return v


def lint_render(lex, decision, rendered):
    """decision: PUBLIC-projected DecisionEnvelope dict. rendered: list of user-facing strings."""
    v = []
    blob = " || ".join(rendered)

    # 1. global over-claim vocabulary
    for term in lex["global_banned"]:
        if _has(blob, term):
            v.append(("global_banned", f"over-claiming term in rendered text: '{term}'"))

    # 2. conditional 'accessible' (bare) — allow only 'accessibility information' / 'step-free'
    for m in re.finditer(r"\baccessible\b", blob.lower()):
        ctx = blob.lower()[max(0, m.start() - 12): m.end() + 12]
        if "accessibility information" not in ctx and "step-free" not in ctx:
            v.append(("conditional:accessible", "bare 'accessible' claim (use 'accessibility information published' / 'step-free access stated')"))
            break

    # predicate states across decision (+ candidate attributes)
    states = {p["predicate_id"]: p["evidence_state"] for p in decision.get("predicates", [])}
    for c in decision.get("candidates", []):
        for a in c.get("attributes", []):
            states.setdefault(a["predicate_id"], a["evidence_state"])

    # 3. R-U-not-negative: a value-negative term while any predicate is U
    #    ('free' must not match the legitimate accessibility compound 'step-free')
    if any(s == "U" for s in states.values()):
        for neg in U_VALUE_NEGATIVES:
            hit = re.search(r"(?<!step-)\bfree\b", blob.lower()) if neg == "free" else _has(blob, neg)
            if hit:
                v.append(("R-U-not-negative", f"'{neg}' rendered while a predicate is unknown (U) — missing evidence shown as a negative fact"))

    # 4. R-no-collapse-claim: definite listing_attribute claim over a U/B predicate
    for cl in decision.get("claims", []):
        if cl.get("claim_type") == "listing_attribute" and states.get(cl.get("predicate")) in ("U", "B"):
            v.append(("R-no-collapse-claim", f"definite claim over {cl.get('predicate')} which is {states.get(cl.get('predicate'))}"))

    # 5. R-bnm-coverage
    if decision.get("terminal_decision") == "bounded_non_match":
        stmt = (decision.get("coverage_qualifier") or {}).get("statement")
        if not stmt and not any("we searched" in r.lower() or "checked" in r.lower() for r in rendered):
            v.append(("R-bnm-coverage", "bounded_non_match rendered without a coverage qualifier"))

    # 6. R-abstain-not-nomatch
    if decision.get("recommendation_action") == "model_abstained":
        for bad in ["no results", "no match", "nothing found", "nothing matched"]:
            if _has(blob, bad):
                v.append(("R-abstain-not-nomatch", f"model_abstained worded as '{bad}'"))

    # 7. R-scope-visible
    if decision.get("scope_qualifier") == "scope_indeterminate":
        if not any(_has(r, "incomplete") or "not fully" in r.lower() or "weren't fully" in r.lower() for r in rendered):
            v.append(("R-scope-visible", "scope_indeterminate not surfaced in rendered text"))

    return v


def _public_decision(fixture_rel):
    sys.path.insert(0, CB05)
    import projection_and_invariants as proj
    fields, planes = proj.load_classes()
    env = json.load(open(os.path.join(CB05, fixture_rel)))
    pub = proj.project(env, fields, set(planes["public"]))
    return pub["payload"]["decision"]


def main():
    lex = load_lexicon()
    fails = 0

    print("== completeness ==")
    cv = lint_completeness(lex)
    print("OK: every canonical enum value has approved wording" if not cv else "MISSING:")
    for e in cv: print("  -", e)
    fails += len(cv)

    dec = _public_decision("fixtures/valid/discovery_supported.json")

    print("\n== compliant render (should PASS) ==")
    good = [
        "Matches your confirmed needs",
        "Swimming: confirmed (published by the provider)",
        "Step-free access: confirmed",
        "Price: not published",
        "Suggested order",
        "across all feeds we searched",
    ]
    gv = lint_render(lex, dec, good)
    print("OK: compliant render clean" if not gv else "UNEXPECTED violations:")
    for rid, d in gv: print(f"  - {rid}: {d}")
    fails += len(gv)

    print("\n== over-claiming / collapsing render (should be FLAGGED) ==")
    bad = ["Best for you", "This pool is free", "fully accessible", "guaranteed suitable"]
    bv = lint_render(lex, dec, bad)
    caught = {rid for rid, _ in bv}
    want = {"global_banned", "R-U-not-negative"}
    ok_bad = want.issubset(caught)
    print(("DETECTED: " + ", ".join(sorted(caught))) if ok_bad else f"MISSED (caught={sorted(caught)})")
    for rid, d in bv: print(f"  - {rid}: {d}")
    fails += 0 if ok_bad else 1

    print("\n== adversarial fixture unknown_rendered_as_no (collapse in the DATA) ==")
    dec2 = _public_decision("fixtures/adversarial/unknown_rendered_as_no.json")
    av = lint_render(lex, dec2, ["Price: not published"])
    hit = any(rid == "R-no-collapse-claim" for rid, _ in av)
    print("DETECTED R-no-collapse-claim" if hit else "MISSED R-no-collapse-claim")
    for rid, d in av: print(f"  - {rid}: {d}")
    fails += 0 if hit else 1

    print("\nRESULT:", "ALL CONTENT-LINT CHECKS PASS" if fails == 0 else f"{fails} problem(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
