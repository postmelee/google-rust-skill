# Implementation evaluation on rhwp

This suite measures whether an agent can modify real Rust source and deliver a
patch that compiles, preserves existing tests, and passes independent consumer
tests. It complements the original 15 static-review cases.

The [2026-10-23 comparison](../results/rhwp-2026-10-23/REPORT.md) records 12 runs:
all four conditions passed all three cases. It demonstrates working patches for
these tasks, without establishing an advantage for any skill.

The subject is the complete `rhwp-contracts` crate from
[edwardkim/rhwp](https://github.com/edwardkim/rhwp), pinned in
[provenance/rhwp.json](../../provenance/rhwp.json). Its source is downloaded into
an ignored cache and verified by SHA-256. Source is not copied into the skill.
The crate intentionally separates machine-readable contracts from the main
document engine, making its existing tests independently buildable.

## Scope and tasks

| Case | Requested change | Main checks |
| --- | --- | --- |
| R1 | Add an in-place provenance annotation API | Borrowed mutation, shared logic, existing consuming API, payload preservation |
| R2 | Deduplicate ontology actions | First occurrence wins, invalid names, stable order, separate namespaces, counts |
| R3 | Write registry JSON to a writer | Borrowed/dynamic writers, typed I/O errors, representation reuse, no flush |

These are maintainer-designed feature and robustness requests on actual source,
not claims that upstream has accepted these requirements or reported these bugs.
The candidate skill was not changed while constructing or running this suite.
The cases are new development evaluations, not a blinded held-out benchmark.

The harness replaces the large root workspace with a minimal workspace containing
the full crate. It preserves the crate manifest, all five source files, all 15
existing tests, the upstream Rust 1.93.1 toolchain file, and the policy document
included by an existing test. The reduced lockfile retains the same versions and
checksums for all 12 packages as the upstream lockfile.

This does **not** build the root rhwp engine, CLI, native bindings, WASM, Studio,
or rendering pipeline. Upstream contribution/review/visual gates are not claimed
to pass. Evaluation patches are local artifacts, not submitted upstream fixes.
The extracted workspace has an explicit evaluation protocol; the upstream root's
operational agent manuals are not supplied as a competing instruction layer.
Original Korean source comments and contract values remain intact. New task
instructions, reports, and evaluation documentation are English.

## Freeze before running

Keep [cases.json](cases.json), [rubric.json](rubric.json), the
[external consumer tests](oracles), workspace files, source pins, and skill hashes
fixed before launching any condition. Archive exact copies, their SHA-256 hashes,
the protocol, tool versions, and packet manifests with the results. Do not update
criteria after seeing outputs or tune the skill during the comparison.

Use the same four conditions as the pilot: candidate, StudentWeis, 0xMassi, and
no added skill. The existing skills retain the earlier pinned commits. Each
case/condition gets a fresh context and an independent writable workspace.
Record unsuccessful runs and infrastructure failures; do not replace or repair
an agent's patch before grading it. Self-correction inside its initial session is
allowed. This initial comparison has one run per cell and no variance estimate.

## Prepare and execute

Install Python development dependencies as described in the root README and
install Rust 1.93.1 with rustfmt and Clippy. Fetch sources and baseline skills:

```sh
python3 scripts/fetch_sources.py
python3 scripts/rhwp_eval.py fetch
python3 scripts/rhwp_eval.py prepare --condition candidate --case R1 --output /tmp/rhwp-candidate-r1
```

Populate Cargo's dependency cache before isolating evaluated sessions:

```sh
cd /tmp/rhwp-candidate-r1/workspace
cargo +1.93.1 fetch --locked
```

Give a fresh agent only the packet path and ask it to follow `TASK.md`. The packet
contains the task, source, pinned configuration, optional skill, and manifest.
It does not contain the rubric, external tests, prior results, or other skills.
Do not give the agent the parent evaluation repository as its working context.
The current host shares a filesystem: isolation is enforced by the task protocol,
not by a security boundary that makes other files inaccessible.

The evaluated agent edits source, adds integration tests, executes Cargo checks,
and writes `response.json`. It uses offline Cargo and may not browse or delegate.
Existing source tests and configuration must remain unchanged. Changes are
limited to one specified source file plus new integration tests.

## Independently replay and grade

From this repository:

```sh
python3 scripts/rhwp_eval.py assess --packet /tmp/rhwp-candidate-r1 --output /tmp/rhwp-candidate-r1-results
```

The harness captures the patch, manifests, and response. In a fresh workspace it:

1. Checks patch scope and preserves the upstream inline tests byte for byte.
2. Applies the captured patch to verified, pristine source.
3. Runs `cargo build`, all original and new tests, Clippy with warnings denied,
   and rustfmt check on the agent's code.
4. Adds independent external-consumer tests after the agent has finished and
   runs them through the public crate API.
5. Restores the original source while keeping the agent's tests, then confirms
   those tests fail on the missing API or requested behavior.

All Cargo builds use `--offline --locked --target-dir target/pr-review` and
Rust 1.93.1. The sensitivity check is separate from a successful patched build:
for new APIs, an unresolved-import failure is expected and means the API did not
exist before the patch. It is not described as an upstream test regression.
For R2, the unmodified source must fail behavioral assertions.

Inspect the raw logs to distinguish an expected sensitivity failure from an
environment failure. Review the task-specific frozen criteria against the actual
source patch. Only then record a final pass. The primary agent performs this
source review; it is not blinded or independently human-adjudicated. Compiler
and external tests provide executable evidence, but do not prove all behavior.

## Replay the published patches

No model access is needed to reproduce the recorded compiler/test gates:

```sh
python3 scripts/rhwp_eval.py fetch
python3 scripts/summarize_integration.py evals/results/rhwp-2026-10-23
python3 scripts/replay_integration.py --output .cache/rhwp-replay --fetch-dependencies
```

Use `--run R1-candidate` to replay one cell, and choose a new output directory for
each replay. `--fetch-dependencies` permits an initial Cargo download; all grading
commands remain offline. Omit it when dependencies are already cached. The script
checks reconstructed input/output hashes, applies the recorded patches, and
compares gate exit codes to the archive. It does not regenerate model responses
or constitute a new statistical repetition. Use the evaluation's repository
revision if task definitions or source pins later change.

## Evidence and limits

The result archive retains all 12 patches, actual responses, input/output
manifests, compiler/test/lint logs, external-test results, sensitivity failures,
manual judgments, and frozen criteria. Oracle preflight records show that the
untouched source fails each requested contract and an author sanity implementation
can pass it. Those sanity implementations are not given to evaluated agents and
are not counted as model runs.

Within-session command outcomes in `response.json` are agent-reported; complete
inference/tool traces are not available. Independent replay logs are captured by
the harness. Local filesystem paths may be normalized for publication, without
changing diagnostics, grades, patches, or substantive response text.

Report per-condition outcomes and failure categories. Do not treat test count,
patch size, or entrypoint bytes as model quality, token savings, or inference
efficiency. The host does not expose a fixed backend model identifier, sampling
settings, or token/cost instrumentation. Compilation happens locally on macOS
arm64; no cross-platform or whole-engine claim follows from these results.

Upstream source excerpts retained in patch evidence are MIT licensed under
[LICENSES/rhwp-MIT.txt](../../LICENSES/rhwp-MIT.txt). Original evaluation tooling
and Rust tests use this repository's MIT license; prose uses CC BY 3.0.
