# 7. Bayesian Preference Modelling and Observability-Aware Clarification

*Status: provisional machinery for supervisor and team ratification, consistent with the §4 status line. This section specifies the preference model whose posterior Stage R4 (§6.6) consumes, the clarification-question policy, and the simulation-first evaluation design behind RQ3. Stretch items enter scope only by decision-log entry.*

---

## 7.1 Framing: two uncertainties, and a policy that must know the difference

Clarification exists to reduce exactly one uncertainty: what this user values. It cannot reduce the other: what is true of the catalogue. A question policy that ignores this distinction wastes the user's scarcest resource — their patience — on questions whose answers the evidence cannot act on. The central design commitment of this layer is therefore that question value is computed *against the certified candidate universe at the current vintage*, not against an idealised complete catalogue. Asking about an attribute the supported pool cannot discriminate on has, by construction, no decision value; the policy should know that before asking, not after.

This coupling of elicitation to item-side evidence states is the layer's candidate contribution, and it is stated as a candidate, not an assertion. Attribute-asking conversational recommendation exists (System Ask–User Respond, Zhang et al., CIKM 2018; Estimation–Action–Reflection, Lei et al., WSDM 2020), and Bayesian expected-value-of-information elicitation is mature (Chajewska, Koller & Parr, AAAI 2000; Boutilier, AAAI 2002; Viappiani & Boutilier, NeurIPS 2010; Vendrov et al., AAAI 2020; Martin et al., IJCAI 2024). Both traditions, however, assume the catalogue's attribute values are known. The candidate novelty is their composition under a four-valued evidence model — question selection that is explicitly aware of unknown-by-mechanism and conflicted item facts, with a measurable decomposition of wasted questions. Whether any incumbent or academic system already does this is a §17 capability-audit question, and no novelty language freezes before that audit reports.

## 7.2 Preference representation and inference — deliberately boring

The user is represented by a low-dimensional, interpretable preference vector θ over the same soft attributes consumed by §6.6: distance tolerance, time-of-day fit, price sensitivity, indoor/outdoor, social format, intensity band (d ≈ 6, frozen before evaluation from the barrier-scenario literature review). The prior is weakly informative and population-generic; there is no demographic input, no profiling, and — honouring the §8 privacy commitment — preference state is transient by default: the posterior lives for the session and is discarded.

Inference is exact by enumeration: θ is represented on a discrete grid (or particle set) whose size is trivial at this dimensionality, so posterior updates are a normalising multiplication — no MCMC in the interaction loop, no variational approximation, nothing to diverge. Answer likelihoods include a frozen misreport-noise parameter ε, acknowledging that users answer imperfectly. Correctness of the update machinery is testable by the posterior-quantile method of Cook, Gelman & Rubin (JCGS 2006), with workflow diagnostics per Gabry et al. (JRSS A 2019, already among the §10 foundations).

## 7.3 The question space

Three question types, each with a typed answer schema consumed directly by the pipeline:

| Type | Example surface form | What the answer changes |
|---|---|---|
| Soft-attribute value | "Mornings, evenings, or no preference?" | Likelihood update on the relevant θ dimension → re-ranking via R4 |
| Must-versus-nice reclassification | "Is 'free' a must-have, or just preferred?" | Moves a constraint between the hard-predicate set (gate, R1) and the soft-utility set (R4); exclusionary constraints always require this explicit confirmation |
| Pairwise profile comparison *(stretch)* | "Which suits you better: A or B?" | Probit/Bradley–Terry likelihood update on θ (Guo & Sanner, AISTATS 2010) |

The reclassification type is distinctive to this architecture: because hard and soft constraints route to different pipeline stages, one question can move candidates between gate partitions, and its value is computed accordingly. Question *wording* may be rendered by templates in core (an LLM surface-form renderer is stretch, subject to §8's control/data separation — the policy chooses the question; language models never do).

## 7.4 The policy: decision-EVOI over evidence-bounded utility

At each turn the policy scores every askable question by myopic expected value of information: the expected improvement in the best achievable decision, where the expectation runs over the answer distribution under the current posterior, and — critically — the "decision" is the actual pipeline output. EVOI is evaluated by running stages R1–R4 counterfactually per candidate answer, which is computationally cheap because the gate is an indexed lookup and utility is additive. Two properties follow and are enforced as tests, not hopes:

- **Null-effect property.** A question whose every answer induces an identical top-k slate and gate partition has EVOI exactly zero.
- **Observability property.** If attribute j is unknown or conflicted across the entire relevant pool, a soft question about j has decision-EVOI exactly zero — because §6.6's utility contributes no imputed value for uncertified attributes, no answer can propagate to any score.

The second property is what makes the policy observability-aware without an ad-hoc penalty term: the awareness is inherited from the evidence-bounded utility, and the experimental contrast in RQ3 isolates it, because the uncertainty-only baseline (which asks about the most uncertain θ dimension regardless of actionability) and the conventional-EVOI baseline (computed over an imputed-complete catalogue) lack precisely this inheritance.

**The equity trap, and the designed answer.** A purely decision-optimal policy would never ask about attributes the catalogue is silent on — so a user with accessibility needs would never be asked about them wherever publishers fail to state accessibility, silently reproducing catalogue gaps inside the dialogue. This is unacceptable for barrier-relevant attributes. The policy therefore carries a declared floor: barrier-relevant attributes (accessibility, price) may be asked once regardless of decision-EVOI, and when the answer cannot be acted on, the system says so honestly — "you asked for step-free access; N of M otherwise-matching listings don't state this" — and the gap is logged as a publisher-priority signal feeding the staff dashboard and R4/R5 outputs. A limitation of the catalogue becomes a diagnostic product rather than a hidden bias of the dialogue.

## 7.5 Budget, cost and stopping

A frozen question budget B (provisionally 5) bounds every session. The policy stops early when the best remaining question's EVOI falls below a frozen per-question cost c, or when expected regret under the current posterior falls below a frozen threshold. Both constants are set on the development split and enter the tagged freeze commit; the budget and cost model are reported with results, since regret-by-turn curves, not endpoint scores, are the primary RQ3 output.

## 7.6 Evaluation: simulation-first, ethics-gated for humans

RQ3 is answered primarily in simulation, the standard paradigm of the elicitation literature cited above, and deliberately so: it requires no ethics approval, so the confirmatory comparison cannot be blocked by the ethics timeline. Simulated users are drawn with θ_true from the prior — and, for robustness, from mismatched and adversarial distributions — answering with noise ε. Each of the five frozen policies runs on identical simulated users, identical vintages and identical seeds:

| Policy | Description |
|---|---|
| P1 Fixed order | Frozen question sequence |
| P2 Random | Uniform over askable questions |
| P3 Uncertainty-only | Maximum posterior entropy reduction on θ, blind to the catalogue |
| P4 Conventional EVOI | EVOI over an imputed-complete catalogue (unknown attributes filled by population-frequency draws) |
| P5 Observability-aware EVOI | EVOI over evidence-bounded utility, with reclassification questions and the barrier floor |

Primary quantities per RQ3 and H-E: integrated preference regret (expected utility shortfall of the recommended slate against the θ_true-optimal slate, integrated over turns) and the wasted-question rate, where a question is wasted if no possible answer changes the top-k slate or gate partition, decomposed by cause: **preference-side waste** (posterior already decisive, or attribute non-discriminating among candidates) versus **observability-side waste** (evidence missing or conflicted, so answers cannot propagate). H-E's frozen success logic: at the same budget, P5 improves integrated regret and wasted-question rate beyond frozen margins against the strongest of P1–P4, without higher false assurance. The decomposition is itself a reportable finding: it measures how much of the clarification burden is caused by publisher data gaps rather than user vagueness — a number London Sport can act on. Human construct validation (are the questions intelligible? are honest-gap explanations acceptable?) is stretch, contingent on the confirmed postgraduate ethics route; without approval it remains supervision-level feedback and is excluded from analysis.

## 7.7 What this layer will not do

No demographic questions or inferred sensitive attributes. No persistent user profiles by default; the posterior is session-transient. No language model selects, orders or invents questions — templates render policy choices in core. No question is asked to *appear* thorough: every question must justify itself in decision-EVOI or through the declared barrier floor. No answer is treated as a publisher fact: user statements update θ, never the evidence store.

## 7.8 Layer acceptance evidence

| Check | Mechanism |
|---|---|
| Posterior correctness | Known-answer conjugate/grid tests; posterior-quantile validation (Cook, Gelman & Rubin, JCGS 2006) on the simulation harness |
| Policy correctness | Hand-computable micro-world EVOI unit tests; property tests for the null-effect and observability properties (§7.4); metamorphic test — adding an all-unknown attribute to every candidate never changes P5's question ranking |
| Waste metric | Synthetic scripted dialogues with known waste labels reproduce the decomposition exactly |
| Determinism | Seeded simulations; frozen question bank, budget, cost, ε and thresholds in the tagged commit |
| Interface contracts | Posterior schema consumed unchanged by §6.6; typed question/answer schema consumed by §8; per-turn logs consumed by §§10–11 |
| Latency | Full counterfactual EVOI sweep within the interactive budget on CPU (measured; enumeration scale makes this comfortable) |

## 7.9 Core scope versus labelled stretch

| Tier | Content | Entry criterion | Fallback |
|---|---|---|---|
| **Core** | Grid posterior over d ≈ 6 attributes; soft-attribute and reclassification questions; myopic decision-EVOI with exact counterfactual evaluation; barrier floor with honest-gap reporting; budget/cost stopping; full five-policy simulation harness; regret and decomposed-waste metrics | — | — |
| Stretch T1 | Pairwise-comparison queries (probit/BT likelihood) | Core harness green | Attribute questions only |
| Stretch T2 | LLM-rendered question surface forms | §8 verifier operational | Templates |
| Stretch T3 | Hierarchical population prior | *Only* from consented evaluation sessions or synthetic populations — cross-session learning from real users would breach the transient-state privacy commitment and is otherwise out of scope | Fixed population prior |
| Stretch T4 | Non-myopic lookahead (POMDP framing, Boutilier 2002) | Demonstrated myopic shortfall on dev | Myopic EVOI |
| Stretch T5 | Human construct validation | Confirmed ethics route | Simulation + assessor evidence only |

## 7.10 Evaluation hooks: the contract with §§10–11

Per turn, the layer logs as versioned JSON: posterior summary before and after; the full question-score table (all policies' choices, enabling counterfactual policy comparison on identical states); the asked question, answer and likelihood applied; gate-partition deltas from reclassification answers; stopping decision and governing rule; and waste labels with cause. Regret-by-turn curves regenerate from logs alone, and every H-E headline number is auditable back to seeded simulation state — the cross-review surface for the evaluation stream.

## 7.11 Risks and mitigations specific to this layer

Attribute-set misspecification — the frozen d dimensions may not span real preferences (mitigate: derive the set from the barrier literature before freezing; report residual misfit; treat expansion as a later-vintage question, not a mid-evaluation change). Sim-to-real gap — simulated users are not Londoners (state it as the primary RQ3 limitation; human validation only under ethics; robustness runs under mismatched θ distributions and inflated ε). Question fatigue and over-clarification (budget, cost-sensitive stopping, and the wasted-question metric make over-asking a measured failure, not an invisible one). Barrier-floor gaming of the comparison (the floor applies identically across all five policies, so it cannot flatter P5). Hard/soft misclassification harming recall (exclusionary constraints require explicit confirmation before entering the gate). Circularity between elicitation and evaluation (development-only tuning; the locked set never touches policy constants).

## 7.12 Novelty positioning — precise and audit-gated

Prior art acknowledged by name: attribute-asking conversational recommendation (Zhang et al., CIKM 2018; Lei et al., WSDM 2020), Bayesian and EVOI preference elicitation (Chajewska et al., AAAI 2000; Boutilier, AAAI 2002; Viappiani & Boutilier, NeurIPS 2010; Guo & Sanner, AISTATS 2010; Vendrov et al., AAAI 2020; Martin et al., IJCAI 2024), and conversational-recommendation evaluation (Jannach, AI Review 2023, already in §10). The candidate claim is narrow and checkable: question selection computed over four-valued, mechanism-typed item evidence, with a provable zero-EVOI observability property and a cause-decomposed waste metric that converts dialogue inefficiency into publisher-actionable diagnostics. If the §17 audit finds an incumbent or published system with this coupling, the claim narrows to a controlled comparative evaluation, per the §9 novelty gate.

## Section references (peer-reviewed; merge into §10 foundations at assembly)

Chajewska, Koller & Parr, *Making rational decisions using adaptive utility elicitation*, AAAI 2000. Boutilier, *A POMDP formulation of preference elicitation problems*, AAAI 2002. Viappiani & Boutilier, *Optimal Bayesian recommendation sets and myopically optimal choice query sets*, NeurIPS 2010. Guo & Sanner, *Real-time multiattribute Bayesian preference elicitation with pairwise comparison queries*, AISTATS 2010. Zhang, Chen, Ai, Yang & Croft, *Towards conversational search and recommendation: System Ask, User Respond*, CIKM 2018. Lei et al., *Estimation–Action–Reflection: Towards deep interaction between conversational and recommender systems*, WSDM 2020. Cook, Gelman & Rubin, *Validation of software for Bayesian models using posterior quantiles*, Journal of Computational and Graphical Statistics, 2006. (Forward references already in §10: Vendrov et al., AAAI 2020; Martin et al., IJCAI 2024; Jannach, AI Review 2023; Gabry et al., JRSS A 2019.)
