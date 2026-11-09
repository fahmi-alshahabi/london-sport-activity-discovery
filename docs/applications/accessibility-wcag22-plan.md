# C-12 — WCAG 2.2 AA conformance plan (public slice)

**Owner (proposed):** Clarence · **Independent evaluation:** non-author HCI/accessibility reviewer (C-BLOCK-03, `RATIFY-14-02`; not Clarence)
**Status:** **PROPOSED — target, not a conformance claim.**
**Legal basis:** Public Sector Bodies (Websites and Mobile Applications) (No. 2) Accessibility Regulations 2018 → **WCAG 2.2 AA** (GOV.UK); Equality Act 2010.

> **Claim discipline (WP §11.1).** We claim **"evaluated toward WCAG 2.2 AA within the tested
> matrix"** — never "fully accessible" or "accessible to everyone". One examiner-found failure
> falsifies a blanket conformance claim; a scoped, dated, self-evaluated claim survives. Automated
> checks are ONE input; manual, assistive-technology and non-author evidence are required.

## 1. WCAG 2.2 — what's new since 2.1 (W3C, Rec 5 Oct 2023)

9 new success criteria; `4.1.1 Parsing` removed. New **AA** (and A) criteria and how the slice meets them:

| SC | Level | How the slice meets it |
|----|-------|------------------------|
| 2.4.11 Focus Not Obscured (Minimum) | AA | No sticky/overlay chrome hides the focused control; skip link; scroll-into-view on focus. |
| 2.5.7 Dragging Movements | AA | No drag anywhere; compare/reorder use buttons/links (single-pointer). |
| 2.5.8 Target Size (Minimum) | AA | Interactive targets ≥ 24×24 CSS px with spacing; enforced in CSS and checked. |
| 3.2.6 Consistent Help | A | A persistent "Help / get assistance" link in the same relative position on every page. |
| 3.3.7 Redundant Entry | A | The confirmed query is carried across steps (never re-typed); shown as editable. |
| 3.3.8 Accessible Authentication (Min) | AA | **No account for the public core** (WP §7.3) ⇒ no cognitive-function login test. N/A by design. |
| 2.4.13 Focus Appearance | AAA (targeted) | ≥ 2px focus indicator, ≥ 3:1 contrast — we aim for it though it's AAA. |

## 2. AA coverage mapped to the slice (2.0/2.1 carried into 2.2)

**Perceivable:** text alternatives for all non-text (icons decorative or labelled); no colour-only
meaning — every evidence state (`T/F/U/B`), grade and terminal decision has a **text label**
(C-11), not just colour/icon; contrast ≥ 4.5:1 (text) / 3:1 (large text, UI, focus); content
reflows at 320px / 400% zoom with no loss (relative units, single-column); maps always have an
**address/text equivalent** (GOV.UK maps guidance) and a list is authoritative.

**Operable:** full keyboard operation, visible `:focus-visible` indicator; logical focus order;
skip link; focus managed after navigation; no keyboard trap; no motion without
`prefers-reduced-motion`; targets meet 2.5.8.

**Understandable:** `lang="en"`; plain English with terms defined; consistent navigation and help
(3.2.6); errors identified in an **error summary** with links to fields, suggestions given (3.3.1/3.3.3);
`autocomplete` on inputs (1.3.5); redundant entry avoided (3.3.7).

**Robust:** valid semantic HTML5 landmarks (`header/nav/main/footer`), one `h1` per page, correct
heading order; name/role/value via native elements first, ARIA only where needed (4.1.2); status
messages via `aria-live`/`role="status"` (4.1.3).

## 3. Test matrix (WP §11.3) — to be executed, then dated

| Dimension | Minimum |
|-----------|---------|
| Browsers | Chromium, Firefox, WebKit/Safari-class |
| Viewports | mobile portrait, tablet, desktop; 200% zoom / 400% reflow |
| Keyboard | complete route, focus order, skip link, escape/recovery |
| Screen reader | ≥1 desktop (NVDA/VoiceOver) and ≥1 mobile route |
| Visual modes | forced-colours/high-contrast, dark/light, reduced motion |
| Network | slow/intermittent/offline states; **no-JS core** |
| Input | keyboard, touch, speech/voice control |
| Content states | supported, bounded-non-match, unknown, conflict, scope, failure |
| Alternatives | list for map; table/text for any chart; non-chat route |

## 4. What is automated here vs. what still must be manual

`apps/public-discovery/a11y_check.py` statically checks a **subset** on the rendered HTML: `lang`,
single `h1`, heading presence, form-control labels, `alt` on images, no positive `tabindex`,
buttons/links have accessible names, target-size CSS present, skip link present, consistent help
present. This is a guard, **not** conformance: contrast, screen-reader output, focus behaviour and
real-AT testing are manual and reviewed by a non-author (C-BLOCK-03).

## 5. Accessibility statement (WP §11 / GOV.UK)

A statement is mandatory under the regulations. It must state the scope tested, the standard
(WCAG 2.2 AA), known failures/exemptions (e.g. maps → address alternative), the date, and a contact
+ escalation route. Drafted separately as `accessibility-statement.md` once the matrix is executed
against a dated build — not before (no claim without evidence).

## Sources
- W3C *What's New in WCAG 2.2*: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- GOV.UK *Accessibility requirements for public sector bodies*: https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps
