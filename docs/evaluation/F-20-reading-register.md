# F-20 — Reading Register (evaluation stream)

**Owner:** Fahmi Alshahabi · Created 14 August 2026 · Updated 19 August 2026 · v1.2
**Status:** ACTIVE. This register supersedes the §20 reading list of `FAHMI_ALSHAHABI_SPECIALISED_WORK_PACKAGE.md` for the evaluation stream.
**Why it exists:** the work package is no longer available to its owner and no copy could be obtained. Rather than reconstruct a list from memory — which would produce plausible but unverifiable citations, the failure mode CA-01.A11 exists to prevent — this register is derived from the opposite direction: **from the committed artifacts in this repository and the claims they actually make.** Every row therefore traces to a file and a claim that exists and can be checked, not to a remembered document.
**Rule (CA-01.A11):** no source is attested until it binds to a version of record with DOI, personally read, with the reader's own claim and limit wording. A surname alone is not a citation.
**Companion:** `docs/evaluation/source-reading-matrix.md` holds the completed attestations.

---

## 1. Attested (in the matrix)

| # | Source (version of record) | Depends on it | Status |
|---|---|---|---|
| R-01 | Westfall, Judd & Kenny (2014), *J. Exp. Psychol.: General* 143(5):2020–2045. DOI 10.1037/xge0000014 | CA-01.A9 (item-sample power ceiling; participant × item power surface); F-06 sizing outputs | ✅ row 1 |
| R-02 | Artstein & Poesio (2008), *Computational Linguistics* 34(4):555–596. DOI 10.1162/coli.07-034-R2 | F-05 §6 agreement commitments (weighted alpha, per-category reporting, no universal threshold, two-assessor limitation); CB-D3 linear weights | ✅ row 2 |
| R-03 | Bates, Angelopoulos, Lei, Malik & Jordan (2021), *J. ACM* 68(6). DOI 10.1145/3478535 | CA-01.A4 validity conditions; F-08 risk control; CAL-RISK partition (F-03/F-04) | ✅ row 3 |
| R-04 | Lakens (2017), *Social Psychological and Personality Science* 8(4):355–362. DOI 10.1177/1948550617697177 | RATIFY-values memo (margin justification hierarchy; last-resort fallback); SAP equivalence-testing conditions | ✅ row 4 |
| R-05 | Angelopoulos & Bates (2023), *Foundations and Trends in ML* 16(4):494–591. DOI 10.1561/2200000101 — Appendix A (Learn then Test) | F-08 procedure; why LTT rather than conformal risk control (non-monotone conditional risk) | ✅ row 5 |
| R-06 | Buckley & Voorhees (2004), *SIGIR '04*, pp. 25–32. DOI 10.1145/1008992.1009000 | F-07 pooling decisions PD-1 to PD-6; unjudged-means-non-relevant rule; dual standard/evidence-conditioned measurement | ✅ row 6 |
| R-07 | Vehtari, Gelman, Simpson, Carpenter & Bürkner (2021), *Bayesian Analysis* 16(2):667–718. DOI 10.1214/20-BA1221 | F-02 §6 diagnostics (R̂ ≤ 1.01; bulk-ESS and tail-ESS ≥ 400); F-02 amendment A-01 | ✅ row 7 |
| R-08 | Lundberg, Johnson & Stewart (2021), *American Sociological Review* 86(3):532–565. DOI 10.1177/00031224211004187 | F-02 registry structure; theoretical/empirical estimand separation; F-02 amendment A-02 | ✅ row 8 |
| R-12 | Dror, Baumer, Shlomov & Reichart (2018), *ACL 2018 (Vol. 1: Long Papers)* pp. 1383–1392. DOI 10.18653/v1/P18-1128 | F-06 test-selection governance: paired-first protocol, parametric assumption check, pre-declared multiplicity handling | ✅ row 9 |

## 2. Required next — each gates a claim already committed

| # | Source | Claim in the repo that requires it | Priority |
|---|---|---|---|
| R-13 | Geifman & El-Yaniv (2017), *Selective classification for deep neural networks*, NeurIPS. **Verify VoR + DOI.** | The abstention/coverage framing behind `U`, `Q` and the risk–coverage reporting in F-08. | **High — gates F-08 fallback** |
| R-14 | Gelman — **which paper is undecided.** Candidates: (2006) variance priors, *Bayesian Analysis* 1(3); (2008) weakly informative separation priors, *Ann. Appl. Stat.* 2(4). | F-10 prior choices. Cannot be attested as "Gelman" — CA-01.A11 requires a specific version of record. | Medium — gated on F-10 scope |
| R-15 | Dror, Baumer, Bogomolov & Reichart (2017), *Transactions of the ACL* 5:471–486 — replicability analysis across multiple datasets | Required **only if** multi-dataset replicability becomes load-bearing. R-12 covers test selection but explicitly defers the multi-dataset framework to this paper. | Conditional |

**Deferred, dated 18 August 2026 — not yet load-bearing.** No committed artifact currently makes a
claim that depends on these, so under §6 they do not gate a freeze: Bowman & Dahl; Raji et al.;
Cook, Gelman & Rubin; Modrák et al.; Gardner et al.; Ribeiro et al.; Selbst et al. Revisit if F-10
survives at full scope or if the fairness/robustness suites are executed.

## 3. Conditional — required only if the Bayesian secondary survives at full scope

Deferred pending the ratification decision on analysis primacy (CA-01.A8) and F-10's scope. If the hierarchical layer narrows to fewer outcome families or is reported estimatively, these are not needed.

| # | Source | Would support |
|---|---|---|
| R-09 | Gelman (2006), prior distributions for variance parameters, *Bayesian Analysis* 1(3) | Prior choices in F-10 |
| R-10 | Gabry, Simpson, Vehtari, Betancourt & Gelman (2019), *JRSS A* 182(2) | Bayesian workflow and predictive checks in F-10 |
| R-11 | Cook, Gelman & Rubin (2006), *JCGS* 15(3) | Simulation-based calibration of the F-10 implementation |

## 4. Unresolved inherited citations

| Entry | Problem | Disposition |
|---|---|---|
| "Angelopoulos 2025" | Does not resolve. The Gentle Introduction is 2023; Conformal Risk Control is ICLR 2024; Learn then Test appears to remain a preprint; *Theoretical foundations of conformal prediction* (arXiv:2411.11824, 2025) is a pre-publication book draft. None is both 2025 and peer-reviewed in a form our rules accept. | **CLOSED 18 August 2026 — formally declared unresolvable.** No candidate binds to a 2025 version of record meeting CA-01.A11. The entry is withdrawn rather than repaired; R-05 (Angelopoulos & Bates 2023, Appendix A) covers the LTT material the claim actually needed. Any future use of "Angelopoulos 2025" in project documents should be treated as a citation defect. |

## 5. Open governance issue

**Updated 18 August 2026: the work package has been recovered.** It exists outside this repository and remains outside it. Under the team's founding rule — a protocol that exists only outside the repository does not exist — any load-bearing content still needed from it must be re-committed to the repo by its custodian, or superseded by artifacts that are in the repo. This register supersedes its §20 list for the evaluation stream; the phase plan, viva/defence bank (§21) and ownership statement (§25) remain outstanding and should be re-issued into `docs/` or re-authored.

## 6. Working rule

A source enters section 2 only when a committed artifact makes a claim that depends on it. Sources are not read because they appear on a list; lists are derived from claims. Where no committed claim depends on a source, it does not gate a freeze.

---
*Change log: v1.2 — 19 Aug 2026: R-12 attested (Dror et al. 2018, matrix row 9); R-15 added as a conditional requirement. v1.0 — 14 Aug 2026, created from committed repo artifacts after loss of the work package §20 list. v1.1 — 18 Aug 2026: R-06/R-07/R-08 moved to attested; Angelopoulos 2025 closed as unresolvable; next-required set replaced with R-12/R-13/R-14; seven sources deferred as not-yet-load-bearing; work package recovery recorded.*
