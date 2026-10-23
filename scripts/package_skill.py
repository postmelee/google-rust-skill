#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a deterministic, self-contained runtime ZIP."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/google-rust-guidelines"


def package(output):
    output = Path(output).resolve()
    if output.is_relative_to(SKILL):
        raise ValueError("Write release archives outside the skill directory")
    for required in ["SKILL.md", "NOTICE.md", "LICENSE"]:
        if not (SKILL / required).is_file():
            raise ValueError(f"Missing runtime file: {required}")
    files = []
    for path in sorted(SKILL.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Runtime package must not contain symlinks: {path}")
        if path.is_file() and not any(p.startswith(".") for p in path.relative_to(SKILL).parts):
            files.append(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(str(Path(SKILL.name) / path.relative_to(SKILL)))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".cache/dist/google-rust-guidelines.zip")
    args = parser.parse_args()
    print(package(args.output))
