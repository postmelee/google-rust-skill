#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare, assess and replay the repeated chart implementation comparison."""
import argparse
import difflib
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from fetch_sources import fetch
from rhwp_eval import cargo, inventory, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "evals/integration-hard"
CACHE = ROOT / ".cache/rhwp-chart-source"
ARCHIVE = ROOT / "evals/results/rhwp-hard-2026-10-23"
CRATE = "crates/rhwp-ooxml-chart"
SOURCE = CRATE + "/src/patch.rs"
CONDITIONS = ("candidate", "studentweis", "0xmassi", "none")
BASE_TESTS = 165
GATES = ("patch", "build", "tests", "clippy", "format", "oracle")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(work, args, log):
    try:
        run = subprocess.run(args, cwd=work, capture_output=True, text=True, timeout=180)
        output, code = run.stdout + run.stderr, run.returncode
    except subprocess.TimeoutExpired as error:
        output, code = "TIMEOUT after 180 seconds\n" + str(error.stdout or "") + str(error.stderr or ""), 124
    for path in sorted({str(work), str(Path(work).resolve()), str(ROOT)}, key=len, reverse=True):
        output = output.replace(path, "<evaluation-repository>" if path == str(ROOT) else "<workspace>")
    Path(log).write_text(output)
    return {"command": [arg.replace(str(ROOT), "<evaluation-repository>") for arg in args], "exit_code": code, "log": Path(log).name}


def fetch_source():
    pin = read_json(ROOT / "provenance/rhwp-chart.json")
    for item in pin["files"]:
        fetch(pin["repository"], pin["commit"], item["path"], CACHE / item["path"], expected=item["sha256"])


def workspace(destination):
    for item in read_json(ROOT / "provenance/rhwp-chart.json")["files"]:
        if digest(CACHE / item["path"]) != item["sha256"]:
            raise ValueError("Pinned source mismatch: " + item["path"])
    destination.mkdir(parents=True)
    shutil.copytree(CACHE / "crates", destination / "crates")
    for name in ("LICENSE", "rust-toolchain.toml"):
        shutil.copyfile(CACHE / name, destination / name)
    for file in (SPEC / "workspace").iterdir():
        shutil.copyfile(file, destination / file.name)


def case_by_id(case_id):
    return next(case for case in read_json(SPEC / "cases.json")["cases"] if case["id"] == case_id)


def prepare(condition, case_id, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Refusing to overwrite a packet")
    case = case_by_id(case_id)
    sources = {"candidate": ROOT / "skills/google-rust-guidelines",
               "studentweis": ROOT / ".cache/baselines/studentweis",
               "0xmassi": ROOT / ".cache/baselines/0xmassi"}
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    if condition != "none":
        expected = read_json(SPEC / "conditions.json")[condition]
        if inventory(sources[condition]) != expected:
            raise ValueError("Skill differs from the pinned comparison input")
    workspace(destination / "workspace")
    if condition != "none":
        shutil.copytree(sources[condition], destination / "skill")
    write_json(destination / "case.json", case)
    shutil.copyfile(SPEC / "TASK.md", destination / "TASK.md")
    write_json(destination / "manifest.json", inventory(destination))
    return destination


def automated(result):
    return (not result["scope_errors"]
            and all(result["commands"].get(g, {}).get("exit_code") == 0 for g in GATES)
            and result["commands"].get("sensitivity", {}).get("exit_code") not in (None, 0, 124)
            and result.get("passing_tests_before_oracle", 0) > BASE_TESTS)


def assess(packet, destination):
    packet, destination = Path(packet).resolve(), Path(destination).resolve()
    if destination.exists():
        raise ValueError("Refusing to overwrite evidence")
    case = case_by_id(read_json(packet / "case.json")["id"])
    original = read_json(packet / "manifest.json")
    before = {name.removeprefix("workspace/"): value for name, value in original.items() if name.startswith("workspace/")}
    after = inventory(packet / "workspace")
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    new_tests = [name for name in changed if name.startswith(CRATE + "/tests/") and name.endswith(".rs") and name not in before]
    errors = [name for name in changed if name != SOURCE and name not in new_tests]
    pristine = (CACHE / SOURCE).read_text()
    modified_path = packet / "workspace" / SOURCE
    modified = modified_path.read_text() if modified_path.is_file() else ""
    if pristine.split("#[cfg(test)]", 1)[1] != modified.split("#[cfg(test)]", 1)[-1]:
        errors.append("Original inline tests changed or source deleted")
    if SOURCE not in changed or not new_tests:
        errors.append("Missing implementation or new integration tests")
    destination.mkdir(parents=True)
    patch = []
    for name in changed:
        old_path = SPEC / "workspace" / name if (SPEC / "workspace" / name).is_file() else CACHE / name
        old = old_path.read_text() if name in before else ""
        new_path = packet / "workspace" / name
        new = new_path.read_text() if new_path.is_file() else ""
        patch.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                     fromfile="a/" + name if name in before else "/dev/null",
                     tofile="b/" + name if new_path.is_file() else "/dev/null"))
    (destination / "patch.diff").write_text("".join(patch))
    shutil.copyfile(packet / "manifest.json", destination / "packet-manifest.json")
    if (packet / "response.json").is_file():
        response = (packet / "response.json").read_text().replace(str(packet), "<packet>").replace(str(ROOT), "<evaluation-repository>")
        (destination / "response.json").write_text(response)
    else:
        errors.append("Missing response.json")
    write_json(destination / "output-manifest.json", after)
    result = {"case": case["id"], "changed_files": changed, "scope_errors": errors, "commands": {}}
    with tempfile.TemporaryDirectory(prefix="chart-assess-") as temporary:
        work = Path(temporary) / "workspace"
        workspace(work)
        result["commands"]["patch"] = command(work, ["git", "apply", "--check", str(destination / "patch.diff")], destination / "patch.log")
        if not errors and result["commands"]["patch"]["exit_code"] == 0:
            subprocess.run(["git", "apply", str(destination / "patch.diff")], cwd=work, check=True)
            for gate, args in [("build", cargo("build", "--workspace")), ("tests", cargo("test", "--workspace")),
                               ("clippy", cargo("clippy", "--workspace", "--all-targets", "--", "-D", "warnings")),
                               ("format", ["cargo", "+1.93.1", "fmt", "--all", "--", "--check"])]:
                result["commands"][gate] = command(work, args, destination / (gate + ".log"))
            test_dir = work / CRATE / "tests"
            shutil.copyfile(SPEC / "oracles" / (case["id"] + ".rs"), test_dir / "__external.rs")
            shutil.copyfile(SPEC / "oracles/support.rs", test_dir / "__support.rs")
            shutil.copytree(SPEC / "oracles/golden", test_dir / "__golden")
            result["commands"]["oracle"] = command(work, cargo("test", "--test", "__external"), destination / "oracle.log")
            (test_dir / "__external.rs").unlink()
            (test_dir / "__support.rs").unlink()
            shutil.rmtree(test_dir / "__golden")
            (work / SOURCE).write_text(pristine)
            result["commands"]["sensitivity"] = command(work, cargo("test", "--tests"), destination / "sensitivity.log")
            result["passing_tests_before_oracle"] = sum(map(int, re.findall(r"test result: ok\. (\d+) passed", (destination / "tests.log").read_text())))
            result["external_tests"] = dict(re.findall(r"^test (\w+) \.\.\. (ok|FAILED)$", (destination / "oracle.log").read_text(), re.M))
    result["automated_pass"] = automated(result)
    result["manual_review_required"] = True
    write_json(destination / "assessment.json", result)
    return result


def summarize(archive):
    archive = Path(archive)
    experiment = read_json(archive / "experiment.json")
    for name, expected in experiment["frozen_inputs_sha256"].items():
        if digest(archive / "frozen" / name) != expected:
            raise ValueError("Frozen input mismatch: " + name)
    rubric = read_json(archive / "frozen/evals/integration-hard/rubric.json")
    totals, rows = {}, []
    for run in experiment["runs"]:
        record = archive / "runs" / run["id"]
        if digest(record / "packet-manifest.json") != run["packet_manifest_sha256"] or digest(archive / "input-manifests" / (run["id"] + ".json")) != run["packet_manifest_sha256"]:
            raise ValueError("Packet manifest mismatch: " + run["id"])
        result, review = read_json(record / "assessment.json"), read_json(record / "manual-review.json")
        if result["automated_pass"] != automated(result):
            raise ValueError("Inconsistent automated grade: " + run["id"])
        if [item["criterion"] for item in review["criteria"]] != rubric["manual_criteria"][run["case"]]:
            raise ValueError("Review criteria differ from the freeze")
        for item in review["criteria"]:
            if type(item["pass"]) is not bool or not item["quote"] or item["quote"] not in (record / item["file"]).read_text():
                raise ValueError("Invalid review evidence: " + run["id"])
        passed = automated(result) and review["scope_pass"] and review["sensitivity_expected"] and all(item["pass"] for item in review["criteria"])
        row = {**run, "pass": passed, "automated_pass": automated(result), "external_tests": result.get("external_tests", {}),
               "failed_gates": [gate for gate in GATES if result["commands"].get(gate, {}).get("exit_code") != 0],
               "failed_manual_criteria": [item["criterion"] for item in review["criteria"] if not item["pass"]]}
        rows.append(row)
        group = totals.setdefault(run["condition"], {"passed": 0, "total": 0, "cases": {}})
        group["total"] += 1; group["passed"] += int(passed)
        case = group["cases"].setdefault(run["case"], {"passed": 0, "total": 0})
        case["total"] += 1; case["passed"] += int(passed)
    return {"conditions": totals, "runs": rows}


def replay(archive, destination, run_id=None, fetch_dependencies=False):
    archive, destination = Path(archive).resolve(), Path(destination).resolve()
    summarize(archive)
    if destination.exists():
        raise ValueError("Refusing to overwrite replay evidence")
    experiment = read_json(archive / "experiment.json")
    for name, expected in experiment["frozen_inputs_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Use the evaluation revision: " + name)
    runs = [run for run in experiment["runs"] if run_id is None or run["id"] == run_id]
    if not runs:
        raise ValueError("Unknown run ID")
    destination.mkdir(parents=True)
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="chart-replay-") as temporary:
        for index, run in enumerate(runs):
            packet = Path(temporary) / run["id"]; work = packet / "workspace"
            workspace(work)
            record = archive / "runs" / run["id"]
            manifest = read_json(record / "packet-manifest.json")
            before = {k.removeprefix("workspace/"): v for k, v in manifest.items() if k.startswith("workspace/")}
            if inventory(work) != before:
                raise ValueError("Reconstructed source mismatch")
            if index == 0 and fetch_dependencies:
                subprocess.run(["cargo", "+1.93.1", "fetch", "--locked"], cwd=work, check=True)
            subprocess.run(["git", "apply", str(record / "patch.diff")], cwd=work, check=True)
            if inventory(work) != read_json(record / "output-manifest.json"):
                raise ValueError("Patch output mismatch")
            shutil.copyfile(record / "packet-manifest.json", packet / "manifest.json")
            if (record / "response.json").exists():
                shutil.copyfile(record / "response.json", packet / "response.json")
            write_json(packet / "case.json", {"id": run["case"]})
            actual = assess(packet, destination / run["id"])
            expected = read_json(record / "assessment.json")
            codes = lambda result: {key: value["exit_code"] for key, value in result["commands"].items()}
            if codes(actual) != codes(expected) or actual["automated_pass"] != expected["automated_pass"]:
                raise ValueError("Replay differs: " + run["id"])
            outcome = {"run": run["id"], "matches_recorded_gates": True, "automated_pass": actual["automated_pass"]}
            outcomes.append(outcome); print(outcome, flush=True)
    write_json(destination / "summary.json", outcomes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch")
    p = sub.add_parser("prepare"); p.add_argument("--condition", choices=CONDITIONS, required=True); p.add_argument("--case", choices=["H1", "H2"], required=True); p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("assess"); p.add_argument("--packet", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("summarize"); p.add_argument("--results", type=Path, default=ARCHIVE)
    p = sub.add_parser("replay"); p.add_argument("--results", type=Path, default=ARCHIVE); p.add_argument("--output", type=Path, required=True); p.add_argument("--run"); p.add_argument("--fetch-dependencies", action="store_true")
    args = parser.parse_args()
    if args.command == "fetch": fetch_source()
    elif args.command == "prepare": print(prepare(args.condition, args.case, args.output))
    elif args.command == "assess": print(assess(args.packet, args.output))
    elif args.command == "summarize": print(__import__("json").dumps(summarize(args.results), indent=2))
    else: replay(args.results, args.output, args.run, args.fetch_dependencies)
