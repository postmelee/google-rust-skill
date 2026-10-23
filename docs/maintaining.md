# Maintaining Google Rust Guidelines

[Back to the README](../README.md) · [User guide](using.md) · [Evaluation](evaluation.md)

This page is for contributors and release maintainers. To install and use the
skill, start with the [user guide](using.md).

## Design

- A small entrypoint establishes scope, routes the task, and defines verification.
- Five focused references group decisions by API design, ownership/errors,
  organization, safety/documentation, and platform-specific rules.
- Twenty-five rule groups carry source links. [The rule map](../provenance/rule-map.json)
  connects them to upstream anchors.
- Conditions and exceptions live beside the rule they qualify.
- Existing formatters and linters handle mechanical checks; semantic review
  covers what those tools cannot establish.

This is a paraphrased, task-oriented adaptation, not a complete mirrored manual,
a replacement for rustc/Clippy, or proof that unsafe code is sound.
Uncovered edge cases route to the relevant authoritative source.
The package follows the [Agent Skills specification](https://agentskills.io/specification).
Optional Codex UI metadata lives in `agents/openai.yaml`; host-specific discovery
and activation need their own verification.

## Develop and verify

From the repository root, use Python 3.10+ and Rust 1.94.1 for the recorded
fixture checks:

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
(2026-10-21), retrieved 2026-10-23. [Provenance](../provenance/upstream.json)
records the full commit, file blob, origin, and licenses.

To update, inspect the upstream diff, revise affected rules and their mapping,
update attribution and pins, and rerun relevant behavior cases. Retain old results
with their manifests. Do not silently refresh installed references during a
normal code task or claim a pinned release is always current.

## Release maintenance

1. Run the validation commands and inspect the package and evaluation report.
2. Push changes and wait for the GitHub Actions workflow to pass on that commit.
3. Verify installation from GitHub in a fresh temporary project and compare all
   installed files with the runtime package.
4. Tag the verified commit, attach the generated ZIP and its SHA-256 checksum,
   and state the tested host/model conditions and upstream version in the release notes.
5. Verify installation from the tag and download the published assets to check
   their bytes. Update the versioned installation links for the next release.

No GitHub repository is created or published by the maintenance scripts.
The included GitHub Actions workflow runs structural checks, source verification,
fixture compilation, tooling tests, archived-result integrity checks, packaging,
and separate replays of the 12 initial rhwp patches and 24 chart patches. These
replays verify recorded code, including failed runs; fresh model evaluations
are run separately.

## License and acknowledgements

Adapted guide prose, original documentation, and skill instructions:
**CC BY 3.0**, under [LICENSE](../LICENSE). Attribution and changes are recorded
in the installed skill's [NOTICE](../skills/google-rust-guidelines/NOTICE.md).

Original Python tooling, Rust/Python fixtures, and CI configuration:
**MIT**, under [LICENSES/MIT.txt](../LICENSES/MIT.txt).

Google licenses its original example code separately under Apache 2.0. No
upstream example-code bundle is included in this runtime package; any future
copied example must preserve its applicable license and notices.

Existing skills are credited as comparison baselines, not claimed as our work:
[StudentWeis](https://github.com/StudentWeis/google-rust-style-guide) and
[0xMassi](https://github.com/0xMassi/google-rust-style-skill).
Their pinned sources are fetched only into ignored development caches and are
not redistributed in the runtime ZIP.

The implementation evaluation uses [edwardkim/rhwp](https://github.com/edwardkim/rhwp).
Upstream source excerpts in recorded patches retain its MIT license and attribution
under [LICENSES/rhwp-MIT.txt](../LICENSES/rhwp-MIT.txt). The evaluated source is fetched
into an ignored cache and is not part of the installed skill or release ZIP.
