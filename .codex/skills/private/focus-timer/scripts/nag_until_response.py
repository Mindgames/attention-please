#!/usr/bin/env python3
"""Repeat attention alerts until the user responds."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def get_pending_checkins_path() -> Path:
    return get_repo_root() / "operator" / "pending_checkins.json"


def get_time_log_path() -> Path:
    return get_repo_root() / "operator" / "time_log.jsonl"


def load_pending_checkins() -> list[dict[str, object]]:
    path = get_pending_checkins_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def focus_started_after(after_iso: str) -> bool:
    path = get_time_log_path()
    if not path.exists():
        return False
    after_dt = parse_iso(after_iso)
    if not after_dt:
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("event") != "focus_start":
            continue
        ts = payload.get("timestamp")
        if not isinstance(ts, str):
            continue
        parsed = parse_iso(ts)
        if parsed and parsed > after_dt:
            return True
    return False


def has_pending_session(session_id: str) -> bool:
    if not session_id:
        return False
    for entry in load_pending_checkins():
        if entry.get("session_id") == session_id:
            return True
    return False


def run_attention_notice() -> None:
    script = (
        Path.home()
        / ".codex"
        / "skills"
        / "public"
        / "attention-please"
        / "scripts"
        / "attention-please.sh"
    )
    if not script.exists():
        return
    subprocess.run(
        ["env", "ATTENTION_PLEASE_PROJECT=satcom", str(script)],
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Repeat attention alerts until response.")
    parser.add_argument("--mode", choices=["focus", "break"], required=True)
    parser.add_argument("--session-id", default="")
    parser.add_argument("--started-at", default="")
    parser.add_argument("--interval-minutes", type=int, default=5)
    args = parser.parse_args()

    interval = max(1, args.interval_minutes) * 60
    while True:
        if args.mode == "focus":
            if not has_pending_session(args.session_id):
                return 0
        else:
            if args.started_at and focus_started_after(args.started_at):
                return 0
        run_attention_notice()
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
