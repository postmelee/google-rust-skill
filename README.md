# Google Rust Guidelines — Agent Skill

[![Validate skill](https://github.com/postmelee/google-rust-skill/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/postmelee/google-rust-skill/actions/workflows/validate.yml)

Help your coding agent write and review Rust using
[Google's Rust Style Guide](https://google.github.io/styleguide/rustguide.html).
Use it with **Codex, Claude Code, Gemini CLI**, or another agent that supports skills.

- Review ownership, cloning, errors, and public API changes.
- Refactor code while preserving existing callers and project conventions.
- Apply relevant rules with their exceptions, including library vs. application differences.

This is an independent community adaptation, not affiliated with or endorsed by Google.

## Quick start

Run this in the Rust project where you want to use the skill, then select your
coding agent. Requires Node.js 22.20+; the installer is pinned to the tested version.

```sh
npx skills@1.7.4 add postmelee/google-rust-skill \
  --skill google-rust-guidelines
```

This installs into the current project. Add `-g` to use it across your projects.
For a specific agent, a fixed release, or installation without Node, see the
[installation guide](docs/using.md).

## Use it in your agent

Open your project in the agent after installing, then start with:

| Agent | Invoke the skill | Setup and first prompt |
| --- | --- | --- |
| Codex CLI / IDE | `$google-rust-guidelines` | [Codex guide](docs/using.md#codex) |
| Claude Code | `/google-rust-guidelines` | [Claude Code guide](docs/using.md#claude-code) |
| Gemini CLI | Ask it to use `google-rust-guidelines` | [Gemini CLI guide](docs/using.md#gemini-cli) |
| Claude web / Desktop chat | Upload the release ZIP and enable the skill | [Claude chat guide](docs/using.md#claude-web-and-desktop-chat) |

Try a review:

```text
Use the google-rust-guidelines skill to review this Rust diff.
Focus on ownership, error handling, and public API compatibility.
Report actionable findings and explain any relevant exceptions.
```

Or an implementation:

```text
Use the google-rust-guidelines skill to implement this change.
Preserve existing callers, follow this repository's conventions,
and run the relevant Rust checks. Report what you verified.
```

Give the agent the diff, files, or concrete task you want it to work on. The skill
supplies guidance; compilation and tests use the tools available in your agent's
workspace. It is most useful when you explicitly want Google Rust style or your
project adopts it.

## Learn more

- [Installation and usage](docs/using.md): agent-specific commands, ZIP installation,
  other agents, and troubleshooting.
- [Evaluation results](docs/evaluation.md): recorded comparisons, runnable patches,
  and limits. Current evidence does **not** establish a general skill advantage.
- [Contributor guide](docs/maintaining.md): design, source updates, validation,
  licensing details, and releases.

The bundled rules are pinned to a documented upstream version. Read the
[attribution and source notice](skills/google-rust-guidelines/NOTICE.md).
Prose and skill instructions are [CC BY 3.0](LICENSE); original tooling, tests,
and CI are [MIT](LICENSES/MIT.txt).
