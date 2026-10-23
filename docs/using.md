# Installation and usage

[Back to the README](../README.md)

Choose your setup: [Codex](#codex) · [Claude Code](#claude-code) ·
[Gemini CLI](#gemini-cli) · [Claude chat](#claude-web-and-desktop-chat) ·
[Other agents](#other-agents).

For more options: [Pinned release](#install-a-fixed-release) ·
[ZIP / manual installation](#zip-and-manual-installation) ·
[Troubleshooting](#troubleshooting) · [Verification status](#verification-status).

## Before you install

The commands below use [Skills CLI 1.7.4](https://github.com/vercel-labs/skills/tree/v1.7.4)
and require Node.js 22.20+ and Git. Run them from your Rust project's root.
They install from this repository's default branch into the current project;
add `-g` for a user-wide installation. You can choose multiple agents interactively
by omitting `-a`. See the [installer reference](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/commands.md#skills-add).

The installed skill is a folder of instructions and references. It needs no
separate API key, Python environment, or MCP server. Your coding agent still
needs its own normal setup, and Rust checks require the project's toolchain.

## Codex

Install for Codex:

```sh
npx skills@1.7.4 add postmelee/google-rust-skill \
  --skill google-rust-guidelines -a codex
```

In Codex CLI or the IDE extension, use `/skills` or type `$` to find the skill.
Then send:

```text
Use $google-rust-guidelines to review this Rust diff.
Focus on ownership, error handling, and compatibility with existing callers.
```

Local skills use `.agents/skills/` in a project or `~/.agents/skills/` for your
user. If a new skill does not appear, restart Codex. In the ChatGPT desktop app,
use its skill picker to select the installed skill; the CLI/IDE `$` example above
is specific to those interfaces. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Claude Code

Install for Claude Code:

```sh
npx skills@1.7.4 add postmelee/google-rust-skill \
  --skill google-rust-guidelines -a claude-code
```

In a local Claude Code session in your project, send:

```text
/google-rust-guidelines Review this Rust diff for ownership, errors, and API compatibility.
```

Claude Code reads project skills from `.claude/skills/` and personal skills from
`~/.claude/skills/`. The installer may link that folder to a shared copy in
`.agents/skills/`; keep the target with the link. The skill can also be selected
automatically when your request matches its description.
See [Claude Code's skill documentation](https://code.claude.com/docs/en/skills).

For Claude web, Desktop chat, or Cowork, use the account upload flow below.

## Gemini CLI

Install for Gemini CLI:

```sh
npx skills@1.7.4 add postmelee/google-rust-skill \
  --skill google-rust-guidelines -a gemini-cli
```

Inside Gemini CLI, refresh discovery and check the list:

```text
/skills reload
/skills list
```

Then ask:

```text
Use the google-rust-guidelines skill to review this Rust diff.
Check ownership, recoverable errors, and compatibility with existing callers.
```

Gemini CLI activates matching skills through its skill tool and may show a consent
prompt. `/skills` manages discovery; use the named natural-language request above
to ask for this skill. See [Gemini CLI's skill overview](https://geminicli.com/docs/cli/skills/).

As an alternative to the shared installer, Gemini CLI has a native installer:

```sh
gemini skills install https://github.com/postmelee/google-rust-skill.git \
  --path skills/google-rust-guidelines --scope workspace
```

Use one installation method. The shared installer uses `.agents/skills/` for the
project; Gemini also recognizes `.gemini/skills/`. Its native installer defaults
to user scope unless you specify `--scope workspace`.
See [Gemini CLI skill management](https://geminicli.com/docs/cli/using-agent-skills/).

## Claude web and Desktop chat

1. Download [google-rust-guidelines.zip](https://github.com/postmelee/google-rust-skill/releases/download/v0.1.0/google-rust-guidelines.zip)
   from the [v0.1.0 release](https://github.com/postmelee/google-rust-skill/releases/tag/v0.1.0).
2. Open **Customize → Skills**, choose **+ → Create skill → Upload a skill**,
   and upload that ZIP. Enable the uploaded skill.
3. Attach the Rust code or diff and ask: “Use google-rust-guidelines to review this
   code for ownership, error handling, and API compatibility.”

Claude requires its code execution/file creation capability for skills; account
or organization settings can control availability. See [Anthropic's upload and
usage instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
The release ZIP contains the named skill folder and its supporting files, following
[Anthropic's packaging guidance](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

A chat review can use the code you supply. To edit a local repository and run its
Cargo checks, use an agent with access to that repository and toolchain. See the
verification table below for what has actually been tested.

## Other agents

Run the README's interactive install command and choose your agent. Skills CLI
also lists targets such as Cursor, GitHub Copilot, and OpenCode in its
[supported-agent reference](https://github.com/vercel-labs/skills/blob/v1.7.4/docs/agents.md).
Use that host's skill picker or ask it to use `google-rust-guidelines`; invocation
syntax and tool access depend on the host. The Codex `$` syntax and Claude Code
slash command are examples for those specific products.

For a chat tool without a skill loader, you can supply `SKILL.md` and the relevant
reference files as context and ask it to apply them to your code. That is a manual
reference workflow; it does not install a discoverable skill or provide a compiler.

## Install a fixed release

To install the published v0.1.0 contents instead of the default branch:

```sh
npx skills@1.7.4 add \
  https://github.com/postmelee/google-rust-skill/tree/v0.1.0 \
  --skill google-rust-guidelines
```

Choose your agent when prompted, or append `-a codex`, `-a claude-code`, or
`-a gemini-cli`. Add `-g` if you want a user-wide installation.

## ZIP and manual installation

Download the release [ZIP](https://github.com/postmelee/google-rust-skill/releases/download/v0.1.0/google-rust-guidelines.zip)
and [SHA256SUMS](https://github.com/postmelee/google-rust-skill/releases/download/v0.1.0/SHA256SUMS)
into the same directory. Verify before extracting:

```sh
# macOS
shasum -a 256 -c SHA256SUMS

# Linux
sha256sum -c SHA256SUMS
```

Extract and copy the **entire `google-rust-guidelines` folder** to one location:

| Host | Current project | All your projects |
| --- | --- | --- |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |

These are the [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills), and
[Gemini CLI](https://geminicli.com/docs/cli/using-agent-skills/) discovery locations.
For example, a manual Claude Code install should contain
`.claude/skills/google-rust-guidelines/SKILL.md`.

Keep `references/`, `agents/`, `NOTICE.md`, and `LICENSE` beside `SKILL.md`.
You can also copy `skills/google-rust-guidelines/` from a repository checkout.
Check for an existing installation before replacing it. Codex-specific UI
metadata in `agents/openai.yaml` can stay in the folder for other hosts.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Installer fails | Check Node.js 22.20+, Git, and access to GitHub; use the ZIP method if preferred. |
| Skill is missing | Run `npx skills@1.7.4 list` in the project (`-g` for user-wide installs), then check the host's skill list and the manual paths above. |
| Files are installed but unavailable | Start the agent in the correct project. Restart Codex if needed; in Gemini CLI run `/skills reload`. Check that the host has enabled the skill. |
| Agent does not use it | Name the skill explicitly using your host's example above and provide the actual code or diff. |
| Conflicting copies | Inspect project and user locations; keep the intended version and avoid duplicate installs. |
| Cargo cannot run | Supply a workspace with the project's Rust toolchain and dependencies. A skill installation does not install Rust. |

## Verification status

Documentation checked on **2026-10-23**. Installation and model behavior are
separate checks:

| Surface | Evidence |
| --- | --- |
| Skills CLI → Codex, Claude Code, Gemini CLI | Version 1.7.4 on Node.js 24.15.0 installed this public repository in three separate temporary projects. All nine installed files matched the source. |
| Codex bundled installer and release ZIP | The v0.1.0 release checks verified installed/downloaded file integrity. |
| Claude Code and Gemini CLI invocation; Gemini native installer; Claude chat upload | Instructions checked against the official pages linked above. These host flows were not executed in this environment. |
| Rust behavior | Separate [evaluation records](evaluation.md) cover an inherited agent host; they are not cross-host model benchmarks or proof of automatic activation. |

For updates, review the release and its recorded upstream version before replacing
your installation. For contributing or publishing a release, use the
[maintainer guide](maintaining.md).
