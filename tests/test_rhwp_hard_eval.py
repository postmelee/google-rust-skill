"""Protect input isolation and failed-run classification for chart evaluations."""
# SPDX-License-Identifier: MIT
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rhwp_hard_eval as harness


class ChartEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cache = self.root / ".cache/source"
        self.spec = self.root / "evals/integration-hard"
        files = {harness.SOURCE: "pub fn original() {}\n#[cfg(test)]\nmod tests {}\n",
                 "LICENSE": "MIT\n", "rust-toolchain.toml": "[toolchain]\nchannel = \"1.93.1\"\n"}
        for name, contents in files.items():
            path = self.cache / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(contents)
        (self.root / "provenance").mkdir()
        harness.write_json(self.root / "provenance/rhwp-chart.json", {"files": [
            {"path": name, "sha256": hashlib.sha256(contents.encode()).hexdigest()} for name, contents in files.items()]})
        (self.spec / "workspace").mkdir(parents=True)
        (self.spec / "workspace/Cargo.toml").write_text("[workspace]\nmembers = []\n")
        (self.spec / "TASK.md").write_text("Implement the task\n")
        (self.spec / "rubric.json").write_text("private criteria")
        (self.spec / "oracles").mkdir()
        (self.spec / "oracles/H1.rs").write_text("private oracle")
        harness.write_json(self.spec / "cases.json", {"cases": [{"id": "H1", "prompt": "Implement a writer", "source_file": harness.SOURCE}]})
        self.addCleanup(patch.stopall)
        patch.multiple(harness, ROOT=self.root, SPEC=self.spec, CACHE=self.cache).start()

    def test_packet_excludes_grading_data_and_cannot_be_overwritten(self):
        packet = harness.prepare("none", "H1", self.root / "packet")
        files = harness.inventory(packet)
        self.assertFalse(any("rubric" in name or "oracle" in name or "skill/" in name for name in files))
        with self.assertRaises(ValueError):
            harness.prepare("none", "H1", packet)

    def test_source_corruption_prevents_packet_creation(self):
        (self.cache / harness.SOURCE).write_text("tampered")
        with self.assertRaises(ValueError):
            harness.prepare("none", "H1", self.root / "packet")
        self.assertFalse((self.root / "packet").exists())

    def test_deleted_source_is_retained_as_a_failed_run(self):
        packet = harness.prepare("none", "H1", self.root / "packet")
        (packet / "workspace" / harness.SOURCE).unlink()
        output = self.root / "result"
        result = harness.assess(packet, output)
        self.assertFalse(result["automated_pass"])
        self.assertTrue(result["scope_errors"])
        self.assertEqual(set(result["commands"]), {"patch"})
        self.assertTrue((output / "patch.diff").exists())
        self.assertTrue((output / "assessment.json").exists())

    def test_compile_success_alone_cannot_pass_and_timeout_is_not_sensitivity(self):
        result = {"scope_errors": [], "commands": {key: {"exit_code": 0} for key in harness.GATES},
                  "passing_tests_before_oracle": 166}
        result["commands"]["sensitivity"] = {"exit_code": 101}
        self.assertTrue(harness.automated(result))
        result["commands"]["oracle"]["exit_code"] = 101
        self.assertFalse(harness.automated(result))
        result["commands"]["oracle"]["exit_code"] = 0
        result["commands"]["sensitivity"]["exit_code"] = 124
        self.assertFalse(harness.automated(result))


class ChartEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.archive = Path(self.temporary.name) / "archive"
        shutil.copytree(harness.ARCHIVE, self.archive)
        experiment = harness.read_json(self.archive / "experiment.json")
        experiment["runs"] = experiment["runs"][:3]
        harness.write_json(self.archive / "experiment.json", experiment)

    def test_frozen_oracle_changes_are_rejected(self):
        path = self.archive / "frozen/evals/integration-hard/oracles/H1.rs"
        path.write_text(path.read_text() + "\n// changed after freeze\n")
        with self.assertRaises(ValueError):
            harness.summarize(self.archive)

    def test_an_external_test_failure_cannot_keep_a_passing_grade(self):
        path = self.archive / "runs/r01/assessment.json"
        result = json.loads(path.read_text())
        result["commands"]["oracle"]["exit_code"] = 101
        harness.write_json(path, result)
        with self.assertRaises(ValueError):
            harness.summarize(self.archive)

    def test_manual_evidence_must_be_present(self):
        path = self.archive / "runs/r02/manual-review.json"
        result = json.loads(path.read_text())
        result["criteria"][0]["quote"] = "invented implementation evidence"
        harness.write_json(path, result)
        with self.assertRaises(ValueError):
            harness.summarize(self.archive)


if __name__ == "__main__":
    unittest.main()
