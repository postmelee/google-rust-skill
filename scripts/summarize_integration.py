#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify frozen evidence and summarize reviewed implementation results."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def summarize(root):
    root = Path(root)
    experiment = read(root / "experiment.json")
    for name, expected in experiment["frozen_inputs_sha256"].items():
        actual = hashlib.sha256((root / "frozen" / name).read_bytes()).hexdigest()
        require(actual == expected, f"Frozen input mismatch: {name}")
    require(hashlib.sha256((root / "frozen/conditions.json").read_bytes()).hexdigest() == experiment["conditions_manifest_sha256"], "Condition manifest mismatch")
    require(hashlib.sha256((root / "frozen/assessment-runner.py").read_bytes()).hexdigest() == experiment["assessment_implementation_sha256"], "Assessment runner mismatch")
    rubric = read(root / "frozen/evals/integration/rubric.json")
    totals = {}
    rows = []
    for run in experiment["runs"]:
        case, condition = run["case"], run["condition"]
        result_dir = root / case / condition
        require(hashlib.sha256((root / "input-manifests" / (run["id"] + ".json")).read_bytes()).hexdigest() == run["packet_manifest_sha256"], f"Frozen packet mismatch: {run['id']}")
        require(hashlib.sha256((result_dir / "packet-manifest.json").read_bytes()).hexdigest() == run["packet_manifest_sha256"], f"Run packet mismatch: {run['id']}")
        result = read(result_dir / "assessment.json")
        review = read(result_dir / "manual-review.json")
        require([c["criterion"] for c in review["criteria"]] == rubric["manual_criteria"][case], f"Criterion mismatch: {run['id']}")
        patch = (result_dir / "patch.diff").read_text()
        for criterion in review["criteria"]:
            require(type(criterion["pass"]) is bool, "Expected boolean criterion grade")
            require(criterion["evidence"] in patch, f"Evidence missing from patch: {run['id']}")
        sensitivity_path = result_dir / "test-sensitivity.log"
        sensitivity = sensitivity_path.read_text() if sensitivity_path.exists() else ""
        require(sensitivity_path.exists() or not review["sensitivity_expected_failure"], "Cannot confirm a sensitivity check without its log")
        require(review["sensitivity_evidence"] in sensitivity, f"Sensitivity evidence missing: {run['id']}")
        gates = result["commands"]
        computed = not result["scope_errors"] and all(gates.get(g, {}).get("exit_code") == 0 for g in ["patch_check", "build", "tests", "clippy", "format", "oracle"]) and gates.get("test_sensitivity", {}).get("exit_code") not in (None, 0, 124) and result.get("passing_tests_before_oracle", 0) > 15
        require(computed == result["automated_pass"], f"Automated grade inconsistent: {run['id']}")
        passed = computed and all(c["pass"] for c in review["criteria"]) and review["sensitivity_expected_failure"] and review["scope_review_pass"]
        totals.setdefault(condition, {"passed": 0, "total": 0})
        totals[condition]["passed"] += int(passed)
        totals[condition]["total"] += 1
        rows.append({"case": case, "condition": condition, "pass": passed,
                     "existing_tests": 15, "new_agent_tests": max(0, result.get("passing_tests_before_oracle", 0) - 15),
                     "automated_gates_pass": computed})
    return {"conditions": totals, "runs": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.results), indent=2))
