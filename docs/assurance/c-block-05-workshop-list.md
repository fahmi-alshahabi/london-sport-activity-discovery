# C-BLOCK-05 workshop list — items that require the joint session

**Purpose:** the single list of things that cannot be closed by one person on one branch. Each row
names what must be decided, who must be in the room, and which claim or finding it unblocks. Nothing
here is a code task; each is a contract freeze, a design decision, or a ratification.

**Session:** 30 min, Clarence + Michael (+ Wesley for the reference-interpreter leg) — slot TBC.
**Baseline:** `clarence/c-block-05` @ current tip. **Status:** PROPOSED agenda.

---

## A. Section 09 contract freeze — receipt semantics and binding

| # | Item | Origin | Unblocks | Decision needed |
|---|------|--------|----------|-----------------|
| A1 | **Receipt semantics** — what a receipt attests to, and what it explicitly is *not* evidence of; existence + supports-this-claim + compatible-release | MS-2 (Michael) | CL-1, CL-3, CL-6 | Freeze as §09 contract text |
| A2 | **Receipt↔predicate binding** — a valid receipt must not be movable from one predicate to another | MS-4 | CL-6 | Define the binding; checker enforces |
| A3 | **Cryptographic binding** — candidate identity, witness content and claimed decision bound to the `DecisionEnvelope`: what is signed, over what canonical form, by whom, and what a verifier does when the binding fails | MS-5 | CL-1, CL-6 | Freeze; then implement + test |
| A4 | **Attribute↔claim binding ("verifier-approved")** — what makes a rendered candidate attribute verifier-approved. Scenarios show attributes are certified per-predicate evidence states while `claims[]` is a separate, sparser set (e.g. `sess-102` carries no claims), so a render filter cannot be written correctly until this is defined. Also: which artefact is normative if schema, manifest and contract text disagree | MS-10 (reclassified from Clarence-only) | CL-3 | Define in §09; then render filter + test |
| A5 | **`RATIFY-09-04`** — production / reference / checker ownership and independence; must explicitly answer CA-2 (may the claim-contract author also author the production interpreter?) | Michael's review; CA-2 | CL-6 authority | Write and record the decision text |
| A6 | **`RATIFY-09-05`** — claim vocabulary and rendering obligations | Michael's review | CL-3, CL-14 authority | Write and record |
| A7 | **SOURCE-CONFLICT-M01** — reference/checker ownership, recorded in the canonical decision log (D-033+), no invented register namespaces (CA-4) | Michael | independence record | Disposition in the same sitting |

**Michael's CA-2 position (for the record):** the claim-contract author may also author the production
interpreter **only if** the contract is jointly frozen and independently reviewed, the *reference*
interpreter has a different owner, and the checker remains independently authored and code-reviewed.

---

## B. Evaluation instruments — fields and units

| # | Item | Origin | Unblocks | Decision needed |
|---|------|--------|----------|-----------------|
| B1 | **Opening-query envelope digest** — a NEW field in `event-schema.json`, distinct from the terminal `envelope_digest` shipped at `21c788b` (M-6, closed). Fahmi's repair screen compares the envelope digest for the query *as first interpreted* against the terminal one; the terminal digest is only half the comparison | Michael/Fahmi, 30 Aug | F-BLOCK-09 repair screen | Name the field, add to schema, bump version, add a negative test |
| B2 | **P2 judgment unit — CLOSED.** Confirmed by Clarence and recorded as a manifest fact: a P2 item is the multi-turn **episode**; the assessor judges final-state usefulness given the conversation, not per-turn. Recorded as C-17 successor `condition-manifest.json` **v0.2.0-PROPOSED** (`judgment_units`), 2026-08-30. Consequences carried in the record: episodes read at ~5–8 min vs 2–3, so P2 dominates judging cost — cut template count rather than rush judgments; and **F-05 needs an episode-level usefulness anchor** — Fahmi to confirm §2 covers it or amend before the pilot | Michael, 30 Aug | Fahmi's sizing (unblocked); F-05 codebook | **Done** — no session time needed |
| B3 | **Designated arm** — fixed P2, pre-registered before any outcome inspection; plus pre-name **P1 vs P0** as the secondary contrast (estimative, reported regardless) because P2 carries repair exclusions and its effective n can shrink | Clarence proposed; Michael agreed | evaluation pre-registration | Team ratifies both lines |
| B4 | **Q (ranking construct)** — invariant and never collected, because ordering is validator-enforced identical across arms (`validate_conditions.py`, C-BLOCK-06). Registry edit: `Q -> invariant_not_collected` | Clarence's answer; Michael accepted pending byte-verification | Fahmi's registry; arbitration load ~0 | Confirm after Michael's byte-verification |
| B5 | **First-screen display depth — CLOSED (measured, not chosen).** Recorded in `condition-manifest.json` v0.2.0 (`first_screen_depth`), 2026-09-01: **the full certified slate, no cap, no pagination**, identical across arms. Method: `results.html` iterates the whole candidate list with no slice; `build_view` applies no truncation; rendered count equals slate length in every scenario; no next-page/show-more control exists. Consequence: judged depth = slate length N per task, not a fixed top-k, so judging cost varies with slate length once realistic slates are minted. A cap would be a **design change** (implement in the interface first, identical across P0/P1/P2) — not a reporting choice | Fahmi's item 6; Michael 1 Sep | assessor workload maths; ranking-depth RATIFY row | **Done** — number comes from the interface |

---

## C. Transport / IAM design (Wesley) — for the same or an adjacent session

| # | Item | Origin | Unblocks | Decision needed |
|---|------|--------|----------|-----------------|
| C1 | **Staleness bound** — maximum tolerated staleness, measured from which event, and behaviour at the bound. Nothing in the block expires today; compatibility is exact-match only | WY-4 | CL-1 | Design decision |
| C2 | **App-side version gate** — where it sits relative to `_c_version`; duplicates or defers to the checker's enforcement (MS-7) | WY-5 | CL-1 | Design decision |
| C3 | **WY-2a / WY-3a** — both are "where does the boundary check live" questions; Wesley asked to fold them into the same session. (WY-2a already fixed at the `load_public` boundary; WY-3a — a manifest pinning a stale `checker_version` is silently tolerated — still open) | Wesley re-review | CL-5, CL-1 | Confirm placement rule |
| C4 | **Real IAM against C-BLOCK-04** — identity source and trust boundary; how it composes with `_cap_for`'s default-deny so WY-1's fix is not quietly widened; fail-closed behaviour when IAM is unreachable. `RATIFY-15-06` stays withheld until real IAM replaces the stub | Wesley | CL-5 authority | Agree design shape, owner, target commit |

---

## D. Not in scope for this session (tracked elsewhere)

- **M-2** — the terminal referent produced *and verified* by the evidence engine. Two distinct surfaces
  now exist: the corpus-side referent (`s1_engine` v0.2 `MASTER_RECEIPT`) and the evaluation-side
  referent (per-query envelope-digest equality). Fahmi to write acceptance criteria naming **which
  receipt binds which claim**. Routed by Fahmi to Michael, not through Clarence.
- **CL-13 / `RATIFY-15-07`** — institutional security reviewer; WY-7 and the threat-register
  corrections (restated against `7cf65ca`) go to them.
- **Team ratifications** — `RATIFY-19-04`, Section 08 owner, `public_safe_demonstration` gate,
  Section 18 owner. See `team-ratification-agenda.md`.
