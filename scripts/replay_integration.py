#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rebuild archived rhwp patches without running a model or installing a skill."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

import rhwp_eval as harness
from summarize_integration import summarize


def replay(results, output, run_id=None, fetch_dependencies=False):
    results, output = Path(results).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Refusing to overwrite replay evidence")
    summarize(results)  # Verify archived inputs, reviews, and reported outcomes first.
    experiment = harness.read_json(results / "experiment.json")
    # Require this checkout's source pins, task definitions, and workspace to match.
    # The historical runner is retained separately for auditing later harness changes.
    for name, expected in experiment["frozen_inputs_sha256"].items():
        if name == "scripts/rhwp_eval.py":
            continue
        if hashlib.sha256((harness.ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Use the evaluation's source revision; current input differs: {name}")
    runs = [run for run in experiment["runs"] if run_id is None or run["id"] == run_id]
    if not runs:
        raise ValueError("Unknown run ID")
    output.mkdir(parents=True)
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="rhwp-archive-replay-") as temporary:
        for index, run in enumerate(runs):
            packet = Path(temporary) / run["id"]
            work = packet / "workspace"
            harness.workspace(work)
            record = results / run["case"] / run["condition"]
            manifest = harness.read_json(record / "packet-manifest.json")
            before = {k.removeprefix("workspace/"): v for k, v in manifest.items() if k.startswith("workspace/")}
            if harness.inventory(work) != before:
                raise ValueError("Reconstructed source does not match the evaluated input")
            if fetch_dependencies and index == 0:
                subprocess.run(["cargo", "+1.93.1", "fetch", "--locked"], cwd=work, check=True)
            subprocess.run(["git", "apply", "--check", str(record / "patch.diff")], cwd=work, check=True)
            subprocess.run(["git", "apply", str(record / "patch.diff")], cwd=work, check=True)
            if harness.inventory(work) != harness.read_json(record / "output-manifest.json"):
                raise ValueError("Applied patch does not reproduce the recorded output files")
            shutil.copyfile(record / "packet-manifest.json", packet / "manifest.json")
            shutil.copyfile(record / "response.json", packet / "response.json")
            harness.write_json(packet / "case.json", {"id": run["case"]})
            actual = harness.assess(packet, output / run["id"])
            expected = harness.read_json(record / "assessment.json")
            for gate, detail in expected["commands"].items():
                if actual["commands"].get(gate, {}).get("exit_code") != detail["exit_code"]:
                    raise ValueError(f"Replay outcome differs: {run['id']} {gate}")
            if actual["automated_pass"] != expected["automated_pass"]:
                raise ValueError(f"Replay grade differs: {run['id']}")
            outcomes.append({"run": run["id"], "matches_recorded_gates": True,
                             "automated_pass": actual["automated_pass"]})
            print(json.dumps(outcomes[-1]), flush=True)
    harness.write_json(output / "summary.json", outcomes)
    return outcomes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("evals/results/rhwp-2026-10-23"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--run", help="Optional run ID, for example R1-candidate")
    parser.add_argument("--fetch-dependencies", action="store_true", help="Allow Cargo to populate its cache before offline replay")
    args = parser.parse_args()
    replay(args.results, args.output, args.run, args.fetch_dependencies)
