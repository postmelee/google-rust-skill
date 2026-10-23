#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate packaging, source links, and evaluation inputs, not agent quality (MIT)."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/google-rust-guidelines"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(check_sources=False, check_rust=False):
    entry = (SKILL / "SKILL.md").read_text()
    parts = entry.split("---", 2)
    require(len(parts) == 3 and not parts[0].strip(), "Missing frontmatter")
    metadata = yaml.safe_load(parts[1])
    require(metadata["name"] == SKILL.name, "Name/directory mismatch")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]), "Invalid name")
    require(len(metadata["name"]) <= 64, "Name too long")
    require(isinstance(metadata["description"], str) and 0 < len(metadata["description"]) <= 1024,
            "Invalid description")
    require(metadata["license"] == "CC-BY-3.0", "Unexpected prose license")
    require(len(entry.splitlines()) < 500, "Entrypoint exceeds recommended size")
    upstream = json.loads((ROOT / "provenance/upstream.json").read_text())
    require(metadata["metadata"]["upstream-commit"] == upstream["commit"], "Upstream pin mismatch")
    require((SKILL / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes(), "Missing bundled license")
    interface = yaml.safe_load((SKILL / "agents/openai.yaml").read_text())["interface"]
    require("$" + SKILL.name in interface["default_prompt"], "Default prompt must name the skill")
    require(25 <= len(interface["short_description"]) <= 64, "Invalid UI description length")

    anchors_used = set()
    rule_ids = []
    for path in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        content = path.read_text()
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            if target:
                require((path.parent / target).exists(), f"Broken file link in {path}: {target}")
        if path.is_relative_to(SKILL):
            anchors_used.update(re.findall(r"rustguide.html#([a-z0-9-]+)", content))
            rule_ids.extend(re.findall(r"^## ([A-Z]+-\d+) ", content, flags=re.M))
    require(len(rule_ids) == len(set(rule_ids)), "Duplicate rule IDs")
    rule_map = json.loads((ROOT / "provenance/rule-map.json").read_text())
    require(set(rule_map["rules"]) == set(rule_ids), "Rule map differs from packaged rules")
    for rule_id, mapping in rule_map["rules"].items():
        content = (SKILL / mapping["file"]).read_text()
        require(f"## {rule_id} " in content, f"Wrong destination for {rule_id}")
        require(mapping["anchors"], f"No source anchors for {rule_id}")
        section = content.split(f"## {rule_id} ", 1)[1].split("\n## ", 1)[0]
        actual = set(re.findall(r"rustguide.html#([a-z0-9-]+)", section))
        require(actual == set(mapping["anchors"]), f"Stale source mapping for {rule_id}")
    if check_sources:
        source_path = ROOT / ".cache/upstream/rustguide.md"
        require(source_path.exists(), "Run scripts/fetch_sources.py --upstream-only first")
        data = source_path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == upstream["blob"], "Upstream bytes do not match the pinned blob")
        anchors = set(re.findall(r'<a id="([^"]+)"', data.decode()))
        require(not (anchors_used - anchors), f"Unknown upstream anchors: {anchors_used - anchors}")

    cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
    rubric = json.loads((ROOT / "evals/rubric.json").read_text())["cases"]
    ids = [case["id"] for case in cases]
    require(len(ids) == 15 and len(set(ids)) == 15, "Expected 15 distinct cases")
    require(set(ids) == {case["id"] for case in rubric}, "Case/rubric mismatch")
    require(all(case["criteria"] and case["fatal_errors"] for case in rubric), "Incomplete rubric")
    for case in cases:
        require(case["prompt"] and case["files"], "Missing prompt or fixtures")
        require(not {"criteria", "fatal_errors", "expected_output"} & case.keys(), "Oracle leakage")
        for name in case["files"]:
            path = (ROOT / name).resolve()
            require(path.is_relative_to(ROOT / "evals/fixtures") and path.is_file(), f"Bad fixture: {name}")
    if check_rust:
        require(shutil.which("rustc"), "rustc is required with --check-rust")
        with tempfile.TemporaryDirectory(prefix="rust-skill-fixtures-") as temporary:
            for path in sorted((ROOT / "evals/fixtures").glob("*/input.rs")):
                # Compile only. Never execute intentionally defective unsafe examples.
                subprocess.run(["rustc", "--edition=2021", "--crate-type=lib", "--emit=metadata",
                                "--crate-name", "case_" + path.parent.name, str(path),
                                "-o", str(Path(temporary) / (path.parent.name + ".rmeta"))],
                               check=True, capture_output=True, text=True)
    return {"cases": len(ids), "rules": len(rule_ids), "source_anchors": len(anchors_used),
            "entrypoint_utf8_bytes": len(entry.encode()), "rust_fixtures_compiled": 14 if check_rust else 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-sources", action="store_true")
    parser.add_argument("--check-rust", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.check_sources, args.check_rust), indent=2))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n{getattr(error, 'stderr', '')}")
