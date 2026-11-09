# ADR-0001 — Public vertical slice: stack & rendering architecture

**Status:** PROPOSED (deciders: Clarence + Wesley, per WP §16) · **Date:** 2026-08-08
**Relates to:** C-BLOCK-05 (contracts), C-BLOCK-11/14 (fallbacks/order), C-04 (IA), C-11 (wording), C-BLOCK-12 (maturity).

> **AI-ASSISTED SCAFFOLD.** Not authorship evidence; Clarence confirms the stack with Wesley and
> records the ratified decision (`RATIFY-14-04` layout; §16 physical layout agreed with Wesley).

## Context

The team prefers **React + TypeScript + FastAPI**, and the UK legal target is **WCAG 2.2 AA**
(Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018,
which GOV.UK now maps to WCAG 2.2 AA; plus Equality Act 2010). The work package imposes a
**non-negotiable no-JavaScript core** for essential content and actions (WP §7.1, §11.2) and
requires non-chat and non-map routes (C-BLOCK-11/14). A pure client-side React SPA cannot satisfy a
no-JS core.

## Decision

Build the public slice as **FastAPI server-side rendering (Jinja2) with React + TypeScript as
progressive enhancement**:

1. **FastAPI** renders every core route as complete, semantic HTML on the server, driven by the
   **public projection** of a terminal `DecisionEnvelope` (it imports the C-BLOCK-05 projector and
   the C-11 wording lexicon directly — one source of truth, disclosure-safe by construction).
2. FastAPI also exposes a **JSON `ApplicationEnvelope` API** — the same public projection — as the
   contract boundary for the enhancement layer and for evaluation instrumentation.
3. **React + TypeScript** enhances the already-working HTML (e.g. inline query editing, client-side
   compare) and is **never required** for the core. With JS off, every route still works.

## Rationale

- **No-JS core is guaranteed**, not hoped for — the server emits full pages and real form
  submissions/navigation. This is also the GDS-recommended, most robust path to WCAG 2.2 AA, and
  "use web technologies rather than native apps" (GOV.UK).
- **No logic duplication / no drift:** the projection, disclosure classes and evidence wording live
  once in Python and are reused verbatim; the TS client consumes the projected JSON, never
  re-deriving evidence. This directly serves C-BLOCK-09 (public/staff non-interference) and C-BLOCK-10
  (no unverified token) — the client cannot invent a fact the server did not project.
- **Evaluation integrity (C-BLOCK-06):** P0/P1/P2 all render server-side, so an interface effect is
  not confounded with a client's JS capability.

## Rejected alternatives

- **Pure React/Next SPA** — fails the no-JS core; would reimplement projection/wording in TS
  (drift + a second place to leak staff fields); harder AA story. Rejected.
- **Static HTML only** — not a realistic app; no JSON contract boundary for evaluation. Rejected as
  the primary, kept only as the no-JS baseline the SSR already provides.
- **Node + Express SSR** — viable, but the evidence projector/lexicon are Python; FastAPI reuses
  them with zero reimplementation. Rejected to avoid a second implementation of the contract.

## Consequences

- The TS client is optional by construction; a CI check asserts core routes are complete with JS
  disabled.
- All user-facing facts flow from the projected `DecisionEnvelope`; the client may reorder nothing
  and must preserve certified order (C-BLOCK-14).
- Maturity stays `research_demonstration` / local-authorised-staging (C-BLOCK-12); this is not a
  public deployment.

## Sources

- W3C, *What's New in WCAG 2.2* (Rec 5 Oct 2023): https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- W3C, *WCAG 2.2*: https://www.w3.org/TR/WCAG22/
- GOV.UK, *Understanding accessibility requirements for public sector bodies* (maps to WCAG 2.2 AA): https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps
