# C-08 — Conversational UX integration

**Owner (proposed):** Clarence (conversational UX) · **Evidence semantics / verifier:** Michael (Section 09) · **Section 08 accountable owner:** unresolved (C-BLOCK-01)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Basis: WP §9; enforces C-BLOCK-10. App: `apps/public-discovery` (`/chat`); parser: `server/intent.py`; tests: `test_conversation.py`.

> **Authorship notice.** AI-assisted scaffold; not evidence Clarence authored/accepted it. Clarence's
> defensible title is conversational-UX & application-integration owner — **not** "chatbot owner"
> until a dated Section 08 decision (C-BLOCK-01, CA-4).

## 1. Governing contract (WP §9.1)

> The model may interpret and communicate; certified evidence and deterministic decision modules
> determine what it may assert.

The conversational layer is **not a second truth system**. This slice implements it **deterministically**
(a closed-vocabulary intent parser + template rendering), so the discipline is demonstrable without a
model; an LLM parser/verbaliser can later replace the parse and surface-form steps **behind the same
typed-intent + evidence contract** (constrained decoding; section-8 stretch T2).

## 2. Pipeline (WP §9.2) and the distinct states (WP §9.3)

`/chat` runs: interpret → typed intent → (if unclear) **parse clarification** → (if a high-consequence
constraint) **explicit confirmation** → resolve to the upstream **DecisionEnvelope** → render only
verified claims → safe fallback. Each visible state maps to an `action_kind`: parse ambiguity
(`parse_clarification`), preference/evidence questions (`preference_/evidence_clarification`), the
result (`discovery_decision`), and failure (`service_failure`) — never merged.

## 3. Properties proven (executable — `test_conversation.py`, all passing)

- **Convergence:** a chat query resolves to the **same certified slate and order** as guided search
  (compatible terminal semantics) — the same `DecisionEnvelope`, not a parallel answer.
- **No fabrication:** an unclear query routes to **parse clarification** and shows no result.
- **High-consequence confirmation:** a step-free-access requirement is **confirmed before** any
  result is shown.
- **No unverified token (C-BLOCK-10):** the chat surface renders only lexicon/verified-claim wording
  (C-11 render-lint clean) and leaks no staff/research value.
- **Safe degradation (§9.5):** with the model off, the chat route shows a safe notice and the
  deterministic guided route still returns the same evidence — nothing is guessed.
- **Accessibility:** every conversational page passes the static a11y subset.

## 4. Conversation memory (WP §9.4)

Transient by default: no account for the public core; the query is echoed for editing but not
persisted; correction/issue tokens carry references only (no raw dialogue / exact location). Cross-
session memory is out of scope (privacy commitment, C-13).

## 5. Status / next
PROPOSED. Needs: the Section 08 accountable owner + component split (C-BLOCK-01/CA-4); the real LLM
parse/verbalise integrated behind the contract with the section-8.4 injection battery run to a
measured bypass rate; and a non-author review. Registered as claim **CL-14** in the C-16 assurance case.
