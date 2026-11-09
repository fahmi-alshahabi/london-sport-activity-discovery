# D4 → envelope handoff interface, v0.1

**From:** Clarence (contract owner) · **To:** Wesley (D4) · **Date:** 14 September 2026
**Status:** INTERFACE SPECIFICATION, PROPOSED. Nothing here executes §09-1.

Answering Wesley's question of 14 Sep: *"do you want me to emit objects matching your
`$defs/candidate` and `$defs/predicate` directly, or a simpler intermediate you transform?"*

---

## The answer: emit `$defs/candidate` directly

Match the schema objects exactly. No intermediate.

The reason is not convenience. A transform on my side is a piece of code with no owner, no test and
no reviewer, sitting on the seam between two streams — and this week has produced four separate
findings about vocabulary drifting across exactly that kind of boundary. If you emit the contract
shape, there is nothing between your output and `candidates[]`, so there is nothing to drift.

Your ownership boundary as you drew it is right and I'm adopting it unchanged: **you supply ranked,
gated candidates with their per-field predicates; I assemble the envelope, the metadata blocks and
the digest, and run the certificate checker.** The digest is defined by my checker and must stay
there.

## Your predicates are already correct

`build_predicate` in `d4_envelope.py` emits the right shape: `grade` unconditional, `provenance`
present on `T`/`F` and omitted on `U`/`B`. Validated against the v0.2 schema — accepted.

## Your candidate wrapper needs three changes

Validated against `#/$defs/candidate`, your current candidate object returns three rejections:

```
'pool' is a required property
'rank' is a required property
Additional properties are not allowed ('decision' was unexpected)
```

`additionalProperties` is `false` on `$defs/candidate`. The permitted keys are exactly:

| key | type | required | notes |
|---|---|---|---|
| `candidate_id` | string | **yes** | the record `@id` — you already do this |
| `rank` | integer ≥ 1 | **yes** | certified display order; ties broken upstream |
| `pool` | enum | **yes** | see the mapping below |
| `attributes` | array of `$defs/predicate` | no | your `build_predicate` output |
| `provider_link` | string (uri) | no | sanitised at my render boundary |
| `internal_score` | number | no | `STAFF_AGGREGATE` — projects out of the public plane, safe to include |

**`decision` is not a key.** The gate verdict becomes `pool`, and the slate-level terminal decision
is mine to compute from the verdicts — don't send it per-candidate.

## The `pool` mapping — not a rename

Your gate vocabulary and my pool vocabulary are different sets. This is the one place you would
have got a wrong answer that still validated:

| reducer verdict | `pool` | schema meaning |
|---|---|---|
| `supported_match` | `supported` | eligible |
| `evidence_indeterminate` | `indeterminate` | held separately, **never interleaved as supported** |
| `bounded_non_match` | `excluded` | removed, **with a `why_not`** |

Note `bounded_non_match → excluded`. Not a synonym: `excluded` is a statement about what the
interface did with the candidate, and it carries an obligation.

## `excluded` requires a `why_not` entry

Each excluded candidate needs a `$defs/why_not_entry`:

```json
{ "predicate_id": "<the blocking field>",
  "blocking_state": "F" | "U" | "B",
  "relaxation_suggestion": "<optional, plain text>" }
```

`predicate_id` and `blocking_state` are required. Both are `STAFF_EVIDENCE`, so they project to the
staff workbench and not to the public page — which is the point: the public surface says a bounded
non-match occurred, the workbench says which predicate blocked it and what could be relaxed.

You have this already. `reduce_decision`'s `detail` gives you the blocking field and its state
directly — the value you kept when you stopped discarding it.

## What I need per query, in full

```
{ "candidates":   [ <$defs/candidate>, ... ],      # ranked, rank starting at 1
  "why_not":      [ <$defs/why_not_entry>, ... ],  # one per excluded candidate's blocker
  "coverage_qualifier": { "statement": "<honest capped-slice sentence>" } }
```

On the last one: the coverage statement must name the loaded count and the skipped providers. A
`bounded_non_match` over a capped slice means "none of the candidates retrieved from the loaded
slice matched" — never "no matches exist". That distinction is the whole claim boundary, and it is
the one sentence in this handoff I'd ask you to write rather than have me write for you, because
only your run knows the numbers.

## What I assemble, so you don't

`contract`, `schema_version`, `identity`, `versions`, `terminal_decision`, `recommendation_action`,
`scope_qualifier`, `predicates[]`, `claims[]`, and the digest. Then the certificate checker.

## Status and what this does not unblock

This interface is buildable and testable today against
`PROPOSED-decision-envelope.v0.2.schema.json`. It does not clear either gate:

- **§09-1** remains scheduled post-submission by the ratification record of 13 September. The frozen
  contract is unchanged at `0.1.0-PROPOSED`.
- **RATIFY-14-02** remains unfilled. `CL-2`, `CL-4` and `CL-10` read `name: null`. Until a
  non-author HCI/content reviewer is named and has approved the wording, `provenance` has no
  approved user-facing text, so a valid envelope carrying it still cannot render that field.

So the data-side handoff can be built and validated now; the render side cannot. Both facts belong
in the write-up as stated, not as a shortfall.
