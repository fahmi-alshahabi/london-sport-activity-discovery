# C-11 — Content & evidence-language rules

**Owner (proposed):** Clarence · **Review:** non-author HCI/content reviewer (C-BLOCK-03; not Clarence)
**Status:** **PROPOSED — DRAFT SCAFFOLD.** Machine source: `packages/accessible-design-system/content/evidence-language.json`; linter: `render_lint.py`.
**Basis:** WP §4.2 (states), §7.3–7.4 (public prohibitions, evidence card), §9.3 (UX distinctions), §11.1/§11.4 (accessibility claim discipline, plain English), §19.3 (prohibited claims).

> **Authorship notice.** AI-assisted scaffold. Not evidence Clarence authored or accepted it. The
> user-facing wording especially must be **rewritten in his own words** and checked by a non-author
> reviewer before use. The design goal is **appropriate reliance, not persuasion** (WP §7.4).

## 1. The one rule

The interface may simplify but **may never strengthen a claim**. Missing evidence is never rendered
as a negative fact; uncertainty and abstention are shown and made actionable, never hidden.

## 2. Wording per typed state (summary — the JSON is authoritative)

| Field | Value | Say (approved) | Never say (banned) |
|---|---|---|---|
| evidence_state | `T` | "confirmed", "published as" | — |
| | `F` | "not offered (published)", "does not meet" | "unknown", "not published" |
| | `U` | "not published", "not stated", "we don't know from the data" | "no", "none", "free", "0", "inaccessible", "unavailable" |
| | `B` | "sources disagree", "conflicting information" | "yes", "no", "confirmed" |
| grade | `schedule_derived` | "derived from the published schedule" | "confirmed time", "guaranteed" |
| | `specification_default` | "assumed from the standard's default" | "published", "confirmed" |
| terminal | `supported_match` | "Matches your confirmed needs" | "best for you", "guaranteed suitable", "perfect match" |
| | `bounded_non_match` | "No listed match in what we searched" (+ coverage) | "nothing exists", "no activities available" |
| | `evidence_indeterminate` | "We can't tell from the available data" | "no results", "nothing found" |
| scope | `scope_indeterminate` | "some feeds or areas weren't fully checked" | "complete", "all activities" |
| recommendation | `model_abstained` | "We didn't rank these automatically" | "no recommendations", "no results" |
| | `browse_only` | "Browse results (not a recommendation)" | "recommended for you", "best options" |

Global over-claim terms banned everywhere (WP §19.3): *best for you, guaranteed, safe, fully
accessible, secure, private, compliant, trustworthy, first ever, production-ready, cheapest,
fastest*. Conditional terms: **"free"** only when a structured price is published as 0 (never when
price is `U`); **"accessible"** only as "accessibility information published" / "step-free access
stated" — never a blanket "accessible".

## 3. Worked examples (price is unknown, U)

- **Bad:** "Free swimming, best for you — fully accessible." → collapses `U`→free, over-claims
  suitability, blanket accessibility. The linter flags `R-U-not-negative`, `global_banned`,
  `conditional:accessible`.
- **Good:** "Matches your confirmed needs. Swimming: confirmed (published by the provider).
  Step-free access: confirmed. Price: not published."

## 4. The linter (executable, WP §17.3 "a test that cannot fail is not evidence")

`render_lint.py` runs two checks: **completeness** (every canonical enum value has approved
wording) and **render lint** (over-claim vocabulary, bare "accessible", `free`-while-`U`, definite
claims over `U`/`B` predicates, missing coverage on `bounded_non_match`, `model_abstained` worded as
"no match", hidden `scope_indeterminate`). It reuses the C-BLOCK-05 projector so it lints the real
**public** surface. Current status: completeness passes; a compliant render passes; an over-claiming
render and the `unknown_rendered_as_no` fixture are both flagged.

## 5. Accessibility language (WP §11.1, §11.4)

Claim exactly: **"WCAG 2.2 AA conformance in named tested routes/environments"** — never "fully
accessible" or "accessible to everyone". Plain English; define technical terms at first use; no
colour-only meaning in wording; every evidence state has a text equivalent independent of icon or
colour; error messages state what happened and the next safe action.

## 6. Status / next

PROPOSED. Needs: Clarence's own wording pass; alignment of the state vocabulary with the ratified
Section 09 terms (`RATIFY-09-02/05`); and a non-author HCI/content review (C-BLOCK-03). Once frozen,
this lexicon is the shared wording source for the public slice (Phase D) and the conversational
renderer (C-08, C-BLOCK-10).
