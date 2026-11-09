# F-12 — Condition manifest and telemetry schema, reviewed against the estimands

**Reviewer:** Fahmi Alshahabi (evaluation stream) · **Author of artefacts:** Clarence Zhen Jin Tan
**Reviewed:** `packages/evaluation/condition-manifest.json`, `packages/evaluation/event-schema.json`
(both `0.1.0-PROPOSED`), branch `clarence/c-block-05`
**Date:** 18 August 2026
**Question asked:** do these artefacts support the estimands in F-02 and the contrasts in F-13, and
does the telemetry carry what the denominators need?

**Answer: not yet.** The contract is sound in design — the shared-referent principle is right and
the no-study fallback is correct. But the task set cannot support a powered contrast, and three
fields my estimands depend on are absent.

---

## Findings

| ID | Severity | Finding |
|---|---|---|
| **M-1** | blocking | **Three tasks.** `T-swim-croydon`, `T-climb-havering`, `T-yoga-croydon` — q=3. Under CA-01.A9 the attainable power ceiling is fixed by the item sample, so no participant count rescues it. Using the placeholder variance components in `power_ceiling.py` (illustrative only, not estimates for this design): ceiling ≈ 0.18 at q=3, ≈ 0.31 at q=6, ≈ 0.77 at q=20; q=22 needed for a 0.80 ceiling. The exact figures depend on the stimulus-side component B, but the structure does not. Three tasks is a demonstration fixture set, not a benchmark. |
| **M-2** | major | **The shared referent is hardcoded, not established.** Each task maps 1:1 to a fixed scenario and `scenario_overrides` must stay empty, so identical terminal envelopes across a family are true by construction. Against a real engine that identity must be produced and verified, not assumed. `L_reliance` (F-BLOCK-09) binds to it, and no current test exercises the non-fixture case. |
| **M-3** | major | **No mechanism for minting a repaired-query task.** `identification_honesty` states that a conversation-changed query is recorded as a different task, never silently — correct, and it is the basis of my F-BLOCK-09 exclusion rule. But no field, id convention or process exists for creating that task. The repair screen cannot be operated from this manifest. |
| **M-4** | major | **Origins and publishers are not recorded.** Tasks are identified by activity and borough only. PD-6 (a `task_template_id` must not span splits) and the CAL-RISK clustering structure are both defined over origins and publishers. Splits cannot be built, and the question of whether origins constitute a third variance level beyond participants and tasks cannot be examined from this artefact. |
| **M-5** | minor | **Conditions are not bound to a vintage.** The applications display `H1-2026-06-30`, but the manifest does not pin a vintage per condition. Nothing currently prevents two conditions in the same family running against different vintages, which would confound the interface effect with a data difference. |
| **M-6** | major | **No opening-query envelope in the telemetry.** `event-schema.json` carries a single `envelope_digest`, it is not in `required`, and `additionalProperties: false` blocks informal addition. The F-BLOCK-09 mechanical repair screen needs an opening-query digest or a logged shadow-resolve, and it cannot be recovered after the fact. Already raised for the C-BLOCK-05 contract workshop; recorded here because it is an estimand dependency, not only a schema preference. |

## Confirmed as written

- The family principle — all conditions in a surface family resolve the identical terminal
  `DecisionEnvelope`, only presentation differs — is the correct design for an interface contrast,
  and `validate_conditions.py` checks projected-digest equality rather than asserting it.
- `scenario_overrides` being required-empty is the right guard against confounding.
- P0 is explicitly labelled comparator-baseline-only, with no direct Get Active / imin superiority
  claim. That matches the prohibited-claims discipline.
- `no_study_fallback` retains conformance, accessibility and non-interference testing while
  removing usability, actionability, organisational-effectiveness and lived-equity claims. This is
  consistent with the F-BLOCK-09 ethics disposition (defined but unmeasured absent an approved
  participant route).
- `tuning_freeze` versions and re-runs any condition whose semantics or task flow change after
  freeze, which is the behaviour my locked-run rules require.

## Consequences for my stream

1. F-06 sizing must treat task count as the primary design variable, not participant count. The
   first output of the harness should be the minimum q whose ceiling reaches each target, per
   confirmatory claim.
2. F-04 splits cannot be built until M-4 is resolved.
3. The F-BLOCK-09 repair screen is unimplementable until M-3 and M-6 are resolved.
4. M-2 means the shared-referent assumption becomes an empirical check against Michael's engine
   rather than a property of the manifest, and belongs in the locked-run preconditions.

*Raised with Clarence 18 August 2026.*
