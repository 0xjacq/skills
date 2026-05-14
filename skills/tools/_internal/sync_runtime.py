#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path


def main() -> int:
    internal_root = Path(__file__).resolve().parent / "python_runtime"
    tools_root = Path(__file__).resolve().parents[1]
    targets = [
        tools_root / "build-or-not" / "scripts",
        tools_root / "find-tools" / "scripts",
    ]
    packages = ["diligence", "prebuild_engine"]

    for target in targets:
        target.mkdir(parents=True, exist_ok=True)
        for package in packages:
            source = internal_root / package
            destination = target / package
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
