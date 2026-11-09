# ethics (C-15)

Machine-readable **ethics activity matrix** + intended/prohibited use registers + maturity states,
with a validator enforcing that every activity is gated and every human-participant activity requires
an ethics route. Doc: [`docs/applications/C-15-ethics-responsible-ai.md`](../../docs/applications/C-15-ethics-responsible-ai.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence prepares the pack; the Bristol PGT
> ethics route decides (`RATIFY-15-03`). Status `0.1.0-PROPOSED`.

## Files
- `ethics-activity-matrix.json` — activities (default/gate/fallback/ethics-route), intended & prohibited use, responsible-AI requirements, maturity states, incident controls, no-study fallback.
- `validate_ethics.py` — every activity gated with a fallback; human-participant ⇒ ethics route; prohibited-use completeness; canonical non-compensatory maturity states; responsible-AI + intended-use present.

## Run
```bash
python packages/ethics/validate_ethics.py
```
Exit 0 means no activity is un-gated, no human-participant activity escapes the ethics route, the
prohibited-use categories are all covered, and the maturity ladder is the canonical non-compensatory four.
