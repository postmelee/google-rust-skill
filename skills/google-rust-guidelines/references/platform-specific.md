# Platform-specific policy

Apply a section only when the repository/task establishes that platform.
A dependency on a Google crate does not make an application Chromium or Fuchsia.
When replacing prohibited facilities, inspect the repository's actual APIs;
do not invent task-system function names.

## PLATFORM-01 — Chromium

Prefer small compilation units around an abstraction, ideally but not necessarily
one file. Coherence constraints or foundational libraries can justify larger
crates. For a `rust_library` target, keep its Rust source files in one directory.
Third-party code also built with Cargo keeps its conventional Cargo layout.
Sources: [crates](https://google.github.io/styleguide/rustguide.html#small-crates),
[layout](https://google.github.io/styleguide/rustguide.html#structure).

Use `chromium::import!` and the repository formatter (for example
`git cl format`). Do not use async/await. Prefer Chromium sequences rather than
starting threads through the Rust standard library. Use `rust_gtest_interop`
for integrated tests. Style arbiters may approve specific unstable features;
verify approval rather than assuming it.
Sources: [imports](https://google.github.io/styleguide/rustguide.html#import-macro),
[formatting](https://google.github.io/styleguide/rustguide.html#formatting-other),
[async](https://google.github.io/styleguide/rustguide.html#async-await-chrome),
[threads](https://google.github.io/styleguide/rustguide.html#std-thread),
[tests](https://google.github.io/styleguide/rustguide.html#test-framework),
[features](https://google.github.io/styleguide/rustguide.html#unstable-features).

## PLATFORM-02 — Fuchsia and Android

Fuchsia uses `fuchsia_sync::Mutex` and `#[fuchsia::test]`; follow Fuchsia's
own unstable-feature approval guidance. Android embedded work may require
unstable features, subject to review for necessity and alternatives.
Do not transfer these exceptions to ordinary Cargo applications.
Sources: [mutex](https://google.github.io/styleguide/rustguide.html#fuchsia-mutex),
[tests](https://google.github.io/styleguide/rustguide.html#test-framework),
[features](https://google.github.io/styleguide/rustguide.html#unstable-features).

## PLATFORM-03 — Panic strategy

The pinned guide describes Chromium, Android, and Fuchsia as requiring
`panic=abort`; its defense-in-depth `catch_unwind` exception therefore does
not apply there. Preserve the repository's actual panic configuration and flag
a source/version conflict if current project evidence differs.
[Source](https://google.github.io/styleguide/rustguide.html#catch-unwind).
