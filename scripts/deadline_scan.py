#!/usr/bin/env python3
"""Run the deadline scan script from the private Codex skills bundle."""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    target = (
        repo_root
        / ".codex"
        / "skills"
        / "private"
        / "deadline-guard"
        / "scripts"
        / "deadline_scan.py"
    )
    if not target.exists():
        sys.stderr.write(f"Missing script: {target}\n")
        raise SystemExit(1)
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
