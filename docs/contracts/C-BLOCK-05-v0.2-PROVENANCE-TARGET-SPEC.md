# C-BLOCK-05 v0.2 — target specification for the `provenance` leaf (§09-1)

> **REVISED 15 September 2026 — v0.2.1. `provenance` is `STAFF_EVIDENCE`, not `PUBLIC_SAFE`.**
> The original issue of this document classed all three provenance leaves `PUBLIC_SAFE`. That is
> superseded by the team design decision of 15 Sep: locus is an audit concept, not a public one.
> An inherited value is not less reliable — the `SessionSeries` is the authoritative record for
> series-level attributes, and a failed parent resolution is already a separate `U` state
> (`UNRESOLVABLE_PARENT_UNAVAILABLE`), so by the time a value reaches a user as `T` the locus
> carries no action they could take. It carries a great deal for a practitioner auditing
> publication quality, which is the staff plane's job.
>
> **Consequence, accepted and to be stated in the report:** M-21's finding that 696,652 of 722,036
> supported venues (96.5%) are held by inheritance is therefore *not* communicated on the public
> surface. The analysis establishes it; the interface does not say it, by decision rather than by
> omission.
>
> **Separately and independently:** the public wording for `grade.explicit` — currently "published
> by the provider" — implies the value was published on the individual listing, which is wrong
> 96.5% of the time. That implicature exists whether or not provenance is public, so the wording
> fix stands on its own. A locus-neutral candidate ("published") has been tested and passes the
> completeness and render lints, but lint passing is not semantic approval: the wording remains
> C-BLOCK-03's to approve and RATIFY-14-02 is still unfilled. `schedule_derived` and
> `specification_default` are unchanged — neither asserts locus, and both carry real meaning.

**Author:** Clarence (contract owner) · **Issued** 14 September 2026, **revised** 15 September 2026
(v0.2.1) · **Status:** SPECIFICATION, PROPOSED. **This is not a change to the frozen contract.**

The ratified motion of 13 September schedules §09-1 **post-submission**. This document exists so
Michael and Wesley can build against an exact target rather than a guess, without anyone editing a
sealed artefact. `decision-envelope.schema.json` remains at `0.1.0-PROPOSED` and is untouched;
every fixture, digest, invariant seal and certificate remains valid against it.

Build against this document. When §09-1 executes, this is what will land.

---

## 0. One correction to the plan as circulated

The plan says "three grade leaves". It is **two definitions and three disclosure-matrix entries**:

| | |
|---|---|
| `$defs.predicate` | carries `grade`. Referenced **twice** — `payload.decision.predicates[]` and `payload.decision.candidates[].attributes[]` (`"attributes": {"type":"array","items":{"$ref":"#/$defs/predicate"}}`) |
| `$defs.claim_tuple` | carries `evidence_grade`, a separate property |

So `provenance` is added to **two** definitions. Three disclosure-matrix entries follow, because
the matrix is keyed by path, not by definition.

---

## 1. `$defs.predicate` — add `provenance`

`additionalProperties` is `false`, so the property must be declared explicitly.

```json
"provenance": {
  "description": "Locus of the published value: on_record = published on this record (lineage ON_CHILD, CHILD_OVERRIDES or BOTH_EQUAL); inherited_from_parent = published on the parent series and inherited (lineage INHERITED). Orthogonal to grade: an inherited value is grade 'explicit' and MUST NOT be rendered as weaker than a value published on the record (§09-1 clause 2).",
  "enum": ["on_record", "inherited_from_parent"],
  "x-release-class": "STAFF_EVIDENCE"
}
```

**Conditional.** `provenance` is required when a value exists and absent when it does not. This
mirrors the existing `mechanism` idiom rather than inventing a second one. Add a second entry to
the existing `allOf`:

```json
{ "if":   { "properties": { "evidence_state": { "enum": ["T", "F"] } } },
  "then": { "required": ["provenance"] } },
{ "if":   { "properties": { "evidence_state": { "enum": ["U", "B"] } } },
  "then": { "not": { "required": ["provenance"] } } }
```

**Why `provenance` does not share `grade`'s rule.** `grade` is in `required` unconditionally, and
the current fixtures rely on that: `discovery_supported.json` carries
`{"predicate_id":"price","evidence_state":"U","mechanism":"source_absence","grade":"specification_default"}`.
On a `U`, `grade` describes how the *fallback* was derived, which is coherent. `provenance` has no
such reading — there is no published value, so there is no locus. It must be absent, not defaulted.

**Why `B` also excludes it.** A `B` state says two sources disagree and the conflict is unresolved.
Assigning one provenance would assert a winner, which is exactly what `B` records as undecidable.
The existing contract already handles `B` through `mechanism: conflicting_value`; provenance stays
out.

`grade` itself is **unchanged** — enum, required status and semantics all stand. §09-1 clause (2):
inherited values keep `grade: "explicit"`.

## 2. `$defs.claim_tuple` — add `provenance`

```json
"provenance": {
  "description": "Aggregate locus over the claim's contributing values — see §4. Present only when the claim rests on at least one located value. STAFF_EVIDENCE: carried for audit, never projected to the public plane.",
  "enum": ["on_record", "inherited_from_parent"],
  "x-release-class": "STAFF_EVIDENCE"
}
```

Not added to `required`: a claim may rest entirely on unknowns. `evidence_grade` is unchanged.

## 3. Disclosure matrix — three entries, landing in the same change

```
payload.decision.predicates[].provenance                 STAFF_EVIDENCE
payload.decision.candidates[].attributes[].provenance    STAFF_EVIDENCE
payload.decision.claims[].provenance                     STAFF_EVIDENCE
```

`STAFF_EVIDENCE` per the 15 Sep decision — carried for audit and validation, never projected to
the public plane. This is evidence symmetry with authority asymmetry: both surfaces agree on the
retained decision, the staff plane alone sees where each value was published.

**These must land in the same commit as the schema change.** Projection is fail-closed: a leaf
present in the schema but absent from the matrix is silently dropped from every plane. The field
would validate and never render.

## 4. Aggregation — the rules, and the one that refuses

Per-predicate values are atomic. Aggregation applies only to `claim_tuple`, whose `receipt_ids` is
`minItems: 1` and may carry several contributing values.

**Provenance.** `inherited_from_parent` if **any** contributing value is inherited; `on_record` if
all are on-record; absent if none is located. Conservative, and it cannot overstate: a claim resting
partly on a parent is never described as published on the record.

**Grade.** `explicit` only if **every** contributing value is `explicit`. If the non-explicit
contributors all agree, the claim carries that shared value. **If they disagree, the claim is
refused — not downgraded by guess.**

**Why refuse.** Nothing in the contract orders `schedule_derived` against `specification_default`.
The schema's prose and the lexicon guidance both say each is "visibly weaker than explicit", which
orders them against `explicit` and not against each other; `_GRADES` in the checker, `CANON` in the
linter and the schema enum are all unordered sets. A rule requiring a weaker-of comparison between
them has no definition to appeal to, so it cannot be implemented honestly. The refusal is
fail-closed and logged as a named open item, in the same family as `UNSUPPORTED` in the pack
verifier and the typed `service_failure` route.

**Refusal behaviour, for the render layer.** A refused claim is dropped whole before projection —
never rendered with a missing or guessed grade. This is the existing path for an attribute whose
evidence state has no approved wording, which is dropped entirely rather than shown with a blank
qualifier.

**Not the reducer's precedence.** An earlier draft of these rules described them as "weakest
contributing value wins" by analogy with `reduce_decision`. That analogy is wrong and was
withdrawn on 13 September: executed, one `T:unsatisfied` plus one `U` returns `bounded_non_match`,
not `evidence_indeterminate` — a demonstrated failure beats an unknown, and `supported_match`
requires unanimity. The rules above are stated on their own terms.

## 5. Mapping from lineage class — for Michael and Wesley

The engine's per-field `record["lineage"][field]["class"]` is the source:

| lineage class | `provenance` | note |
|---|---|---|
| `ON_CHILD` | `on_record` | |
| `CHILD_OVERRIDES` | `on_record` | child value wins; locus is the record |
| `BOTH_EQUAL` | `on_record` | attested both sides; record is sufficient |
| `INHERITED` | `inherited_from_parent` | |
| `SOURCE_ABSENT` | *(absent)* | `U` state — no value, no locus |
| `UNRESOLVABLE_PARENT_UNAVAILABLE` | *(absent)* | `U` state |

Total over the classes that occur. Sampled against
`WESLEY_S1_CORPUS_V2026-08-27` (Oxford University, 30 records): `ON_CHILD` 210, `INHERITED` 197,
`SOURCE_ABSENT` 103 — every class present maps.

## 6. What executing this will require in the applications stream

Recorded so the cost is visible, not to be done now.

1. Schema: two `$defs` edits plus the two `allOf` conditionals.
2. Disclosure matrix: three entries, same commit.
3. Certificate checker: `_GRADES` is unaffected; a `provenance` validity check is added, and
   `CHECKER_VERSION` bumps from `chk-1.0`. Version compatibility is exact equality, so every
   certificate and release manifest moves with it.
4. Render lexicon: a new `provenance` category with approved wording for both values, plus the
   `CANON` completeness list.
5. Fixtures: 2 valid and 6 adversarial re-sealed; 8 invariants and 11 mutation branches re-run;
   assurance case re-validated.

**The blocker is item 4, and it is not effort.** Approved wording requires a non-author
HCI/content reviewer under C-BLOCK-03. That role has no holder: `CL-2`, `CL-4` and `CL-10` in the
assurance case all read `name: null`, and naming the eligible reviewer is `RATIFY-14-02`, open since
August. The wording cannot be self-approved. Until the reviewer is named, the schema can change and
the field still cannot render.

## 7. Status

Specification only. The frozen contract is unchanged at `0.1.0-PROPOSED`. Building against this
document is safe; executing it is a C-BLOCK-05 freeze change scheduled post-submission by the
ratification record of 13 September 2026, and gated on `RATIFY-14-02`.
