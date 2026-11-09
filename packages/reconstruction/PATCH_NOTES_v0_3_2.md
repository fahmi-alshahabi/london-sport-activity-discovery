# Engine v0.3.2 — the extended parent sidecar (D4 option (c))

**Date:** 11 September 2026 · AI-assisted, PROPOSED, unreviewed. One additive change over v0.3.1,
behind a flag that is **off by default**.

## Why this is not the "packaging step" it was described as

The provenance-only sidecar (`s1_parent_provenance.jsonl`, added in v0.3.1) already exists in every
run directory and has simply never been sent — that part *is* packaging.

Option (c) is not. The parent's descriptive field values are held in memory only, at the moment the
sidecar is written, and are not persisted to any artefact:

```python
parents_by_atid = {v["data"]["@id"]: v for v in p_state.values() ...}
...
for atid in sorted(parents_by_atid):
    pv = p_prov.get(parents_by_atid[atid].get("id")) or {}
    f.write(json.dumps({"@id": atid, **pv}, ...))     # <- pv only; data discarded
```

`parents_by_atid[atid]["data"]` is right there and is thrown away. So the fix is small, but it is an
engine change plus a re-run, not a repackage of files already on disk. Correcting that
characterisation is the point of this note.

## The change

Three edits, ~30 lines total.

1. **`ENGINE_VERSION`** → `s1-engine-0.3.2-PROPOSED`; `SUPERSEDES` gains v0.3.1's sha256
   (`31513ceb0a20534105d8d00fc74c7e2ce18fd71b4617f5a8d200701ab55b3866`).
2. **New `parent_descriptive()`**, placed immediately after `reconstruct()`.
3. **The sidecar write site** calls it when `--parent-descriptive` is passed.

```python
def parent_descriptive(parent, atid, parent_feed):
    pd = (parent.get("data") if parent else None) or {}
    fields, lineage = {}, {}
    for f in INHERITABLE_WHOLE:
        present = f in pd and pd[f] is not None
        if present:
            fields[f] = pd[f]
        lineage[f] = {"class": "INHERITED" if present else "SOURCE_ABSENT",
                      "rule": f"{POLICY_ID}:SessionSeries->ScheduledSession:{f}",
                      **({"parent_@id": atid, "parent_feed": parent_feed} if present else {})}
    return {"fields": fields, "lineage": lineage}
```

## The design decision that matters: no fourth vocabulary

A schedule-derived occurrence has **no `ScheduledSession` record of its own** — that is the whole
reason Open Sessions is invisible to an S1-records index. So every governed field such an occurrence
can carry comes from its parent, and only two outcomes exist: the parent has the field
(**`INHERITED`**) or it does not (**`SOURCE_ABSENT`**).

Those are already `reconstruct()`'s own class tokens. Nothing new is invented, which means:

- B0's `CLASS_MAP` needs no change — `INHERITED → T`, `SOURCE_ABSENT → U`, as today;
- any consumer that already reads `s1_records.jsonl` lineage rows reads these with the same code;
- the grade/class contract collision recorded in memo 73 is not widened by a fourth vocabulary.

The alternative — an `ON_PARENT` token — was rejected for exactly that reason, and the self-test
now asserts no such token can appear.

## Off by default, on purpose

With the flag off, the sidecar rows carry precisely the v0.3.1 key set and the five per-provider data
outputs are byte-identical. Only the receipt's engine identity differs, as it must. So v0.3.2 does
not silently change anything already delivered or reproduced, and turning the extension on is an
explicit, recorded act.

## Self-test

`python3 s1_engine_v0_3_2.py --selftest` → **61/61 checks pass** (v0.3.1's 54, plus 7 new):

| New check | What it asserts |
|---|---|
| default OFF | sidecar rows carry only the v0.3.1 keys — no silent shape change |
| every governed field gets a lineage row | values present iff `INHERITED`, absent iff `SOURCE_ABSENT` |
| no new class token | the class set is a subset of `{INHERITED, SOURCE_ABSENT}` |
| INHERITED rows bind back | `parent_@id` equals the row's own `@id`, `parent_feed` present |
| cross-output agreement | a child's `INHERITED` value for field *f* equals the sidecar's own copy for the same parent |
| flag changes nothing else | the four other per-provider outputs hash identically with and without it |
| receipt rebinds | `parent_provenance_sha256` matches the new file and differs from the flag-off run |

**These checks were mutation-tested**, because a suite that cannot fail is not evidence:

| Mutant | Result |
|---|---|
| class token changed to `ON_PARENT` | **59/61 — killed** |
| field values truncated on write | **60/61 — killed** |
| flag ignored (always emit) | **59/61 — killed** |

## Running it

```
python3 s1_engine_v0_3_2.py \
  --zip 2026-08-27.zip --zip-sha256 5b19cbdd49040dc85a7410bcd129a879dfa47435602cd60e30e6535513f33472 \
  --pages-csv pages.csv --ledger feeds_ledger.csv --terminals walk_terminals.csv \
  --snapshot 2026-08-27 --horizon-days 28 \
  --parent-descriptive \
  --out s1_full_run_v032
```

Same inputs, same runtime as the 8 September run. Afterwards, confirm the records really are
unchanged before anything downstream trusts it:

```
for p in s1_full_run_v031/*/; do
  diff -q "$p/s1_records.jsonl" "s1_full_run_v032/$(basename $p)/s1_records.jsonl"
done
```

Then check the coverage question left open on 10 September — that Playwaze's 214 expanded series all
resolve to a sidecar row:

```
python3 - <<'EOF'
import json, pathlib
d = pathlib.Path("s1_full_run_v032/Playwaze")
sidecar = {json.loads(l)["@id"] for l in open(d/"s1_parent_provenance.jsonl")}
series  = {json.loads(l)["series"] for l in open(d/"s1b_occurrences.jsonl")}
print(len(series), "occurrence series;", len(series & sidecar), "resolve to a sidecar row")
EOF
```

## Still open

- **PROPOSED and unreviewed.** This has not had a non-author read, and the corpus run under it has
  not happened. Nothing here is ratified.
- **The horizon is still `PROVISIONAL-M05-D-HORIZON`** — agenda 3.2 unratified — so a re-run under
  this engine inherits that label unchanged.
- **`category`, `level` and `ageRange`** get lineage rows here because they are in
  `INHERITABLE_WHOLE`, but they are not among B0's eight governed predicates. That asymmetry is
  pre-existing, not introduced here; it is worth a decision before either list is cited in the report.
