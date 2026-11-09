# C-14 — Security & abuse package

**Owner (proposed):** Clarence (application-facing controls + evidence) · **Infra controls + sign-off:** Wesley (Section 16) + a security/assurance reviewer (not Clarence)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §12.8 (threat/abuse coverage), §15.4 (security tests). Machine model: `packages/security/threat-register.json` + `sanitize.py`; validator: `validate_security.py`.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. A
> security/assurance reviewer must sign the residuals; infrastructure controls (rate limits,
> security headers, IAM, SBOM, egress) are Wesley's.

## 1. Threat register (WP §12.8)

Fifteen threat categories, each with a control, an evidence reference and an honest status
(`mitigated` / `partial` / `planned`). `validate_security.py` fails if a required category is missing
or any threat lacks a control, evidence, owner or valid status.

| Threat | Status | Evidence |
|--------|--------|----------|
| disclosure (public/staff/research) | mitigated | INV-DISCLOSURE / non-interference + slice tests |
| authorization (object/field/role) | mitigated | role gate + per-role matrix |
| receipt forgery / version confusion | mitigated | C-09 checker |
| stale-cache / replay | mitigated | service_failure + replay digest |
| unsafe HTML / URLs | mitigated | autoescape + `safe_url()` + link scan |
| spreadsheet formula injection | mitigated | `csv_field()` + tests |
| arbitrary SQL/tool/URL/exec | mitigated | no ad-hoc SQL / no tool surface |
| prompt injection | partial | contract design; conversational layer not built |
| model/supply-chain drift | partial | version pinning; SBOM planned |
| malicious/mistaken staff action | partial | action-card gates + per-role caps |
| telemetry re-identification | partial | transient minimised telemetry (C-13); small-cell planned |
| deceptive interface / automation bias | partial | responsible-AI reqs; reliance metric (Fahmi) |
| denial / cost abuse | planned | rate limits (Wesley) |
| deletion / withdrawal failure | planned | deletion path (Wesley + governance) |
| incident concealment / unowned residual | partial | assurance-case orphan detection |

## 2. Executable controls (`sanitize.py`, tested)

- **`csv_field()`** neutralises spreadsheet formula injection (prefixes a quote to leading `= + - @`)
  — any staff export must route through it.
- **`safe_url()`** allows only absolute `http(s)` URLs, blocking `javascript:`/`data:` — provider
  links and any user-influenced URL pass through it (the shipped scenarios' provider links are scanned).
- **`escape_html()`** — defence in depth over template autoescaping.

`validate_security.py` also runs a **secret scan** across the repo (AKIA keys, private-key blocks,
`key = "long-value"`) — currently clean — and confirms every scenario provider link is http(s).

## 3. What's referenced vs. what's here

Most controls are *evidenced by tests already built* (C-09, disclosure/non-interference invariants,
role matrix, replay). This package adds the application-facing sanitisers and the consolidated register.
Infrastructure-level items (rate limits, CSRF/session/security headers, restricted model egress, SBOM/
dependency workflow, verified deletion) are **Wesley's** and are marked `planned`/`partial` honestly.

## 4. Status / next
PROPOSED. Needs the security/assurance reviewer sign-off, Wesley's infrastructure controls, and — when
the conversational layer is built — the adversarial injection battery (section-8.4) run to a measured
bypass rate. Registered as claim **CL-13** in the C-16 assurance case.
