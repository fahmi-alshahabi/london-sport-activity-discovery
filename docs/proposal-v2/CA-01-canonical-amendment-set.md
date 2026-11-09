# CA-01 — Canonical Amendment Set: F-BLOCK Propagation and Review Amendments

**Project:** Evidence-Bounded Conversational Activity Discovery and Recommendation over OpenActive for London Sport
**Prepared:** 7 August 2026
**Origin:** `FAHMI_ALSHAHABI_SPECIALISED_WORK_PACKAGE.md` (7 Aug 2026) and its review `review-fahmi-work-package-2026-08-07.md` (verdict: CONFIRMED WITH AMENDMENTS, FA-1 blocking)
**Formal status:** **PROPOSED — takes effect only as dated amendments applied to the canonical protocols after unanimous `RATIFY-19-04`.** This document is the change request and PR vehicle required by review amendment FA-1. It does not itself amend anything: a work package cannot amend a canonical protocol, and neither can this file.

> **Authorship notice:** this is an AI-assisted coordination scaffold prepared from the current project protocols. It is not evidence that Fahmi authored, read, accepted or completed the work. Fahmi must inspect it, correct it in his own words, complete his own primary-source reading, accept or amend every decision attributed to him, work through his own branch and obtain scoped non-author review.

**Why this exists (FA-1, verbatim problem):** F-BLOCK-01–07 are resolved inside a member's work package while the canonical corpus still carries the defective text — verified in review: `00_CANONICAL_DECISIONS` §5 still does not name K or U, and Protocol 13 §12.4 still reads "subject only to weighting and rounding." Until dated amendments land in 00/06/09/11/13, two definitions of H-P coexist and implementation would proceed against text the corpus contradicts — the mixed-release failure mode Section 16 forbids, applied to semantics. **Must clear before Phase C.**

---

## Part 1 — Amendments propagating F-BLOCK-01…07 into the canonical protocols

Each amendment states: target file(s) and section(s) → the defect → the frozen amendment text to be applied verbatim (drawn from the work package's dispositions, already confirmed by review §2–3) → application note.

### CA-01.A1 — Frozen outcome vocabulary (propagates F-BLOCK-01; resolves register EQ-12)
**Targets:** `00_CANONICAL_DECISIONS.md` §5; `06` symbol table; `09` and `13` wherever `K/U/R/H` appear; `11` decision-rule text.
**Defect:** Section 06's `C_m`/`U_m` collide with Sections 09/13's `K/U/R/H`; H-P's coverage quantity is never canonically named; `U` is overloaded with ranking utility.
**Amendment text to apply:**
> `K` = selection/emission coverage. `U` = useful evidence-supported decision coverage; the H-P coverage component. `Q` = ranking utility; `U` is never reused for ranking. `R_evidence` = conditional evidence false-assurance risk among emitted decisions. `R_decision` = conditional whole-decision risk among emitted decisions. `H_evidence` / `H_decision` = the corresponding unconditional harmful-emission probabilities, **computed directly** (see CA-01.A5). Every legacy symbol (`C_m`, `U_m`, and any prior use of `U` for ranking) is explicitly mapped to this vocabulary at its point of occurrence; no silent renaming.
**Application note:** add the mapping table to 00 §5 and a pointer in each affected protocol; date and initial each edit.

### CA-01.A2 — H-P loss identity (propagates F-BLOCK-02)
**Targets:** `09`, `11` (H-P definition sites); any Section 2 restatement of H-P.
**Defect:** H-P described with response factual risk in one place and whole-decision loss in Sections 9/11.
**Amendment text to apply:**
> H-P's risk gate is defined on `L_decision` (= `L_evidence` OR the independently frozen unacceptable-decision condition). `L_evidence` (unsupported catalogue assertion, unsupported mandatory implication, or unjustified bounded non-match) is reserved as H-G's loss. Both components are always reported separately. Every occurrence of H-P phrased on response factual risk is amended to `L_decision`.

### CA-01.A3 — Calibration partition independence (propagates F-BLOCK-03 — the review's "sharpest catch")
**Targets:** `09` (risk-control procedure); `10`/`11` (partition definitions and sizing).
**Defect:** model probability calibration may consume the same `CAL` partition reserved for LTT/RCPS risk certification — fitting and certifying on the same examples.
**Amendment text to apply:**
> Model probability calibration and risk certification never share examples. Either (a) model calibration is fitted entirely by DEV-only cross-validation and no `CAL-MODEL` partition exists, or (b) a prospective `CAL-MODEL` / `CAL-RISK` split is declared and sized **before any data access**, with `CAL-RISK` untouched by model or prompt fitting. The choice between (a) and (b) is prospective, recorded, and reflected in the joint sizing simulation.

### CA-01.A4 — Risk-guarantee validity conditions (propagates F-BLOCK-04)
**Targets:** `09` (LTT/RCPS procedure preconditions).
**Amendment text to apply:**
> The finite-sample risk guarantee is claimed only if the frozen observable loss and the declared exchangeability/grouping unit are supported by the chosen LTT/RCPS method under the actual clustered, weighted, grouped design. If any precondition fails, the output is the empirical risk–coverage curve with cluster-respecting uncertainty and **no guarantee language**.

### CA-01.A5 — Compute H directly (propagates F-BLOCK-05; resolves register EQ-11)
**Targets:** `13` §12.4; any occurrence of `H = K × R`.
**Defect:** `13` §12.4 currently reads "subject only to weighting and rounding."
**Amendment text to apply:**
> `H_evidence` and `H_decision` are computed directly. The identity `H = K × R` may be used only as a reconciliation check where task universe, inclusion rules and weights are identical across the factors; where they differ, the quantities are reported separately and the identity is not asserted.

### CA-01.A6 — Adversarial abstention mechanism (propagates F-BLOCK-06; resolves register SE-1)
**Targets:** `09` abstention taxonomy; `10.1`-equivalent vocabulary sites; robustness reporting in `12`.
**Amendment text to apply:**
> Abstention mechanisms are: evidence-required; model uncertainty; policy/safety; **adversarial containment / retrieval jamming**; collection/scope limitation; and service failure. The mechanisms are disjoint in reporting; induced refusal under attack is never scored as safe abstention.

### CA-01.A7 — Assessor/custodian eligibility is a joint, cross-section decision (propagates F-BLOCK-07; per FA-6 this **is** `RATIFY-19-06`)
**Targets:** jointly `09 / 10 / 14 / 15 / 16 / 19` — one resolution, referenced from each.
**Amendment text to apply:**
> Before any task authorship, the team resolves one versioned `task × condition × construct × assessor` eligibility matrix satisfying simultaneously: task authors do not judge their tasks in locked annotation; component owners do not judge their own outputs where ownership defeats blinding; the codebook owner is not sole adjudicator; Section 16's custodian-controlled locked evaluator and non-author clean-room reproducer are assigned; and every locked construct retains at least two eligible assessors plus an adjudication route. If four internal members cannot satisfy the assignment, the recorded fallback is an authorised external assessor or a pre-lock claim narrowing — never a silent relaxation.
**Application note:** this cannot be resolved inside any single protocol; it is a ratification-meeting agenda item with the matrix as its exit artefact.

---

## Part 2 — Amendments arising from the review itself

### CA-01.A8 — F-BLOCK-08: analysis primacy conflict (FA-2) — **TEAM DECISION REQUIRED**
**Conflict:** locked Section 2 and work package §12.1 fix the paired design-weighted finite-benchmark analysis as primary with Bayesian analysis secondary; Packet 11's `D23` proposed the hierarchical posterior as the decision instrument with the design-based test as concordance check. Both cannot be primary, and Fahmi owns both sides, so the resolution must not be his unilateral reading.
**Decision options:**
> **Option 1 (recommended, consistent with locked Section 2):** affirm design-based primacy; hierarchical Bayesian analysis estimates heterogeneity and model-dependent generalisation, standardised to design weights; it cannot overturn a failed primary decision. Packet 11 `D23` is superseded and marked as such.
> **Option 2:** adopt `D23` — requires re-opening locked Section 2, re-freezing H-P's decision rule, and a recorded rationale for why a model-dependent instrument should carry the confirmatory decision on a finite designed benchmark.
**Status:** carried as blocker until ratified; no estimator implementation against either reading before then.

### CA-01.A9 — Crossed-design power ceiling in the sizing simulation (FA-3)
**Target:** work package §9 and the canonical sizing text in `10`/`11`; applies with greatest force to the P/W application studies in `14`.
**Defect:** §9's inputs cover task/origin/paraphrase/publisher dependence but omit the crossed participants-by-stimuli result: where participants are crossed with tasks or stimuli, **power does not approach 1 as participants increase — it plateaus at a ceiling set by the item sample** (Westfall, Judd & Kenny, *Journal of Experimental Psychology: General*, 143(5), 2020–2045, 2014; publication status verified in this workstream). Without it, participants can be added to the application studies indefinitely and target power never reached.
**Amendment text to apply:**
> Sizing inputs additionally declare the participant × task/stimulus crossed structure and its variance components. Sizing outputs additionally report, per crossed design: the item-sample power ceiling and a maximum-attainable-power surface over (participants × items). A confirmatory claim whose target power exceeds the attainable ceiling under the feasible item budget is demoted to estimative **before** freeze.

### CA-01.A10 — Oral-defence outcomes must be recorded (FA-4)
**Target:** `19` (contribution assurance) — augmenting work package §21.
**Amendment text to apply:**
> For each of the ten §21 explanation topics, a dated result — `defended` / `partial` / `not-yet` — is recorded against the topic, examined by the member's two named cross-reviewers, with a scheduled re-test for any result short of `defended`. An unrecorded defence is unevidenced.
**Template row:** `| topic # | date | examiners | result | evidence link | re-test date |`

### CA-01.A11 — Reading-list binding to the foundation matrix (FA-5)
**Target:** work package §20 and the canonical foundation matrix.
**Amendment text to apply:**
> Every §20 entry binds to a foundation-matrix row carrying version-of-record and DOI before K7 attestation, which is per-claim and cannot attach to a bare surname. Ambiguous surnames are disambiguated at binding time — e.g. "Gelman" resolves explicitly to the 2006 variance-prior paper, the 2008 separation-prior paper, or the workflow line, per claim.

---

## Part 3 — Application instructions

1. This file is committed on a branch and PR'd for team visibility; it is the **change request**, not the change.
2. On `RATIFY-19-04` plus per-item approval, each amendment is applied **inside the target canonical file** as a dated, initialled edit; this file then records the application date and commit hash per item and closes.
3. **Repository condition (raised, not resolved, here):** the canonical bundle's authoritative paths currently include locations outside the shared repository (`exceptional-section-bundle-2026-08-04/…` and a member's local `docs/` path). The team's own governance rule — a protocol that exists only outside the repository does not exist — requires the canonical bundle to live in the private repo before these amendments can be applied to it. Proposed disposition: commit the bundle to `docs/canonical/` as part of the same ratification.
4. Nothing in Fahmi's stream that depends on the amended definitions (estimators, thresholds, task authorship) is implemented until the corresponding amendment has landed. Interim work is limited to: estimand-registry drafting against the CA-01 vocabulary marked provisional, schema/linter scaffolding, and reading/attestation.

**Ratification-meeting agenda items generated by this set:** `RATIFY-19-04` (unanimous ownership); CA-01.A8 primacy decision; CA-01.A7/`RATIFY-19-06` eligibility-matrix solve (with external-assessor fallback authorised or claim narrowed); repository condition in Part 3.3; ethics-route confirmation (Phase A exit condition).
