# Reconstruction and Evidence Layer

**Owner:** Michael Chellam Sebastian · **Status:** PROPOSED (see *Status and limits*) · **Python:** 3.9+ · **Dependencies:** none

This module turns an archived OpenActive feed snapshot into analysable activity records, and attaches to every field a statement of *where that value came from and how well it is evidenced*. It is the layer the report's central claim rests on: that a discovery system can tell the difference between **"no matching activity exists"** and **"we cannot tell"**, instead of returning an empty list for both.

Two problems are solved here. First, **inheritance**: in OpenActive, a repeating activity is published as a `SessionSeries` and each dated occurrence as a `ScheduledSession`, and a session may omit anything its series already states. A consumer reading sessions alone sees a location on 3.44% of records; resolving inheritance raises that to 97.94%. Second, **honest absence**: once a value can be inherited, "missing" stops being a single thing — it may be absent at source, or unresolvable because the parent was never collected. Those are different facts about the world and the evidence model keeps them apart.

---

## Quick start — 60 seconds, nothing to install

Every script is standard-library Python. There is no `pip install` step, no virtualenv and no lock file to reconcile, because there are no third-party imports anywhere in this module.

```bash
python3 s1_engine_v0_3_2.py          --selftest    # expect: SELFTEST: 61/61 checks pass — ALL PASS
python3 s1_engine_v0_3_1.py          --selftest    # expect: SELFTEST: 54/54 checks pass — ALL PASS
python3 b0_evidence_substrate_v0_1_1.py --selftest # expect: SELFTEST: 18/18 checks pass — ALL PASS
python3 lineage_pack_v0_2_0.py       --selftest    # expect: SELFTEST: 30/30 checks pass — ALL PASS
python3 provenance_map.py            --selftest    # expect: SELFTEST: 20/20 checks pass — ALL PASS
```

All five run offline against built-in fixtures. None of them needs the corpus, which is not in this repository (see *Data*).

To run the engine on a real snapshot:

```bash
python3 s1_engine_v0_3_2.py \
    --snapshot <snapshot-dir> \
    --pages-csv <acquisition-ledger>/pages.csv \
    --vintage-date 2026-08-09 \
    --horizon-days 28 \
    --out <output-dir>
```

`--pages-csv` binds every record to the sha256 of the bytes the provider actually served; the run fails closed on any mismatch unless `--continue-on-mismatch` is passed, which quarantines the offending feed and says so in the output rather than dropping it silently.

---

## What is here

| File | What it does |
|---|---|
| `s1_engine_v0_3_2.py` | Reconstruction engine. Folds RPDE pages, resolves series→session inheritance recording a **lineage class per field**, expands recurrence rules into dated occurrences, and carries page-level provenance (`page_index`, `page_sha256`) on every surviving item. |
| `s1_engine_v0_3_1.py` | The predecessor. Retained deliberately — see *Two engine versions*. |
| `b0_evidence_substrate_v0_1_1.py` | Projects each lineage class to an evidence state and computes the per-dimension exposure figures the analysis chapter uses. Cross-validates its own record-by-record counts against the engine's independent aggregate counters, and **fails closed (exit 14) on any six-decimal disagreement**. |
| `reducer_v0_1_1.py` | The R1 evidence gate. Classifies a candidate as `supported_match`, `bounded_non_match` or `evidence_indeterminate`. Imported as a library; it has no CLI by design. |
| `lineage_pack_v0_2_0.py` | Generates an audit pack for one decision over one slate: every predicate's evidence state, the value relied on, the served page it came from, and receipts binding those pages to the engine run. |
| `lineage_pack_v0_1.py`, `lineage_pack_v0_1_1.py` | Superseded generators, retained so earlier packs remain regenerable. `lineage_pack_v0_1_1_to_v0_2_0.patch` is the diff between them. |
| `provenance_map.py` | The single shared lineage-class → provenance-locus table, imported by both this module and the downstream envelope assembly. |
| `lineage_pack_schema_v0_2.json` | JSON Schema the generated packs validate against before they are written. |
| `PATCH_NOTES_v0_3_2.md`, `IR15_REPRESENTATION_CLAUSE_20260913.md`, `C_BLOCK_03_PROVENANCE_WORDING_FOR_REVIEW_20260914.md` | Change records and the interface clauses agreed with the downstream consumers. |

### The evidence model in one table

The engine assigns each governed field one of six lineage classes; the substrate projects those to evidence states:

| Lineage class | Meaning | Evidence state |
|---|---|---|
| `ON_CHILD`, `CHILD_OVERRIDES`, `BOTH_EQUAL` | value published on the session itself | supported |
| `INHERITED` | value taken from the parent series | supported |
| `SOURCE_ABSENT` | neither session nor series published it | unknown |
| `UNRESOLVABLE_PARENT_UNAVAILABLE` | session named a series that was never collected | unknown |

The last two are both "missing" to a naive consumer and are kept distinct here, because only the second is a *collection* failure the project can act on.

---

## What the self-tests establish — and what they do not

They **do** establish: that inheritance resolution, schedule expansion and the evidence projection behave as specified on fixtures with hand-computed expected outputs; that daylight-saving transitions are handled to the stated PEP 495 rule at both the March and October 2026 boundaries; that `exceptDate` and `repeatCount` are honoured; that non-weekly recurrence frequencies are skipped with a typed reason rather than silently; that outputs are byte-deterministic across repeated runs; and that receipt verification fails closed.

They do **not** establish that the reconstruction rules match the OpenActive specification in every respect. They do not validate the corpus, and they say nothing about whether a provider's published claim is true in the world — provenance can certify that a value *was published*, never that it is correct. Five inherited properties remain unreconciled against the published specification; this is reported in the report rather than silently corrected.

---

## Verification record

Independently re-verified on **18 September 2026** on two machines — macOS/arm64 and a Linux cloud container running Python 3.11 — with hashes recomputed from the artefacts rather than carried forward from the build record:

| File | SHA-256 (first 16) | Self-test |
|---|---|---|
| `s1_engine_v0_3_1.py` | `31513ceb0a205341` | 54/54 PASS |
| `s1_engine_v0_3_2.py` | `26ce3030c38d40e8` | 61/61 PASS |
| `b0_evidence_substrate_v0_1_1.py` | `f3507213906efde2` | 18/18 PASS |
| `lineage_pack_v0_1.py` | `2ab75237cb5b48b9` | — |
| `lineage_pack_v0_2_0.py` | `420dd6a5594c592d` | 30/30 PASS |
| `reducer_v0_1_1.py` | `2d543be33220943a` | library |
| `provenance_map.py` | `077416acc57265f9` | 20/20 PASS |

Separately, the full corpus was reproduced from the stored source bytes on a clean virtual machine, **264 of 264 output files byte-identical**.

---

## Where the report's numbers come from

| Claim in the report | Produced by |
|---|---|
| 737,227 sessions against 654,956 series, 66 providers | `s1_engine` corpus run → `corpus_rollup.json` |
| Location coverage 3.44% → 97.94% | `s1_engine` `field_lineage` counters |
| 39.36% of records carry ≥1 unknown field | `b0_evidence_substrate` per-dimension exposures |
| Schedule expansion funnel; 8,034 occurrences | `s1_engine --horizon-days` S1b expansion |
| Per-decision evidence audit trail | `lineage_pack_v0_2_0` |

A marker checking any of these should start with the corresponding script's `--selftest`, then the corpus run.

---

## Two engine versions, and which to use

Both are here on purpose. **v0.3.2's new capability is opt-in:** its only additional flag, `--parent-descriptive`, is off by default, and with it off the five data outputs are byte-identical to v0.3.1. v0.3.2 is therefore a strict superset — safe to run for reproduction, and necessary only for the downstream consumer that needs parent descriptive values.

The practical consequence: if the report quotes a **54-check** self-test, that figure is v0.3.1's; v0.3.2 reports **61**. The counts differ because v0.3.2 adds tests, not because the reconstruction changed. Run either for the data; run v0.3.1 to reproduce the 54.

*Known cosmetic defect:* v0.3.2's opening docstring still carries the v0.3.1 header. Its `ENGINE_VERSION` constant is correct (`s1-engine-0.3.2-PROPOSED`) and is what the outputs record.

---

## Data

No data is in this repository, by team decision — `data/` is git-ignored. The corpus is roughly 0.7 GB of archived RPDE pages plus derived records, held outside version control with a receipt manifest binding each file to its sha256. Every script here runs its self-test without it.

---

## Design rule: imported, never re-implemented

Two tables in this project are load-bearing across three people's code: the R1 classifier and the lineage-class → provenance projection. Both live in exactly one file (`reducer_v0_1_1.py`, `provenance_map.py`) and are **imported** by every consumer, never copied. The lineage pack generator refuses to run without the reducer beside it, exiting with a typed code rather than falling back to a local copy.

This was a deliberate response to a real risk raised in review — three people building inconsistent implementations of the same semantics — and to a defect actually found: an earlier build carried the evidence table in three places, where a cross-check silently passed against a superseded copy. One table, one import, fail closed.

---

## Status and known limits

- Every artefact here is **PROPOSED**. Human acceptance fields are blank; nothing in this module closes a gate or ratifies a decision.
- **The reproduction harness (`repro_harness_v0_1.py`) is not in this module.** It exists in the build record but was not located in the repository or the delivery packs at time of writing. Any claim resting on it should be read as unsupported until it is produced.
- `lineage_pack_v0_2_0.py` cross-checks its evidence table against the substrate when importable. Shipping only `b0_evidence_substrate_v0_1_1.py` means that check reports the table as *taken as copied* rather than verified — the tables do agree, but the verification path is not exercised.
- Five inherited properties (name, activity, category, attendee instructions, `url`) are not yet reconciled against the published specification. The project's rule set is wider than the specification in the case of `url`; this is disclosed rather than corrected.
- Coverage figures describe the snapshot vintage they were computed on. They are not a claim about OpenActive in general.

---

## Authorship

Written by Michael Chellam Sebastian as part of the group project's reconstruction and evidence stream, under the team's ratified ownership allocation. The R1 contract and the provenance clause were agreed with the downstream consumers and are recorded in the interface documents listed above. AI assistance was used in development and is declared separately under the unit's AI-use rules.
