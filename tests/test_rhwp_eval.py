# SPDX-License-Identifier: MIT
"""Exercise isolation, source integrity, and failed-patch evidence retention."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rhwp_eval as harness


class IntegrationPacketTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.spec = self.root / "evals/integration"
        self.cache = self.root / ".cache/rhwp-source"
        self.source = "crates/rhwp-contracts/src/provenance.rs"
        files = {self.source: "pub fn original() {}\n",
                 "mydocs/tech/agent_runtime/version_policy.md": "Policy\n",
                 "crates/rhwp-contracts/Cargo.toml": '[package]\nname = "rhwp-contracts"\nversion = "0.1.0"\n',
                 "LICENSE": "MIT\n", "rust-toolchain.toml": '[toolchain]\nchannel = "1.93.1"\n'}
        for name, value in files.items():
            path = self.cache / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        (self.root / "provenance").mkdir()
        (self.root / "provenance/rhwp.json").write_text(json.dumps({"files": [
            {"path": name, "sha256": hashlib.sha256(value.encode()).hexdigest()}
            for name, value in files.items()]}))
        (self.spec / "workspace").mkdir(parents=True)
        (self.spec / "workspace/Cargo.toml").write_text('[workspace]\nmembers = ["crates/rhwp-contracts"]\n')
        (self.spec / "workspace/Cargo.lock").write_text("version = 4\n")
        (self.spec / "cases.json").write_text(json.dumps({"cases": [{
            "id": "R1", "title": "Task", "prompt": "Add an API", "source_file": self.source,
            "oracle": "secret.rs"}]}))
        (self.spec / "rubric.json").write_text('{"answer":"private"}')
        (self.spec / "oracles").mkdir()
        (self.spec / "oracles/secret.rs").write_text("private expected answer")
        self.addCleanup(patch.stopall)
        patch.multiple(harness, ROOT=self.root, SPEC=self.spec, CACHE=self.cache).start()

    def test_only_task_inputs_enter_packet(self):
        packet = harness.prepare("none", "R1", self.root / "packet")
        names = harness.inventory(packet)
        self.assertNotIn("oracle", harness.read_json(packet / "case.json"))
        self.assertFalse(any("rubric" in name or "secret" in name for name in names))
        self.assertNotIn("skill/SKILL.md", names)
        self.assertEqual((packet / "workspace" / self.source).read_bytes(),
                         (self.cache / self.source).read_bytes())
        with self.assertRaises(ValueError):
            harness.prepare("none", "R1", packet)

    def test_corrupted_source_is_rejected_before_packet_creation(self):
        (self.cache / self.source).write_text("corrupted")
        with self.assertRaises(ValueError):
            harness.prepare("none", "R1", self.root / "packet")
        self.assertFalse((self.root / "packet").exists())

    def test_scope_failure_preserves_patch_without_running_cargo(self):
        (self.cache / "Cargo.toml").write_text("unrelated upstream root workspace\n")
        packet = harness.prepare("none", "R1", self.root / "packet")
        (packet / "workspace/Cargo.toml").write_text("[workspace]\nmembers = []\n")
        result_dir = self.root / "result"
        result = harness.assess(packet, result_dir)
        self.assertFalse(result["automated_pass"])
        self.assertIn("Cargo.toml", result["scope_errors"])
        self.assertEqual(set(result["commands"]), {"patch_check"})
        self.assertIn("members = []", (result_dir / "patch.diff").read_text())
        self.assertNotIn("unrelated upstream", (result_dir / "patch.diff").read_text())
        self.assertTrue((result_dir / "packet-manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
