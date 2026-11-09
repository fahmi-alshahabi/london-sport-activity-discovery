# F-02 Amendment A-01 — Split ESS threshold into Bulk-ESS and Tail-ESS

**Proposed by:** Fahmi Alshahabi · 15 August 2026
**Target:** `docs/evaluation/estimand-registry.yaml` — the MCMC diagnostic thresholds currently recorded as part of the F-10 readiness conditions.
**Status:** PROPOSED. Takes effect on team ratification, per the standing rule that methodological choices enter the decision log before they enter code.

---

## Current text

> R-hat ≤ 1.01; ESS ≥ 400; zero unexplained divergences.

## Proposed text

> R-hat ≤ 1.01; **Bulk-ESS ≥ 400 and Tail-ESS ≥ 400**, reported separately per parameter and per reported derived quantity; zero unexplained divergences.

## Rationale

Effective sample size is not a single quantity. Bulk-ESS describes sampling efficiency in the body of the posterior and governs the reliability of posterior means and central summaries. Tail-ESS describes sampling efficiency in the tails and governs the reliability of extreme quantiles.

The distinction is load-bearing for this project specifically, because the quantities we report as headline numbers are disproportionately tail quantities:

| Reported quantity | Which ESS governs it |
|---|---|
| Posterior means for secondary outcome families | Bulk |
| **Interval endpoints on every reported estimate** | **Tail** |
| **The `R_decision` risk ceiling and risk–coverage frontier** | **Tail** |
| **Rare `L_evidence` events (low-probability by construction)** | **Tail** |
| Family and deprivation-stratified estimates | Both |

A model can satisfy a single undifferentiated ESS criterion while its tails remain badly under-sampled. Under the current wording that state would pass the readiness gate, and the estimates most exposed to it are precisely those the confirmatory decision and the published intervals rest on. Reporting one number also makes the failure invisible after the fact: a reader cannot tell from "ESS = 450" whether the tails were sampled adequately.

Separate reporting costs nothing at runtime — both quantities are produced by the same standard diagnostic tooling — and converts a silent failure mode into a visible one.

## Interaction with existing decisions

- Does not change the R-hat threshold (1.01) or the divergence condition.
- Applies wherever F-02 readiness conditions are referenced, including the H-E and H-G readiness gates.
- Consistent with the existing rule that a failed readiness gate permits estimative reporting only: a model meeting Bulk-ESS but failing Tail-ESS may not carry confirmatory or interval-based claims for the affected quantities.

## Source status

The bulk/tail ESS distinction and the ≥ 400 figure originate in Vehtari, Gelman, Simpson, Carpenter & Bürkner (2021), *Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC*, **Bayesian Analysis 16(2), 667–718, DOI 10.1214/20-BA1221**.

**Attestation status: NOT YET ATTESTED.** The reading register (F-20, R-07) carries this source as required-next, and the source-reading matrix has no row for it. Under CA-01.A11 and the K7 per-claim rule, this amendment is therefore **proposed on the strength of the argument above, not on an attested citation**, and the citation must not be treated as discharged until the matrix row exists. The design argument — that our headline quantities are tail quantities — stands on its own and does not depend on the citation being attested; the numeric threshold does.

---
*Change log: A-01 proposed 15 Aug 2026.*
