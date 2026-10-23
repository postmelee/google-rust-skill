#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check evidence quotes and summarize recorded human/agent-reviewed grades."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summarize(directory):
    directory = Path(directory)
    experiment = json.loads((directory / "experiment.json").read_text())
    for filename in ["cases.json", "rubric.json"]:
        archived = directory / filename
        expected = experiment["inputs_sha256"]["evals/" + filename]
        if hashlib.sha256(archived.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Archived input hash mismatch: {filename}")
    rubric = {case["id"]: case for case in json.loads((directory / "rubric.json").read_text())["cases"]}
    rows = []
    for condition in experiment["conditions"]:
        name = condition["name"]
        responses = json.loads((directory / (name + ".responses.json")).read_text())["responses"]
        grades = json.loads((directory / (name + ".grades.json")).read_text())["cases"]
        by_id = {response["id"]: response for response in responses}
        if len(by_id) != len(responses) or set(by_id) != set(rubric):
            raise ValueError(f"Incomplete/duplicate response IDs: {name}")
        if len(grades) != len(rubric) or {grade["id"] for grade in grades} != set(rubric):
            raise ValueError(f"Incomplete/duplicate grade IDs: {name}")
        passed = 0
        for grade in grades:
            expected = rubric[grade["id"]]
            if len(grade["criteria"]) != len(expected["criteria"]):
                raise ValueError(f"Criterion count mismatch: {name}/{grade['id']}")
            for criterion in grade["criteria"]:
                if type(criterion["passed"]) is not bool or not criterion["evidence"]:
                    raise ValueError(f"Missing reviewed grade/evidence: {name}/{grade['id']}")
                if criterion["evidence"] not in by_id[grade["id"]]["response"]:
                    raise ValueError(f"Evidence is not an exact response quote: {name}/{grade['id']}")
            if type(grade["fatal_error"]) is not bool:
                raise ValueError(f"Missing fatal-error review: {name}/{grade['id']}")
            passed += all(c["passed"] for c in grade["criteria"]) and not grade["fatal_error"]
        manifest = json.loads((directory / (name + ".manifest.json")).read_text())
        entry_size = manifest.get("skill/SKILL.md", {}).get("bytes", 0)
        rows.append({"condition": name, "passed": passed, "total": len(rubric),
                     "entrypoint_utf8_bytes": entry_size})
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(summarize(args.directory), indent=2))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"{error}\n")
