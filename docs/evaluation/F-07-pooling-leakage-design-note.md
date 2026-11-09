# F-07 — Pooling, Judgment and Leakage Design Note

**Owner:** Fahmi Alshahabi · 15 August 2026 · v0.1-draft
**Status:** DRAFT — design decisions PD-1 to PD-6 frozen by owner 15 August 2026; numeric parameters marked RATIFY remain open. Binding at the benchmark freeze gate.
**Grounding:** Buckley & Voorhees (2004), SIGIR '04, pp. 25–32, DOI 10.1145/1008992.1009000 — attested, source-reading matrix row 6.
**Depends on:** F-03 (benchmark construction), F-05 (codebook), F-02 (estimands). **Feeds:** F-06 sizing (judgment volume is an assessor-hours input), F-09 estimators.

---

## 1. The problem this note settles

Exhaustive judgment is impossible: every task crossed with every candidate listing would run to hundreds of thousands of judgments. The standard remedy is **pooling** — judge the union of each system's top-ranked results, and treat everything unjudged as non-relevant. The remedy carries a known bias: a system that did not contribute to the pool loses credit for relevant items nobody judged, so it is penalised for retrieving differently rather than worse (Buckley & Voorhees 2004, pp. 25–26).

Our design adds a complication the retrieval literature does not cover. Our evidence gate **removes candidates before ranking**. A gated arm therefore never surfaces a listing that is relevant but unsupported by evidence — which is correct behaviour, and which a relevance-only measure scores as a miss. Pooling and measurement must both account for this, or the comparison between gated and ungated arms is not a comparison of quality at all.

## 2. Frozen design decisions

| ID | Decision | Choice | Rationale (owner) |
|---|---|---|---|
| **PD-1** | Pool contribution | **Every RQ2 arm contributes** (B0–B5 and the proposed system) | A non-contributing arm is systematically penalised; contribution is the cheapest defence against pool bias |
| **PD-2** | Pool depth | **Top 10 per arm for naturalistic tasks; top 20 per arm for the diagnostic suite** | Depth costs assessor hours, so it is spent where bias would do most damage: the diagnostic suite contains planted defects, and a shallow pool there could hide exactly the failures the suite exists to detect |
| **PD-3** | Gated arms' contribution | **Pre-gate top-k as well as post-gate** | Judging only deployed results makes suppressed candidates vanish from the benchmark, and the gap between *relevant* and *relevant and supportable* becomes unmeasurable after the fact. That gap is a primary finding of this project, so the extra judgment is warranted |
| **PD-4** | Unjudged items | **Treated as non-relevant**, with pool depth, judged-item counts, contributing arms and the fact of incompleteness reported alongside every result | Standard practice, but only defensible when the incompleteness is declared rather than assumed away |
| **PD-5** | Measurement of the gated contrast | **Both standard relevance and evidence-conditioned relevance reported; the gap between them reported as a finding** | Relevance-only penalises the gate for correct suppression; evidence-conditioned-only could be accused of redefining relevance to flatter the system. Reporting both is honest in both directions, and their difference measures the phenomenon the project exists to characterise |
| **PD-6** | Leakage grouping key | **Task template** — all paraphrases and threshold variants of the same underlying question stay in one split; different origins may split | Prevents a paraphrase of a LOCKED task appearing in DEV, which is the realistic leakage route. Grouping by family would be needlessly coarse; grouping by origin would not stop paraphrase leakage |

## 3. Pool construction procedure

1. Freeze the arm set and their configurations (tagged commit).
2. Run every arm over the frozen task set at the frozen vintage.
3. For each task, form the judgment pool as the union of:
   - each arm's post-gate top-k (k per PD-2), **and**
   - each gated arm's pre-gate top-k.
4. De-duplicate by stable listing identity; record, per pooled item, which arms contributed it and at what rank. Provenance is retained because contribution patterns are themselves reportable.
5. Present pooled items to assessors in randomised order, with arm identity, rank and gate status masked (F-05 §1).
6. Freeze the pool before judgment begins. A post-freeze addition invalidates affected comparisons unless drawn from an untouched reserve.

## 4. The two relevance measures (PD-5)

| Measure | Definition | Role |
|---|---|---|
| **Standard relevance** | The F-05 §3 grade (0–3), judged against the task's stated constraints, ignoring evidence support | Comparable with the IR literature; secondary |
| **Evidence-conditioned relevance** | The same grade, counted only where the listing's required predicates are also SUPPORTED under F-05 §4 | The fair basis for gated-versus-ungated comparison |
| **The gap** | Difference between the two, per arm and overall | Reported as a finding: it quantifies how much apparently-relevant provision is not supportable from the catalogue |

Both measures are computed from the **same judgments** — relevance and evidence-support are judged separately per CB-D1, so no additional assessor pass is required to produce the pair. Where an incompleteness-robust measure is wanted for the ranking comparison, bpref is the candidate (Buckley & Voorhees 2004), subject to its own assumption that the judged relevant items are a representative sample.

## 5. Splits and leakage control

- **Splits:** DEV (development, tuning, codebook piloting), CAL (see the CAL-MODEL / CAL-RISK split, F-BLOCK-03 / CA-01.A3), LOCKED (one-shot confirmatory), ROBUST (robustness suites).
- **Grouping key (PD-6):** `task_template_id`. Every task carries it; all tasks sharing it land in the same split.
- **Assignment:** splits are assigned by grouped random assignment on `task_template_id`, seeded, before any task text is written to disk in final form; the assignment is part of the freeze commit.
- **Development items are permanently excluded** from locked evaluation.
- **Post-freeze leakage correction invalidates** the affected confirmatory run unless a genuinely untouched reserve exists.
- **Verification:** an automated check confirms no `task_template_id` appears in more than one split, and no LOCKED item's text is a near-duplicate of a DEV item. Failure blocks the freeze.

## 6. Reported alongside every result (PD-4)

Pool depth per suite; number of arms contributing; judged-item count and pooled-item count; proportion of returned items that were judged, per arm; whether pre-gate candidates were included; and an explicit statement that unjudged items are scored non-relevant and the judgments are therefore incomplete.

## 7. Open parameters (RATIFY)

| Parameter | Status |
|---|---|
| Judged ranking depth for `Q` | RATIFY — must reconcile with PD-2 and with F-02 discrepancy D-2; judged depth should not exceed the depth the interface displays |
| Total judgment volume and assessor-hours envelope | Output of F-06 sizing; PD-2 and PD-3 are inputs to it |
| Whether bpref joins the reported ranking measures | Pending the D-2 metric decision |

## 8. Known limitations

Pooling remains vulnerable to a systematically missing class of relevant items — bpref's robustness assumes the judged relevant set is representative, and does not rescue evaluation where the pool misses an entire category (Buckley & Voorhees 2004). Pre-gate contribution (PD-3) mitigates this for evidence-driven suppression specifically, but not for items no arm retrieves at all. This is declared as a coverage limitation of the benchmark, distinct from the acquisition-coverage qualifier that applies to the corpus.

---
*Change log: v0.1-draft 15 Aug 2026 — PD-1 to PD-6 frozen by owner; RATIFY parameters open.*
