#!/usr/bin/env python3
# cspell:words Flathub
"""Render Homebrew and Flathub metadata from immutable release assets."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def asset(directory: Path, pattern: str) -> Path:
    matches = list(directory.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {pattern!r} asset, found {len(matches)}")
    return matches[0]


def render_homebrew(template: Path, assets: Path, repository: str, tag: str, version: str) -> str:
    values: dict[str, str] = {"VERSION": version}
    for key, pattern in {
        "MACOS_ARM64": "*macos-arm64*.tar.gz",
        "MACOS_X64": "*macos-x64*.tar.gz",
        "LINUX_ARM64": "*linux-arm64*.tar.gz",
        "LINUX_X64": "*linux-x64*.tar.gz",
    }.items():
        path = asset(assets, pattern)
        values[f"{key}_URL"] = f"https://github.com/{repository}/releases/download/{tag}/{path.name}"
        values[f"{key}_SHA256"] = sha256(path)
    rendered = template.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace(f"@{key}@", value)
    leftovers = re.findall(r"@[A-Z0-9_]+@", rendered)
    if leftovers:
        raise RuntimeError(f"unresolved Homebrew placeholders: {leftovers}")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--homebrew-template", required=True, type=Path)
    parser.add_argument("--homebrew-output", required=True, type=Path)
    args = parser.parse_args()
    rendered = render_homebrew(
        args.homebrew_template, args.assets, args.repository, args.tag, args.version
    )
    args.homebrew_output.parent.mkdir(parents=True, exist_ok=True)
    args.homebrew_output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
