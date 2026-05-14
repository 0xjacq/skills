#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEPS = [
    "hishel[httpx]>=0.1.3",
    "httpx>=0.27",
    "pydantic>=2.7",
    "rich>=13.7",
    "typer>=0.12",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local build-or-not runtime.")
    parser.add_argument("capability", help="Capability, product idea, or tool concept to assess.")
    parser.add_argument("--limit", type=int, default=8, help="Maximum leading candidates to keep.")
    parser.add_argument("--json", action="store_true", help="Print the raw runtime JSON result.")
    args = parser.parse_args()

    payload = run_runtime(args.capability, limit=args.limit)
    if payload is None:
        return 1
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Verdict: {payload['verdict']}")
    print(f"Confidence: {payload['confidence']}")
    print(f"Rationale: {payload['verdict_rationale']}")
    print(f"HTML report: {payload['artifacts']['html_report']}")
    print(f"JSON result: {payload['artifacts']['result_json']}")
    print(f"Audit bundle: {payload['artifacts']['audit_bundle']}")
    if payload.get("warnings"):
        print("Warnings:")
        for warning in payload["warnings"]:
            print(f"- {warning}")
    return 0


def run_runtime(capability: str, *, limit: int) -> dict | None:
    scripts_dir = Path(__file__).resolve().parent
    env = os.environ.copy()
    env["PYTHONPATH"] = str(scripts_dir) + os.pathsep + env.get("PYTHONPATH", "")
    runtime_args = [
        "python",
        "-m",
        "prebuild_engine",
        "build-or-not",
        capability,
        "--limit",
        str(limit),
        "--artifacts-root",
        str(Path.cwd()),
        "--json",
    ]

    if shutil.which("uv") is not None:
        command = ["uv", "run"]
        for dep in DEPS:
            command.extend(["--with", dep])
        command.extend(runtime_args)
    else:
        command = [sys.executable, "-m", "prebuild_engine", "build-or-not", capability, "--limit", str(limit), "--artifacts-root", str(Path.cwd()), "--json"]

    completed = subprocess.run(command, capture_output=True, text=True, env=env)
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr or completed.stdout)
        return None
    return json.loads(completed.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
