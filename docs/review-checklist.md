# Review & analyse checklist — Clarence's stream

**How to use:** work top-down and tick as you go. Goal: understand, verify, and **make this yours**
(correct scaffolds into your own words) before reviewers and the viva. Live status tracker lives in
`docs/assurance/assurance-case.md`; this file is your reading/analysis order.

## Fastest hour (if short on time)
- [ ] Step 1 (run it) → Step 4 (the contract) → Step 6 (click the apps). Enough to defend the core thesis and spot anything to change.

## 1. Prove the ground truth
- [ ] `python docs/assurance/validate_assurance.py` → expect **14 checks green, 15 claims, all BLOCKED pending human sign-off**.
- [ ] Run the apps: `uvicorn server.main:app --app-dir apps/public-discovery` and `… --app-dir apps/staff-assurance`.

## 2. Re-read your authority docs (scope check)
- [ ] Your **work package** + its **review (CA-1…CA-7)**.
- [ ] Confirm the branch matches your §2 ownership boundary, and that **CA-1** (`L_reliance` referent) and **CA-3** (C-BLOCK-05 keystone) are reflected.

## 3. Open the map
- [ ] `docs/assurance/assurance-case.md` — every claim → control → test → reviewer/authority still needed. Use it to jump anywhere.

## 4. Scrutinise the keystone hardest (everything builds on it)
- [ ] `docs/applications/C-BLOCK-05.md` + `decision-envelope.schema.json` + `application-envelope.schema.json` + `disclosure-classes.json`.
- [ ] Are these the exact field names/enums to **freeze with Michael & Wesley**?
- [ ] Is **every field's disclosure class correct** (nothing staff-only in `PUBLIC_SAFE`)?
- [ ] Note anything to change before the contract workshop.

## 5. Walk the rest in dependency order
Order: C-09 → C-01 → C-11 → C-02/C-04 → C-06 → apps → C-17 → C-13/C-14/C-15 → C-08 → C-16.
For **each**: read the `docs/applications/C-*.md`, run its validator/test, and apply the three acid tests:
- [ ] (a) Anything **over-claimed** beyond the permitted wording?
- [ ] (b) Any **independence** boundary blurred (esp. the "independent" checker; no self-review)?
- [ ] (c) Does it say **PROPOSED / scaffold**, not "done"?

## 6. Experience the apps as a user
- [ ] Public: every typed state (supported / no-match / can't-answer / service-failure / scope-limited).
- [ ] `/chat`: a vague query (should **clarify**, not invent) and a step-free query (should **confirm** first).
- [ ] `/compare` (unknown/conflict preserved, no "winner").
- [ ] Staff: switch `?role=analyst` vs `?role=authoriser` and watch the **send** gate flip.

## 7. Make it yours (your individual mark)
- [ ] Rewrite each doc's prose **in your own words**.
- [ ] Record **K7 primary-source reading** actually done (Lee & See; Buçinca; WCAG 2.2; etc.) with version-of-record/DOI.

## 8. Your cross-reviews
- [ ] C-19 — review Michael's evidence stream (use work-package §17 questions).
- [ ] C-20 — review Fahmi's evaluation stream.

## 9. Act on the PR
- [ ] Respond to reviewer findings; make code changes.
- [ ] As each review/decision lands, set `reviewer.name`/`status` + `authority.holder`/`status` in `docs/assurance/assurance-case.json` and re-run `validate_assurance.py` → claim flips **BLOCKED → AUTHORISED**.
- [ ] When all 14 read AUTHORISED, the stream is genuinely complete.
