"""
D4 envelope assembly — §09-1 integration, Wesley's side.

Builds the slate-level DecisionEnvelope from D4's per-candidate gates, carrying the
(grade, provenance) pair per Clarence's C-BLOCK-05 v0.2 target spec.

KEY DISCIPLINE (Michael's instruction): the lineage->provenance mapping is IMPORTED
from provenance_map.py, never re-implemented here — so Wesley's and Michael's sides
cannot diverge. Same pattern as importing the reducer instead of re-implementing it.

Needs in the same folder: provenance_map.py (Michael's), reducer_v0_1_1.py.
Build against Clarence's target spec: C-BLOCK-05-v0.2-PROVENANCE-TARGET-SPEC.md.

STATUS: PROPOSED. Safe to build on a branch under either §09-1 outcome. Does NOT
render — the render wording is blocked by RATIFY-14-02 (non-author HCI review,
open since August); this module produces schema-valid envelopes, not rendered output.
"""
from reducer_v0_1_1 import reduce_decision, evidence_state
from provenance_map import provenance_of, strength_of, claim_provenance, claim_grade


# --- clause (2): a value's grade is strength, an inherited value stays 'explicit' ---
# The reducer already computes evidence_state per field; the lineage class comes from
# the record. We map: lineage class -> provenance (Michael's table), and lineage grade
# -> strength grade (Michael's table). Inherited => grade 'explicit', provenance 'inherited_from_parent'.

def _field_grade_and_provenance(record, field):
    """Return (grade, provenance) for one governed field, per the target spec.
       provenance is None for U states (spec: forbidden on U/B); grade still present."""
    lineage = record.get("lineage", {}) or {}
    meta = lineage.get(field)
    if not isinstance(meta, dict):
        # child-only field with no lineage row = U state (ABSENT_CHILD_ONLY_FIELD)
        return ("specification_default", None)     # U: grade present (how fallback derived), no provenance
    lineage_class = meta.get("class")
    lineage_grade = meta.get("grade")              # 'explicit' | 'inherited' | None in v0.1 packs
    grade = strength_of(lineage_grade) or "explicit"   # clause (2): inherited -> explicit
    provenance = provenance_of(lineage_class)      # None for U states
    return (grade, provenance)


def build_predicate(record, field, satisfied, mechanism=None):
    """Assemble one predicate object for the envelope, with (grade, provenance).
       Follows the spec: provenance required on T/F, absent on U/B."""
    state = evidence_state(record, field)          # T / U (reducer's own classing)
    grade, provenance = _field_grade_and_provenance(record, field)

    pred = {
        "predicate_id": field,
        "evidence_state": state,        # T = satisfied-and-supported / U = indeterminate
        "grade": grade,                 # strength (required, unconditional)
    }
    if mechanism:
        pred["mechanism"] = mechanism
    # spec conditional: provenance present iff a located value exists (T/F), forbidden on U/B
    if state == "T" and provenance is not None:
        pred["provenance"] = provenance
    # (U -> no provenance key at all, per spec)
    return pred


# --- clause (7) aggregation for a claim spanning several fields ---
def build_claim(record, fields):
    """Assemble a claim_tuple aggregating several governed fields (clause 7).
       Uses Michael's claim_provenance / claim_grade — the ratified aggregation rules.
       claim_grade may REFUSE (raise) if non-explicit contributors disagree — fail-closed."""
    contributing_prov = [_field_grade_and_provenance(record, f)[1] for f in fields]
    contributing_grade = [_field_grade_and_provenance(record, f)[0] for f in fields]

    claim = {"contributing_fields": list(fields)}
    prov = claim_provenance(contributing_prov)      # 7(i): inherited if any inherited
    if prov is not None:
        claim["provenance"] = prov
    # 7(ii): 'explicit' only if all explicit; disagreement -> claim_grade raises (refuse)
    claim["evidence_grade"] = claim_grade(contributing_grade)
    return claim


# --- slate-level terminal decision (Michael's own rule from the reducer generator) ---
def terminal_decision(candidate_verdicts):
    """Slate-level terminal decision from per-candidate gate verdicts:
       supported if ANY candidate is supported_match; else indeterminate if ANY is
       evidence_indeterminate; else bounded_non_match. (Michael's generator's stated rule.)"""
    if any(v == "supported_match" for v in candidate_verdicts):
        return "supported_match"
    if any(v == "evidence_indeterminate" for v in candidate_verdicts):
        return "evidence_indeterminate"
    return "bounded_non_match"


def assemble_envelope(query, constraints, ranked_cards, coverage_qualifier, versions):
    """Build the DecisionEnvelope from D4's ranked, gated candidates.
       ranked_cards: the D4 output list, each with card['_record'] and its gate verdict.
       Emits per-candidate attributes carrying (grade, provenance) for the constrained fields."""
    candidates, verdicts = [], []
    for card in ranked_cards:
        record = card["_record"]
        decision, detail = reduce_decision(record, constraints)   # keep detail (not discarded)
        verdicts.append(decision)

        # per-candidate attributes = the constrained fields, each with (grade, provenance)
        attributes = [build_predicate(record, field, sat)
                      for field, sat in constraints]

        candidates.append({
            "candidate_id": record.get("@id"),      # spec identity: the record @id, not item_id
            "decision": decision,
            "attributes": attributes,
        })

    envelope = {
        "payload": {
            "decision": {
                "terminal_decision": terminal_decision(verdicts),
                "scope_qualifier": _scope_qualifier(query),
                "coverage_qualifier": coverage_qualifier,   # honest capped-slice statement
                "candidates": candidates,
                "versions": versions,
            }
        }
    }
    return envelope


def _scope_qualifier(query):
    """A short scope statement for the query. Placeholder — align to app's expected text."""
    parts = []
    if query.get("activity"): parts.append(f"activity={query['activity']}")
    if query.get("region"):   parts.append(f"region={query['region']}")
    return "; ".join(parts) or "unconstrained"


if __name__ == "__main__":
    # smoke test the projection against provenance_map's own selftest
    from provenance_map import selftest
    print("provenance_map selftest:", selftest())
    print("\nd4_envelope assembly ready — imports provenance_of/strength_of/claim_* from Michael's map.")
    print("Build/validate against C-BLOCK-05 v0.2 target spec. Does not render (RATIFY-14-02).")
