# evaluation (C-17)

Frozen evaluation **condition manifests** (P0/P1/P2, W0/W1/W1-NA) + telemetry event schema, with a
validator that proves the C-BLOCK-06 shared-backend guarantee. Docs:
[`docs/applications/evaluation-conditions.md`](../../docs/applications/evaluation-conditions.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Fahmi owns estimands/analysis; Clarence supplies
> the frozen builds. Status `0.1.0-PROPOSED`.

## Files
- `condition-manifest.json` — the six conditions, capability licence, and frozen task→scenario bindings.
- `event-schema.json` — privacy-minimised telemetry event (§13.3); raw utterances/location impossible by construction.
- `validate_conditions.py` — capability relationships; shared-backend digest equality per family (C-BLOCK-06); confound detection; event-schema validation.

## Run
```bash
pip install -U jsonschema   # required for the event-schema check (needs Draft202012Validator)
python packages/evaluation/validate_conditions.py
```
> The event-schema check needs `jsonschema` ≥ 4.18. If it's missing or too old the validator now
> reports a clear `run: pip install -U jsonschema` line instead of stopping — install/upgrade it and
> re-run. (This is the only validator in the repo that needs jsonschema.)
Exit 0 means: capabilities are correct (P0<P1<P2, W1-NA = W1 − assistant); every task's decision is
identical across a family (no confound); a deliberately confounded binding is caught; and the event
schema validates a sample while rejecting a `raw_utterance` field.
