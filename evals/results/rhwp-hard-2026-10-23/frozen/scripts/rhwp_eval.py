#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare isolated rhwp tasks and independently compile/test captured patches."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from fetch_sources import fetch

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "evals/integration"
CACHE = ROOT / ".cache/rhwp-source"
CONDITIONS = ("candidate", "studentweis", "0xmassi", "none")


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def inventory(directory):
    return {p.relative_to(directory).as_posix(): {
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size
    } for p in sorted(Path(directory).rglob("*")) if p.is_file()
        and not {"target", ".git"}.intersection(p.relative_to(directory).parts)}


def case_by_id(case_id):
    return next(c for c in read_json(SPEC / "cases.json")["cases"] if c["id"] == case_id)


def fetch_source():
    source = read_json(ROOT / "provenance/rhwp.json")
    for entry in source["files"]:
        fetch(source["repository"], source["commit"], entry["path"],
              CACHE / entry["path"], expected=entry["sha256"])


def verify_source():
    for entry in read_json(ROOT / "provenance/rhwp.json")["files"]:
        if hashlib.sha256((CACHE / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Source mismatch: {entry['path']}")


def workspace(destination):
    verify_source()
    destination = Path(destination)
    destination.mkdir(parents=True)
    for name in ("crates", "mydocs"):
        shutil.copytree(CACHE / name, destination / name)
    for name in ("LICENSE", "rust-toolchain.toml"):
        shutil.copyfile(CACHE / name, destination / name)
    for path in (SPEC / "workspace").iterdir():
        shutil.copyfile(path, destination / path.name)


def prepare(condition, case_id, destination):
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    case = case_by_id(case_id)
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Refusing to overwrite an evaluation packet")
    verify_source()
    sources = {"candidate": ROOT / "skills/google-rust-guidelines",
               "studentweis": ROOT / ".cache/baselines/studentweis",
               "0xmassi": ROOT / ".cache/baselines/0xmassi"}
    if condition != "none" and not (sources[condition] / "SKILL.md").is_file():
        raise ValueError("Fetch baseline skills first")
    workspace(destination / "workspace")
    if condition != "none":
        shutil.copytree(sources[condition], destination / "skill")
    write_json(destination / "case.json", {k: case[k] for k in ("id", "title", "prompt", "source_file")})
    (destination / "TASK.md").write_text("""# Isolated Rust implementation task

Read case.json and implement its request in workspace/. This contains the complete
rhwp-contracts crate from a pinned public rhwp commit, with a minimal workspace
and the upstream-compatible dependency lock. Existing Rust source and tests are
unmodified. This is a component evaluation, not an upstream contribution or a
whole-engine validation. The new task's explicit scope governs this workspace.

If skill/SKILL.md exists, read its metadata and apply it and relevant references
to this Rust task. Do not impose unrelated platform policies. Read only this
packet, the installed Rust toolchain, and dependencies needed for Cargo. Do not
read parent repositories, other packets, answer keys, prior runs, or browse the
web. Do not delegate. Work only inside this packet. Do not push or create PRs.

Run commands from workspace/. Dependencies are cached. Use Rust 1.93.1,
--offline --locked, and --target-dir target/pr-review. Keep source declarations,
existing tests, configuration, and all other files unchanged. Add tests only
under crates/rhwp-contracts/tests/ with ordinary Rust integration tests. Do not
disable tests, checks, or warnings. Complete the implementation and tests in
this one session; fix issues you observe before finishing.

Required commands (with the options above): cargo build --workspace,
cargo test --workspace, cargo clippy --workspace --all-targets -- -D warnings,
and cargo +1.93.1 fmt --all -- --check (fmt needs no offline/locked/target options).

Save response.json at packet root with keys summary (English), references_read
(actual packet-relative files), commands (actual command and result), and
limitations. Report tool failures honestly. Leave the source patch in workspace/.
Do not create a Git repository. No expected answers are provided in this packet.
""")
    write_json(destination / "manifest.json", inventory(destination))
    return destination


def command(work, args, log):
    try:
        result = subprocess.run(args, cwd=work, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        code = result.returncode
    except subprocess.TimeoutExpired as error:
        output = "TIMEOUT after 180 seconds\n" + str(error.stdout or "") + str(error.stderr or "")
        code = 124
    # Keep commands and logs portable without disclosing host-specific paths.
    output = output.replace(str(work), "<workspace>")
    log.write_text(output)
    return {"command": args, "exit_code": code, "log": log.name}


def cargo(action, *extra):
    return ["cargo", "+1.93.1", action, "--offline", "--locked",
            "--target-dir", "target/pr-review", *extra]


def assess(packet, destination):
    packet, destination = Path(packet).resolve(), Path(destination).resolve()
    if destination.exists():
        raise ValueError("Refusing to overwrite results")
    case = case_by_id(read_json(packet / "case.json")["id"])
    original = read_json(packet / "manifest.json")
    before = {k.removeprefix("workspace/"): v for k, v in original.items() if k.startswith("workspace/")}
    after = inventory(packet / "workspace")
    changed = [name for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)]
    source = case["source_file"]
    tests = [name for name in changed if name.startswith("crates/rhwp-contracts/tests/")
             and name.endswith(".rs") and name not in before]
    scope_errors = [name for name in changed if name != source and name not in tests]
    expected_source = (CACHE / source).read_text()
    source_path = packet / "workspace" / source
    actual_source = source_path.read_text() if source_path.is_file() else ""
    if not source_path.is_file():
        scope_errors.append("specified source file deleted")
    if "#[cfg(test)]" in expected_source and expected_source.split("#[cfg(test)]", 1)[1] != actual_source.split("#[cfg(test)]", 1)[-1]:
        scope_errors.append("upstream inline tests changed")
    if source not in changed or not tests:
        scope_errors.append("missing implementation or new integration tests")
    destination.mkdir(parents=True)
    patch = []
    for name in changed:
        # Root workspace/lock are reduced harness inputs, not upstream's root files.
        old = SPEC / "workspace" / name if (SPEC / "workspace" / name).is_file() else CACHE / name
        old_text = old.read_text() if name in before else ""
        new_path = packet / "workspace" / name
        new_text = new_path.read_text() if new_path.exists() else ""
        patch.extend(difflib.unified_diff(old_text.splitlines(True), new_text.splitlines(True),
                     fromfile="a/" + name if name in before else "/dev/null",
                     tofile="b/" + name if new_path.exists() else "/dev/null"))
    (destination / "patch.diff").write_text("".join(patch))
    shutil.copyfile(packet / "manifest.json", destination / "packet-manifest.json")
    if (packet / "response.json").exists():
        shutil.copyfile(packet / "response.json", destination / "response.json")
    else:
        scope_errors.append("missing response.json")
    write_json(destination / "output-manifest.json", after)
    results = {"case": case["id"], "changed_files": changed, "scope_errors": scope_errors, "commands": {}}
    with tempfile.TemporaryDirectory(prefix="rhwp-replay-") as temporary:
        work = Path(temporary) / "workspace"
        workspace(work)
        applied = command(work, ["git", "apply", "--check", str(destination / "patch.diff")], destination / "patch-check.log")
        results["commands"]["patch_check"] = applied
        if applied["exit_code"] != 0 or scope_errors:
            results["automated_pass"] = False
            write_json(destination / "assessment.json", results)
            return results
        subprocess.run(["git", "apply", str(destination / "patch.diff")], cwd=work, check=True)
        for gate, args in [("build", cargo("build", "--workspace")),
                           ("tests", cargo("test", "--workspace")),
                           ("clippy", cargo("clippy", "--workspace", "--all-targets", "--", "-D", "warnings")),
                           ("format", ["cargo", "+1.93.1", "fmt", "--all", "--", "--check"])]:
            results["commands"][gate] = command(work, args, destination / f"{gate}.log")
        oracle = work / "crates/rhwp-contracts/tests/__external_contract.rs"
        shutil.copyfile(SPEC / "oracles" / case["oracle"], oracle)
        results["commands"]["oracle"] = command(work, cargo("test", "-p", "rhwp-contracts", "--test", "__external_contract"), destination / "oracle.log")
        oracle.unlink()
        (work / source).write_text(expected_source)
        results["commands"]["test_sensitivity"] = command(work, cargo("test", "-p", "rhwp-contracts", "--tests"), destination / "test-sensitivity.log")
    passed_tests = sum(int(n) for n in re.findall(r"test result: ok\. (\d+) passed", (destination / "tests.log").read_text()))
    results["passing_tests_before_oracle"] = passed_tests
    results["automated_pass"] = all(results["commands"][g]["exit_code"] == 0 for g in ("build", "tests", "clippy", "format", "oracle")) and results["commands"]["test_sensitivity"]["exit_code"] not in (0, 124) and passed_tests > 15
    # A reviewer must confirm sensitivity failed for the intended missing API/behavior,
    # not an environment failure, and inspect all frozen manual criteria.
    results["manual_review_required"] = True
    write_json(destination / "assessment.json", results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch")
    prep = sub.add_parser("prepare")
    prep.add_argument("--condition", required=True, choices=CONDITIONS)
    prep.add_argument("--case", required=True, choices=["R1", "R2", "R3"])
    prep.add_argument("--output", required=True, type=Path)
    grade = sub.add_parser("assess")
    grade.add_argument("--packet", required=True, type=Path)
    grade.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "fetch":
        fetch_source()
    elif args.command == "prepare":
        print(prepare(args.condition, args.case, args.output))
    else:
        print(json.dumps(assess(args.packet, args.output), indent=2))


if __name__ == "__main__":
    main()
