# IR-15 representation clause — §09-1 clause (3), register owner's text

**Status:** DRAFTED 13 September 2026, AI-assisted; PROPOSED. **Do not insert into the Interpretation
Register until the ratification record carrying §09-1 has merged.** The clause cites that decision by
date, and a register clause citing a decision that has not been recorded is the defect this project
exists to catch. On merge: replace `[RATIFICATION DATE]`, bump the register to v0.2.2, and record the
edit in the register's own change line.

**Target:** Interpretation Register v0.2.1 (10 Aug 2026), entry **IR-15 — Generated-occurrence field
derivation (source rules plus ⚠ L5 lineage grades)**. The existing entry is retained verbatim; the
clause is appended.

---

## IR-15 as it stands (v0.2.1, unchanged)

> L2 supplies generated `@type` from `scheduledEventType`; IR-10 supplies identity and IR-19 end
> calculation. ⚠ **L5 provenance policy:** derived fields carry `schedule_derived`; later inheritance
> carries `inherited`; neither may collapse into `explicit`.

## Clause to append (v0.2.2)

> ⚠ **L5 representation clause (team decision §09-1, recorded [RATIFICATION DATE]):** the lineage
> grades above are *lineage* grades — they say where a value came from. At every contract boundary
> (the DecisionEnvelope, the lineage pack, the evidence substrate's outputs) a lineage grade is carried
> as the **pair (`grade`, `provenance`)**, where `grade` is the boundary's derivation-*strength* scale
> (`explicit` | `schedule_derived` | `specification_default`) and `provenance` is the locus of the
> published value (`on_record` | `inherited_from_parent`). Under this representation the lineage grade
> `inherited` is carried as (`grade: explicit`, `provenance: inherited_from_parent`) — the value *was*
> published, on the parent — and **the no-collapse rule is satisfied when the inheritance fact is
> carried, never erased.** Carrying `inherited` as `explicit` *without* the provenance leaf remains a
> collapse and is rejected. No rendering may describe an inherited value as weaker than one published
> on the record. `provenance` is projected from the S1 lineage class by the single shared table
> (`provenance_map.py`: `ON_CHILD` / `CHILD_OVERRIDES` / `BOTH_EQUAL` → `on_record`; `INHERITED` →
> `inherited_from_parent`; U states carry no locus) and is present iff a located value exists.
> **Scope:** this clause fixes the representation for values carrying an S1 lineage class. It does not
> define the locus of a *schedule-derived* value, which carries no lineage class; that is an open
> item recorded against this clause (see note below), not a rule.

## Note recorded with the clause — one open item, named rather than decided

A schedule-derived value (an S1b occurrence's start or end time) is computed from a `Schedule`
published on the parent series; the value itself was never published anywhere. It carries
`grade: schedule_derived` on the strength axis, but **no S1 lineage class**, so `provenance_map.py`
has nothing to project and the envelope target specification's conditional (provenance required on
every located value) would not be satisfiable for it. This does not arise in lineage pack v0.2
(S1b occurrences are not candidates) and does not arise in the delivered D4 corpus slice (S1 records
only). If S1b occurrences ever enter the envelope, the register owner and the contract owner must
decide one of: (a) a seventh class for the map (the defensible candidate is `inherited_from_parent`,
because the generating rule was published on the parent and `on_record` would falsely locate the
value on the record); or (b) exempting `schedule_derived` values from the provenance conditional.
**Not decided here.** Recorded so the next person to hit it finds a named gap and not a silent one.

## Why this is the register owner's clause and not the contract owner's

IR-15 is where the no-collapse rule lives. The envelope and pack schemas *implement* a representation;
only the register can say that the representation *satisfies* the rule. Without this clause, a
verifier reading IR-15 ("neither may collapse into `explicit`") and then a v0.2 pack row reading
`grade: explicit` for an inherited value would be entitled to call it a collapse. With it, the same
verifier reads the pair and finds the inheritance fact carried in `provenance` and in
`lineage_class`, which is what the rule protects.

## Verification the clause rests on (all executed 13 Sep 2026)

- `provenance_map.py` self-test 20/20; domain and T/U split cross-checked equal to the B0 substrate's
  `CLASS_MAP` (b0-evidence-substrate-0.1.1-PROPOSED).
- Corpus totality from the frozen engine's own counters (`corpus_rollup.json`, s1-engine-0.3.1,
  V2026-08-27): 7,372,270 field-level lineage assignments over 10 governed fields × 737,227 records;
  every field totals exactly 737,227; **every observed class maps** — 1,785,551 `on_record`;
  2,689,489 `inherited_from_parent`; 2,897,230 no locus (U).
- `lineage_pack_v0_2_0.py` self-test 32/32, including a differential against v0.1.1 on seven queries
  over one fixture run (digests identical; every non-evidence byte identical; the evidence delta is
  exactly the projection) and the two delivered real packs migrated with their stored digests
  unchanged (`135ca092…`, `64f5a60c…`) and valid against schema v0.2 under both the generator's
  validator and the independent `jsonschema` library (Draft 2020-12).
