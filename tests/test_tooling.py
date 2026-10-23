# SPDX-License-Identifier: MIT
"""Behavioral checks for packet isolation and pinned downloads (MIT)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


prepare = module("prepare_eval").prepare
fetch = module("fetch_sources").fetch
package = module("package_skill").package


class PacketTests(unittest.TestCase):
    def test_packet_has_inputs_but_no_answer_key(self):
        with tempfile.TemporaryDirectory() as temp:
            output = prepare("candidate", Path(temp) / "packet", "11")
            cases = json.loads((output / "cases.json").read_text())
            self.assertEqual([case["id"] for case in cases], ["11"])
            self.assertEqual(set(cases[0]), {"id", "prompt", "files"})
            self.assertTrue((output / "skill/SKILL.md").is_file())
            self.assertFalse(any(p.name == "rubric.json" for p in output.rglob("*")))
            self.assertEqual((output / cases[0]["files"][0]).read_bytes(),
                             (ROOT / "evals/fixtures/11/input.rs").read_bytes())

    def test_none_condition_and_existing_packet_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            output = prepare("none", Path(temp) / "packet", "15")
            self.assertFalse((output / "skill").exists())
            with self.assertRaises(ValueError):
                prepare("none", output)
            self.assertEqual(len(json.loads((output / "cases.json").read_text())), 1)

    def test_unknown_case_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "packet"
            with self.assertRaises(ValueError):
                prepare("none", output, "99")
            self.assertFalse(output.exists())


class SourceTests(unittest.TestCase):
    def test_cached_source_is_verified_without_network(self):
        data = b"pinned\n"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "source"
            output.write_bytes(data)
            with patch("urllib.request.urlopen", side_effect=AssertionError("network called")):
                fetch("owner/repo", "a" * 40, "guide.md", output,
                      expected=hashlib.sha256(data).hexdigest())
                with self.assertRaises(ValueError):
                    fetch("owner/repo", "a" * 40, "guide.md", output, expected="0" * 64)
            self.assertEqual(output.read_bytes(), data)

    def test_mutable_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                fetch("owner/repo", "main", "guide.md", Path(temp) / "source")


class PackageTests(unittest.TestCase):
    def test_portable_licensed_package_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temp:
            first = package(Path(temp) / "first.zip")
            second = package(Path(temp) / "second.zip")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
                self.assertIn("google-rust-guidelines/NOTICE.md", names)
                self.assertIn("google-rust-guidelines/LICENSE", names)
                self.assertIn("google-rust-guidelines/SKILL.md", names)
                self.assertFalse(any("evals/" in name or ".cache/" in name for name in names))
                self.assertTrue(all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names))


if __name__ == "__main__":
    unittest.main()
