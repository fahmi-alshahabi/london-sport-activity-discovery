# Ethics application — outline, materials checklist & data plan (to complete and submit)

**Owner:** Clarence prepares the pack · **Decides:** Bristol PGT ethics route via the supervisor (Dalila) — **not** self-approved (WP §2.4, §12.6)
**Status:** **PROPOSED — SCAFFOLD to complete.** Relates to C-15 (ethics matrix), C-13 (privacy/DPIA), C-17 (study design). Progress this **now, in parallel** so it is never on the critical path (WP §6).

> **Authorship notice.** This is a coordination scaffold — a structure and checklist. The words in the
> submitted application, the information sheet, the consent form and any reflective account are
> **yours**; complete them in your own words. Route the application through Dalila; the University
> committee grants or refuses.

## 0. First action — confirm the route

Confirm with Dalila **which PGT ethics route applies** before any practitioner feedback is collected
as research evidence. Until confirmed and approved, human feedback stays supervision-level and is
excluded from analysis (WP §12.6).

## 1. What actually needs ethics (from the C-15 activity matrix)

| Activity | Needs ethics? | If not approved (fallback) |
|----------|:---:|----------------------------|
| RQ3 simulation study (§7 policies) | **No** — simulated users | proceed; it is the confirmatory route regardless |
| Synthetic/unit/fixture testing | No | proceed |
| Expert accessibility inspection | **Yes** (may involve people/data) | report technical inspection only |
| Public application study (P0/P1/P2 usability) | **Yes** — human-participant research | no usability/effect claim; keep deterministic + a11y + replay evidence |
| Staff/practitioner study (W0/W1/W1-NA) | **Yes** | expert walkthrough only |
| Children / NHS-linked / safeguarding | **Yes** (elevated) | exclude unless separately authorised |

**Design consequence:** the confirmatory result (RQ3, simulation) needs **no approval**, so the
project cannot be blocked by the ethics timeline. Only the *human construct-validation* arms do.

## 2. Application sections to complete

1. **Summary & aims** — evidence-bounded activity discovery; explicitly **non-clinical, non-diagnostic**; the prototype is a research demonstration, not a service.
2. **Design & methods** — simulation-first (no participants) + the human arms you are seeking approval for; reference the frozen conditions (C-17).
3. **Participants** — who (e.g. assisted-pathway practitioners; adult public users), number, recruitment route, inclusion/**exclusion** (exclude children/NHS/safeguarding contexts here), no cold-contact of vulnerable groups.
4. **Consent** — information sheet + consent form (see §3 checklist); voluntary; right to withdraw without penalty.
5. **Data** — collected fields are the **minimised telemetry** only (C-13 dictionary): no raw utterances, no exact location, no free text; pseudonymous/ephemeral session id; storage location, **retention & deletion** schedule; note that hashes are **not** automatically anonymous.
6. **Risks & mitigations** — low-risk, non-clinical; distress unlikely; mitigations = plain-language boundary statements, ability to stop, no sensitive-attribute collection.
7. **Data protection / DPIA** — attach the DPIA screening (C-13 → full DPIA indicated before live collection); controller/processor determination pending governance.
8. **Dissemination** — group report + presentation; anonymised/aggregate only; no participant identification.

## 3. Participant-materials checklist (draft in your words)

- [ ] Participant information sheet (purpose, what they'll do, time, voluntary, withdrawal, data use, contact)
- [ ] Consent form (explicit, itemised: participation, data use, recordings if any)
- [ ] Recruitment message (neutral, no inducement)
- [ ] Debrief sheet (what the study was really testing; support contacts if relevant)
- [ ] Task script (from the frozen scenarios; identical across P0/P1/P2 or W0/W1/W1-NA)

## 4. Data management plan (link C-13)

- **Planes:** research data lives only in `approved_research`; never joined to source/staff stores without a registered purpose, minimum fields, logging and expiry.
- **Minimisation:** the event schema forbids raw utterance/location/free text by construction.
- **Retention/deletion:** default `transient`; approved-research data kept per the approved schedule with a verified deletion path; withdrawal honoured.
- **Security:** transport/IAM controls (Wesley); no personal data leaves to a hosted model unless the data path is verified first (`RATIFY-15-05`).

## 5. No-study fallback (if approval is delayed or refused) — WP §13.5

Retain: deterministic conformance testing, accessibility/AT inspection, semantic-replay /
non-interference / security tests, and the **simulation** RQ3 result. **Remove:** public-usability,
practitioner-actionability, organisational-effectiveness and lived-equity claims. The project stays
complete and honest with **no participant data at all**.

## 6. Track it

Draft now → review with Dalila → submit → record decision. Log the status against `RATIFY-15-03` and
flip the C-16 assurance-case authority for CL-12 to `done` only when approval is recorded — not before.
