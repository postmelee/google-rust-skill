# Evaluation protocol

The 15 cases in [cases.json](cases.json) were authored before the candidate skill.
The [rubric](rubric.json) is a separate oracle and must not enter evaluated contexts.
Fixtures are intentionally small and sometimes defective; do not execute case 11's
unsafe input. Rust fixture compilation checks syntax, not correctness.

## Conditions

- **none**: existing model knowledge, supplied user prompts and fixtures.
- **studentweis**: pinned community entrypoint plus the complete source reference.
- **0xmassi**: pinned community entrypoint with lint configuration and judgment rules.
- **candidate**: this repository's entrypoint plus selectively loaded references.

[Baseline versions](../provenance/baselines.json) fix commits, paths, and hashes.
Download their development-only sources with:

```sh
python3 scripts/fetch_sources.py
```

For a fresh single-case session:

```sh
python3 scripts/prepare_eval.py --condition candidate --case 07 --output /tmp/rust-eval-candidate-07
```

Ask an independent agent to read that packet's TASK.md and produce responses.json.
The output directory must not already exist. It contains only the prompt,
fixtures, skill (if any), task protocol, and a content-hash manifest.
Agents must not read the oracle, other conditions, previous answers, or browse.
Existing tools and model knowledge remain part of the experimental environment.

Omit --case to create a batch packet. This is cheaper for development but allows
context carryover between cases. Do not describe batch results as independent
per-case sessions. Each condition should have a fresh context.

For a stronger evaluation, use identical pinned model IDs, reasoning settings,
tool policies, and software versions; run multiple fresh repetitions per case
and condition. Add held-out prompts after the development phase and keep their
answers out of the skill. If model IDs or token usage are unavailable, say so.
The supplied repository does not include a paid model API runner or fabricate
token, latency, or cost measurements.

## Grade behavior

For each case, evaluate every frozen criterion against the actual response,
record a quoted excerpt, and check the listed fatal errors. A case passes only
when every criterion passes and no fatal error occurs. Do not score incidental
formatting outside the requested question or reward verbosity.

Record suggested edits that break compatibility, unsupported source claims,
and invented checks as observations even when outside the narrow rubric.
Distinguish selection from execution: the negative case tests applicability
reasoning inside the packet, not a host's real implicit-trigger mechanism.

Save raw responses, criterion grades, packet manifests, context limitations,
and any structural changes between runs. Preserve failed runs. Case count is
not statistical confidence; this development set is not a general benchmark.

## What the pilot measures

The [2026-10-23 pilot](results/2026-10-23/REPORT.md) is a static review task.
It does not test agent-generated patches with a compiler. The repository separately
compiles its input fixtures to ensure they are parsable.

Entrypoint UTF-8 bytes and whole-reference file sizes are reproducible packaging
measurements. They are not token counts or evidence that a model loaded every
byte. references_read is agent-reported, not a captured tool trace.

Recompute recorded grade counts and entrypoint sizes with:

```sh
python3 scripts/summarize_results.py evals/results/2026-10-23
```
