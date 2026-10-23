---
name: google-rust-guidelines
description: Apply Google's Rust Style Guide to Rust implementation, review, and refactoring when the user requests Google Rust style or the project adopts it. Preserve library/application distinctions, platform scope, and exceptions. Not for unrelated languages or imposing Google policy on every Rust task.
license: CC-BY-3.0
metadata:
  version: "0.1.0"
  upstream-commit: "2ac1584cd3c9854760f02418ec24687ec1698fb8"
---

# Google Rust guidelines

Use the adapted rules below to make context-sensitive decisions. This community
skill is not maintained or endorsed by Google. Attribution: [NOTICE.md](NOTICE.md).
The bundled guidance is pinned, not a claim about today's upstream.

## Establish applicability

- Read relevant repository instructions, surrounding code, formatter/lint config,
  supported features, and toolchain/MSRV. Explicit user requirements and project
  policy govern this task; explain conflicts instead of replacing local policy.
- Identify the actual API audience: reusable code consumed by other projects,
  or code serving one application. A `lib.rs` or `pub` keyword alone does not
  establish a cross-team API. Within an adopted Google policy, library API rules
  are binding; application API rules are strong recommendations, with simplicity
  and immediate requirements taking priority over hypothetical reuse.
- Apply platform rules only with evidence that the target belongs to that
  codebase. Ordinary Cargo code keeps its layout, runtime, and test framework.
- Stay within the requested change or review. A review is not permission to
  rewrite configuration, break existing callers, or migrate a runtime.

## Load only relevant guidance

Paths are relative to this skill directory. Read the relevant file and its
exceptions before using a rule; do not load the whole directory by default.

| Decision in the task | Read |
| --- | --- |
| Signatures, iterators, data types, traits, constructors, public API evolution | [api-design.md](references/api-design.md) |
| Ownership, cloning, errors, panics, mutex poisoning, implementation clarity | [ownership-errors.md](references/ownership-errors.md) |
| Modules, imports, formatter configuration, macros | [organization.md](references/organization.md) |
| Unsafe, documentation, names, unstable features | [safety-docs.md](references/safety-docs.md) |
| Chromium, Android, Fuchsia policies or platform-specific exceptions | [platform-specific.md](references/platform-specific.md) |

For a broad review, cover relevant topics in turn. For a narrow change, inspect
only the affected decisions. Rule IDs support traceability, not severity.

## Guard against misleading shortcuts

- A preference is not an unconditional ban: shared ownership and deep copies
  have exceptions; library generic APIs need not become application APIs.
- Determine the error contract before suggesting `expect`. An expected I/O
  failure needs recovery/propagation, not a better panic message.
- Check downstream construction and matching before recommending
  `#[non_exhaustive]`. Options structs supporting struct update are an exception.
- Unsafe comments do not prove soundness. Inspect the actual safety contract.
- Treat compiler/formatter/linter coverage as partial. Check option availability
  on the pinned toolchain; do not add nightly or indiscriminate lint profiles.

## Apply and verify

For implementation, make the smallest change that satisfies the requested
behavior and applicable guidance. Preserve compatibility unless a change was
requested. Use existing validation entrypoints. In ordinary Cargo projects,
select appropriate `cargo fmt --check`, `cargo clippy`, and `cargo test`
commands with supported packages, targets, and feature combinations; do not
assume `--all-features` is valid. Run checks only relevant to the work.

For review, report an actionable finding with location, rule/source, why it
applies, and a concrete correction. Distinguish correctness defects, adopted
style requirements, and optional improvements. Check exceptions before reporting
a violation. If there is no actionable issue in scope, say so.

Report checks actually run and remaining uncertainty. For uncovered edge cases
or requests for current guidance, consult the relevant
[upstream section](https://google.github.io/styleguide/rustguide.html), identify
any version difference, and do not silently modify this installed skill.

For matters not covered here, use the public
[Rust Style Guide](https://doc.rust-lang.org/style-guide/) and
[Rust API Guidelines](https://rust-lang.github.io/api-guidelines/).
Within an adopted Google policy, its specific rules take precedence over those
general guides. [Source](https://google.github.io/styleguide/rustguide.html#public-rules).
