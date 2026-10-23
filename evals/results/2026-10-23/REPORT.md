# Pilot comparison — 2026-10-23

The candidate and both existing skills passed all 15 development cases in this
pilot. The no-skill condition passed 14: it chose the correct behavior in the
remaining case but described an async restriction too broadly. **This does not
establish a general quality advantage for the candidate over existing skills.**

## Recorded results

| Condition | Cases passed | Criteria passed | Fatal errors | Entrypoint UTF-8 bytes |
| --- | ---: | ---: | ---: | ---: |
| Candidate, final package | 15/15 | 30/30 | 0 | 4,774 |
| StudentWeis | 15/15 | 30/30 | 0 | 7,809 |
| 0xMassi | 15/15 | 30/30 | 0 | 22,811 |
| No added skill | 14/15 | 29/30 | 0 | 0 |

The candidate's entrypoint is 38.9% smaller than StudentWeis's and 79.1% smaller
than 0xMassi's by UTF-8 bytes. This compares only SKILL.md. It excludes loaded
references, fixtures, prompts, and reasoning, and is **not measured token savings**.
The no-skill row means no added skill entrypoint, not zero total model context.

No token, time, cost, repeated-run variance, or statistical-significance
measurement was available.

## Versions and method

- Google source:
  [2ac1584cd3c9854760f02418ec24687ec1698fb8](https://github.com/google/styleguide/commit/2ac1584cd3c9854760f02418ec24687ec1698fb8).
- StudentWeis:
  [07b5b14c68d8bfc978575d347de59ca715e0deab](https://github.com/StudentWeis/google-rust-style-guide/commit/07b5b14c68d8bfc978575d347de59ca715e0deab).
- 0xMassi:
  [5d5eeca939d723f76317fc1e41276ed3bc1548d9](https://github.com/0xMassi/google-rust-style-skill/commit/5d5eeca939d723f76317fc1e41276ed3bc1548d9).
- Candidate: exact runtime file hashes in [its manifest](candidate.manifest.json).
  The delivered runtime files were checked against that evaluated manifest.

Each condition used a fresh Codex collaboration subagent with the inherited
host model and the same review protocol. The backend model identifier, sampling
settings, and token metering were not exposed. This is therefore a recorded,
inspectable pilot, not an exactly reproducible model benchmark.

Each agent answered all 15 prompts in **one batch context**. Cases did not have
independent sessions, and earlier questions can influence later answers. Agents
received input fixtures and the relevant skill packet, but not the separate
rubric, other conditions, or web access. The prompts deliberately provide fairly
clear task constraints; the high no-skill score indicates limited discrimination.

A fresh grading agent received the frozen rubric and condition aliases, then
the primary agent inspected the grades and notable judgments. This is
agent-based grading without human adjudication. Some response text can reveal
the kind of skill used, so aliases do not guarantee complete blinding.
The summarizer checks that every evidence quote occurs in its raw response;
it does not independently judge semantic correctness.

The frozen [prompts](cases.json), [rubric](rubric.json), and
[experiment metadata](experiment.json) are archived here. The fixture content
is in the repository's evals/fixtures directory and hashed in each manifest.
references_read is agent-reported; no complete execution traces were captured.

## Case outcomes

| Case | Main distinction | Candidate | StudentWeis | 0xMassi | None |
| --- | --- | --- | --- | --- | --- |
| 01 | Ordinary Cargo async vs Chromium restriction | Pass | Pass | Pass | Scope precision fails |
| 02 | Necessary Arc sharing vs deep copying | Pass | Pass | Pass | Pass |
| 03 | Application slice/Vec API vs generic overdesign | Pass | Pass | Pass | Pass |
| 04 | Borrowed library string input | Pass | Pass | Pass | Pass |
| 05 | Recoverable I/O vs expect substitution | Pass | Pass | Pass | Pass |
| 06 | Invariant panic vs unnecessary Result | Pass | Pass | Pass | Pass |
| 07 | External options construction and Default | Pass | Pass | Pass | Pass |
| 08 | Fixed enum vs evolving cross-team enum | Pass | Pass | Pass | Pass |
| 09 | Production glob vs allowed local globs | Pass | Pass | Pass | Pass |
| 10 | Stable formatter and existing width | Pass | Pass | Pass | Pass |
| 11 | Empty-input unsafe defect | Pass | Pass | Pass | Pass |
| 12 | Trait purpose vs method grouping | Pass | Pass | Pass | Pass |
| 13 | Actual Chromium concurrency policies | Pass | Pass | Pass | Pass |
| 14 | Explicit repository policy conflict | Pass | Pass | Pass | Pass |
| 15 | Python-only task with a Rust string key | Pass | Pass | Pass | Pass |

In none/01, the response correctly preserved async but said “Google-internal
restrictions” without the required Chromium-only qualification. The first
criterion explicitly required that distinction when discussing the restriction.
This was a precision failure, not a recommendation to break the application.
No condition incurred a rubric-defined fatal error.

## Raw evidence

| Condition | Responses | Reviewed criteria | Input manifest |
| --- | --- | --- | --- |
| Candidate | [responses](candidate.responses.json) | [grades](candidate.grades.json) | [manifest](candidate.manifest.json) |
| StudentWeis | [responses](studentweis.responses.json) | [grades](studentweis.grades.json) | [manifest](studentweis.manifest.json) |
| 0xMassi | [responses](0xmassi.responses.json) | [grades](0xmassi.grades.json) | [manifest](0xmassi.manifest.json) |
| None | [responses](none.responses.json) | [grades](none.grades.json) | [manifest](none.manifest.json) |

A candidate preflight is also retained:
[responses](preflight/responses.json), [manifest](preflight/manifest.json).
Before the final run, a broken source anchor was corrected and links to the
public Rust fallback guides were added. The final candidate was evaluated in a
new context; these are not two independent replications of an identical version.
No earlier run was discarded to improve the reported score.

## What was separately validated

The repository's structural checks found 25 rule groups and 67 distinct upstream
anchors. Fourteen Rust input fixtures compiled with rustc 1.94.1; deliberately
unsafe examples were not executed. Six tooling tests passed. The local bundled
skill-creator validator accepted the skill.

Fresh downloads of the pinned Google source and baseline files matched recorded
hashes. Skills CLI 1.7.4 on Node.js 24.15.0 discovered exactly one skill with
add . --list. The ZIP's extracted runtime files matched their source bytes and
included attribution and license files. No host-wide skill installation was
performed for this discovery check.

These checks do not mean the review agents compiled their proposed fixes:
the pilot is static review, not a patch-generation benchmark. Broad configuration
migration, full-project refactoring, and all platform-specific paths are untested.
The negative case measures applicability reasoning after packet presentation,
not a host's real automatic skill-discovery behavior.

## Next evidence needed

Add held-out tasks with less explicit context, cross-file APIs, real downstream
consumers, and conflicting feature configurations. Use fresh sessions for every
case and condition, pin an exposed model version, repeat runs, capture actual
token/latency traces, and compile/test resulting patches where appropriate.
Include false positives and compatibility regressions in grading. Keep the
current 15-case set as a development regression suite rather than advertising
it as evidence that this skill is generally better than existing alternatives.
