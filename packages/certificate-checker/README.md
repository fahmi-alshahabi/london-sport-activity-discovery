# certificate-checker (C-09)

A deliberately small, **independent** checker that validates a `Certificate` (the compact witness
emitted alongside a terminal `DecisionEnvelope`) without trusting the production interpreter (WP
§10). Decision record: [`docs/applications/C-09-certificate-checker.md`](../../docs/applications/C-09-certificate-checker.md).

> **AI-ASSISTED SCAFFOLD — not authorship evidence.** Clarence must inspect, correct in his own
> words, and obtain a **non-author** code review. He cannot certify his own checker (WP §2.6).
> Status: `0.1.0-PROPOSED`; outcome names bind to `RATIFY-09-04`.

## Files
- `certificate.schema.json` — the certificate/witness contract (Draft 2020-12).
- `certificate_checker.py` — the checker (stdlib only; no production imports; fails closed).
- `test_certificate_checker.py` — golden PASS + every WP §10.5 negative case + branch mutation testing.
- `discrepancy-register.md` — production/reference/checker disagreement log (empty until production emits certificates).

## Run
```bash
python test_certificate_checker.py        # golden PASS; each negative hits its exact code; 0 surviving mutants
python certificate_checker.py cert.json context.json   # one-off check -> outcome (exit 0 iff PASS)
```

## What "passing" means (WP §10.5)
Golden certificate returns `PASS`; each of the thirteen negative fixtures returns its exact
`FAIL_*` code; deleting any single decision branch changes at least one negative outcome (no
surviving mutants). Completion still requires the Section 09 contract confirmation and a non-author
review — see the decision doc.
