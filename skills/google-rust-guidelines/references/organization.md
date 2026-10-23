# Organization and tooling

## ORG-01 — Keep structure separate from implementation

Name a leaf module after its primary user-defined item, when it has one.
Non-leaf modules normally contain declarations and re-exports; a little core
glue is acceptable. Inline tests and cross-language binding submodules do not
stop a module from being a leaf for this purpose.

Small-crate and flat-directory prescriptions are Chromium policies, not a
reason to flatten ordinary Cargo projects. See the platform route in SKILL.md
when that codebase is relevant.
Sources: [names](https://google.github.io/styleguide/rustguide.html#userdefined-item),
[leaf modules](https://google.github.io/styleguide/rustguide.html#non-leaf-modules).

## ORG-02 — Avoid ambiguous imports while keeping exceptions

Avoid glob imports, with these allowed cases:
- `use super::*` in inline modules.
- Enum variant globs in enum methods or functions primarily dealing with that enum.
- `pub use submodule::*` from non-leaf modules.
- Merging C++ namespaces into a private, non-exported compatibility module.
- A third-party prelude when the reviewer accepts it.

Avoid defining preludes. Import items from one module per `use` statement
(the intended shape of rustfmt's `imports_granularity = "Module"`).
Prefer trait imports inside functions unless used widely throughout the file.
Sources: [globs](https://google.github.io/styleguide/rustguide.html#glob-imports),
[grouping](https://google.github.io/styleguide/rustguide.html#use-statement),
[trait imports](https://google.github.io/styleguide/rustguide.html#prefer-local-trait-imports).

## ORG-03 — Qualify functions, normally import types

Normally call external free functions through their module. Direct calls are
allowed for sufficiently disambiguated names, colliding module namespaces, and
Chromium's small single-purpose first-party crates. Explicit project policy
still governs adoption of this convention.

Normally import type/trait names and use them unqualified. Qualified names or
aliases are reasonable for ambiguity, large families of types, macros/generated
code, or unusually large import lists.
Sources: [functions](https://google.github.io/styleguide/rustguide.html#toplevel-functions),
[types](https://google.github.io/styleguide/rustguide.html#type-names).

## TOOL-01 — Use the repository formatter and supported options

Use the existing formatting entrypoint and configuration. Google's intended
format includes a 100-column width, lowercase hexadecimal literals, and formatted
macro matchers; write invisible characters as explicit escapes. Stable-only
projects may omit options unavailable on their toolchain. Inspect actual support
before adding `imports_granularity`, `hex_literal_case`, or
`format_macro_matchers`; availability is version-dependent.

Do not switch to nightly or overwrite a project's width during an ordinary
review. Suggest configuration changes only when requested or required by an
explicit adoption task, explaining any conflict with local policy.
Allow `#[rustfmt::skip]` for meaningful hand alignment or generated code,
not personal formatting preferences.
Sources: [formatter](https://google.github.io/styleguide/rustguide.html#formatting-other),
[skip](https://google.github.io/styleguide/rustguide.html#formatting-optout).

Clippy catches some patterns, not full guide compliance. Its lint scopes,
exceptions, and feature availability may differ from the prose. Do not convert
all preferences to unconditional `deny`/`forbid`, use lint suppression as a
substitute for reasoning, or disable exported-API protection without considering
compatibility. The validation workflow in SKILL.md is this skill's implementation
guidance, not a claim that Google mandates particular Cargo command flags.

## ORG-04 — Escalate abstraction only when it pays for itself

Prefer ordinary functions/types/traits/modules, then `macro_rules!`, then
other code generation, then procedural macros. Balance the benefit against
searchability, IDE support, local language dialects, and refactoring cost.
This does not ban useful macros already serving a clear purpose.
[Source](https://google.github.io/styleguide/rustguide.html#macros).
