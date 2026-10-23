# Google Rust Guidelines — Agent Skill

[![Validate skill](https://github.com/postmelee/google-rust-skill/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/postmelee/google-rust-skill/actions/workflows/validate.yml)

An independent community skill for applying [Google's Rust Style Guide](https://google.github.io/styleguide/rustguide.html)
while writing, reviewing, or refactoring Rust. It preserves library/application
distinctions, platform scope, and exceptions instead of treating every preference
as a universal rule.

**Not affiliated with, maintained by, or endorsed by Google.**

The runtime is Markdown plus optional Codex UI metadata: no service, API key,
MCP server, Python, or network access is required to read the bundled guidance.
Rust tooling is needed only when the requested coding task requires it.

## Install

Install from GitHub with the [Skills CLI](https://github.com/vercel-labs/skills)
and Node.js 22.20+. Version 1.7.4 is the installer version tested for this release:

```sh
npx skills@1.7.4 add postmelee/google-rust-skill --skill google-rust-guidelines -a codex
```

This installs from the default branch. To select the published v0.1.0 contents:

```sh
npx skills@1.7.4 add https://github.com/postmelee/google-rust-skill/tree/v0.1.0 --skill google-rust-guidelines -a codex
```

Omit `-a codex` to select another supported agent. Add `-g` for a user-wide
installation; omit it for the current project. Inspect discovery before installing
with `npx skills@1.7.4 add postmelee/google-rust-skill --list`.
From a local checkout, replace the repository argument with `.`.
These are installer commands, not Rust dependencies.

Without Node, download [google-rust-guidelines.zip](https://github.com/postmelee/google-rust-skill/releases/download/v0.1.0/google-rust-guidelines.zip)
and [SHA256SUMS](https://github.com/postmelee/google-rust-skill/releases/download/v0.1.0/SHA256SUMS)
from the [v0.1.0 release](https://github.com/postmelee/google-rust-skill/releases/tag/v0.1.0).
Verify the download with `shasum -a 256 -c SHA256SUMS` on macOS or
`sha256sum -c SHA256SUMS` on Linux, then extract it. Copy the **entire**
`google-rust-guidelines` folder into your agent's skill directory. You can also
copy `skills/google-rust-guidelines` from a checkout. For Codex, common locations are
`~/.agents/skills/` (user) and `.agents/skills/` (project). For Claude Code,
use `~/.claude/skills/` or `.claude/skills/`. Keep `NOTICE.md`, `LICENSE`,
`references/`, and `agents/` with `SKILL.md`; copying the entrypoint alone
loses both guidance and attribution. Check for an existing installation before
replacing it. See the [official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills)
for host-specific setup.

The package follows the [Agent Skills specification](https://agentskills.io/specification).
Codex UI metadata lives in `agents/openai.yaml`; other hosts may ignore it.
Host-specific discovery, implicit activation, and execution behavior still need
verification in the host you use. This repository does not claim all-agent
runtime compatibility from format validation alone.

Verified for this release: Skills CLI 1.7.4 on Node.js 24.15.0 installed from the
public GitHub repository into an isolated Codex project and listed exactly one
installed skill. Codex's bundled installer also installed from the published
commit into a temporary directory. All nine installed files and the ZIP contents
matched the source bytes, including attribution and licenses. These checks verify
installation and file integrity; they do not test every host's activation behavior.

## Use

In Codex:

```text
Use $google-rust-guidelines to review this Rust diff.
Keep the repository's existing API contracts and report actionable findings.
```

Other examples:

- “Apply Google's Rust guide to this new library API; explain relevant exceptions.”
- “Review this Cargo application's error handling without changing its Tokio runtime.”
- “Check these public options types without breaking downstream struct literals.”

The description supports automatic selection when the user requests Google
style or the project adopts it. The skill should not impose Google policy on
unrelated Rust work. It preserves explicit user requirements and repository
policy and explains conflicts.

## Design

- A small entrypoint establishes scope, routes the task, and defines verification.
- Five focused references group decisions by API design, ownership/errors,
  organization, safety/documentation, and platform-specific rules.
- Twenty-five rule groups carry source links. [The rule map](provenance/rule-map.json)
  connects them to upstream anchors.
- Conditions and exceptions live beside the rule they qualify.
- Existing formatters and linters handle mechanical checks; semantic review
  covers what those tools cannot establish.

This is a paraphrased, task-oriented adaptation, not a complete mirrored manual,
a replacement for rustc/Clippy, or proof that unsafe code is sound.
Uncovered edge cases route to the relevant authoritative source.

## Evaluation and current evidence

The repository contains **15 development cases**, fixtures, and a separate
answer rubric. Cases include correct behavior that must remain unchanged,
actual violations, platform scope, conflicting local policy, and a non-Rust task.

See [the evaluation protocol](evals/README.md) and
[the pilot comparison](evals/results/2026-10-23/REPORT.md) for recorded responses,
grading, source versions, and limitations. The pilot compares this skill,
two existing community skills, and no added skill.

These cases are not a held-out benchmark. A small, single-model pilot with
batch sessions cannot establish a general accuracy improvement or token savings.
The report distinguishes measured file size from actual model context usage.

A separate [implementation evaluation](evals/integration/README.md) uses three
tasks on the complete `rhwp-contracts` crate from a pinned public rhwp commit.
Agents modify source and add tests; captured patches are independently rebuilt
and checked against existing tests and external consumer tests. This component
suite does not validate the full rhwp engine, WASM, or rendering pipeline.
The [recorded comparison](evals/results/rhwp-2026-10-23/REPORT.md) passed all three
tasks in each of the four conditions (12 runs): a tie, with no measured skill
advantage. Patches, logs, frozen criteria, and a replay command are included.

## Develop and verify

Use Python 3.10+ and Rust 1.94.1 for the recorded fixture checks:

```sh
python3 -m venv .cache/dev-env
.cache/dev-env/bin/python -m pip install -r requirements-dev.txt
.cache/dev-env/bin/python scripts/fetch_sources.py --upstream-only
.cache/dev-env/bin/python scripts/validate.py --check-sources --check-rust
.cache/dev-env/bin/python -m unittest discover -s tests -v
.cache/dev-env/bin/python scripts/package_skill.py
```

The source fetch is a maintenance operation and needs network access on its first
run. It verifies immutable commits and content hashes; cached data is verified
without fetching again. Development caches and virtual environments are ignored
by Git. Runtime skill use does not execute these scripts.

Validation checks metadata, packaged attribution, local links, source anchors,
rule mapping, and case/rubric integrity. It compiles 14 Rust inputs **without
executing deliberately defective unsafe examples**. These checks do not grade
agent behavior. The ZIP at `.cache/dist/google-rust-guidelines.zip` contains
only the self-contained runtime skill.

## Upstream and maintenance

This release uses Google commit
[`2ac1584`](https://github.com/google/styleguide/commit/2ac1584cd3c9854760f02418ec24687ec1698fb8)
(2026-10-21), retrieved 2026-10-23. [Provenance](provenance/upstream.json)
records the full commit, file blob, origin, and licenses.

To update, inspect the upstream diff, revise affected rules and their mapping,
update attribution and pins, and rerun relevant behavior cases. Retain old results
with their manifests. Do not silently refresh installed references during a
normal code task or claim a pinned release is always current.

## Release maintenance

1. Run the validation commands and inspect the package and evaluation report.
2. Push changes and wait for the GitHub Actions workflow to pass on that commit.
3. Verify installation from GitHub in a fresh temporary project and compare all
   installed files with the runtime package.
4. Tag the verified commit, attach the generated ZIP and its SHA-256 checksum,
   and state the tested host/model conditions and upstream version in the release notes.
5. Verify installation from the tag and download the published assets to check
   their bytes. Update the versioned installation links for the next release.

No GitHub repository is created or published by the maintenance scripts.
The included GitHub Actions workflow runs structural checks, source verification,
fixture compilation, tooling tests, archived-result integrity checks, packaging,
and a separate replay of the 12 archived rhwp patches. Fresh model evaluations
are run separately.

## License and acknowledgements

Adapted guide prose, original documentation, and skill instructions:
**CC BY 3.0**, under [LICENSE](LICENSE). Attribution and changes are recorded
in the installed skill's [NOTICE](skills/google-rust-guidelines/NOTICE.md).

Original Python tooling, Rust/Python fixtures, and CI configuration:
**MIT**, under [LICENSES/MIT.txt](LICENSES/MIT.txt).

Google licenses its original example code separately under Apache 2.0. No
upstream example-code bundle is included in this runtime package; any future
copied example must preserve its applicable license and notices.

Existing skills are credited as comparison baselines, not claimed as our work:
[StudentWeis](https://github.com/StudentWeis/google-rust-style-guide) and
[0xMassi](https://github.com/0xMassi/google-rust-style-skill).
Their pinned sources are fetched only into ignored development caches and are
not redistributed in the runtime ZIP.

The implementation evaluation uses [edwardkim/rhwp](https://github.com/edwardkim/rhwp).
Upstream source excerpts in recorded patches retain its MIT license and attribution
under [LICENSES/rhwp-MIT.txt](LICENSES/rhwp-MIT.txt). The evaluated source is fetched
into an ignored cache and is not part of the installed skill or release ZIP.
