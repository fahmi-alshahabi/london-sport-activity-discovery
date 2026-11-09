# public-ia (C-04)

Machine-readable public information architecture + a validator that keeps it aligned to the
C-BLOCK-05 contract. Human docs: [`docs/applications/public-information-architecture.md`](../../docs/applications/public-information-architecture.md)
and the actors dossier [`docs/applications/actors-and-jobs.md`](../../docs/applications/actors-and-jobs.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence corrects it in his own words and
> obtains a non-author HCI review (`RATIFY-14-05`, C-BLOCK-03). Status `0.1.0-PROPOSED`.

## Files
- `public-state-machine.json` — routes, screens + minimum obligations, transitions, coverage map, fallback guarantees.
- `validate_ia.py` — reads the C-BLOCK-05 schema enums and checks coverage, distinct terminal experiences, required routes + non-chat/non-map/no-JS fallbacks, and no-stale-after-failure.

## Run
```bash
cd packages/public-ia
python validate_ia.py     # prints the coverage map; exit 0 means the IA covers the whole contract
```
Because the enums are read from the contract, this fails automatically if the contract grows a new
state that the IA hasn't given a distinct screen — the drift guard between C-BLOCK-05 and the UI.
