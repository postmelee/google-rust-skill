# Ownership, errors, and implementation

## OWN-01 — Prefer a clear owner before shared ownership

Prefer unique ownership and borrows. Keep `Rc`/`Arc` when the alternative would
be unreasonably complex to write, understand, or maintain. Explain the actual
shared lifetime/ownership requirement during review; a blanket prohibition
misrepresents the guide. Cloning a reference-counted pointer is expected use
and is not a deep copy.
[Source](https://google.github.io/styleguide/rustguide.html#avoid-rc-arc).

Avoid deep cloning merely to bypass a natural borrowing design. A needed
independent copy is valid, and cloning can be pragmatic when borrowing becomes
excessively complicated. Consider actual performance requirements rather than
assuming all clones are unacceptable.
[Source](https://google.github.io/styleguide/rustguide.html#prefer-borrows).

## ERR-01 — Classify the failure before changing its spelling

Use `Option` when failure is anticipated and its cause is obvious, so more detail
does not help. Use `Result` for recoverable errors whose cause the caller needs,
especially external I/O failures. Reserve panic for bugs or violated invariants.
Project policy may require `Result` even for invariants; developer-facing
binaries and tests have additional latitude for panics.
[Source](https://google.github.io/styleguide/rustguide.html#reporting-errors).

For example, an unreadable user configuration should propagate an I/O error;
changing `read_to_string(path).unwrap()` to `expect("config")` still leaves the
recoverable failure as a panic. If a necessary invariant panic cannot be expressed
in types/control flow, prefer `expect` with its reason. Prefer matching,
`if let`, or `let else` over checking then unwrapping.
Sources: [invariants](https://google.github.io/styleguide/rustguide.html#expect-over-unwrap),
[matching](https://google.github.io/styleguide/rustguide.html#dont-check-then-unwrap).

## ERR-02 — Respect poisoning and panic strategy

Do not access the contents of a poisoned mutex under this policy.
First-party `catch_unwind` is prohibited except as defense in depth at critical
boundaries in a program already doing what it can to avoid panics. No correctness
property may rely on that recovery. The exception needs a possible
`panic=unwind` configuration; it does not apply to Chromium, Android, or Fuchsia.
Do not invent a panic strategy or change one during a style review.
Sources: [poison](https://google.github.io/styleguide/rustguide.html#poison),
[recovery](https://google.github.io/styleguide/rustguide.html#catch-unwind).

## IMPL-01 — Make inference and control flow readable

Add type annotations when readers cannot readily infer results, especially
`into`, `parse`, or complex chains. Prefer annotations on bindings; use a
turbofish when needed and inference markers when appropriate.

When matching a foreign non-exhaustive enum, normally name all known variants
and group intentionally ignored ones with the wildcard. If only particular
variants matter, `if let`/`let else` may be clearer; a selective `match` is
also allowed when it is clearer. Check the project's toolchain before proposing
a lint mentioned by the guide.
Sources: [inference](https://google.github.io/styleguide/rustguide.html#type-inference),
[exhaustiveness](https://google.github.io/styleguide/rustguide.html#non-exhaustive-enum-matching).

## IMPL-02 — Prefer useful diagnostics and straightforward iteration

Assertion messages should add invariant rationale, offending values, or distinguish
caller misuse from an implementation bug. Do not merely restate the condition.

Prefer direct loops over long, branching chains or external mutation. Short
combinators that clearly express the operation remain appropriate. Bind a chain
to a descriptive variable before consuming it in a `for` header. Usually prefer
`for` over `for_each`, allowing a justified exception.
Sources: [assertions](https://google.github.io/styleguide/rustguide.html#assertion-context),
[chains](https://google.github.io/styleguide/rustguide.html#combinator-chains).

Use `format!`/`write!` for more-than-two-string concatenation or substitution
into a literal. Do not arrange executable initialization before `main`.
Sources: [strings](https://google.github.io/styleguide/rustguide.html#prefer-format-or-write),
[initialization](https://google.github.io/styleguide/rustguide.html#global-initialization).
