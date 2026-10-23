# Maintaining this repository

The installable skill is under skills/google-rust-guidelines. Root documentation,
scripts, provenance, and evaluations are for maintainers, not runtime instructions.

- Preserve explicit conditions, exceptions, and upstream attribution when editing rules.
- Keep the entrypoint short and route substantial detail into relevant references.
- Treat rule IDs as traceability identifiers, not severities.
- Keep evals/rubric.json and result files out of evaluation packets. Freeze criteria
  before a comparison and retain unsuccessful runs as well as successful ones.
- Pin source commits and hashes; inspect diffs before updating. Do not vendor
  baseline skills into the runtime package.
- After changing runtime files, record a new evaluation packet manifest for any
  new behavior claim. Report actual model/host limitations without inventing metrics.
- Run scripts/validate.py, meaningful tooling tests, and applicable behavior cases.
  Use --check-sources with a verified upstream cache and --check-rust for fixtures.
- Prose is CC BY 3.0. Original tooling, fixtures, and CI are MIT. Keep installed
  NOTICE.md and LICENSE self-contained.
