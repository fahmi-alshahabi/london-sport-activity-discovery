# 8. Conversational Assistant: Evidence-Contract Generation and Verified Rendering

*Status: provisional machinery for supervisor and team ratification, consistent with the §4 status line. This section specifies the dialogue layer that consumes §6's ranked candidates and §7's question policy, and the generation discipline behind RQ4. The claim contract and certifying verifier sit in the reconstruction/evidence stream; conversational UX sits in the applications stream — this draft is input to both. Stretch items enter scope only by decision-log entry.*

---

## 8.1 Framing: the model may be creative about wording, never about facts

Ordinary retrieval-augmented generation (Lewis et al., NeurIPS 2020) reduces hallucination but does not eliminate it: with retrieved listings in the prompt and free generation out, a fluent model can still assert what the evidence does not support — precisely the "confident invention" the §1 challenge names, and a failure mode now measurable at scale (RAGTruth, ACL 2024; attributable-to-identified-sources framing, Rashkin et al., Computational Linguistics 2023 — both already among the §10 foundations). The design commitment of this layer is therefore that the language model never writes user-facing prose about the catalogue directly. It parses, it clarifies, and it composes responses *as data* — structured claim tuples carrying receipt identifiers — and a deterministic verifier, plain versioned code with no model inside it, authorises every tuple against the certified evidence store before anything renders. The principle mirrors §6.3 exactly, one level up: the gate guarantees no unsupported candidate is shown; the contract guarantees no unsupported sentence is rendered.

## 8.2 The turn pipeline

| Stage | Function | Discipline |
|---|---|---|
| C1 Parse | Natural language → typed intent (hard-constraint predicates, soft-preference signals, task frame) via constrained decoding against a frozen, versioned intent schema (PICARD-style constrained decoding: Scholak et al., EMNLP 2021; Synchromesh: Poesia et al., ICLR 2022) | Malformed output cannot exist by construction; low-confidence or ambiguous slots route to clarification, never to guessing. Slot accuracy is evaluated under task-oriented-dialogue conventions (MultiWOZ: Budzianowski et al., EMNLP 2018) |
| C2 Ground & clarify | Intent routed to the §6 pipeline; clarification decisions routed to the §7 policy. Intent-repair questions ("did you mean the borough or the station?") and preference questions share one user-facing question budget | One budget prevents the two question sources from jointly exhausting user patience |
| C3 Compose claims | The model emits a set of typed claim tuples: (claim type, subject, predicate, value, receipt IDs, evidence grade, qualifiers). The claim-type vocabulary is closed: listing-attribute, match-cardinality, bounded non-match (always coverage-qualified), uncertainty (mechanism-typed), and process claims. Anything outside the vocabulary cannot render | Closed vocabulary makes "sayable" a finite, testable set |
| C4 Verify | The deterministic verifier resolves every receipt in the frozen store and checks each claim against the certified state and grade. Outcomes: verified / failed / unresolvable. Any non-verified tuple triggers the declared repair policy: bounded regeneration, claim-dropping with an explicit omission note, or abstention | The verifier is independent of the generator and is never an LLM; NLI/LLM judges are secondary comparators only |
| C5 Render | Verified tuples → surface text via templates (core). Evidence badges, grades and receipt IDs pass through to the interface (§14) | Templates are trivially faithful; LLM verbalisation of verified tuples is stretch, with a per-sentence tuple-mapping check |
| C6 Abstain & hedge | Explicit unsupported-request responses; why-not blockers from the gate ledger; honest-gap statements from §7's barrier floor; declared refusal categories (medical suitability, capacity promises) | Abstention is a designed output with its own metrics, not a failure state |

## 8.3 The evidence contract

Seven clauses, each enforced by a named test in §8.7: (1) every user-facing factual assertion about the catalogue is a rendered claim tuple; (2) every tuple carries at least one receipt resolving in the frozen evidence store; (3) verification precedes rendering, without exception; (4) unknown and conflict are rendered as unknown and conflict, mechanism-typed, never smoothed into fluency; (5) bounded non-match claims always carry the acquisition-coverage qualifier — "no observed listed match" is never allowed to read as "no activity exists"; (6) evidence grade (explicit versus schedule-derived) survives to the surface; (7) model, prompt, schema and verifier versions are pinned, and every response logs the full chain. The contract spans the platform end to end: a rendered sentence traces through its tuple, its receipts and the provenance graph to exact acquired bytes.

## 8.4 Security: the contract is also the firewall

Publisher text is untrusted data, never executable instruction. Indirect prompt injection through listing descriptions (Greshake et al., AISec @ CCS 2023) is an in-scope threat, met with layered controls: control/data separation with delimited untrusted channels; structured decoding, so injected text cannot smuggle free-form output past the schema; an allow-listed tool surface; free-text PII redaction before model exposure (§8 privacy table); and — the structural defence — the verifier itself. A successful jailbreak of the *generator* still cannot render an unreceipted fact, because the deterministic verifier sits downstream of the model and resolves receipts against a store the model cannot write to. The assurance mechanism and the injection defence are the same mechanism. An adversarial battery (injection strings planted in synthetic listings; requests for unsupported capacity, accessibility and suitability; instruction-smuggling in constraints) reports a measured bypass rate; the target on the planted set is zero, reported as a rate, never claimed as universal safety.

## 8.5 Evaluation: the RQ4 experiment

Four arms on identical intents, candidates, retrieval and base model, differing only in generation discipline:

| Arm | Generation discipline |
|---|---|
| A0 | Deterministic templates over structured results — no LLM in the response path |
| A1 | Ordinary RAG: retrieved listings in prompt, free generation |
| A2 | Schema-constrained generation, no verifier |
| A3 | Full claim contract with independent verification (proposed) |

Primary outcome: response-level false assurance — a response fails if it renders any unsupported claim; the unit is the response, not the nested claim, matching §5. Costs measured alongside: supported-fact completeness (of facts the evidence could support, how many were delivered — the over-refusal price), task success on frozen scenarios, correct-abstention and over-refusal rates, wasted questions (shared metric with §7), latency, and usability proxies. Automated verification settles most support judgments; residual and completeness judgments are human-annotated under the frozen codebook with blinded system identity and sampled adjudication per §5. H-G's frozen logic: at matched answer coverage, A3 improves response-level false assurance beyond the frozen margin against the strongest of A0–A2, with supported-fact completeness and task success non-inferior. All headline analyses repeat under the §6 robustness grid: paraphrase, planted defects, injection, capacity-trap requests, publisher holdout and later vintages. A0 is retained deliberately: if templates match the contract system on usefulness, that is a reportable finding about where LLMs earn their place, not an embarrassment to bury.

## 8.6 What this layer will not do

Never assert capacity, bookability or medical suitability. Never generate a publisher fact. Never let an NLI or LLM judge gate rendering. No free-text catalogue prose outside verified tuples in core. No chat memory beyond the session, consistent with §7's transient-state commitment. No unpinned model, prompt or schema anywhere in the response path.

## 8.7 Layer acceptance evidence

| Check | Mechanism |
|---|---|
| Verifier correctness | Known-answer suites covering all four evidence states, both grades, conflict and coverage qualifiers; mutation testing over verifier logic with survivor taxonomy |
| Contract soundness | Property test: no rendered factual sentence lacks a mapped verified tuple (checkable by construction under template rendering); clause-by-clause tests for §8.3 |
| Injection battery | Planted-injection corpus; measured bypass rate; regression-locked cases for every discovered bypass |
| Parse quality | Frozen paraphrase sets; slot accuracy and clarify-routing correctness on development data |
| Determinism | Temperature-0 / seeded decoding for confirmatory runs; pinned model, prompt, schema and verifier hashes in the registry |
| Latency | p95 turn time ≤ 5 s on the public path with template rendering; per-stage timings logged; bounded verification retries |
| Reproducibility | Every RQ4 headline regenerates from response logs alone |

## 8.8 Core scope versus labelled stretch

The base model is a named decision-log item (a pinned small open-weights model or a pinned API tier are both acceptable; the pinning rule is the commitment, not the vendor), and the RQ4 design requires the LLM arms regardless, so parsing and claim composition sit in core.

| Tier | Content | Entry criterion | Fallback |
|---|---|---|---|
| **Core** | C1–C6 with template rendering; closed claim vocabulary; deterministic verifier and repair policy; shared question budget; abstain/hedge paths; injection battery; full four-arm RQ4 harness | — | — |
| Stretch U1 | LLM verbalisation of verified tuples with per-sentence tuple-mapping check | Core latency and contract-soundness green | Templates |
| Stretch U2 | Multi-turn context carryover beyond slot memory | U1 landed; privacy review recorded | Single-turn slot memory |
| Stretch U3 | NLI-assisted completeness annotation (assessor aid only, never gating) | Development judgments available | Manual annotation |
| Stretch U4 | Few-shot intent-parser tuning on development data only | Slot-accuracy shortfall demonstrated on dev | Zero-shot constrained parsing |

## 8.9 Evaluation hooks: the contract with §§10–11

Per response, logged as versioned JSON: intent parse with confidences; clarify decisions and budget state; the full tuple set with receipts, grades and verification outcomes; repair actions taken; rendered text with its tuple mapping; abstention decisions and category; model, prompt, schema and verifier versions; per-stage latency; seeds. RQ4 regenerates from logs alone, and every headline number is auditable back to a specific verified (or refused) tuple — the cross-review surface for the evaluation stream.

## 8.10 Risks and mitigations specific to this layer

Parser brittleness on colloquial London queries (constrained decoding prevents malformed intents, not misunderstanding — the clarify path is the mitigation, and slot accuracy is measured, not assumed). Over-refusal eroding usefulness (completeness and over-refusal are first-class metrics; the frontier is reported, not a single point). Template stiltedness harming perceived quality (usability proxies in evaluation; U1 exists for exactly this, gated). Version skew between verifier and evidence store (one vintage stamp per session; contract clause 7). Annotation cost of residual human judgment (sampled adjudication under the §5 design; the automated verifier settles the bulk — but assessor hours land on the shared cap and are budgeted in the §10 sizing simulation). Base-model dependence of findings (all arms share the model; claims concern the contract's marginal effect, holding the model fixed — never the model's quality).

## 8.11 Novelty positioning — precise and audit-gated

Prior art acknowledged by name: retrieval-augmented generation (Lewis et al., NeurIPS 2020); fact verification against evidence (FEVER: Thorne et al., NAACL 2018); attributable generation and its measurement (Rashkin et al., CL 2023; RAGTruth, ACL 2024); constrained decoding (Scholak et al., EMNLP 2021; Poesia et al., ICLR 2022); selective prediction and abstention (Geifman & El-Yaniv, NeurIPS 2017; Traub et al., NeurIPS 2024, already in §10); task-oriented dialogue evaluation (Budzianowski et al., EMNLP 2018); conversational-recommendation evaluation (Jannach, AI Review 2023, already in §10). The candidate claim is narrow: an end-to-end contract in which every rendered factual sentence resolves through typed claim tuples and mechanism-typed four-valued evidence to exact acquired bytes, with a deterministic verifier that simultaneously bounds false assurance and functions as an injection firewall — evaluated at matched retrieval and model against template, RAG and schema-only controls. If the §17 audit finds a deployed or published system with this end-to-end coupling, the claim narrows to a controlled comparative evaluation, per the §9 novelty gate.

## Section references (peer-reviewed; merge into §10 foundations at assembly)

Lewis et al., *Retrieval-augmented generation for knowledge-intensive NLP tasks*, NeurIPS 2020. Thorne et al., *FEVER: a large-scale dataset for fact extraction and verification*, NAACL 2018. Scholak, Schucher & Bahdanau, *PICARD: parsing incrementally for constrained auto-regressive decoding from language models*, EMNLP 2021. Poesia et al., *Synchromesh: reliable code generation from pre-trained language models*, ICLR 2022. Budzianowski et al., *MultiWOZ: a large-scale multi-domain Wizard-of-Oz dataset for task-oriented dialogue modelling*, EMNLP 2018. Greshake et al., *Not what you've signed up for: compromising real-world LLM-integrated applications with indirect prompt injection*, AISec @ CCS 2023. (Forward references already in §10: RAGTruth, ACL 2024; Rashkin et al., CL 2023; Traub et al., NeurIPS 2024; Jannach, AI Review 2023; Geifman & El-Yaniv cited in §6.)
