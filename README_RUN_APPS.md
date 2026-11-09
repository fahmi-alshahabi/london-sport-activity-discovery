# Running the applications — public, staff, and the Oxford-integrated public app

0. Prerequisites

bash:
pip install fastapi jinja2 uvicorn --break-system-packages     # to RUN the apps

1. Public Discovery App

The Public Discovery App runs on port `8000`.

From the project root, run:

python -m uvicorn server.main:app --app-dir apps/public-discovery --port 8000

Once the server is running, open:

http://127.0.0.1:8000/

The application supports several demonstration scenarios. For example:

http://127.0.0.1:8000/discover?scenario=supported

Other available scenarios include `no_match`, `indeterminate`, and `service_failure`.


2. Staff Assurance App

The Staff Assurance App is a separate application from the Public Discovery App. Run it on **port 8001** so that it can run alongside the public app on port 8000.

From the project root, run:

python -m uvicorn server.main:app --app-dir apps/staff-assurance --port 8001

The workbench is role-gated. In this demonstration, a role is supplied using the `?role=` query parameter. In a real deployment, roles would be provided through an identity and access management (IAM) system.

Opening the staff app without a role returns **403 Access restricted**:

http://127.0.0.1:8001/

To open the assurance workbench:

http://127.0.0.1:8001/?role=assurance

The staff app also supports public-state replay:

http://127.0.0.1:8001/replay?scenario=supported&role=assurance

and the gated action-card workflow:

http://127.0.0.1:8001/action-card?state=drafted&role=assurance

The available roles are `analyst`, `assurance`, and `authoriser`. The `analyst` role can view, triage, and draft; `assurance` additionally supports review and approval; and `authoriser` can send.


3. Oxford-Integrated Public App (`d4_live`)

The Oxford-integrated version is **not a separate application**. It is the Public Discovery App from Section 1 with an additional `d4_live` scenario containing records assembled from real Oxford University OpenActive data.

start Public Discovery App:

python -m uvicorn server.main:app --app-dir apps/public-discovery --port 8000


Open the Oxford-integrated scenario at:

http://127.0.0.1:8000/discover?scenario=d4_live

The scenario displays ten real Oxford sessions, real OpenActive identifiers, and records from the `2026-08-27` corpus vintage.

The same scenario can also be replayed through the Staff Assurance App:

http://127.0.0.1:8001/replay?scenario=d4_live&role=assurance

Both applications must be running to use the public view and staff replay at the same time.
