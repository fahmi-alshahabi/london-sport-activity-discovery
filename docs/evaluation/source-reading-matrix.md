# Source-reading matrix — Fahmi Alshahabi

**Owner:** Fahmi Alshahabi · Consolidated 18 August 2026 · Updated 19 August 2026 · v1.3
**Companion:** `docs/evaluation/F-20-reading-register.md` (which sources are needed and why).
**Rule (CA-01.A11):** no source is attested until it binds to a version of record with DOI,
personally read, with the reader's own claim and limit wording.
**Reviewer spot-check:** all rows pending; spot-check is a non-author task under Section 19.

> **v1.3 change:** row 9 added — Dror et al. 2018 attested (R-12), gating F-06 test selection.
> **v1.2 change:** rows 1 and 3 completed. Row 1's page ranges, claim and limits written;
> row 3 transcribed from the RCPS attestation worksheet, resolving the inconsistency where F-20
> listed R-03 as attested with no matrix row.
> **v1.1 change:** rows 4–8 consolidated from separate `matrix-row-*.md` files into this single
> matrix. Those files are superseded and should be deleted from `docs/evaluation/`.

---

## Row 1 — Westfall, Judd & Kenny (2014)

| field | entry |
|---|---|
| source | Westfall, J., Judd, C. M., & Kenny, D. A. (2014). Replacing puny studies with powerful ones. *Journal of Experimental Psychology: General*, 143(5), 2020–2045. DOI 10.1037/xge0000014. Version of record. |
| sections/pages read | Introduction and motivation (pp. 2020–2023); crossed random-effects framework and variance decomposition (pp. 2023–2032); power analysis and design implications (pp. 2032–2038). Technical derivations and simulation appendices skimmed. |
| claim supported | In crossed participant-by-item designs, statistical power depends on both the participant sample and the item sample because both contribute independent sources of variance. Increasing participants alone cannot remove the ceiling imposed by too few items, so valid power analysis must model both variance components rather than treating items as fixed. |
| assumptions/limits | Assumes crossed random-effects sampling with participants and items treated as random effects. Does not apply when items are fixed or confounded with condition, because item variance cannot be estimated separately. |
| decision affected | CA-01.A9 (crossed-design power ceiling); F-06 sizing outputs; `src/evaluation/power_ceiling.py` |
| date / reader | 2026-08-07 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 2 — Artstein & Poesio (2008)
| field | entry |
|---|---|
| source | Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. Computational Linguistics, 34(4), 555–596. DOI 10.1162/coli.07-034-R2. Version of record, peer-reviewed, open access. |
| sections/pages read | §§2.3–2.6 (558–568); §3.2 (573–574); §§4.1.2–4.1.3 (575–577) |
| claim supported | Raw percentage agreement isn't enough because some agreement happens by chance, especially when one category is very common. κ, π/Fleiss and α differ in how they model chance; α is useful with multiple coders and different levels of disagreement, including ordinal data. The value of α depends on how disagreement is weighted, and the paper does not support treating 0.67 or 0.8 as universal pass/fail thresholds. |
| assumptions/limits | α depends on the distance/weighting scheme chosen; different reasonable choices give different results, so the weighting must be justified and fixed before seeing results. Agreement doesn't automatically mean the coding is valid. |
| decision affected | F-05 codebook + adjudication design; agreement-reporting fields in the SAP |
| date / reader | 2026-08-10 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 3 — Bates, Angelopoulos, Lei, Malik & Jordan (2021)

| field | entry |
|---|---|
| source | Bates, S., Angelopoulos, A., Lei, L., Malik, J., & Jordan, M. I. (2021). Distribution-free, risk-controlling prediction sets. *Journal of the ACM*, 68(6), Article 43. DOI 10.1145/3478535. Version of record. |
| sections/pages read | Risk-controlling prediction sets and calibration procedure; validity theorem and finite-sample guarantee; implementation discussion and assumptions. Detailed proofs skimmed. |
| claim supported | RCPS provides a distribution-free finite-sample procedure that controls expected risk under valid calibration. The guarantee is one of statistical validity rather than an empirical performance claim. |
| assumptions/limits | Requires i.i.d. calibration data drawn from the same distribution as test data. Our clustered, design-weighted CAL-RISK partition — tasks nested within origins and publishers — does not automatically satisfy this assumption, so the guarantee cannot currently be claimed. |
| decision affected | CA-01.A4 validity conditions; F-08 risk-control route; CAL-RISK partition (F-03/F-04) |
| date / reader | 2026-08-14 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 4 — Lakens (2017)

| field | entry |
|---|---|
| source | Lakens, D. (2017). Equivalence tests: a practical primer for t-tests, correlations, and meta-analyses. Social Psychological and Personality Science, 8(4), 355–362. DOI 10.1177/1948550617697177. |
| sections/pages read | Introduction (pp. 355–356); Testing for Equivalence (p. 356); Power Analysis (p. 358); Setting Equivalence Bounds (pp. 359–360). Mathematical derivations for dependent t-tests, correlations and meta-analysis skimmed. |
| claim supported | TOST provides evidence for practical equivalence by testing whether an effect falls inside prespecified equivalence bounds, which a non-significant NHST result alone cannot establish. Bounds must be justified from theory, practical importance or cost–benefit reasoning and prespecified; where no such justification exists, the smallest effect detectable at the available sample size is a last-resort fallback. Narrower bounds substantially increase the required sample size. |
| assumptions/limits | Equivalence bounds must be justified and prespecified — Lakens warns against choosing bounds after seeing results or picking numbers that merely seem reasonable. The sample-size-based bound is explicitly a last resort, because it states what the design could detect rather than what would matter operationally; a margin justified from practice is not interchangeable with one justified from our budget. Tighter margins substantially increase required sample size. |
| decision affected | RATIFY margins in F-02 (Q non-inferiority, U superiority, R_decision ceiling); equivalence-testing conditions in the SAP; F-06 sizing simulation |
| date / reader | 2026-08-14 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 5 — Angelopoulos & Bates (2023), Appendix A (Learn then Test)

| field | entry |
|---|---|
| source | Angelopoulos, A. N., & Bates, S. (2023). Conformal prediction: a gentle introduction. *Foundations and Trends in Machine Learning*, 16(4), 494–591. DOI 10.1561/2200000101. Version of record, peer-reviewed. |
| sections/pages read | Appendix A, "Distribution-Free Control of General Risks", including A.1 (Instructions for Learn then Test), A.1.1 (p-values) and A.1.2 (familywise-error rate algorithms); plus §4.3 (conformal risk control) and §5.5 (selective classification) for contrast. **Read from arXiv:2107.07511v6, pp. 39–44; version-of-record pagination not verified** — page numbers in the FnT edition differ (51 pages in the preprint vs 494–591 in the VoR) and have not been checked against that copy. Detailed proofs and derivations skimmed. |
| claim supported | LTT reframes threshold selection as a multiple-hypothesis-testing problem: each candidate λ carries the null hypothesis that its risk exceeds the tolerance α, a p-value is computed from the calibration data via a concentration inequality (Hoeffding, or the stronger Hoeffding–Bentkus bound), and a familywise-error-rate-controlling procedure returns the set of λ that control the risk. The resulting guarantee is **high-probability** — risk at or below α with probability at least 1−δ over the calibration draw — as distinct from the **in-expectation** guarantee of conformal risk control (§4.3). LTT therefore extends risk control to risks that are not monotone in the threshold, which conformal risk control cannot handle. |
| assumptions/limits | The guarantee assumes i.i.d. calibration data drawn from the same distribution as test data, plus a valid (super-uniform) p-value and a genuine FWER-controlling combination step. Naively thresholding all p-values at δ does not control FWER; the paper uses Bonferroni, with **fixed-sequence testing** as the less conservative improvement for monotone and near-monotone risks (hypotheses ordered before seeing data, tested sequentially at level δ, stopping at the first acceptance). Appendix A offers no relaxation for clustered or design-weighted calibration data, so the conclusion recorded for Bates et al. (2021) stands unchanged: our CAL-RISK partition — tasks nested within origins and publishers, design-weighted — does not automatically satisfy the assumption, and the finite-sample guarantee is not claimable without further work. |
| decision affected | F-08 risk-control procedure; CA-01.A4 validity conditions; CAL-RISK partition design; H-P risk gate. **Why LTT rather than conformal risk control:** our conditional risk among emitted decisions is not monotone in the abstention threshold — directly analogous to the selective-classification case (§5.5), where selective accuracy is non-monotone in the confidence cutoff and therefore outside conformal risk control's scope. **Recommendation to the team:** pursue a grouped/clustered risk-control variant first; if no variant can be justified for our design, follow CA-01.A4 and report empirical risk–coverage curves with cluster-respecting uncertainty, removing guarantee language rather than claiming validity we have not earned. |
| date / reader | 2026-08-14 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

**Open citation issue (not part of this attestation):** the §20 entry "Angelopoulos 2025" does not resolve to this paper (2023) or to any 2025 Angelopoulos item fitting our use. Flagged as a CA-01.A11 ambiguous-citation case pending clarification from the §20 drafter.

---

## Row 6 — Buckley & Voorhees (2004)

| field | entry |
|---|---|
| source | Buckley, C., & Voorhees, E. M. (2004). Retrieval evaluation with incomplete information. In *Proceedings of the 27th Annual International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '04)*, Sheffield, UK, pp. 25–32. DOI 10.1145/1008992.1009000. |
| sections/pages read | Introduction and Sections 2–4 and Conclusion (pp. 25–31), read closely; the detailed bpref formula and some experimental tables skimmed. |
| claim supported | When unjudged documents are treated as non-relevant, systems lose credit for retrieving genuinely relevant documents that were never judged — penalising systems that did not contribute to the pool or that retrieve a different kind of relevant document. Degrading judgment sets progressively (90% down to 1% of the original) and comparing system rankings by Kendall's tau shows that MAP, P@10 and R-precision destabilise quickly under incompleteness, while bpref remains substantially more stable, because it counts only judged relevant against judged non-relevant documents. With complete judgments bpref agrees closely with MAP. |
| assumptions/limits | bpref's robustness relies on the judged relevant documents being a **representative sample** of the relevant set; it does not rescue evaluation where the pool systematically misses an entire class of relevant documents, which is precisely the risk for a genuinely novel system whose relevant documents never enter the pool. The paper also does not address a distinction that matters for us: it treats relevance as the only construct, whereas our design separates relevance from evidence-support. |
| decision affected | Pool construction and judgment rules (F-03/F-07); treatment of unjudged items; RQ2 comparability across arms. **Pooling decision:** every RQ2 arm (B0–B5 and the proposed system) contributes to the pool, since a non-contributing arm is systematically penalised; the pool is the union of arms' candidate sets at a frozen depth (proposed: top 10 per system, to be reconciled with the F-02 D-2 ranking depth); pool depth, judged-document counts, contributing systems and the fact of incompleteness are reported alongside every result. **Measurement decision (option c):** the gated-versus-ungated contrast is reported under **both** standard relevance (comparable with the IR literature) and evidence-conditioned relevance (a listing counts only if relevant *and* supportable), with the gap between the two reported as a finding in its own right. Rationale: a relevance-only measure penalises the evidence gate for correctly suppressing a relevant-but-unsupported listing — scoring correct behaviour as a miss — while an evidence-conditioned measure alone could be accused of redefining relevance to flatter the proposed system. Reporting both, and treating their difference as a quantity of interest, is honest in both directions; the gap is a direct measure of the phenomenon this project exists to characterise. |
| date / reader | 2026-08-15 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 7 — Vehtari, Gelman, Simpson, Carpenter & Bürkner (2021)

| field | entry |
|---|---|
| source | Vehtari, A., Gelman, A., Simpson, D., Carpenter, B., & Bürkner, P.-C. (2021). Rank-normalization, folding, and localization: an improved R̂ for assessing convergence of MCMC. *Bayesian Analysis*, 16(2), 667–718. DOI 10.1214/20-BA1221. Open access, peer-reviewed. |
| sections/pages read | §2, pp. 670–671 (failure modes of the classic R̂); early summary of recommendations, pp. 672–673; §§4.1–4.3, pp. 677–680 (rank-normalization, folding, localization); §5, pp. 688–690 (practical recommendations). Proofs and most simulation detail skimmed. |
| claim supported | R̂ compares between-chain to within-chain variation; values well above 1 indicate the chains are still exploring different regions and have not converged. The classic statistic misses two failure modes: chains with similar means but differing variances, and heavy-tailed distributions where the variance on which it depends is unstable or undefined (§2, pp. 670–671). Three modifications address this — **rank-normalization** replaces raw values with ranks, making the statistic robust to heavy tails; **folding** measures distances from the median, exposing between-chain variance differences; **localization** assesses convergence in specified regions of the distribution, particularly the tails, rather than only the whole posterior (§§4.1–4.3, pp. 677–680). The recommended thresholds are R̂ below 1.01 — the traditional 1.1 is too lenient and can conceal material convergence problems — together with both **bulk-ESS** and **tail-ESS** of at least 400 (§5, pp. 688–690). |
| assumptions/limits | These are convergence and sampling-efficiency diagnostics only. Passing them is necessary but not sufficient: they say nothing about whether the model is correctly specified, whether the priors are appropriate, or whether the estimand is the right one. A well-mixed sampler can converge cleanly on a wrong model. |
| decision affected | F-02 §6 diagnostic thresholds (R̂ ≤ 1.01; ESS ≥ 400) — this source is the origin of both numbers, which were previously carried without an attested basis. Also F-10 Bayesian implementation and convergence reporting. **Supports F-02 amendment A-01:** the paper's separation of bulk-ESS from tail-ESS is the basis for splitting our single ESS criterion, since several reported quantities — interval endpoints, the `R_decision` risk ceiling, and rare `L_evidence` events — are tail quantities that a bulk-only criterion would not protect. |
| date / reader | 2026-08-15 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 8 — Lundberg, Johnson & Stewart (2021)

| field | entry |
|---|---|
| source | Lundberg, I., Johnson, R., & Stewart, B. M. (2021). What is your estimand? Defining the target quantity connects statistical evidence to theory. *American Sociological Review*, 86(3), 532–565. DOI 10.1177/00031224211004187. |
| sections/pages read | Introduction (pp. 532–533); theoretical and empirical estimands (pp. 533–541); the three-step framework, Figure 1 and accompanying text (pp. 533–545); estimation (to p. 546). Later worked examples and the detailed estimation case study skimmed. |
| claim supported | Research that moves straight to a statistical model without first defining the target quantity ends up treating "the coefficient on X" as the research question, when it is a property of one particular model rather than a theoretical quantity. The remedy is an explicit chain: define the **theoretical estimand** (the quantity of interest, which may involve unobservables), link it to an **empirical estimand** defined over observable data with a specified unit-level quantity and target population, via stated identification assumptions, and only then choose an **estimation strategy**. The order is load-bearing: the model answers the question rather than defining it, and once the estimand is fixed, competing estimation methods can be compared on equal terms. |
| assumptions/limits | The framework disciplines how quantities are defined; it does not establish that a construct is valid, nor that the identification assumptions linking theoretical to empirical estimand hold. Stating an estimand clearly makes the gap between what is wanted and what is measured visible — it does not close it. |
| decision affected | F-02 estimand registry structure and definitions; estimand-conformance checks in the SAP; F-06 sizing (a quantity must be defined before it can be sized). **Audit finding:** applying the paper's test to F-02, most entries name a unit and denominator, but `U` ("useful evidence-supported decision coverage") remains partly defined by how it would be computed rather than by what it represents. The operational definition does exist — F-05 §2 defines usefulness as evidence-grounded service rather than user satisfaction (PU1–PU3, worked cases U1–U4) — but F-02 does not reference it, and the distinction between the theoretical and empirical versions of `U` is not recorded. Carried as F-02 amendment A-02. |
| date / reader | 2026-08-15 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Row 9 — Dror, Baumer, Shlomov & Reichart (2018)

| field | entry |
|---|---|
| source | Dror, R., Baumer, G., Shlomov, S., & Reichart, R. (2018). The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing. *Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, Melbourne, pp. 1383–1392. DOI 10.18653/v1/P18-1128. Version of record, ACL Anthology. |
| sections/pages read | pp. 1383–1385, motivation and the test-selection protocol; pp. 1385–1388, choosing between parametric and non-parametric tests for paired experimental designs, including the practical sample-size guidance discussed by the authors; pp. 1388–1391, repeated testing across datasets and conditions, with the paper's treatment of multiple comparisons; p. 1392, conclusions and practical guidance. |
| claim supported | The paper establishes a decision protocol for selecting statistical significance tests rather than recommending a single default procedure. The first decision is whether observations are paired; the second is whether the assumptions required by parametric tests are satisfied. When those assumptions are doubtful, the authors recommend non-parametric alternatives instead of relying on inappropriate parametric tests. For experiments that compare multiple systems, datasets or conditions, the paper warns that repeated hypothesis testing increases false-positive risk and that multiplicity must be declared and controlled rather than ignored. |
| assumptions/limits | The paper governs hypothesis-test selection and valid p-value interpretation; it does not justify practical significance, effect-size thresholds or study design. It also does not provide a complete replicability framework for multi-dataset inference, instead pointing readers toward the authors' separate 2017 replicability work for that setting. |
| decision affected | F-06 test-selection governance: the paired design-weighted benchmark must pre-declare an appropriate paired significance test, justify whether parametric assumptions hold, and declare multiplicity handling before any confirmatory sizing or analysis. This attestation supports the test-selection protocol only; any load-bearing replicability framework across multiple datasets must be attested separately (Dror, Baumer, Bogomolov & Reichart 2017, *TACL* 5:471–486). |
| date / reader | 2026-08-19 / Fahmi Alshahabi |
| reviewer spot-check | — pending — |

---

## Outstanding

- Reviewer spot-check pending on all nine rows — non-author task, blocked with RATIFY-19-04.
- Row 5: version-of-record pagination not verified; read from arXiv:2107.07511v6.
- Dror et al. 2017 (*TACL* 5:471–486, replicability analysis across multiple datasets) is required
  only if multi-dataset replicability becomes load-bearing. Not currently attested.