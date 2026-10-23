# Evaluation results and limits

[Back to the README](../README.md) · [Installation and usage](using.md)

The skill has development evaluations with recorded responses, patches, and
checks. Current results do **not** establish a general advantage over other
skills or no added skill. Installation checks are listed separately in the
[user guide](using.md#verification-status).

## Recorded studies

| Study | What it exercises | Results and evidence |
| --- | --- | --- |
| Static development pilot | 15 review cases: correct code, violations, exceptions, local policy, and applicability | [Pilot report](../evals/results/2026-10-23/REPORT.md) |
| rhwp-contracts implementation | Three real-code tasks; four conditions; 12 fresh sessions | All conditions passed 3/3. [Report and patches](../evals/results/rhwp-2026-10-23/REPORT.md) |
| Repeated rhwp chart implementation | Two tasks combining ownership, error recovery, and API compatibility; three repetitions per condition; 24 sessions | All 24 passed automated checks. [Report and per-run evidence](../evals/results/rhwp-hard-2026-10-23/REPORT.md) |

The comparisons use this skill, pinned versions of
[StudentWeis](https://github.com/StudentWeis/google-rust-style-guide) and
[0xMassi](https://github.com/0xMassi/google-rust-style-skill), and no added skill.
[Baseline provenance](../provenance/baselines.json) records commits and hashes.

## Latest repeated comparison

| Condition | Automated checks | Including source review |
| --- | ---: | ---: |
| This skill v0.1.0 | 6/6 | 5/6 |
| StudentWeis | 6/6 | 6/6 |
| 0xMassi | 6/6 | 5/6 |
| No added skill | 6/6 | 6/6 |

One candidate run and one 0xMassi run removed existing consistency checks without
equivalent replacements. They failed the frozen source-review constraint while
passing compilation, tests, Clippy, and formatting. These were non-blinded reviewer
judgments. If that refactoring were accepted, the full results would also be tied.
See the [failure analysis](../evals/results/rhwp-hard-2026-10-23/REPORT.md#r04-and-r22-automated-passes-source-review-failures).

## What the evidence cannot establish

- These are small, selected development cases, not a representative held-out benchmark.
- Three repetitions per task and condition do not justify statistical rankings.
- Exact backend identity, sampling settings, token use, and inference cost were
  unavailable; file size is not a measurement of model context use or efficiency.
- Explicit skill use does not test every host's automatic activation. Reference
  reads in agent responses are self-reported, not complete tool traces.
- The implementation suites test isolated rhwp crates, not the full engine, WASM,
  native bindings, full-document round trips, or a visual rendering corpus.

## Reproduce or extend an evaluation

Start with the [evaluation protocol](../evals/README.md), then choose the
[rhwp-contracts suite](../evals/integration/README.md) or
[repeated chart suite](../evals/integration-hard/README.md). They document packet
preparation, frozen criteria, independent checks, and replay commands.

GitHub Actions replays archived patches, including runs that failed source review.
A successful replay means the recorded code checks were reproduced; it is not a
new model repetition or a change to the original grade.
See the [validation workflow](https://github.com/postmelee/google-rust-skill/actions/workflows/validate.yml).
