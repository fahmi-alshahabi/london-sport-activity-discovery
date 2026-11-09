# application-contracts / c-block-05

Frozen (proposed) machine contracts for Clarence's applications stream: the versioned
`ApplicationEnvelope`, the immutable terminal `DecisionEnvelope`, the field-level disclosure
classes, and the **executable** release-blocking invariants. Decision record and rationale:
[`docs/applications/C-BLOCK-05.md`](../../../docs/applications/C-BLOCK-05.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Prepared from
> `CLARENCE_ZHEN_JIN_TAN_SPECIALISED_WORK_PACKAGE.md`. Clarence must inspect, correct in his own
> words, and obtain non-author review before any of this is treated as agreed. He cannot certify his
> own contracts (WP §2.6). Status: `0.1.0-PROPOSED`.

## Files
- `decision-envelope.schema.json` — terminal, immutable evidence decision (the CA-1 referent).
- `application-envelope.schema.json` — discriminated union on `action_kind`; embeds the DecisionEnvelope.
- `disclosure-classes.json` — field → release class; single source of truth for projection.
- `projection_and_invariants.py` — reference projector + release gates (stdlib only).
- `fixtures/valid/*` , `fixtures/adversarial/*` — golden + seeded-defect envelopes.

## Run
```bash
# fill correct digests into sealed fixtures (done once by the build step)
python projection_and_invariants.py --seal fixtures/valid/discovery_supported.json

# run the invariant battery (valid must pass; adversarial must be detected)
python projection_and_invariants.py

# optional: JSON Schema validation of every fixture
pip install jsonschema --break-system-packages
```

## What "passing" means
Valid fixtures satisfy every applicable invariant; each adversarial fixture is *caught* by exactly
the gate it targets (a gate that cannot fail is not evidence — WP §17.3). This is the Phase B exit
evidence for C-BLOCK-05: schemas validate, unsafe combinations fail, examples have stable hashes.
