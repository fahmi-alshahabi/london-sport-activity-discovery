#!/usr/bin/env python3
"""Independent pack verifier — recompute a stored decision digest from a pack's OWN fields.

Michael, 2 Sep: "confirm both packs load in your validator and decision_digest reproduces when
you recompute it from the pack's own fields, not just that the file parses."

--------------------------------------------------------------------------------------------
TYPED OUTCOMES (v0.2, 9 Sep) — absence is not refutation.
--------------------------------------------------------------------------------------------
v0.1 of this file hard-coded ONE artefact family (the C-BLOCK-05 `payload.decision` envelope) and
returned a FAILURE verdict for anything else, with the message "carries no payload.decision".
Run against Michael's lineage packs — a different family, with no `payload` at all — it printed
"RESULT: 2 FAILURE(S)" and exited 1. That output reads as a negative fact about the artefacts,
when the true state is that the verifier could not read them. That is precisely the collapse the
applications are built to prevent (INV-NO-COLLAPSE), committed by the tool that checks for it.

So outcomes are now a closed, typed set, and "cannot determine" is first-class:

    PASS         digest recomputed from the pack's own fields and matched
    MISMATCH     recomputed and DID NOT match          -> adverse finding about the artefact
    MALFORMED    unparseable / structurally incoherent -> adverse finding about the artefact
    INCOHERENT   digest REPRODUCES, but the artefact contradicts an invariant of its own format
                 -> adverse. A digest check alone cannot find this (v0.3 passed such a pack at
                 exit 0 before the check existed).
    UNSUPPORTED  family recognised, but this verifier implements no construction for it
                 -> NOT an adverse finding. Says nothing about the artefact.

A fault in THIS TOOL is a fourth thing again, and is never counted as a finding about an
artefact: exit 3, result INCOMPLETE.

Exit: 0 all PASS · 1 any MISMATCH/MALFORMED · 2 only UNSUPPORTED (indeterminate, no verdict)
      · 3 tool faulted, result incomplete.

--------------------------------------------------------------------------------------------
INDEPENDENCE — read-order is the evidence, and it is recorded per family
--------------------------------------------------------------------------------------------
A second implementation is evidence only if it was derived SEPARATELY from the one under test.
Copying the sender's recipe and then confirming their digests proves the copy was faithful and
nothing about the artefact. So each family's construction carries a PROVENANCE note stating what
was read, and when, relative to the result being recorded. For the lineage-pack family the
construction was written from the pack's own `decision_ref.digest_rule`, the result committed at
951bffb, and only then was the sender's generator opened — so that run is rule-conformance
evidence, and the later confirmation is explicitly not claimed as independent.

Where no construction has been derived for a recognised family, the tool does NOT guess and does
NOT accept a supplied recipe: it returns UNSUPPORTED and prints the pack's own `digest_rule`,
which is the correct oracle to implement from, because implementing from it tests whether the
artefact does what it claims.

Run:  python3 packages/evaluation/verify_pack.py <pack.json> [<pack2.json> ...]
"""
from __future__ import annotations
import copy, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
CB05 = os.path.join(REPO, "packages", "application-contracts", "c-block-05")
sys.path.insert(0, CB05)
import projection_and_invariants as proj  # noqa: E402

FIELDS, PLANES = proj.load_classes()

PASS, MISMATCH, MALFORMED, UNSUPPORTED = "PASS", "MISMATCH", "MALFORMED", "UNSUPPORTED"
ADVERSE = (MISMATCH, MALFORMED, "INCOHERENT")
# A fault in THIS TOOL is not a finding about the artefact (Michael, 9 Sep). v0.2 counted a
# crashed control into `adverse`, so a tool exception printed under a heading that reads as a
# verdict on the pack — the same collapse as v0.1, one level down. Tracked separately, own exit.
TOOL_FAULT = "TOOL_FAULT"
# Digest reproduces, but the pack contradicts an invariant of its own format. Adverse, and kept
# distinct from MISMATCH because it names a different category of violation.
INCOHERENT = "INCOHERENT"


def _rank_incoherence(cands):
    """INV-SLATE-ORDER: array position must equal certified rank.

    Michael, 9 Sep: a lineage pack whose `rank` values are altered WITHOUT reordering the array
    still verifies, because the digest covers array order and not rank. Confirmed by running the
    tamper — swapping two ranks reproduced the stored digest byte-for-byte and this tool returned
    exit 0. The pack violates the generator's own stated invariant ("slate order is rank order",
    lineage_pack_v0_1.py docstring l.28) and passes every digest check.

    The same hole existed in THIS TOOL for our own family: a C-BLOCK-05 envelope MINTED with rank
    [2,1] over array order [A,B] is self-consistent — its digest is correct for its contents — and
    v0.3 passed it at exit 0, because this verifier checked digest reproduction and nothing else.
    So the check runs for both families.

    SCOPE CORRECTION (9 Sep, after asserting otherwise to Michael). This is a gap in THIS TOOL, and
    NOT in the C-BLOCK-05 invariant battery. I claimed the battery was structurally blind to minted
    (as opposed to perturbed) artefacts and that INV-SLATE-ORDER was therefore a release gate not
    holding. Both claims are false, and checking them takes one run:
      · `inv_slate_order` DOES fail on the minted rank-[2,1] envelope, with the correct message.
      · `fixtures/adversarial/client_sort_reorder.json` is ALREADY that exact case — ids
        [sess-102, sess-101], ranks [2,1], sealed with a self-consistent digest.
      · 5 of the 6 adversarial fixtures are minted, not perturbed. The one perturbation
        (tampered_public_digest) targets INV-REPLAY, where a stale digest IS the defect.
      · All 6 isolate their target invariant exactly.
    What is true and survives: a digest establishes integrity, never validity, so a verifier that
    checks only digest reproduction cannot find this class of defect. That was this tool's gap.

    Not yet frozen schema text for the lineage family — it is the generator's docstring invariant,
    proposed as schema clause 3. Fires only when every candidate carries a rank.
    """
    ranks = [c.get("rank") for c in cands if isinstance(c, dict)]
    if not ranks or any(r is None for r in ranks):
        return None                                   # rank absent -> no invariant to check
    if not all(isinstance(r, int) for r in ranks):
        return f"non-integer rank values: {ranks}"
    expected = list(range(1, len(ranks) + 1))
    if ranks != expected:
        return (f"rank does not equal array position: ranks {ranks}, expected {expected}. "
                f"The digest does NOT cover this, so the pack reproduces its stored digest while "
                f"contradicting its own slate-order invariant.")
    return None


# ------------------------------------------------------------------ family detection
def family_of(doc):
    """Classify by SHAPE only. Never guesses a digest construction."""
    if not isinstance(doc, dict):
        return None
    if isinstance(doc.get("payload"), dict) and isinstance(doc["payload"].get("decision"), dict):
        return "envelope"          # C-BLOCK-05 terminal DecisionEnvelope
    if isinstance(doc.get("decision_ref"), dict) and isinstance(doc.get("candidates"), list):
        return "lineage_pack"      # Michael's lineage packs
    return None


# ------------------------------------------------------------------ envelope family (ours)
def _verify_envelope(doc, name):
    pub = proj.project(doc, FIELDS, set(PLANES["public"]))
    if pub is proj.DROP or not (pub.get("payload") or {}).get("decision"):
        return (MALFORMED, f"{name}: public projection is empty — cannot reproduce a digest")
    pd = copy.deepcopy(pub["payload"]["decision"])
    stored = pd.pop("digest", None)
    if not stored:
        return (MALFORMED, f"{name}: no stored digest in the projected decision — nothing to compare")
    recomputed = proj.sha(pd)
    cands = pd.get("candidates") or []
    order = [c.get("candidate_id") for c in cands]
    ranks = [c.get("rank") for c in cands]
    if stored != recomputed:
        return (MISMATCH, f"{name}: DIGEST MISMATCH\n     stored     = {stored}\n"
                          f"     recomputed = {recomputed}")
    bad = _rank_incoherence(cands)
    if bad:
        return (INCOHERENT, f"{name}: DIGEST REPRODUCES BUT ENVELOPE IS INCOHERENT\n     {bad}")
    return (PASS, f"{name}: REPRODUCES  {recomputed}\n"
                  f"     covers slate content+order: {order} (ranks {ranks})\n"
                  f"     terminal={pd.get('terminal_decision')} scope={pd.get('scope_qualifier')} "
                  f"action={pd.get('recommendation_action')}")


# ------------------------------------------------------------------ lineage_pack family
def _lineage_digested_object(doc):
    """The digested object for the lineage-pack family.

    PROVENANCE, because it bears on what a run of this licenses: written on 9 Sep from the pack's
    own `decision_ref.digest_rule` alone, with the sender's recipe and generator unopened, and the
    result recorded at commit 951bffb BEFORE either was read. Subsequently confirmed against
    `lineage_pack_v0_1.py` l.402 in the sender's Part 2. So the construction is rule-derived; the
    confirmation is not independent and is not claimed as such.
    """
    cands = doc.get("candidates") or []
    return {
        "query_id":    (doc.get("query") or {}).get("query_id"),
        "constraints": (doc.get("query") or {}).get("constraints"),
        "slate":       [c.get("candidate_id") for c in cands],
        "decisions":   [[c.get("candidate_id"), c.get("decision"), c.get("detail")] for c in cands],
    }


def _lineage_sha(obj):
    # ensure_ascii=False is REQUIRED and neither real pack demonstrates it: both digested subsets
    # are pure ASCII, so both settings reproduce. Generator l.77 pins False; the sender's first
    # recipe omitted it and silently took True, which would have produced a false MISMATCH against
    # a correct pack on the first accented venue name. Pinned here explicitly for that reason.
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _verify_lineage_pack(doc, name):
    ref = doc.get("decision_ref") or {}
    stored = ref.get("decision_digest")
    if not stored:
        return (MALFORMED, f"{name}: lineage pack carries no decision_ref.decision_digest")
    recomputed = _lineage_sha(_lineage_digested_object(doc))
    cands = doc.get("candidates") or []
    order = [c.get("candidate_id") for c in cands]
    if stored != recomputed:
        return (MISMATCH, f"{name}: DIGEST MISMATCH\n     stored     = {stored}\n"
                          f"     recomputed = {recomputed}")
    bad = _rank_incoherence(cands)
    if bad:
        return (INCOHERENT, f"{name}: DIGEST REPRODUCES BUT PACK IS INCOHERENT\n     {bad}")
    return (PASS, f"{name}: REPRODUCES  {recomputed}\n"
                  f"     covers slate content+order ({len(order)} candidates) and per-candidate decisions\n"
                  f"     rank is positional and NOT digest-covered — invariant checked separately: OK\n"
                  f"     terminal={ref.get('terminal_decision')} pools={ref.get('pools')}")


VERIFIERS = {"envelope": _verify_envelope, "lineage_pack": _verify_lineage_pack}


def verify(path):
    name = os.path.basename(path)
    try:
        doc = json.load(open(path))
    except Exception as ex:
        return (MALFORMED, f"{name}: PARSE FAILED — {ex!r}")
    fam = family_of(doc)
    if fam is None:
        return (UNSUPPORTED,
                f"{name}: unrecognised artefact family (top-level keys: {sorted(doc)[:10]}) — "
                f"no verdict. This is NOT a finding about the artefact.")
    return VERIFIERS[fam](doc, name)


# ------------------------------------------------------------------ order-sensitivity control
def order_sensitivity(path):
    """Positive control (agenda 4.3): perturb the pack, show the digest moves.

    Only runs for families with an implemented construction. A field that is absent from the
    digested object is reported as NOT COVERED — an observation about what the digest spans,
    never an automatic failure, because a family may legitimately pin order by other means.
    """
    doc = json.load(open(path))
    fam = family_of(doc)
    if fam is None:
        return None

    if fam == "lineage_pack":
        base = _lineage_sha(_lineage_digested_object(doc))
        out, c = [], doc.get("candidates") or []
        if len(c) >= 2:
            e = copy.deepcopy(doc); e["candidates"].reverse()
            out.append(("slate ORDER reversed", _lineage_sha(_lineage_digested_object(e)) != base, True))
            # rank is NOT in this family's digested object, and it is DERIVED from array position
            # (generator l.388, `enumerate(slate, 1)`), so it carries no independent ordering
            # information. An UNCHANGED digest here is the CORRECT result -> expected=False.
            e = copy.deepcopy(doc); cc = e["candidates"]
            cc[0]["rank"], cc[1]["rank"] = cc[1]["rank"], cc[0]["rank"]
            out.append(("rank values swapped", _lineage_sha(_lineage_digested_object(e)) != base, False))
        if c:
            e = copy.deepcopy(doc); e["candidates"][0]["candidate_id"] = "cand-PERTURBED"
            out.append(("candidate_id changed", _lineage_sha(_lineage_digested_object(e)) != base, True))
            e = copy.deepcopy(doc); e["candidates"][0]["decision"] = "__perturbed__"
            out.append(("a decision changed", _lineage_sha(_lineage_digested_object(e)) != base, True))
        return out

    def dig(e):
        p = proj.project(e, FIELDS, set(PLANES["public"]))
        d = copy.deepcopy(p["payload"]["decision"]); d.pop("digest", None)
        return proj.sha(d)

    base = dig(doc)
    out = []
    c = (doc.get("payload") or {}).get("decision", {}).get("candidates") or []
    if len(c) >= 2:
        e = copy.deepcopy(doc); e["payload"]["decision"]["candidates"].reverse()
        out.append(("slate ORDER reversed", dig(e) != base, True))
        e = copy.deepcopy(doc); cc = e["payload"]["decision"]["candidates"]
        cc[0]["rank"], cc[1]["rank"] = cc[1]["rank"], cc[0]["rank"]
        out.append(("rank values swapped", dig(e) != base, True))
    if c:
        e = copy.deepcopy(doc); e["payload"]["decision"]["candidates"][0]["candidate_id"] = "sess-PERTURBED"
        out.append(("candidate_id changed", dig(e) != base, True))
    return out


def main(paths):
    if not paths:
        print("usage: python3 packages/evaluation/verify_pack.py <pack.json> [...]"); return 2
    adverse = indeterminate = tool_faults = 0
    print("== pack verification (recomputed from each pack's own fields) ==")
    for p in paths:
        code, msg = verify(p)
        tag = {PASS: "OK ", MISMATCH: "BAD", MALFORMED: "BAD", INCOHERENT: "BAD", UNSUPPORTED: " ? "}[code]
        print(f"[{tag}] {msg}")
        adverse += 1 if code in ADVERSE else 0
        indeterminate += 1 if code == UNSUPPORTED else 0

    print("\n== order-sensitivity control (agenda 4.3: is order inside the digest?) ==")
    for p in paths:
        n = os.path.basename(p)
        try:
            res = order_sensitivity(p)
        except Exception as ex:
            # A tool fault, NOT a finding about the artefact. Never counted into `adverse`.
            print(f"[!! ] {n}: control CRASHED — TOOL FAULT, no verdict on this artefact — {ex!r}")
            tool_faults += 1; continue
        if res is None:
            print(f"[ ? ] {n}: no construction implemented for this family — control not run, no verdict")
            continue
        if not res:
            print(f"[   ] {n}: no candidates — control not applicable")
        for label, changed, expected in res:
            if changed:
                print(f"[OK ] {n}: {label} -> digest differs (covered)")
            elif expected:
                print(f"[BAD] {n}: {label} -> digest UNCHANGED, but this family claims to cover it")
                adverse += 1
            else:
                print(f"[ - ] {n}: {label} -> digest unchanged; not in the digested object "
                      f"(expected — observation, not a fault)")

    if tool_faults:
        print(f"\n!! {tool_faults} TOOL FAULT(S) — this verifier failed, which is not a finding "
              f"about any artefact above.")
    if adverse:
        print(f"\nRESULT: {adverse} ADVERSE FINDING(S)"
              + (f"; {indeterminate} indeterminate" if indeterminate else ""))
        return 1
    if tool_faults:
        print("\nRESULT: NO ADVERSE FINDING, but the tool faulted — result INCOMPLETE.")
        return 3
    if indeterminate:
        print(f"\nRESULT: NO ADVERSE FINDING. {indeterminate} artefact(s) INDETERMINATE — "
              f"recognised but not verified here. This is not a negative result about them.")
        return 2
    print("\nRESULT: ALL PACKS REPRODUCE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
