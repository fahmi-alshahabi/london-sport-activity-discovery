# privacy (C-13)

Machine-readable **telemetry dictionary** + four information planes, with a validator that keeps it
in lock-step with the C-17 event schema and enforces transient-by-default. Doc:
[`docs/applications/C-13-privacy-telemetry.md`](../../docs/applications/C-13-privacy-telemetry.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence coordinates; the controller/processor
> and lawful-basis determinations are governance decisions (`RATIFY-15-02/04`). Status `0.1.0-PROPOSED`.

## Files
- `telemetry-dictionary.json` — every event field (purpose, personal-data flag, retention, minimisation), planes, cross-plane join rule, forbidden concepts.
- `validate_privacy.py` — dictionary ↔ event-schema parity; transient-by-default; personal-data minimisation; forbidden concepts cannot be fields; planes well-formed.

## Run
```bash
python packages/privacy/validate_privacy.py
```
Exit 0 means the telemetry dictionary and the event schema describe exactly the same fields, every
field is documented and minimised, personal-data fields default to transient/session, and no raw
utterance / exact location / free text can be logged by construction.
