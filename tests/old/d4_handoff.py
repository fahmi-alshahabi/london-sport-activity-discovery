"""
D4 handoff — Wesley's side, per Clarence's D4-HANDOFF-INTERFACE-v0.1.

Emits $defs/candidate and $defs/predicate objects DIRECTLY (no intermediate), so
there is nothing on the seam to drift. Clarence's layer assembles these into the
full envelope (adds metadata, computes digest, runs the certificate checker).

Corrections applied from Clarence's schema verification:
  - candidate carries candidate_id, rank, pool (NOT 'decision' — additionalProperties:false)
  - pool vocabulary is NOT the gate vocabulary:
        supported_match       -> pool 'supported'
        evidence_indeterminate -> pool 'indeterminate'   (held separately)
        bounded_non_match      -> EXCLUDED (candidate removed) + a why_not_entry
  - excluded candidates produce a why_not_entry {predicate_id, blocking_state F/U/B}
    from the reducer detail (the detail we stopped discarding)

Imports Michael's provenance_map (shared table) and the reducer (both never re-implemented).
"""
from reducer_v0_1_1 import reduce_decision, evidence_state
from provenance_map import provenance_of, strength_of


# --- gate verdict -> Clarence's pool vocabulary (different sets, not synonyms) ---
VERDICT_TO_POOL = {
    "supported_match":       "supported",
    "evidence_indeterminate": "indeterminate",
    "bounded_non_match":      "excluded",     # candidate is REMOVED from the slate
}


def _grade_and_provenance(record, field):
    lineage = record.get("lineage", {}) or {}
    meta = lineage.get(field)
    if not isinstance(meta, dict):
        return ("specification_default", None)         # U: grade present, no provenance
    grade = strength_of(meta.get("grade")) or "explicit"   # clause (2): inherited -> explicit
    provenance = provenance_of(meta.get("class"))          # None on U states
    return (grade, provenance)


def build_predicate(record, field):
    """$defs/predicate — grade unconditional, provenance on T/F only. (Already validated.)"""
    state = evidence_state(record, field)          # T / U
    grade, provenance = _grade_and_provenance(record, field)
    pred = {"predicate_id": field, "evidence_state": state, "grade": grade}
    if state == "T" and provenance is not None:
        pred["provenance"] = provenance
    return pred


def build_why_not(record, constraints, detail):
    """For an EXCLUDED (bounded_non_match) candidate: one why_not_entry per blocking predicate.
       blocking_state is F/U/B. We derive it from the reducer's per-field detail — the info
       we kept by not discarding `detail` from reduce_decision."""
    entries = []
    for field, _sat in constraints:
        blocking = _blocking_state_for(field, detail)   # F / U / None, from reducer detail
        if blocking:
            entries.append({"predicate_id": field, "blocking_state": blocking})
    return entries


def _blocking_state_for(field, detail):
    """Map one field's reducer detail to the why_not blocking_state (F/U).
       Verified against the real reducer (Clarence, executed): detail only ever contains
       'T:satisfied' | 'T:unsatisfied' | 'U'. Mapping:
         'T:unsatisfied' -> 'F'  (the refuted constraint that produces bounded_non_match)
         'U'             -> 'U'
         'T:satisfied'   -> not blocking (returns None)
       'B' (conflict) is UNREACHABLE from D4: evidence_state() returns only T or U, so no
       D4 path produces a conflict state. Recorded as a coverage fact, not coded for."""
    d = (detail or {}).get(field) if isinstance(detail, dict) else None
    if d == "T:unsatisfied":
        return "F"
    if d == "U":
        return "U"
    return None  # T:satisfied -> not a blocking predicate


def build_candidates(ranked_cards, constraints):
    """Emit $defs/candidate objects directly. Returns (candidates, why_not, verdicts).
       - supported/indeterminate candidates go in `candidates` with their pool.
       - excluded (bounded_non_match) candidates are REMOVED and produce why_not entries.
       Clarence assembles these into the envelope and computes the terminal_decision + digest.
    """
    candidates, why_not, verdicts = [], [], []
    for rank, card in enumerate(ranked_cards, start=1):
        record = card["_record"]
        decision, detail = reduce_decision(record, constraints)   # keep detail
        verdicts.append(decision)
        pool = VERDICT_TO_POOL[decision]

        attributes = [build_predicate(record, field) for field, _ in constraints]

        if pool == "excluded":
            # candidate removed from slate; record why_not (obligation on exclusion)
            for entry in build_why_not(record, constraints, detail):
                why_not.append(entry)
            continue   # do NOT add to candidates[]

        candidates.append({
            "candidate_id": record.get("@id"),
            "rank": rank,
            "pool": pool,                     # 'supported' | 'indeterminate'
            "attributes": attributes,
        })

    return candidates, why_not, verdicts


# ---------------------------------------------------------------------
#  COVERAGE_QUALIFIER — Wesley writes this (only your run knows the coverage).
#  This is the claim boundary for the whole handoff. Fill from your actual run.
# ---------------------------------------------------------------------
def coverage_qualifier(loaded_count, total_corpus, skipped_providers):
    """The honest coverage statement — the claim boundary for the whole handoff.
       A bounded_non_match means 'no retrieved candidate matched', NEVER 'no matches exist'."""
    if not skipped_providers and loaded_count >= total_corpus:
        # full-corpus run: no slice, nothing excluded
        return (
            f"Candidates were retrieved from the full reconstructed corpus "
            f"({loaded_count:,} records, all providers). A bounded non-match therefore means no "
            f"candidate in the corpus satisfied the constraints under the retrieval and evidence "
            f"model, not that no matching activity exists in the wider OpenActive ecosystem or "
            f"in provision not published to it."
        )
    # capped-slice run: state the slice honestly
    return (
        f"Candidates were retrieved from a loaded slice of {loaded_count:,} of "
        f"{total_corpus:,} corpus records; providers {', '.join(skipped_providers)} were "
        f"excluded under documented size caps. A bounded non-match therefore means no candidate "
        f"within the retrieved slice satisfied the constraints, not that no matching activity "
        f"exists in the full corpus or the wider ecosystem."
    )


if __name__ == "__main__":
    print("d4_handoff ready.")
    print("VERDICT_TO_POOL:", VERDICT_TO_POOL)
    print("\nEmits $defs/candidate + $defs/predicate directly per Clarence's interface.")
    print("Excluded (bounded_non_match) candidates -> removed + why_not_entry.")
    print("\nExample coverage_qualifier:")
    print(" ", coverage_qualifier(724361, 724361, []))
