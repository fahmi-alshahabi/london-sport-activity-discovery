# apps/public-discovery (Phase D vertical slice)

Deterministic **public discovery** slice: FastAPI **server-side rendering** with **React+TypeScript
progressive enhancement** and a guaranteed **no-JavaScript core** (see
[`docs/applications/adr-0001-public-slice-stack.md`](../../docs/applications/adr-0001-public-slice-stack.md)
and the [WCAG 2.2 AA plan](../../docs/applications/accessibility-wcag22-plan.md)).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence corrects it in his own words and
> obtains a non-author HCI/accessibility review (C-BLOCK-03). Maturity: `research_demonstration`
> (C-BLOCK-12) — not a public deployment. Status `0.1.0-PROPOSED`.

## What it demonstrates
- Every typed outcome renders as a **distinct** screen and is never collapsed: `supported_match`,
  `bounded_non_match`, `evidence_indeterminate`, `scope_indeterminate`, `service_failure`.
- The UI shows only the **public projection** of the terminal `DecisionEnvelope` (it imports the
  C-BLOCK-05 projector) and words it from the **C-11 lexicon** — `unknown` renders as "not
  published", never "no"/"free".
- Core works with **JS disabled**; React/TS only adds an optional compare view + live status.

## Layout
- `server/` — FastAPI app (`main.py`), view builder (`render.py`), Jinja2 `templates/`, `static/styles.css`, `scenarios/*.json`.
- `client/` — React + TypeScript enhancement (`npm run typecheck` / `npm run build`); optional.
- `a11y_check.py` — static WCAG subset checker over rendered HTML.
- `test_slice.py` — route/a11y/disclosure/no-JS/render-lint verification.

## Run
```bash
pip install fastapi jinja2 httpx uvicorn --break-system-packages
# serve locally (authorised-staging / research demonstration only), from the repo root:
uvicorn server.main:app --app-dir apps/public-discovery --reload --reload-dir apps/public-discovery
# then open http://127.0.0.1:8000
# verify:
python apps/public-discovery/test_slice.py
# optional enhancement build:
cd apps/public-discovery/client && npm install && npm run typecheck && npm run build
```

## What "passing" means
`test_slice.py` exits 0 when: every core route is 200 and passes the static a11y subset; no
staff/research value leaks into the public HTML and no staff/research key appears in the public JSON;
no over-claim vocabulary; no inline critical script (no-JS core); each typed state shows its distinct
honest wording; and the C-11 render linter passes on the app's actual wording.
