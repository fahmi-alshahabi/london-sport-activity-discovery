# staff-ia (C-06 §8.5)

The action-card workflow as a machine-checked state machine. Decision context:
[`docs/applications/staff-information-architecture.md`](../../docs/applications/staff-information-architecture.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Section 18 owner + partner route confirm it.
> Status `0.1.0-PROPOSED`.

## Files
- `action-card-state-machine.json` — canonical states, side states, transitions, gates, required card fields.
- `validate_action_cards.py` — enforces: no transition skips independent review or approval; sending
  requires an authorised role; a correction token may only create an `observed` candidate and can
  never mutate evidence or contact a publisher.

## Run
```bash
python packages/staff-ia/validate_action_cards.py     # exit 0 iff the gates hold
```
