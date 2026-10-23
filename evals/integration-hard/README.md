# Repeated chart implementation evaluation

This suite extends the initial rhwp-contracts comparison with two tasks in the
complete `rhwp-ooxml-chart` crate at the same pinned rhwp commit. Each task combines
ownership, recoverable errors, and existing public API compatibility. Source is
verified against [the manifest](../../provenance/rhwp-chart.json). The minimal
workspace preserves all six crate files, 165 original tests, Rust 1.93.1, and the
three packages' upstream dependency versions and checksums.

See the [recorded 24-run comparison](../results/rhwp-hard-2026-10-23/REPORT.md)
for results, per-run evidence, manual judgments, and interpretation limits.

## Tasks

| Case | Requested outcome | Coupled decisions |
| --- | --- | --- |
| H1 | Stream existing chart edits to a borrowed writer | Validate every range before writing; preserve short-write and I/O error behavior; avoid a full output buffer; preserve existing enums and callers |
| H2 | Consume and reuse an owned XML vector | Recover the untouched allocation on errors; reuse capacity across mixed growth/shrink operations; share planning and preserve existing APIs |

These are new maintainer-designed requests on actual upstream code, not claims
that upstream has requested or accepted these features. Existing source comments
and messages remain intact. New task instructions and public evaluation prose are
English. This component build does not validate the full rhwp engine, document
round trips, WASM, native bindings, or visual rendering against a corpus.

## Frozen comparison

Run candidate v0.1.0, StudentWeis, 0xMassi, and no added skill on both tasks, with
**three fresh sessions per case and condition: 24 sessions total**. Keep the skill
versions from the earlier comparison. Freeze tasks, rubric, tools, source hashes,
golden outputs, and every packet manifest before launching any session. Use a
recorded, seeded shuffled order. Do not change the runtime or tune tasks after
seeing results. Do not replace a failed run with a better attempt.

Each session receives only its own packet and an instruction to follow TASK.md.
It may correct its own implementation before finishing. It may not read external
tests, criteria, other sessions, or prior reports. Reading the supplied skill is
explicit; automatic host selection is not measured. The host shares a filesystem,
so this is procedural isolation rather than an access-control boundary. A fresh
collaboration context excludes parent conversation history; no model override is
used. Backend identifiers, sampling controls, token use, and inference cost are
not exposed and must not be invented.

## Executable and source checks

Every captured patch is replayed in a pristine workspace, with offline locked
Cargo build/test, Clippy with warnings denied, and rustfmt. Existing inline tests
must remain byte-identical. New agent tests must pass with the patch and fail
against the original implementation for the intended absent API or behavior.

External tests are injected only after completion. Ten output files, generated
by the pristine implementation before the freeze, cover the old edit operations.
External consumer code uses old function pointers, exhaustive enum matches, and
struct literals. H1 additionally checks late validation failures, short writes,
Interrupted, WriteZero, typed custom I/O payloads, and no flushing. H2 checks pointer
and capacity preservation, opposing growth/shrink order, recovery after borrowed
inputs expire, and malformed ranges. These tests complement source review for
whole-buffer copying and planner reuse, which output equality alone cannot prove.

The grader records the frozen manual criteria with actual patch/log excerpts.
This review is performed by the primary agent without blinding or independent
human adjudication. It is not a general proof of correctness or a token/memory
benchmark. Pointer/capacity assertions test an explicit API requirement, not
overall allocation counts. Do not grade incidental wording or reward verbosity.

## Run and replay

Install Python development dependencies from the [maintainer guide](../../docs/maintaining.md#develop-and-verify) and Rust 1.93.1
with Clippy and rustfmt. Fetch immutable sources and skill baselines:

```sh
python3 scripts/fetch_sources.py
python3 scripts/rhwp_hard_eval.py fetch
python3 scripts/rhwp_hard_eval.py prepare --condition candidate --case H1 --output /tmp/chart-evaluation-h1
```

Populate the Cargo cache with `cargo +1.93.1 fetch --locked` from the packet's
`workspace/`, then give a fresh agent only the packet path and TASK.md. After it
finishes, capture and independently assess its patch:

```sh
python3 scripts/rhwp_hard_eval.py assess --packet /tmp/chart-evaluation-h1 --output /tmp/chart-evaluation-h1-results
```

Published results use the frozen run schedule and include failures. Once source
reviews are present, summarize and replay without invoking any model:

```sh
python3 scripts/rhwp_hard_eval.py summarize
python3 scripts/rhwp_hard_eval.py replay --output .cache/chart-replay --fetch-dependencies
```

Use `--run r01` to replay one recorded run. Choose new packet/result directories;
the scripts refuse to overwrite evidence. Replays compare recorded exit codes
even when an agent failed. Reproducing an observed failure is a successful replay,
not a successful implementation. A replay is not another model repetition.

## Interpretation limits

Report the three outcomes for each task/condition and the count out of six for
each condition. Also report failing executable gates and frozen source criteria.
Preserve all submitted patches, responses, unsuccessful checks, and any protocol
amendments. Agent-reported commands and reference reads are distinct from captured
independent assessment logs; complete inference traces are unavailable.

Two selected development tasks with three repetitions each are too few for broad
rankings or significance claims, especially with an unexposed backend and shared
host. Repetition reveals observed variability on these tasks; it does not turn
them into a representative held-out benchmark. A tie remains a tie. Differences
must be described by concrete failures rather than attributed causally to a
particular instruction without further evidence.

Original tooling and tests are MIT; prose is CC BY 3.0. Upstream source excerpts
retain [rhwp's MIT attribution](../../LICENSES/rhwp-MIT.txt). The installed skill
and release ZIP contain none of these evaluation sources or baseline skills.
