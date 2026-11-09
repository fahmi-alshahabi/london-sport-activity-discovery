# security (C-14)

Threat/abuse register + executable application-facing sanitisers, with a validator. Doc:
[`docs/applications/C-14-security-abuse.md`](../../docs/applications/C-14-security-abuse.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** A security/assurance reviewer signs residuals;
> infrastructure controls are Wesley's (Section 16). Status `0.1.0-PROPOSED`.

## Files
- `threat-register.json` — the §12.8 categories, each with control + evidence + status.
- `sanitize.py` — `csv_field()` (spreadsheet formula injection), `safe_url()` (scheme allow-list), `escape_html()`.
- `validate_security.py` — register completeness/orphans; sanitiser self-tests; repo secret scan; provider-link scheme scan.

## Run
```bash
python packages/security/validate_security.py
```
Exit 0 means the register covers the required categories with no orphan, the sanitisers behave, no
obvious secret is committed, and every shipped provider link is an http(s) URL.
