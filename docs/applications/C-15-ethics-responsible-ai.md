# C-15 — Ethics, responsible-AI & maturity

**Owner (proposed):** Clarence **coordinates** the evidence · **Decides:** Bristol PGT ethics route + Section 15 authorities (`RATIFY-15-01/03/11`) — not Clarence (WP §2.4)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §12.2/§12.3/§12.6/§12.7/§12.9/§12.10; §13.5. Machine model: `packages/ethics/ethics-activity-matrix.json`; validator: `validate_ethics.py`.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Clarence
> prepares the ethics activity matrix and participant materials; the University route grants or
> refuses approval. **No human-effect claim is made without approval.**

## 1. Intended use (WP §12.2)

Evidence-bounded discovery of published listings; user-controlled refinement/inspection;
provider-controlled contact/link handoff; staff diagnosis of acquisition-to-interface mechanisms;
governed drafting of bounded actions; research evaluation within the approved route.

## 2. Prohibited use (WP §12.3)

No emergency/clinical/diagnosis/prescribing/safeguarding decision; no eligibility determination; no
autonomous booking/payment/referral/contact; no inference of sensitive characteristics; no persistent
behavioural profiling by default; no staff performance surveillance; no publisher enforcement/league
tables; no automatic acceptance of model or staff-assistant recommendations; no reuse of research or
operational data for a new purpose without review. The validator checks each category is present.

## 3. Ethics activity matrix (WP §12.6)

Each activity carries a default position, a gate, and a fallback; every **human-participant** activity
requires an ethics route (validator-enforced):

| Activity | Gate | Fallback | Ethics route |
|----------|------|----------|:---:|
| synthetic/unit/fixture testing | minimise logs | — | no |
| internal team walkthrough | not published as participant evidence | supervision only | no |
| expert accessibility inspection | obtain determination | technical inspection only | yes |
| public application study | favourable Bristol PGT route before collection | no usability/effect claim | yes |
| staff/practitioner study | approved route + consent | expert walkthrough only | yes |
| children/NHS/safeguarding context | separate explicit route | exclude if not authorised | yes |
| live public telemetry | no collection until purposes/notice/retention/approval (DPIA, C-13) | no collection | yes |

## 4. Responsible-AI interaction requirements (WP §12.7)

Identify as automated and bounded; set accurate expectations; confirm high-consequence constraints;
make uncertainty and abstention actionable; provide edit/challenge/correction/human routes; avoid
anthropomorphic authority and persuasion; **measure reliance, not merely satisfaction**; prohibit dark
patterns; expose why a question is asked and allow skip; never hide a deterministic option to
manufacture engagement; preserve human approval for staff/external actions.

## 5. Maturity states (WP §12.9) — non-compensatory

`research_demonstration` → `public_safe_demonstration` → `staff_shadow_mode` →
`controlled_partner_pilot`. Passing one gate never authorises the next; a favourable score elsewhere
cannot offset a failed ethics/privacy/threat/disclosure/supplier/resilience/interaction/assurance
gate. `public_safe_demonstration` is a maturity-state name, **not** an unqualified safety claim.
Current state: `research_demonstration`.

## 6. Incident & kill controls (WP §12.10)

Detector/alert; affected surfaces/claims; immediate safe-mode/kill switch; owner + decision authority;
evidence preservation; notification/escalation; rollback/restore; correction/replay scope; restart
criteria; post-incident learning. Clarence coordinates the user/staff-facing behaviour and evidence;
Wesley implements infrastructure controls; authorised roles approve response/restart.

## 7. No-study fallback (WP §13.5)

If ethics/recruitment/readiness fails, retain deterministic conformance, accessibility/AT,
semantic-replay / non-interference / security tests; **remove** public-usability,
practitioner-actionability, organisational-effectiveness and lived-equity claims. This is what keeps
the project deliverable and honest with no participant data at all.

## 8. Status / next
PROPOSED. Needs the PGT ethics route determination and the named Section 15 authorities; participant
materials and data plan drafted in parallel. Until approval, the no-study fallback is the operating
mode and no human-effect claim is made.
