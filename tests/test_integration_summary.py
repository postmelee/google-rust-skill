# SPDX-License-Identifier: MIT
"""Ensure reported success cannot silently outlive its frozen evidence."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from summarize_integration import summarize

RESULTS = Path(__file__).resolve().parents[1] / "evals/results/rhwp-2026-10-23"


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.copy = Path(self.temporary.name) / "results"
        shutil.copytree(RESULTS, self.copy)

    def test_changed_frozen_task_is_rejected(self):
        path = self.copy / "frozen/evals/integration/cases.json"
        path.write_text(path.read_text() + " ")
        with self.assertRaises(ValueError):
            summarize(self.copy)

    def test_failed_build_cannot_keep_a_passing_aggregate(self):
        path = self.copy / "R1/candidate/assessment.json"
        result = json.loads(path.read_text())
        result["commands"]["build"]["exit_code"] = 1
        path.write_text(json.dumps(result))
        with self.assertRaises(ValueError):
            summarize(self.copy)

    def test_review_quote_must_exist_in_the_actual_patch(self):
        path = self.copy / "R1/candidate/manual-review.json"
        result = json.loads(path.read_text())
        result["criteria"][0]["evidence"] = "fabricated evidence that is not in the patch"
        path.write_text(json.dumps(result))
        with self.assertRaises(ValueError):
            summarize(self.copy)


if __name__ == "__main__":
    unittest.main()
