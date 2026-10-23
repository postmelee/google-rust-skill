# Repeated rhwp chart implementation comparison — 2026-10-23

The 24 submitted implementations passed **24/24 automated assessments** and
**22/24 full frozen assessments**, which also include source review. This
comparison does not establish a general skill advantage. Read the concrete
failure analysis below before interpreting the counts as differences in quality.

| Condition | H1 full pass | H2 full pass | Automated overall | Full assessment |
| --- | ---: | ---: | ---: | ---: |
| Candidate v0.1.0 | 3/3 | 2/3 | 6/6 | 5/6 |
| StudentWeis | 3/3 | 3/3 | 6/6 | 6/6 |
| 0xMassi | 2/3 | 3/3 | 6/6 | 5/6 |
| No added skill | 3/3 | 3/3 | 6/6 | 6/6 |

## Individual repetitions

P means all frozen gates and manual criteria passed; M means an automated pass
with a manual/scope failure; F means an automated gate failed. Repetition numbers
are labels assigned before shuffling, not chronological launch order. The linked
run IDs follow the pre-frozen launch order. Every run is retained.

| Condition | H1 repetition 1 | H1 repetition 2 | H1 repetition 3 | H2 repetition 1 | H2 repetition 2 | H2 repetition 3 |
| --- | --- | --- | --- | --- | --- | --- |
| Candidate v0.1.0 | [P (r17)](runs/r17/assessment.json) | [P (r11)](runs/r11/assessment.json) | [P (r24)](runs/r24/assessment.json) | [P (r03)](runs/r03/assessment.json) | [P (r05)](runs/r05/assessment.json) | [M (r04)](runs/r04/assessment.json) |
| StudentWeis | [P (r15)](runs/r15/assessment.json) | [P (r10)](runs/r10/assessment.json) | [P (r02)](runs/r02/assessment.json) | [P (r16)](runs/r16/assessment.json) | [P (r21)](runs/r21/assessment.json) | [P (r13)](runs/r13/assessment.json) |
| 0xMassi | [P (r06)](runs/r06/assessment.json) | [M (r22)](runs/r22/assessment.json) | [P (r09)](runs/r09/assessment.json) | [P (r01)](runs/r01/assessment.json) | [P (r07)](runs/r07/assessment.json) | [P (r08)](runs/r08/assessment.json) |
| No added skill | [P (r12)](runs/r12/assessment.json) | [P (r19)](runs/r19/assessment.json) | [P (r20)](runs/r20/assessment.json) | [P (r14)](runs/r14/assessment.json) | [P (r18)](runs/r18/assessment.json) | [P (r23)](runs/r23/assessment.json) |

## What differed, and what did not

All final patches passed the build, original and added tests, Clippy, rustfmt,
and four external test functions for their task. All 24 sets of agent-added tests
failed against pristine source because the new API/error types were absent; the
captured sensitivity failures were expected consumer compile errors. These are
final submitted results after within-session self-correction, not first-attempt
success rates. Intermediate command failures reported by agents are preserved;
complete traces are unavailable, so no comparative repair-count metric is claimed.

There was no observed automated pass-rate advantage for any supplied skill over
no added skill. The implementations generally converged on shared planning with
validation before output/mutation, direct writer slices for H1, and forward
compaction followed by backward expansion for H2. Source excerpts and individual
judgments are in each run's `manual-review.json`. Incidental choices such as helper
names, `#[must_use]`, documentation length, or the number of added tests were not
extra scoring criteria.

### r04 and r22: automated passes, source-review failures

[Candidate H2 repetition 3](runs/r04/patch.diff) passed every executable gate but
removed two existing `debug_assert_eq!` checks that compared original numbering
span widths with rescanned fragment widths. It added range bounds checks without
an equivalent width or coordinate-consistency predicate. Its
[response](runs/r04/response.json) explicitly describes removing the debug-only
span-length assumptions.

The frozen [TASK.md](frozen/evals/integration-hard/TASK.md) says “Do not disable
tests or checks.” The frozen H2 criterion also prohibits suppressed checks. The
[manual review](runs/r04/manual-review.json) therefore marks that criterion and
scope review as failed. The failure is **a non-blinded source-review judgment**,
not a failed compiler check, incorrect golden output, or externally demonstrated
allocation error. The submitted patch was retained unchanged.

[0xMassi H1 repetition 2](runs/r22/patch.diff) independently made the same
change: both width assertions were deleted, while new checks only established
range bounds. Its [response](runs/r22/response.json) calls the assertions redundant
because fragment scanning supplies fresh coordinates. The
[scope review](runs/r22/manual-review.json) fails the same frozen no-disabled-checks
constraint. The three H1-specific manual criteria still pass; scope review is a
separate required gate. This is also a source judgment, not a test failure.

The same interpretation was applied to every run: retaining the checks passes;
replacing them with equivalent width rejection or stronger coordinate-consistency
rejection also passes. For example, [r08](runs/r08/patch.diff) uses explicit width
comparison and [r16](runs/r16/patch.diff) uses coordinate comparison. Simply deleting
the predicate does not pass. This evaluates the frozen instruction to preserve
checks, without inventing a new style preference after seeing the outputs.

These two judgments account for the entire difference in full-assessment counts.
If an independent reviewer instead regards removing those assertions as a permitted
internal refactor, the results become a 6/6 tie for every condition. That sensitivity
is a reason not to present the observed candidate/0xMassi 5/6 versus
StudentWeis/no-skill 6/6 as evidence that one skill is generally better. The task
and oracle were not changed to amplify the difference.

The next useful comparison would use independently selected tasks, blinded source
review, more repetitions, and a host with a pinned exposed model configuration.
Less prescriptive API-design tasks could test judgment that these detailed contracts
already specify. Those are future studies, not results established here.

## Why these tasks are harder

The earlier rhwp-contracts comparison passed all 12 runs. This follow-up uses the
complete `rhwp-ooxml-chart` crate, including its existing planner, structural XML
edits, and 165 original tests. Both tasks require a new public API while preserving
old function signatures, exhaustive enum matches, and public struct literals.
They are maintainer-designed feature requests, not upstream bug reports.

| Task | Ownership decision | Error contract | Compatibility obligation |
| --- | --- | --- | --- |
| H1: streaming edits | Borrow a possibly unsized `Write` sink; stream retained input and planned fragments without a complete output buffer | Finish validation before any writer call; retain typed custom I/O payloads; handle short writes, interruption, and WriteZero; document partial output on I/O failure | Reuse all existing edit operations and preserve existing public types and callers |
| H2: owned edits | Consume a `Vec<u8>`; preserve its pointer and capacity whenever the final result fits, including opposing growth/shrink edits | Return the untouched original allocation with a typed cause on validation failure, even after scanner/edit borrows expire | Reuse the planner and old output behavior without a second full output buffer or new unsafe code |

The source is [edwardkim/rhwp at 1a76570](https://github.com/edwardkim/rhwp/tree/1a76570e833917d15817415a53c09ad61ab3203f/crates/rhwp-ooxml-chart).
The [source manifest](../../../provenance/rhwp-chart.json) pins nine source/license/
toolchain/lock files by SHA-256. The minimal workspace retains the entire crate,
Rust 1.93.1, and the upstream dependency versions/checksums: quick-xml 0.42.0 and
memchr 2.8.3. No original rhwp checkout was edited or upstream patch submitted.

## Frozen method and evidence

The [freeze commit](https://github.com/postmelee/google-rust-skill/commit/ba4fdcb63dff9c912a5266c3574d6fd4e302a356)
preceded the evaluated sessions. [experiment.json](experiment.json) records the
source pins, 24 input hashes, seeded run order, host limitations, and frozen
criteria/tool/oracle hashes. [frozen/](frozen/) contains those exact inputs.
The freeze was local before execution and published together with the results;
it was not an independently timestamped public preregistration.

Four conditions use the same versions as the preceding comparisons:

| Condition | Pinned input |
| --- | --- |
| Candidate | This skill v0.1.0, runtime at [`3f85197`](https://github.com/postmelee/google-rust-skill/commit/3f85197d7b39bd4e38406c1c36bcb1eff8e27d7b), nine files |
| StudentWeis | [`07b5b14`](https://github.com/StudentWeis/google-rust-style-guide/tree/07b5b14c68d8bfc978575d347de59ca715e0deab), three files |
| 0xMassi | [`5d5eeca`](https://github.com/0xMassi/google-rust-style-skill/tree/5d5eeca939d723f76317fc1e41276ed3bc1548d9), one file |
| No added skill | The same source, task, and host tools without a supplied skill |

Each task/condition has three fresh sessions, for 24 initial sessions. The launch
order was shuffled using `random.Random(20261023)` and recorded before execution.
Every agent received only its own packet path with the same instruction to follow
TASK.md. Host/system tool instructions and pretrained knowledge remained available
in all conditions; "no added skill" does not mean an empty instruction context.
Fresh contexts excluded parent history; agents were told not to browse,
delegate, or read other packets/reports. Up to three sessions ran concurrently.
They could correct their own work within the original session. No grader feedback,
patch repair, replacement session, or runtime tuning was supplied.

The frozen rubric and external tests were excluded from packets. Each completed
patch was reconstructed against pristine source and independently checked with:

- Locked offline Cargo build and tests, Clippy with warnings denied, and rustfmt.
- Byte-identical original inline tests and file-scope checks.
- Four external test functions per task. Output checks loop over ten frozen XML
  results covering the eight original edit variants, empty edits, and mixed
  structural edits; these were generated from pristine source before the freeze.
- Legacy consumer compilation, typed error/source checks, and task-specific writer
  or allocation contracts, including late malformed-range/overlap failures.
- New agent tests against pristine source: they must fail for the absent API or
  intended behavior, not a timeout or environment problem.
- Primary-agent source review for planner reuse, whole-buffer copying, error
  ownership, documentation, and the frozen prohibition on disabled checks.

[Preflight evidence](preflight/) includes baseline checks, pristine failures,
golden generation, and an author sanity implementation demonstrating that the
requirements and tests are satisfiable. The sanity implementation was not given
to evaluated agents and is not counted as a model run.

Every [run directory](runs/) retains the submitted patch and response, input and
output manifests, independent command logs, automated assessment, and source
review with exact evidence excerpts. Self-reported intermediate failures remain
in responses. Complete inference/tool transcripts are unavailable. Publication
normalizes host-specific paths in JSON/logs; patches and manifests retain their
original bytes. [summary.json](summary.json) is derived from those records.

## Interpretation and limitations

These are two selected development tasks, with only three repetitions per cell.
They do not establish a general ranking, statistical significance, or a causal
benefit from a particular skill rule. Repetitions reveal the observed variation
on these tasks; the tasks are not a random held-out sample. Detailed prompts may
supply enough guidance to reduce differences between skills. Automatic skill
activation and actual reference consumption were not measured.

The model setting was inherited without an override. The host does not expose an
exact backend identifier, sampling settings, token usage, or inference cost, so
none is inferred. Sessions shared a macOS arm64 host and filesystem; isolation
was procedural rather than a security boundary. Concurrent scheduling precludes
using wall-clock durations as a fair skill-efficiency comparison.

The primary agent designed the suite and reviewed source without blinding or
independent human adjudication. Manual judgments are separated from executable
results. Exact excerpts make them auditable, but do not remove reviewer bias.
The external tests cover selected cases rather than proving all malformed scanner
metadata or all possible edit combinations safe. Pointer/capacity assertions test
a requested contract, not total allocations or runtime performance. Test counts
are not a score for test quality.

The complete chart crate is compiled and tested, including its existing renderer
unit tests. This does not validate the root rhwp engine, native bindings, WASM,
full-document round trips, or visual output against a corpus. The installed skill
and v0.1.0 release assets are unchanged; baseline skills and evaluation artifacts
are outside the runtime package.

## Reproduce the recorded code checks

Install the root development dependencies and Rust 1.93.1 with Clippy/rustfmt.
From this evaluation revision, run:

```sh
python3 scripts/rhwp_hard_eval.py fetch
python3 scripts/rhwp_hard_eval.py summarize
python3 scripts/rhwp_hard_eval.py replay --output .cache/chart-replay --fetch-dependencies
```

Use a new output directory; evidence is never overwritten. `--run r04` selects one
run. Replay checks source hashes, reconstructed patch output, and recorded command
exit codes, including expected failures. It does not invoke a model, rerun source
judgment independently, or turn an implementation failure into a pass. The GitHub
Actions `replay-rhwp-hard` job runs this replay separately from the earlier suite.

See [the task protocol](../../integration-hard/README.md) to prepare a new agent
packet. A future model comparison needs its own frozen experiment and archive.
Original tooling/tests are MIT; report prose is CC BY 3.0. Source excerpts retain
[rhwp's MIT attribution](../../../LICENSES/rhwp-MIT.txt).
