# Production / reference / checker discrepancy register (C-09)

**Status:** empty — populated once Michael's production interpreter emits certificates.
**Rule (WP §10.4):** a disagreement is *recorded and triaged*, **never** resolved by editing the
checker to make production pass. If the checker is wrong, fix it with a new test that first
reproduces the fault; if production is wrong, that is a finding.

> AI-assisted scaffold. Clarence owns the triage decisions in his own words; a non-author reviewer
> confirms dispositions.

Each disagreement between the three independent implementations
(production interpreter · reference interpreter · this checker) on the same input gets one row.

| id | date | query_id | decision_digest | production | reference | checker | divergence_type | triage_owner | disposition | resolution_commit |
|----|------|----------|-----------------|------------|-----------|---------|-----------------|--------------|-------------|-------------------|
| _(none yet)_ | | | | | | | | | | |

**divergence_type** vocabulary (proposed): `checker_false_fail`, `checker_false_pass`,
`production_bug`, `reference_bug`, `contract_ambiguity`, `version_skew`.

**Disposition** must state which implementation changed and why, with the commit that carried the
fix and the regression test that locks it. A `contract_ambiguity` disposition routes to a Section 09
decision-log entry, not a silent code change.
