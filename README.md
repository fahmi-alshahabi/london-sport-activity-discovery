# London Sport – Evidence-Bounded Activity Discovery

A research prototype, built with London Sport, that helps people in London find physical activity sessions using [OpenActive](https://www.openactive.io/) open data. The system only tells users what the published data can actually support. When the evidence is missing or unclear, it says so instead of guessing. For example, an unpublished price is shown as "not published", never as "free".

The project includes a public discovery app, a role-gated staff assurance workbench, and a reproducible evaluation framework for testing the system's claims.

## Components

### Public Discovery App – `apps/public-discovery`
- FastAPI server-side rendered app, with optional React + TypeScript progressive enhancement
- Fully usable without JavaScript, designed against WCAG 2.2 AA
- Guided search and conversational search that converge on the same confirmed query
- Five distinct outcomes, kept separate in the interface: supported match, bounded non-match, evidence indeterminate, scope indeterminate and service failure
- Only verified, lexicon-approved wording reaches the public interface

### Staff Assurance Workbench – `apps/staff-assurance`
- Role-gated staff view of the same decision the public sees, with extra diagnostic detail
- Public-state replay, equity audit, collection health and recommender assurance views
- Gated action-card workflow that cannot skip review or approval

### Shared packages – `packages/`
| Package | Purpose |
|---------|---------|
| `certificate-checker` | Validates decision certificates against a JSON schema |
| `security` | Output sanitisers (HTML, URL, CSV) and a threat register |
| `privacy` | Telemetry data dictionary and validation |
| `ethics` | Ethics activity matrix and validation |
| `public-ia` / `staff-ia` | Information-architecture state machines |
| `reconstruction` | Evidence substrate and data lineage packs |
| `evaluation` | Experimental condition manifest and event schema |

### Evaluation framework – `src/evaluation`, `tasks/`, `tests/`
- Estimand registry and paired-binary sample-size analysis
- 14 diagnostic task templates with a SHA-256 manifest and a seeded DEV / LOCKED split
- Structural linting to reduce paraphrase leakage between splits
- Annotation codebook, analysis plan and assessor structure

See [README_EVAL.md](README_EVAL.md) for full details of the evaluation stream.

## Tech stack

Python · FastAPI · Jinja2 · React · TypeScript · Vite · JSON Schema · pandas · NumPy · scikit-learn · pytest

## Getting started

### Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the public discovery app

```bash
python -m uvicorn server.main:app --app-dir apps/public-discovery --port 8000
```

Open [http://127.0.0.1:8000/discover?scenario=supported](http://127.0.0.1:8000/discover?scenario=supported). Other demo scenarios: `no_match`, `indeterminate` and `service_failure`.

### Run the staff assurance workbench

```bash
python -m uvicorn server.main:app --app-dir apps/staff-assurance --port 8001
```

Open [http://127.0.0.1:8001/?role=assurance](http://127.0.0.1:8001/?role=assurance).

See [README_RUN_APPS.md](README_RUN_APPS.md) for more run options.

### Run the tests

```bash
python apps/public-discovery/test_slice.py
python apps/staff-assurance/test_staff.py
python -m pytest tests
```

## Project structure

```
├── apps/
│   ├── public-discovery/     # Public-facing app (FastAPI + React/TS)
│   └── staff-assurance/      # Staff workbench
├── packages/                 # Shared contracts, validators and controls
├── src/evaluation/           # Sizing, power analysis and task linting
├── tasks/                    # Diagnostic task templates + SHA-256 manifest
├── tests/
└── docs/                     # Architecture decisions, assurance case, evaluation design
```

## Team

Group project by Michael Samuel, Clarence, Wesley and Fahmi Alshahabi.
Fahmi Alshahabi led evaluation and benchmarking.
