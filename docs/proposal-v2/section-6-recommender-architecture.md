# 6. Evidence-Gated Cold-Start Recommendation Architecture

*Retitled from "Actual cold-start recommender architecture" — the word "actual" reads as defensive in a formal proposal; the new title states the two properties that matter. Status: provisional machinery for supervisor and team ratification, consistent with the §4 status line. Stretch items below enter scope only by decision-log entry.*

---

## 6.1 Framing: what "cold start" honestly means here

The platform launches with no user accounts, no interaction logs and no click-through history; every session is a first session. Collaborative filtering and interaction-trained learning-to-rank are therefore not merely deprioritised — they are methodologically unavailable, and any design that quietly assumed them would fail the mechanised claim audit. The recommendation problem is: given (a) a frozen, certified candidate universe produced by Layers 1–3, (b) a typed intent carrying hard constraints, and (c) a Bayesian posterior over soft preferences elicited in dialogue (§7), return a ranked, calibrated, selectively withheld set of evidence-supported listings. This places the system in the knowledge-based and constraint-based recommendation tradition, in which item knowledge substitutes for interaction data (Felfernig & Burke, ICEC 2008), under the classic cold-start formulation of Schein et al. (SIGIR 2002).

The architecture operationalises the §3 evidence boundary as an asymmetry between two uncertainties that receive deliberately different treatment:

| Uncertainty | Reducible by this layer? | Treatment |
|---|---|---|
| **Preference uncertainty** — what does this user value? | Yes, through dialogue (§7) | Modelled as a posterior over an interpretable preference vector; integrated over in expected utility |
| **Catalogue uncertainty** — what is true of this listing? | No | Unknown or conflicting facts route candidates to the indeterminate pool or to why-not explanations; they are never imputed into scores |

Every design decision below is an enforcement mechanism for that asymmetry: neural components may order and verbalise authorised candidates; they cannot create eligibility, manufacture a publisher fact, or bypass abstention.

## 6.2 Inputs and candidate representation

Per frozen vintage, the layer consumes: the evidence-eligible listing set from S1b reconstruction, each listing carrying per-predicate four-valued evidence states with mechanism labels and receipt identifiers; normalised text fields (name, description, activity labels) for lexical indexing; pinned sentence-embedding vectors precomputed offline; a structured predicate index giving constant-time gate lookups; and geospatial and temporal occurrence indices. At London OpenActive scale (order 10⁴–10⁵ listings), exact dense scoring is computationally trivial, so no approximate-nearest-neighbour layer is used — removing a tuning surface and an approximation-error source in one decision. All indices are versioned artefacts of the vintage; a single command rebuilds them, and their hashes enter the reproduction manifest.

## 6.3 Stage R1 — symbolic evidence gate

Hard constraints from the typed intent map to atomic predicates evaluated **only** against certified evidence states, partitioning the universe three ways:

| Partition | Condition | Handling |
|---|---|---|
| Supported | Every hard predicate is T | Eligible for retrieval and ranking |
| Excluded | At least one unconflicted F | Removed; retained in the why-not ledger with its blocking predicate |
| Indeterminate | Any hard predicate is unknown-by-mechanism or in conflict | Held in a separate pool; never ranked as supported; exposure governed by the declared evidence policy (closed / permissive / explicit three-state), which is an experimental axis under RQ2, not a hidden default |

Because Layer 3 materialises evidence states offline per vintage, the gate is an indexed filter: correctness costs microseconds, not model calls. Three properties are under continuous test: **soundness** (no supported result carries a non-T hard predicate — the "zero unsupported hard-constraint exposure" acceptance row), **anti-monotonicity** (adding a hard constraint never enlarges the supported set), and **receipt resolvability** (the provenance of every surfaced state resolves). Conflict is reported as conflict, never as missingness, matching the Layer 3 semantics.

## 6.4 Stage R2 — hybrid recall

Within the supported pool only: BM25 over normalised text (Robertson & Zaragoza, Foundations and Trends in IR 2009) runs in parallel with exact cosine retrieval over the pinned sentence-embedding space (Reimers & Gurevych, EMNLP 2019). The two rankings are fused by reciprocal rank fusion (Cormack, Clarke & Büttcher, SIGIR 2009), chosen because it is parameter-light, training-free and robust to score-scale mismatch — properties that matter precisely because no training data exists at launch. Weighted-score fusion is retained as a development-split ablation only. Recall passes the top K = 100 candidates to reranking. Both retrievers are pinned versions recorded with hashes in the model register.

## 6.5 Stage R3 — precision reranking *(stretch-gated)*

A pinned, pretrained cross-encoder rescores query–listing pairs over the top-K set, following the peer-reviewed multi-stage neural ranking literature (Gao, Dai & Callan, ECIR 2021); a late-interaction alternative (ColBERT — Khattab & Zaharia, SIGIR 2020) is the designated substitute if pairwise scoring breaks the latency budget. Core scope uses the reranker zero-shot. Any fine-tuning uses development-split judgments exclusively, with the locked set untouched (leakage control per §5). If the latency gate in §6.10 fails on CPU, the pipeline degrades gracefully to RRF ordering from R2 rather than blocking — a configuration-flagged, logged fallback.

## 6.6 Stage R4 — Bayesian preference utility

Soft preferences form a low-dimensional, interpretable vector θ — distance tolerance, time-of-day fit, price sensitivity, indoor/outdoor, social format, intensity band — with a weakly informative population prior; the dialogue layer (§7) supplies posterior updates via its observability-aware question policy. Item utility u(item, θ) is a transparent additive function over **certified attributes only**: an attribute in an unknown or conflicted state contributes an explicit uncertainty term (or zero, per the declared policy), never an imputed value. The ranking score integrates expected utility over the θ-posterior — uncertainty about the *user* is marginalised; uncertainty about the *catalogue* is surfaced. Final ordering blends reranker relevance and expected utility through a single convex weight frozen on development data; component-only orderings remain available as RQ2 ablations. There is no neural utility model, no demographic feature, and no inferred sensitive attribute anywhere in scoring. The utility interface consumes whatever posterior exists at decision time — including the unupdated prior after zero questions — so this layer has no hard dependency on §7 being complete before integration testing begins.

## 6.7 Stage R5 — calibrated selective recommendation

The system may return fewer than k items, or abstain entirely, under two triggers. First, an empty supported pool: the response surfaces why-not blockers from the gate ledger together with minimal relaxation *suggestions* that the user must explicitly confirm — the system never silently relaxes a constraint. Second, confidence below a threshold τ_α, set on development data to respect the predeclared false-assurance ceiling α, in the selective-prediction framing of Geifman & El-Yaniv (NeurIPS 2017). Conformalised risk control (Angelopoulos et al., PMLR 2023 — already among the §10 foundations) is a labelled stretch upgrade offering distribution-free guarantees; the core mechanism is the frozen threshold. Every output, at every operating point, carries evidence badges, receipt identifiers, the vintage stamp and the acquisition-coverage qualifier. Risk–coverage and utility–coverage frontiers are first-class outputs consumed by §5 and §10–11; no single tuned operating point is reported alone.

## 6.8 What this architecture will not contain

No collaborative filtering or interaction-matrix method (no valid histories exist; the claim audit would reject it). No LLM-generated or imputed publisher facts anywhere in scoring. No demographic profiling or sensitive-attribute inference. No live capacity or bookability inference. No hidden constraint relaxation. No unpinned model. These exclusions are commitments, not omissions, and each is enforced by a named test or audit in §6.10.

## 6.9 Baselines and incumbent comparators (feeding RQ2)

| ID | System | Purpose |
|---|---|---|
| B0 | Structured filters + BM25 | The conventional-finder baseline |
| B1 | Bi-encoder retrieval only | Semantic-only component baseline |
| B2 | Hybrid RRF without the evidence gate | Evidence-agnostic ablation — offline evaluation only, never user-facing |
| B3 | Full stack minus preference utility | Isolates the Bayesian utility contribution |
| B4 | Full stack | The proposed system |

All systems run on the identical candidate universe, vintage and presentation harness, so the gate ablation isolates the assurance cost/benefit at matched ranking machinery. Incumbent behaviour (Get Active / imin-class search) is approximated from public documentation for contextual comparison and is gated by the §17 capability audit before any comparative claim is frozen.

## 6.10 Layer acceptance evidence

| Check | Mechanism |
|---|---|
| Gate soundness | Property and metamorphic tests (constraint-addition anti-monotonicity; policy-projection consistency); mutation testing over gate logic with survivor taxonomy |
| Zero-leakage audit | CI job resolves every receipt on a sampled output corpus; failure blocks merge |
| Reproducibility | Pinned model registry (name, version, SHA-256); vintage-stamped indices; one-command rebuild reproduces frozen dev-set top-K lists byte-identically |
| Latency | p95 end-to-end ≤ 2 s CPU-only at K = 100 on the public path; automatic, logged degradation to R2 ordering if breached |
| Ablation completeness | Every stage removable by configuration; the full RQ2 grid executes from one manifest |
| Determinism | Fixed seeds; declared tie-break (stable sort on listing identifier) |

## 6.11 Core scope versus labelled stretch

Core is buildable in the first three system-build weeks, requires zero fine-tuning and zero GPU inference, and is fully testable stand-alone. Nothing downstream — benchmark, report claims, applications — may depend on a stretch item; stretch items enter scope only through a decision-log entry citing the entry evidence.

| Tier | Content | Entry criterion | Fallback |
|---|---|---|---|
| **Core** | R1 gate with three-state policies; BM25; pinned bi-encoder exact retrieval; RRF; fixed-prior additive utility consuming §7 answers; fixed-threshold abstention; why-not passthrough; full §6.10 battery | — | — |
| Stretch S1 | Cross-encoder reranking (zero-shot, pinned) | Core latency green | RRF ordering |
| Stretch S2 | Conformal risk control for abstention | Development judgments available in volume | Frozen τ threshold |
| Stretch S3 | Development-only cross-encoder fine-tune | S1 landed and assessor throughput ahead of plan | Zero-shot reranker |
| Stretch S4 | Learned fusion weights | Development judgments available | RRF |

## 6.12 Evaluation hooks: the contract with §§10–11

For every query the layer logs, as versioned JSON: candidate-universe snapshot identifier; per-stage candidate sets and scores; the gate partition with mechanism labels; the θ-posterior summary at decision time; the abstention decision and governing threshold; and all receipt identifiers. The benchmark harness (§10) and the hierarchical models (§11) consume these artefacts directly, with no bespoke scraping, and every headline number remains auditable back to stage artefacts — which is also the cross-review surface for the evaluation stream.

## 6.13 Risks and mitigations specific to this layer

Embedding domain mismatch on terse sports-listing text (mitigate: hybrid lexical anchor; measure per-family recall on the development split). High empty-pool frequency under strict constraint sets (measure it; mitigate through explicit, user-confirmed relaxation suggestions driven by why-not blockers). Rank–evidence interaction confounds (mitigate: the RQ2 factorial ablations on an identical harness). Latency versus precision (the automatic degradation policy). Over-abstention eroding usefulness (report the full utility–coverage frontier; margin decisions live in the frozen statistical analysis plan, §§10–11).

## Section references (peer-reviewed; merge into §10 foundations at assembly)

Schein, Popescul, Ungar & Pennock, *Methods and metrics for cold-start recommendations*, SIGIR 2002. Felfernig & Burke, *Constraint-based recommender systems: technologies and research issues*, ICEC 2008. Robertson & Zaragoza, *The probabilistic relevance framework: BM25 and beyond*, Foundations and Trends in Information Retrieval, 2009. Reimers & Gurevych, *Sentence-BERT: sentence embeddings using Siamese BERT-networks*, EMNLP-IJCNLP 2019. Cormack, Clarke & Büttcher, *Reciprocal rank fusion outperforms Condorcet and individual rank learning methods*, SIGIR 2009. Khattab & Zaharia, *ColBERT: efficient and effective passage search via contextualized late interaction over BERT*, SIGIR 2020. Gao, Dai & Callan, *Rethink training of BERT rerankers in multi-stage retrieval pipeline*, ECIR 2021. Geifman & El-Yaniv, *Selective classification for deep neural networks*, NeurIPS 2017. Zadrozny & Elkan, *Transforming classifier scores into accurate multiclass probability estimates*, KDD 2002. (Preference-elicitation interface: Vendrov et al., AAAI 2020; Martin et al., IJCAI 2024 — already in §10.)
