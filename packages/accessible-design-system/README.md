# accessible-design-system

Clarence's accessible content + component foundation (WP §11, §16). First artefact: the
**evidence-language** rules (C-11) — the permitted wording for every typed evidence state, with an
executable linter. Decision doc: [`docs/applications/content-and-evidence-language.md`](../../docs/applications/content-and-evidence-language.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence must rewrite the user-facing wording
> in his own words and obtain a non-author HCI/content review (C-BLOCK-03). Status `0.1.0-PROPOSED`.

## content/
- `evidence-language.json` — approved/banned wording per state, grade, terminal decision, scope and
  recommendation action; global over-claim ban list; required rules.
- `render_lint.py` — completeness + render lint; reuses the C-BLOCK-05 projector to lint the real
  public surface.

## Run
```bash
cd packages/accessible-design-system/content
python render_lint.py     # completeness OK; compliant render clean; over-claim + collapse flagged
```
Exit 0 means: every enum value has approved wording, a compliant render passes, and both an
over-claiming render and the `unknown_rendered_as_no` fixture are correctly flagged.
