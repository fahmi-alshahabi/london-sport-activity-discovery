# Running the applications (public + staff)

Local **research demonstration** — runs on your own machine, no internet deployment. Two apps, two
ports. Run each in its own terminal, from the **repository root** (the folder containing `apps/`).

> On **Windows** use `python` (or `py`); on **macOS/Linux** use `python3`. Commands below show
> `python` — substitute `python3` on a Mac.

## 1. One-time setup

```
python -m pip install fastapi jinja2 uvicorn
```
(The apps' automated tests also use `httpx`, and the evaluation validator uses `jsonschema` — add
`python -m pip install httpx jsonschema` if you'll run those too. Not needed just to view the sites.)

## 2. Start the PUBLIC app — terminal 1

```
python -m uvicorn server.main:app --app-dir apps/public-discovery --port 8000
```
Wait for `Application startup complete.`, then open **http://127.0.0.1:8000**

Try these:
- `http://127.0.0.1:8000/` — search page (pick a "Demonstration outcome", press Search)
- `http://127.0.0.1:8000/discover?scenario=supported` — a supported match (price shows "not published")
- `…?scenario=no_match` — "No listed match" + coverage line
- `…?scenario=indeterminate` — "can't tell" + scope notice
- `…?scenario=service_failure` — safe failure (generic message, no stale result)
- `http://127.0.0.1:8000/chat?q=swimming in Croydon with step-free access` — conversational route
- `http://127.0.0.1:8000/compare?scenario=supported` — side-by-side, no "winner"

## 3. Start the STAFF app — terminal 2

```
python -m uvicorn server.main:app --app-dir apps/staff-assurance --port 8001
```
Open **http://127.0.0.1:8001** — you'll get **403 "Access restricted"**. That's correct: the staff app
is role-gated. Add a role via the dev `?role=` parameter:

- `http://127.0.0.1:8001/?role=analyst` — the workbench
- `http://127.0.0.1:8001/replay?scenario=supported&role=analyst` — public-state replay
- `http://127.0.0.1:8001/failure-chain?scenario=indeterminate&role=analyst`
- `http://127.0.0.1:8001/action-card?state=approved_for_route&role=analyst` — "send" **not** permitted
- `http://127.0.0.1:8001/action-card?state=approved_for_route&role=authoriser` — "send" **is** permitted
- `http://127.0.0.1:8001/equity-audit?scenario=indeterminate&role=analyst`

Roles: `analyst`, `assurance`, `authoriser`. (`?role=` is a dev convenience; in production the role
comes from a server-side `x-staff-role` header / real IAM — Wesley's piece.)

## 4. Stop
Press **Ctrl+C** in each terminal.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `No module named 'fastapi'` (or jinja2/uvicorn) | run the setup pip install above |
| `No module named 'render'` / `server` | use the exact `--app-dir apps/<app>` form, run from the repo root |
| `uvicorn: command not found` | use `python -m uvicorn …` (as shown) |
| `address already in use` | change `--port` (e.g. 8002 / 8003) |
| Staff app shows 403 | expected — add `?role=analyst` (or `assurance` / `authoriser`) |
| Want auto-reload while editing | add `--reload` to the command |

## Notes
- The public app has a **no-JavaScript core** — every page works with JS disabled (server-rendered).
  The optional React/TypeScript enhancement in `apps/public-discovery/client/` is not needed to view or
  demo the site.
- Both apps read fixed demonstration scenarios (`…/server/scenarios/`); there is no live data source,
  booking, or payment — this is a research demonstration only.
