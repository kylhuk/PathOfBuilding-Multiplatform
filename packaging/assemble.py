#!/usr/bin/env python3
"""Combine an upstream Path of Building checkout with a staged SimpleGraphic runtime."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import stat


SOURCE_EXCLUDES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "spec",
    "tests",
    "__pycache__",
}


def copy_source(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*SOURCE_EXCLUDES),
    )


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def unix_launcher() -> str:
    return """#!/bin/sh
set -eu
root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$root"
exec "$root/PathOfBuilding-runtime" "$root/src/Launch.lua" "$@"
"""


def macos_launcher() -> str:
    return """#!/bin/sh
set -eu
resources="$(CDPATH= cd -- "$(dirname -- "$0")/../Resources" && pwd)"
cd "$resources/app"
exec "$resources/app/PathOfBuilding-runtime" "$resources/app/src/Launch.lua" "$@"
"""


def assemble(runtime: Path, source: Path, output: Path, platform: str) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    if platform == "macos":
        app = output / "Path of Building.app"
        payload = app / "Contents" / "Resources" / "app"
        payload.mkdir(parents=True)
        shutil.copytree(runtime, payload, dirs_exist_ok=True, symlinks=True)
        copy_source(source, payload)
        (payload / "installed.cfg").touch()
        host = payload / "PathOfBuilding-SimpleGraphic"
        host.rename(payload / "PathOfBuilding-runtime")
        launcher = app / "Contents" / "MacOS" / "Path of Building"
        launcher.parent.mkdir(parents=True)
        launcher.write_text(macos_launcher(), encoding="utf-8")
        make_executable(launcher)
        (app / "Contents" / "Info.plist").write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleExecutable</key><string>Path of Building</string>
  <key>CFBundleIdentifier</key><string>community.pathofbuilding.PathOfBuilding</string>
  <key>CFBundleName</key><string>Path of Building</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
""",
            encoding="utf-8",
        )
        return

    shutil.copytree(runtime, output, dirs_exist_ok=True, symlinks=True)
    copy_source(source, output)
    (output / "installed.cfg").touch()
    if platform == "windows":
        host = output / "PathOfBuilding-SimpleGraphic.exe"
        host.rename(output / "PathOfBuilding-runtime.exe")
    else:
        host = output / "PathOfBuilding-SimpleGraphic"
        host.rename(output / "PathOfBuilding-runtime")
        launcher = output / "pathofbuilding"
        launcher.write_text(unix_launcher(), encoding="utf-8")
        make_executable(launcher)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--platform", required=True, choices=("windows", "linux", "macos"))
    args = parser.parse_args()
    assemble(
        args.runtime.resolve(),
        args.source.resolve(),
        args.output.resolve(),
        args.platform,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
