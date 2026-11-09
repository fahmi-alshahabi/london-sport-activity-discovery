# Row 5 — unacceptable-decision condition

**Drafted by:** Fahmi Alshahabi · **3 September 2026**
**Status:** DRAFT for team ratification (agenda 4.7). Never back-filled.
**Purpose:** defines what B0 is the rate *of*. Michael computes B0 on H1-DEV
under the F-04 partition, with or before 10 Sep.

## Condition

A terminal decision is **unacceptable** when the response emits
`supported_match` while at least one load-bearing evidence atom for that
match is in state `Um` (unknown-by-mechanism) or `Bm` (conflicting).

That is: the system asserted a match that its own evidence does not support.

**Load-bearing** means the atom is one the match depends on — remove it and the
match no longer follows. Atoms not relied on by the decision are out of scope
for this condition.

## Why this is mechanically decidable

Every result row carries a terminal `DecisionEnvelope` with the evidence state
and a digest, plus per-atom lineage with rule ids (Michael's output contract,
items 9–12). The condition reads those fields. No assessor judgment is required,
which is what makes a 10 Sep B0 possible at all.

## Declared narrowness

This condition covers **assertion errors only** — claiming support that is not
there. Two error classes are deliberately excluded:

- **Scope over-claim** — emitting `scope_complete` where a source was absent.
- **Missed evidence** — emitting `evidence_indeterminate` where the evidence
  would have supported a match.


Both exclusions are declared, not overlooked. Either can be added as an
additional clause if the team rules that way at 4.7; adding one after B0 is
computed would be back-filling and is prohibited.

## Not covered

Anything requiring a human reading of the response. Usefulness and
evidence-support are assessor constructs judged under F-05 and are not part of
this condition.
