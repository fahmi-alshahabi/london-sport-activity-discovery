# London Sport OpenActive Evaluation Stream

This repository contains the work completed for the evaluation stream of the London Sport OpenActive project.

The stream focused on designing and documenting an evaluation that could test the project's main claims in a reproducible way. This included the estimand registry, sample size analysis, diagnostic task set, annotation codebook, analysis plan, assessor structure and supporting validation checks.

## Main work completed

The evaluation work included:

- Estimand definitions and evaluation structure
- Paired binary sample size analysis
- Diagnostic benchmark design
- 14 evaluation templates
- SHA-256 manifest for the task set
- Seeded DEV and LOCKED split
- Structural linting to reduce paraphrase leakage
- Annotation codebook
- Analysis plan
- Assessor eligibility and conflict of interest structure
- Data and hash verification
- Documentation of deviations and changes
- Review of relevant project artefacts and source material

## Reproducibility

The evaluation task set contains 14 templates split into:

- 10 LOCKED templates
- 4 DEV templates
- Random seed: `42`

The task files are recorded in the associated SHA-256 manifest. A structural linter was also used to check the split and reduce the possibility of similar or paraphrased tasks appearing across DEV and LOCKED.

Where possible, data and artefacts were checked independently rather than relying only on reported outputs. For example, the delivered S1b data was independently checked using the recorded hashes and a separate recount of the raw JSONL files.

## Evaluation status

The evaluation design was substantially developed, but the full empirical evaluation was not completed.

The P0/P1/P2 task set was not fully minted. The condition manifest remained pending and only contained three demonstration tasks against a required minimum of 20. As a result, the planned usefulness comparison could not be carried out.

The planned pilot and judging period was also not completed. Therefore, this repository should not be interpreted as containing a completed empirical test of the project's main claims.

The final evaluation record documents these limitations rather than presenting unsupported results.

## Sample size

The F-06 sizing analysis showed that a confirmatory evaluation would require substantially more templates than the available assessor time could support. Depending on the assumed parameters, the estimated requirement ranged from approximately 30 to 762 templates, compared with around 21 to 28 templates being affordable within the available assessment time.

Because of this, the hypothesis was treated as estimative rather than confirmatory before outcome data was available.

## Important limitations

Several limitations are recorded in the evaluation documentation:

- The full P0/P1/P2 task set was not created.
- The usefulness contrast was withdrawn because its required conditions were not in force.
- The pilot and judging stage was not completed.
- No empirical result is reported for the evaluation stream.
- The codebook was not fully piloted or frozen.
- A non-author review was not recorded.
- Full blinding was not possible because the evaluation arms were distinguishable by format.
- The task author, codebook author and sole arbiter were the same person.
- Some planned project dependencies and decisions were changed during the project.

These limitations are retained in the project record so that the final state of the evaluation is clear.

## Repository structure

The repository contains the evaluation artefacts, supporting documentation, scripts and records produced during the project.

The `docs/` directory contains the main evaluation documentation and status records.

The evaluation artefacts include the task definitions, manifests, codebook, estimands, analysis planning and supporting records.

Scripts and validation tools are included where applicable so that parts of the evaluation setup can be checked or reproduced.

## Data verification

The delivered reconstruction data was independently checked rather than being accepted solely from the delivery record.

The recorded delivery contained 8,034 S1b occurrences across 66 providers:

- Open Sessions: 6,597
- Playwaze: 964
- Bookwhen: 473

The six recorded file hashes were also independently verified.

## Project record

The repository should be read together with the evaluation status and scope documentation. These records explain what was planned, what was completed, what changed during the project and which claims could no longer be tested.

The purpose of this repository is therefore to provide a transparent record of the evaluation work and its final state, rather than to suggest that an evaluation result was obtained where the required conditions were not available.
