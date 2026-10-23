#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Prepare an answer-free, isolated packet for an agent evaluation (MIT)."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def prepare(condition, destination, case_id=None):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"Refusing to overwrite existing packet: {destination}")
    cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
    if case_id:
        cases = [case for case in cases if case["id"] == case_id]
        if not cases:
            raise ValueError(f"Unknown case: {case_id}")
    sources = {
        "candidate": ROOT / "skills/google-rust-guidelines",
        "studentweis": ROOT / ".cache/baselines/studentweis",
        "0xmassi": ROOT / ".cache/baselines/0xmassi",
    }
    source = sources.get(condition)
    if condition != "none" and (source is None or not (source / "SKILL.md").is_file()):
        raise ValueError("Skill unavailable. Run scripts/fetch_sources.py first for baselines.")
    destination.mkdir(parents=True)
    if source:
        shutil.copytree(source, destination / "skill")
    inputs = []
    for case in cases:
        paths = []
        for filename in case["files"]:
            original = ROOT / filename
            relative = Path(filename).relative_to("evals")
            output = destination / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, output)
            paths.append(relative.as_posix())
        inputs.append({"id": case["id"], "prompt": case["prompt"], "files": paths})
    (destination / "cases.json").write_text(json.dumps(inputs, indent=2) + "\n")
    instruction = (
        "Answer each user prompt in cases.json using only its supplied files. "
        "Treat each case as independent. Do not edit input files. "
        "If skill/SKILL.md exists, inspect its metadata, decide whether it applies, "
        "and use its instructions and relevant references when applicable. "
        "Do not browse the web or read other evaluation conditions or answer keys. "
        "Return JSON with a responses array: each entry has id, skill_applied "
        "(boolean), response (your actual review or proposed solution), and "
        "references_read (actual packet-relative files read). Do not invent "
        "results of tools you did not run. Save to responses.json. "
        "This packet intentionally contains no expected answers."
    )
    (destination / "TASK.md").write_text(instruction + "\n")
    inventory = {}
    for path in sorted(destination.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            inventory[path.relative_to(destination).as_posix()] = {
                "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)
            }
    (destination / "manifest.json").write_text(json.dumps(inventory, indent=2) + "\n")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", choices=["candidate", "studentweis", "0xmassi", "none"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", dest="case_id", help="Prepare one case for a fresh agent session")
    args = parser.parse_args()
    try:
        print(prepare(args.condition, args.output, args.case_id))
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
