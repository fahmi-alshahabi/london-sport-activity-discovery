> **SUPERSEDED IN PART — read this first.** The eligibility rows in this file
> date from 2026-08-10 and do not reflect sign-off C-a of 2026-08-29, which
> recuses Clarence from usefulness on the ground that he authors the arms. The
> authoritative assignment record is `F-01-assessor-assignments.md`. This header
> was added 2026-09-13, after the omission caused a reader to act on the stale
> rows.
# RATIFY-19-06 — Assessor & Custodian Eligibility Matrix: feasibility check

**Prepared by:** Fahmi Alshahabi · 10 August 2026
**Purpose:** Discharge CA-01.A7 / F-BLOCK-07 by testing whether the four-member team can satisfy every independence constraint simultaneously, *before* task authorship begins.
**Status:** PROPOSED for the ratification meeting. Not a decision — the matrix must be resolved jointly across Sections 09/10/14/15/16/19 and recorded once.

**Inputs confirmed by owner (10 Aug):** benchmark tasks authored by Fahmi alone; masked assessors Clarence and Wesley, Fahmi arbitrating, Michael excluded as engine owner; Michael owns the evidence engine and verifier; Clarence performs the clean non-author reproduction of Wesley's pipeline.

---

## 1. The constraints being tested simultaneously

| # | Constraint | Source |
|---|---|---|
| C1 | Task authors do not judge their own tasks in locked annotation | §19 independence |
| C2 | Component owners do not judge their own system's outputs where ownership defeats blinding | §19 independence |
| C3 | The codebook owner is not sole adjudicator | CA-01.A7 |
| C4 | A custodian-controlled locked evaluator is assigned | §16 |
| C5 | A non-author clean-room reproducer is assigned | §16 |
| C6 | Every locked construct retains **≥2 eligible assessors plus an adjudication route** | CA-01.A7 |

## 2. Eligibility matrix

**Key:** ✅ eligible · ⚠️ eligible with a recorded caveat · ❌ recused (reason)

| Role / construct | Fahmi | Michael | Clarence | Wesley |
|---|---|---|---|---|
| **Usefulness judgment (U)** | ❌ C1 — sole task author; also codebook author | ❌ C2 — owns evidence engine/verifier feeding the response | ✅ | ✅ |
| **Relevance judgment (Q)** | ❌ C1 — sole task author | ❌ C2 | ✅ | ⚠️ owns retrieval/recommender pipeline in v2 ownership — see §3.2 |
| **Evidence-support verification (L_evidence)** | ❌ C1 | ❌ C2 — verifying his own engine's claims | ✅ | ✅ |
| **Adjudication / arbitration** | ⚠️ C3 — currently sole arbiter *and* codebook owner *and* task author | ❌ C2 | ❌ serves as assessor | ❌ serves as assessor |
| **Locked evaluator (custodian, C4)** | ⚠️ owns the analysis the lock protects | ✅ | ✅ | ✅ |
| **Clean-room reproducer (C5)** | ✅ (for Wesley's pipeline) | ✅ | ✅ — currently assigned | ❌ own pipeline |
| **Reproducer of *Fahmi's* headline tables** | ❌ own work | ✅ | ✅ | ✅ |

## 3. Findings

### 3.1 The structural conflict — arbitration (blocking)

With Clarence and Wesley as the two masked assessors and Michael recused as engine owner, **Fahmi is the only remaining arbiter** — while simultaneously being the sole task author and the codebook author. This directly strains C1 and C3: the person who wrote the tasks, wrote the rulebook, and resolves the disagreements is one person, and the disagreements being resolved are about his own instrument.

The 18 July team document already anticipated this, requiring the concentration to be *declared in limitations*. The question for ratification is whether declaration is sufficient, or whether the design must change. **Four members cannot satisfy C1, C2, C3 and C6 simultaneously without either an external assessor or an accepted, recorded caveat.**

### 3.2 Second-order conflict — Wesley on relevance (needs a decision)

Under the v2 ownership table Wesley owns retrieval/reranking and the recommender pipeline. Judging *relevance* of listings his own ranker returned is a C2 risk, even under blinding, because a component owner may recognise his system's output signature. Options: accept with a recorded caveat (blinding is genuine — condition labels are hidden), or restrict Wesley to usefulness and evidence-support and route relevance to Clarence plus an external assessor.

### 3.3 What is comfortably satisfied

C4 and C5 have multiple eligible people. Clarence's reproduction of Wesley's pipeline is clean. Reproduction of Fahmi's headline tables has three eligible candidates — Michael is the natural choice as the designated non-author with the statistical background.

## 4. Options for the meeting

| Option | Description | Cost | Effect on claims |
|---|---|---|---|
| **O1 — Declare and proceed** | Keep the current design; record the arbitration concentration in limitations, as the 18 July document already required | None | Weakest independence story; a reviewer may discount adjudicated results |
| **O2 — Split arbitration** | Michael arbitrates *non-evidence* constructs (usefulness, relevance) where his engine ownership doesn't bite; Fahmi arbitrates only evidence-support | None — uses existing people | Materially stronger; removes the sole-arbiter problem for two of three constructs |
| **O3 — External assessor** | Authorise one external assessor (another MSc student or a TA) for a sampled subset, providing an independence check on the arbiter | Recruitment, training, ethics check on data access | Strongest; also gives a third-coder signal, which A&P (2008) recommend for reducing accidental bias |
| **O4 — Narrow the claim** | Restrict adjudicated constructs to estimative reporting rather than confirmatory | None | Cheapest to run, most expensive to the results chapter |

**Owner's recommendation:** **O2 as the baseline**, with **O3 for a sampled subset if anyone's time allows.** O2 costs nothing, uses people already on the team, and removes the sharpest edge of the conflict. O3 additionally answers the two-assessor limitation already recorded in the codebook (§6.5), where A&P's own conclusion is that more coders reduce accidental bias.

## 5. Decision requested

1. Adopt O1, O2, O3 or O4 (or a combination) and record it once, referenced from Sections 09/10/14/15/16/19.
2. Rule on §3.2 — Wesley's eligibility for relevance judgment.
3. Confirm Michael as the non-author reproducer of Fahmi's headline tables.
4. If O3 is adopted, name the external assessor and confirm the data-access route before task authorship begins.

**Blocking status:** task authorship (F-03) should not begin until items 1 and 2 are decided, since assessor eligibility determines which tasks may be authored by whom.
