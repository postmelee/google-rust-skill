# Safety, documentation, and names

## SAFE-01 — Justify unsafe behavior, not just its syntax

Prefer an equivalent safe implementation. If unsafe is needed, isolate it behind
a safe abstraction where possible and away from business logic, ideally in a
small crate with few dependencies. Explain correctness in `SAFETY:` comments.
Provide a technical justification for the block, file, or target: why safe code
cannot serve the need, and benchmarks if performance is the reason.

Inspect relevant validity, lifetime, aliasing, initialization, and concurrency
contracts before claiming soundness. A comment or passing test does not fix
undefined behavior. If information is missing, state the missing proof obligation.
The contract-inspection checklist is operational guidance for this skill.
[Source](https://google.github.io/styleguide/rustguide.html#unsafe).

## SAFE-02 — Respect stable policy and platform exceptions

The guide prohibits unstable language features by default. Platform exceptions
require the codebase's policy: Android embedded necessities, Chromium's approved
feature list, and Fuchsia's own guidance. Do not assume such approval applies
elsewhere or install a new toolchain as a style fix.
[Source](https://google.github.io/styleguide/rustguide.html#unstable-features).

## DOC-01 — Document contracts and information the code omits

Document public APIs, panic conditions from malformed input, and unsafe-function
or unsafe-trait invariants. Include enough examples across the crate to show how
it works; every function need not repeat one. Use normal sentences and Markdown.

Omit comments that merely restate names; self-explanatory enum variants may go
undocumented. An appropriate local lint exception may be better than filler.
Do not explain elementary Rust concepts to users already reading this API.

Use `///` for items, `//!` for module/crate docs, and `//` for implementation
notes and internal TODOs. Both kinds can accompany one item. Prefer directly
readable documentation over macro-generated comments.
[Source](https://google.github.io/styleguide/rustguide.html#writing-doc).

## NAME-01 — Make names reflect semantics without overexplaining

Use standard-library conversion conventions (`as_`, `to_`, `into_`) with
the corresponding receiver/ownership behavior. Constructors use `new`,
`new_with_foo` for alternatives, and `try_new` when returning `Result`.
Value conversions use `from_foo` with an appropriate `From` implementation.
Extension traits end in `Ext`.
Sources: [methods](https://google.github.io/styleguide/rustguide.html#naming-methods),
[constructors](https://google.github.io/styleguide/rustguide.html#naming-initialization-functions),
[extensions](https://google.github.io/styleguide/rustguide.html#naming-extension-traits).

Use descriptive lifetime names, especially on types. Anonymous lifetimes are
fine; one or two short local lifetimes linking method inputs/outputs or in
higher-ranked bounds are fine. Extremely generic type abstractions are another
exception. Generic parameter names should hint at their role or main bound;
`T`/`U` are fine for broadly unconstrained APIs.

Avoid unfamiliar abbreviations and dropping letters from words. Common terms
recognizable outside the project are acceptable, with reviewer judgment.
Sources: [lifetimes](https://google.github.io/styleguide/rustguide.html#lifetimes),
[generics](https://google.github.io/styleguide/rustguide.html#generic-parameters),
[abbreviations](https://google.github.io/styleguide/rustguide.html#avoid-abbreviations).
