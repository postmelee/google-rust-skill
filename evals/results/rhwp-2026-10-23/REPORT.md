# rhwp implementation comparison — 2026-10-23

All four conditions passed all three implementation tasks. Across 12 fresh agent
sessions, the submitted patches compiled, preserved all 15 existing tests, passed
independent consumer tests, and passed Clippy and rustfmt checks. This establishes
that the candidate can complete these concrete Rust changes under the recorded
conditions. It does **not** establish an advantage over either existing skill or
the no-skill condition: this comparison produced a tie.

## Results

| Condition | R1: in-place annotation | R2: action deduplication | R3: JSON writer | Total |
| --- | --- | --- | --- | --- |
| Google Rust Guidelines v0.1.0 | Pass | Pass | Pass | 3/3 |
| StudentWeis | Pass | Pass | Pass | 3/3 |
| 0xMassi | Pass | Pass | Pass | 3/3 |
| No added skill | Pass | Pass | Pass | 3/3 |

Every pass includes patch-scope review, `cargo build`, the original and new tests,
Clippy with warnings denied, formatting, external consumer tests, a test
sensitivity check, and the task-specific source review. Results come from the
captured patches and independently executed checks, not only agent assertions.
The machine-readable aggregate is [summary.json](summary.json).

The observed implementation patterns were similar across conditions. In R1,
the consuming API delegates to the new in-place API. In R2, separate sets retain
the first exact name in each namespace. In R3, the new writer wrapper serializes
the existing registry builder's result and returns `serde_json::Error` directly.
These tasks therefore did not distinguish the skills on the frozen criteria.
Different test counts are descriptive evidence, not a quality ranking.

## Project and version scope

The subject is the complete `rhwp-contracts` crate from
[edwardkim/rhwp at `1a76570`](https://github.com/edwardkim/rhwp/tree/1a76570e833917d15817415a53c09ad61ab3203f/crates/rhwp-contracts).
The crate contains machine-readable contracts and can be built independently of
the document engine. It is a useful first integration subject: these are real
public APIs with existing tests and downstream compatibility constraints.

The harness preserves all five Rust source files, the crate manifest, the 15
original unit tests, the upstream toolchain file, and the policy document used
by an existing test. It replaces the root workspace with a minimal workspace and
a reduced lockfile. All 12 locked package versions and checksums match upstream.
Sources are pinned and verified with SHA-256 in
[the source manifest](../../../provenance/rhwp.json).

The recorded model runs and independent assessments used Rust/Cargo 1.93.1 on
macOS arm64. The pristine component passed build, tests, Clippy, and formatting
before evaluation; see [baseline checks](preflight/baseline.json).

This evaluation does not build rhwp's root engine, CLI, bindings, WASM, Studio,
or rendering pipeline, and does not satisfy upstream contribution or visual
review gates. The tasks are maintainer-designed feature and robustness requests,
not reproductions of reported upstream issues. Patches were retained as evaluation
artifacts and were not submitted to rhwp. Original Korean comments and contract
strings remain intact; new evaluation prose and public reports are English.
Source excerpts in patches retain the [rhwp MIT license](../../../LICENSES/rhwp-MIT.txt).

## Compared inputs

| Condition | Pinned input |
| --- | --- |
| Candidate | [google-rust-skill v0.1.0, `3f85197`](https://github.com/postmelee/google-rust-skill/tree/3f85197d7b39bd4e38406c1c36bcb1eff8e27d7b/skills/google-rust-guidelines) |
| StudentWeis | [google-rust-style-guide, `07b5b14`](https://github.com/StudentWeis/google-rust-style-guide/tree/07b5b14c68d8bfc978575d347de59ca715e0deab) |
| 0xMassi | [google-rust-style-skill, `5d5eeca`](https://github.com/0xMassi/google-rust-style-skill/tree/5d5eeca939d723f76317fc1e41276ed3bc1548d9) |
| None | Identical task, source, tools, and protocol; no skill supplied |

The candidate runtime was unchanged throughout task design and execution. Each
condition's exact supplied files and hashes are recorded in
[conditions.json](frozen/conditions.json). Existing skills retain the versions
used in the earlier [static-review pilot](../2026-10-23/REPORT.md).

## Tasks and executable checks

- **R1 — in-place annotation:** add `mark_in_place(&mut Value, &str)` while keeping
  the consuming `marked(Value, &str)` API. Preserve payloads, non-object values,
  annotation semantics, and existing declarations. Share implementation without
  cloning the entire envelope. Three external tests cover public API compatibility,
  presence semantics, and payload preservation.
- **R2 — ontology action names:** retain the first valid exact name independently
  for commands and MCP tools. Reject absent, non-string, empty, and whitespace-only
  names while preserving accepted spelling, order, metadata, input values, and IR
  behavior. Two external tests cover duplicate/invalid names and unchanged IR.
- **R3 — JSON writer:** add a writer API accepting borrowed and dynamic writers,
  returning `Result<(), serde_json::Error>`. Reuse the registry builder and produce
  the same compact JSON without a newline or explicit flush. Three external tests
  cover exact bytes, borrowed writers, partial-write failures, and error kinds.

The [task definitions](frozen/evals/integration/cases.json),
[rubric](frozen/evals/integration/rubric.json), and
[external tests](frozen/evals/integration/oracles) were frozen before execution.
External tests were not supplied to evaluated agents. Preflight checks confirmed
that untouched source fails each requested contract and an author sanity
implementation can pass it; see [oracle checks](preflight/oracle-checks.json).
Sanity implementations were not agent inputs or counted as model runs.

Each submitted patch was applied to a fresh verified workspace. The harness
independently ran build, tests, Clippy, and formatting before adding external
tests. It then restored the original implementation while retaining the agent's
new tests. Those tests failed for the intended missing API in R1/R3 and for
behavioral assertions in R2. These expected failures are preserved in
`test-sensitivity.log`; they are not failures of the patched code or claims that
upstream's original tests were broken.

## Per-run evidence

Each linked directory contains the patch, response, input/output manifests,
assessment, source review with quoted evidence, and all independent check logs.
Every run retained and passed the same 15 original tests. The external test count
is per run and excludes the agent's own new tests.

| Case | Condition and evidence | New agent tests | External tests | Result |
| --- | --- | ---: | ---: | --- |
| R1 | [Candidate](R1/candidate) | 6 | 3 | Pass |
| R1 | [StudentWeis](R1/studentweis) | 7 | 3 | Pass |
| R1 | [0xMassi](R1/0xmassi) | 8 | 3 | Pass |
| R1 | [None](R1/none) | 6 | 3 | Pass |
| R2 | [Candidate](R2/candidate) | 3 | 2 | Pass |
| R2 | [StudentWeis](R2/studentweis) | 3 | 2 | Pass |
| R2 | [0xMassi](R2/0xmassi) | 4 | 2 | Pass |
| R2 | [None](R2/none) | 3 | 2 | Pass |
| R3 | [Candidate](R3/candidate) | 3 | 3 | Pass |
| R3 | [StudentWeis](R3/studentweis) | 4 | 3 | Pass |
| R3 | [0xMassi](R3/0xmassi) | 5 | 3 | Pass |
| R3 | [None](R3/none) | 3 | 3 | Pass |

No completed run was discarded or repaired by the grader. Self-correction within
an agent's original session was allowed. Agent-reported intermediate command
failures remain in the responses; full within-session tool traces are unavailable.
Independently captured harness logs include the expected sensitivity failures.

## Protocol and audit notes

Each case/condition used a fresh independent collaboration context with no parent
conversation history. Agents received only their packet path, with instructions
to work inside it, read the supplied skill when present, and use offline Cargo.
The rubric, external tests, and prior results were excluded from every packet.
Isolation was procedural on a shared filesystem, not a security sandbox. Actual
automatic skill selection by a host was not tested: skill reading was explicit.

Run order was frozen and rotated across cases, not randomized. There was one run
per cell and no repeated sampling. The inherited host model had no explicit
override; its exact backend identifier, sampling settings, token counts, latency,
and inference cost were not exposed. Reference-read lists and within-session
commands are self-reports. No token, efficiency, or cost advantage is claimed.

The primary agent reviewed the frozen manual criteria without blinding. The
summarizer checks recorded criteria, evidence excerpts, hashes, and aggregate
consistency; it does not independently establish semantic correctness.

One harness correction was made after the first three sessions began but before
any completed output was inspected or assessed. It corrected diff provenance
for forbidden root workspace/lockfile edits and treated source deletion as a
scope failure. Criteria and packets were unchanged. Both the
[original runner](frozen/scripts/rhwp_eval.py) and
[assessment runner](frozen/assessment-runner.py) are retained, with timing and
hashes in [experiment.json](experiment.json).

Host-specific repository and temporary paths in published JSON/logs were
normalized. Patches, input/output manifests, diagnostics, and substantive response
text were preserved. The archive records the normalization explicitly.

## Reproduce and interpret

Follow [the implementation protocol](../../integration/README.md) for dependency
setup and fresh model runs. Recompute the aggregate and replay the archived
patches without invoking a model:

```sh
python3 scripts/rhwp_eval.py fetch
python3 scripts/summarize_integration.py evals/results/rhwp-2026-10-23
python3 scripts/replay_integration.py --output .cache/rhwp-replay --fetch-dependencies
```

The [validation workflow](../../../.github/workflows/validate.yml) includes a
separate Linux job that replays all 12 archived patches and compares gate exit
codes. Consult its run for the relevant repository commit. A replay checks the
saved artifacts; it is not another model trial.

Compared with the static-review pilot, this adds direct evidence that agents can
implement requested changes and deliver working patches. Its three explicit tasks
in one small crate produce a ceiling effect: all conditions pass. It does not
measure engine-scale refactoring, difficult ownership/concurrency tradeoffs,
general Google-guide adherence, or the benefit of progressive reference loading.
These development cases are not a blinded held-out benchmark.

A future discriminating comparison should freeze harder tasks in additional
crates, include compatibility and architecture decisions that require judgment,
and run repeated trials with a fixed model identifier. These results support
keeping rhwp as one integration subject, while leaving broader skill superiority
and efficiency claims unresolved.
