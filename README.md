# Google Rust Guidelines — Agent Skill

[한국어](README.ko.md)

An independent community skill for applying [Google's Rust Style Guide](https://google.github.io/styleguide/rustguide.html)
while writing, reviewing, or refactoring Rust. It preserves library/application
distinctions, platform scope, and exceptions instead of treating every preference
as a universal rule.

**Not affiliated with, maintained by, or endorsed by Google.**

The runtime is Markdown plus optional Codex UI metadata: no service, API key,
MCP server, Python, or network access is required to read the bundled guidance.
Rust tooling is needed only when the requested coding task requires it.

## Install

From a local checkout, with the [Skills CLI](https://github.com/vercel-labs/skills)
(currently requires Node.js 22.20+):

```sh
npx skills add . --skill google-rust-guidelines -a codex
```

After publishing this repository, replace OWNER/REPOSITORY with its actual
GitHub owner and name:

```sh
npx skills add OWNER/REPOSITORY --skill google-rust-guidelines
```

The CLI lets users select supported agents. Add `-g` for a user-wide installation;
omit it for the current project. Inspect discovery before installing with
`npx skills add . --list`. These are installer commands, not Rust dependencies.

Without Node, copy the **entire** `skills/google-rust-guidelines` directory into
your agent's skill directory. For Codex, common locations are
`~/.agents/skills/` (user) and `.agents/skills/` (project). For Claude Code,
use `~/.claude/skills/` or `.claude/skills/`. Keep `NOTICE.md`, `LICENSE`,
`references/`, and `agents/` with `SKILL.md`; copying the entrypoint alone
loses both guidance and attribution. Check for an existing installation before
replacing it.

The package follows the [Agent Skills specification](https://agentskills.io/specification).
Codex UI metadata lives in `agents/openai.yaml`; other hosts may ignore it.
Host-specific discovery, implicit activation, and execution behavior still need
verification in the host you use. This repository does not claim all-agent
runtime compatibility from format validation alone.

Verified locally: Skills CLI 1.7.4 on Node.js 24.15.0 discovers exactly one skill
with `add . --list`; the release ZIP extracts into a complete skill folder.
This discovery check does not install the skill or test every host's runtime.

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

## Publish on GitHub

1. Run the validation commands and inspect the package and evaluation report.
2. Create a public repository under the desired account or organization.
3. Push this repository and replace the OWNER/REPOSITORY installation example.
4. Tag a release, attach the generated ZIP, and state the tested host/model
   conditions and upstream version in the release notes.

No GitHub repository is created or published by the maintenance scripts.
The included GitHub Actions workflow runs structural checks, source verification,
fixture compilation, and tooling tests; agent evaluations are run separately.

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
