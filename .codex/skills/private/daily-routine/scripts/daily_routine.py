#!/usr/bin/env python3
"""Start or refresh the satcom daily automation routine."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_repo_root() -> Path:
    """Return the repository root based on the .codex directory when possible."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def load_json(path: Path) -> dict[str, object]:
    """Load JSON data from disk."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def save_json(path: Path, payload: dict[str, object]) -> None:
    """Persist JSON data to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2))


def read_pid(path: Path) -> int | None:
    """Read a PID file."""
    if not path.exists():
        return None
    try:
        return int(path.read_text().strip())
    except ValueError:
        return None


def write_pid(path: Path, pid: int) -> None:
    """Write a PID file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{pid}\n")


def is_process_running(pid: int) -> bool:
    """Return True if a process with pid is alive."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def process_command(pid: int) -> str:
    """Return the command line for a pid."""
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def is_auto_checkin_process(pid: int) -> bool:
    """Return True if the pid matches the auto_checkin process."""
    command = process_command(pid)
    return "auto_checkin.py" in command


def detect_auto_checkin(pid_path: Path) -> tuple[bool, int | None]:
    """Detect whether auto_checkin is already running."""
    pid = read_pid(pid_path)
    if pid is None:
        return False, None
    if not is_process_running(pid):
        return False, None
    if not is_auto_checkin_process(pid):
        return False, None
    return True, pid


def start_auto_checkin(
    repo_root: Path,
    interval_minutes: int,
    notify_only: bool,
    config_path: Path,
    log_path: Path,
) -> int:
    """Start auto_checkin in the background and return the pid."""
    script = (
        repo_root
        / ".codex"
        / "skills"
        / "private"
        / "daily-checkin"
        / "scripts"
        / "auto_checkin.py"
    )
    if not script.exists():
        raise FileNotFoundError(f"Missing auto_checkin script at {script}")

    command = [
        sys.executable,
        str(script),
        "--loop",
        "--interval-minutes",
        str(interval_minutes),
    ]
    if config_path.exists():
        command.extend(["--config", str(config_path)])
    if notify_only:
        command.append("--notify-only")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            command,
            stdout=log_handle,
            stderr=log_handle,
            start_new_session=True,
        )
    return int(process.pid)


def run_start_checkin(repo_root: Path, no_prompt: bool) -> int:
    """Run the start-of-day check-in."""
    script = (
        repo_root
        / ".codex"
        / "skills"
        / "private"
        / "daily-checkin"
        / "scripts"
        / "daily_checkin.py"
    )
    if not script.exists():
        raise FileNotFoundError(f"Missing daily_checkin script at {script}")

    command = [
        sys.executable,
        str(script),
        "--mode",
        "start",
    ]
    if no_prompt:
        command.append("--no-prompt")
    result = subprocess.run(command, check=False)
    return int(result.returncode)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Start or refresh the satcom daily routine automation."
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=5,
        help="Auto-checkin loop interval in minutes (default: 5).",
    )
    parser.add_argument(
        "--prompt-checkins",
        action="store_true",
        help="Run auto-checkin with prompts instead of notify-only.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip prompts when running the start-of-day check-in.",
    )
    parser.add_argument(
        "--start-checkin",
        action="store_true",
        help="Run the start-of-day check-in now.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Restart auto-checkin even if it appears to be running.",
    )
    parser.add_argument(
        "--config",
        default="",
        help="Optional path to daily_checkin_config.json.",
    )
    parser.add_argument(
        "--log-path",
        default="",
        help="Optional path for auto-checkin output log.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Only report current status without starting anything.",
    )
    return parser


def main() -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    repo_root = get_repo_root()
    now = datetime.now().astimezone()
    today = now.date().isoformat()

    state_path = repo_root / "operator" / "daily_routine_state.json"
    pid_path = repo_root / "operator" / "auto_checkin.pid"
    log_path = (
        Path(args.log_path)
        if args.log_path
        else repo_root / "operator" / "auto_checkin.log"
    )
    config_path = (
        Path(args.config)
        if args.config
        else repo_root / "operator" / "daily_checkin_config.json"
    )

    state = load_json(state_path)
    was_new_day = state.get("date") != today

    running, pid = detect_auto_checkin(pid_path)

    if args.status:
        status = "running" if running else "stopped"
        print(f"Auto-checkin status: {status}")
        if pid:
            print(f"PID: {pid}")
        if state.get("date"):
            print(f"Last routine date: {state.get('date')}")
        return 0

    notify_only = not args.prompt_checkins
    auto_started = False
    auto_pid = pid

    if args.force or not running:
        auto_pid = start_auto_checkin(
            repo_root=repo_root,
            interval_minutes=max(1, args.interval_minutes),
            notify_only=notify_only,
            config_path=config_path,
            log_path=log_path,
        )
        write_pid(pid_path, auto_pid)
        auto_started = True

    if was_new_day:
        state["date"] = today
        state["pending_start_checkin"] = True

    if args.start_checkin:
        result = run_start_checkin(repo_root, args.no_prompt)
        if result == 0:
            state["pending_start_checkin"] = False
        else:
            print("Start check-in failed.")

    auto_state: dict[str, object] = {}
    if isinstance(state.get("auto_checkin"), dict):
        auto_state = dict(state.get("auto_checkin", {}))

    if auto_started and auto_pid is not None:
        auto_state.update(
            {
                "pid": auto_pid,
                "started_at": now.isoformat(),
                "interval_minutes": max(1, args.interval_minutes),
                "notify_only": notify_only,
                "config_path": str(config_path),
                "log_path": str(log_path),
            }
        )
    elif auto_pid is not None:
        auto_state["pid"] = auto_pid

    auto_state["last_seen_at"] = now.isoformat()
    state["auto_checkin"] = auto_state
    state["last_run_at"] = now.isoformat()

    save_json(state_path, state)

    if auto_started:
        print(f"Auto-checkin started (pid {auto_pid}).")
    else:
        print("Auto-checkin already running.")

    if state.get("pending_start_checkin"):
        print("Start-of-day check-in is pending.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
