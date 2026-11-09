# apps/staff-assurance (Phase E — C-06/C-07)

Role-gated **staff assurance workbench**: FastAPI SSR (ADR-0001, no-JS core) rendering the **staff
projection** of the same `DecisionEnvelope` the public app shows — authority-asymmetric, evidence-symmetric.
Docs: [`docs/applications/C-07-staff-assurance.md`](../../docs/applications/C-07-staff-assurance.md),
[`docs/applications/staff-information-architecture.md`](../../docs/applications/staff-information-architecture.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** The role gate is a demonstration stub; real
> IAM is Wesley's (Section 16, C-BLOCK-04). Non-author HCI review required. Status `0.1.0-PROPOSED`.

## Run
```bash
pip install fastapi jinja2 uvicorn --break-system-packages
uvicorn server.main:app --app-dir apps/staff-assurance --reload --reload-dir apps/staff-assurance
# staff routes require a role header, e.g.:
curl -H "x-staff-role: analyst" http://127.0.0.1:8000/replay?scenario=supported
python apps/staff-assurance/test_staff.py
```

## What "passing" means
`test_staff.py` exits 0 when: every staff route is 403 without a role and 200 with one; staff and
public agree on the shared decision; staff-only fields (`internal_score`, `model_version`, why-not
detail) appear in staff and never in public; public-state replay matches; non-interference holds;
the action-card workflow can't skip review/approval; and the static a11y subset is clean with no
research-identity leak.
