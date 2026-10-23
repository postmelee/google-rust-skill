# Isolated chart implementation task

Read case.json and complete its request in workspace/. It contains the complete
rhwp-ooxml-chart crate from a pinned public rhwp commit, in a minimal workspace.
This is a component evaluation, not an upstream contribution or a full document
engine/visual validation. The supplied request governs this workspace.

If skill/SKILL.md exists, read it and the references relevant to this task. Apply
its guidance within the requested scope. Read only this packet, the installed
Rust toolchain, and dependencies needed for Cargo. Do not read parent repositories,
other packets, evaluation criteria, prior outputs, or browse the web. Do not
delegate. Do not create a Git repository, push, or open a PR.

Work only in this packet. The source file specified in case.json and new .rs
integration tests under crates/rhwp-ooxml-chart/tests/ may change. Preserve all
existing inline tests and configuration. Do not disable tests or checks, suppress
warnings, add unsafe code, or use panic recovery. Complete the task in this one
session; self-correction based on your own checks is allowed.

Dependencies are cached. From workspace/, run:

```sh
cargo +1.93.1 build --offline --locked --workspace --target-dir target/pr-review
cargo +1.93.1 test --offline --locked --workspace --target-dir target/pr-review
cargo +1.93.1 clippy --offline --locked --workspace --all-targets --target-dir target/pr-review -- -D warnings
cargo +1.93.1 fmt --all -- --check
```

Leave the implementation and tests in workspace/. Write response.json at packet
root with keys summary, references_read (actual packet-relative paths), commands
(actual commands and outcomes, including failed checks), design_decisions, and
limitations. Use English. Explain ownership, failure behavior, and compatibility
decisions briefly. Report failures honestly; do not claim checks you did not run.
