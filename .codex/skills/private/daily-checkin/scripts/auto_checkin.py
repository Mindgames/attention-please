#!/usr/bin/env python3
"""Automatically run daily check-ins based on time and focus activity."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path


@dataclass(frozen=True)
class CheckinWindow:
    """Time window for a check-in."""

    start: dt_time
    end: dt_time

    def contains(self, target: dt_time) -> bool:
        """Return True if the time is within the window."""
        if self.start <= self.end:
            return self.start <= target <= self.end
        return target >= self.start or target <= self.end


def get_repo_root() -> Path:
    """Return the repository root based on the .codex directory when possible."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def load_jsonl(path: Path) -> list[dict[str, object]]:
    """Load JSONL entries."""
    if not path.exists():
        return []
    entries: list[dict[str, object]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            entries.append(payload)
    return entries


def parse_iso_datetime(value: str) -> datetime | None:
    """Parse an ISO timestamp into a datetime."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_time(value: str) -> dt_time:
    """Parse a HH:MM string into a time."""
    try:
        return datetime.strptime(value.strip(), "%H:%M").time()
    except ValueError as exc:
        raise ValueError(f"Invalid time format: {value}") from exc


def parse_window(value: str) -> CheckinWindow:
    """Parse a start-end window string."""
    if "-" not in value:
        raise ValueError(f"Invalid window format: {value}")
    raw_start, raw_end = value.split("-", 1)
    return CheckinWindow(start=parse_time(raw_start), end=parse_time(raw_end))


def load_config(path: Path) -> dict[str, object]:
    """Load config file if it exists."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def get_state_log_path() -> Path:
    """Return the state log path."""
    return get_repo_root() / "operator" / "state_log.jsonl"


def get_time_log_path() -> Path:
    """Return the focus time log path."""
    return get_repo_root() / "operator" / "time_log.jsonl"


def get_guard_state_path() -> Path:
    """Return the guard state path."""
    return get_repo_root() / "operator" / "daily_checkin_state.json"


def load_guard_state(path: Path) -> dict[str, object]:
    """Load guard state."""
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def save_guard_state(path: Path, payload: dict[str, object]) -> None:
    """Persist guard state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2))


def todays_checkins(target_date: date) -> set[str]:
    """Return which check-ins already exist today."""
    entries = load_jsonl(get_state_log_path())
    modes: set[str] = set()
    for entry in entries:
        timestamp = entry.get("timestamp")
        mode = entry.get("mode")
        if not isinstance(timestamp, str) or not isinstance(mode, str):
            continue
        parsed = parse_iso_datetime(timestamp)
        if parsed and parsed.date() == target_date:
            modes.add(mode)
    return modes


def focus_stats(target_date: date) -> tuple[int, datetime | None, bool]:
    """Return focus count, last focus end time, and focus activity indicator."""
    entries = load_jsonl(get_time_log_path())
    focus_count = 0
    last_focus_end = None
    has_focus_activity = False
    for entry in entries:
        timestamp = entry.get("timestamp")
        event = entry.get("event")
        if not isinstance(timestamp, str) or not isinstance(event, str):
            continue
        parsed = parse_iso_datetime(timestamp)
        if not parsed or parsed.date() != target_date:
            continue
        if event == "focus_start":
            has_focus_activity = True
        if event == "focus_end":
            focus_count += 1
            has_focus_activity = True
            if last_focus_end is None or parsed > last_focus_end:
                last_focus_end = parsed
    return focus_count, last_focus_end, has_focus_activity


def should_prompt(
    mode: str,
    guard_state: dict[str, object],
    cooldown_minutes: int,
    now: datetime,
) -> bool:
    """Return True if the guard should prompt again."""
    last_prompted = guard_state.get("last_prompted", {})
    if not isinstance(last_prompted, dict):
        return True
    timestamp = last_prompted.get(mode)
    if not isinstance(timestamp, str):
        return True
    parsed = parse_iso_datetime(timestamp)
    if not parsed:
        return True
    return now - parsed >= timedelta(minutes=cooldown_minutes)


def mark_prompted(
    guard_state: dict[str, object],
    mode: str,
    now: datetime,
) -> dict[str, object]:
    """Update guard state with a prompt timestamp."""
    updated = dict(guard_state)
    last_prompted = updated.get("last_prompted")
    if not isinstance(last_prompted, dict):
        last_prompted = {}
    last_prompted[mode] = now.isoformat()
    updated["last_prompted"] = last_prompted
    updated["date"] = now.date().isoformat()
    return updated


def run_daily_checkin(mode: str, no_prompt: bool) -> int:
    """Run the daily check-in script."""
    script = Path(__file__).resolve().parent / "daily_checkin.py"
    command = [
        "python3",
        str(script),
        "--mode",
        mode,
    ]
    if no_prompt:
        command.append("--no-prompt")
    result = subprocess.run(command, check=False)
    return result.returncode


def run_attention_notice() -> None:
    """Play attention notice with a fixed project label."""
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
        [
            "env",
            "ATTENTION_PLEASE_PROJECT=satcom",
            str(script),
        ],
        check=False,
    )


def evaluate_due_modes(
    now: datetime,
    checkins_done: set[str],
    focus_count: int,
    last_focus_end: datetime | None,
    has_focus_activity: bool,
    start_window: CheckinWindow,
    mid_window: CheckinWindow,
    end_window: CheckinWindow,
    mid_after_focus: int,
    idle_minutes_for_end: int,
    enabled_modes: set[str] | None,
    start_on_focus_activity: bool,
) -> list[str]:
    """Return modes that should trigger now."""
    modes: list[str] = []
    current_time = now.time()

    def is_enabled(mode: str) -> bool:
        return enabled_modes is None or mode in enabled_modes

    if is_enabled("start") and "start" not in checkins_done:
        if start_window.contains(current_time) or (
            start_on_focus_activity and has_focus_activity
        ):
            modes.append("start")

    if is_enabled("mid") and "mid" not in checkins_done:
        if focus_count >= mid_after_focus or mid_window.contains(current_time):
            if has_focus_activity or "start" in checkins_done:
                modes.append("mid")

    if is_enabled("end") and "end" not in checkins_done:
        end_due = end_window.contains(current_time)
        idle_due = False
        if last_focus_end:
            idle_due = now - last_focus_end >= timedelta(minutes=idle_minutes_for_end)
        if end_due or idle_due:
            if has_focus_activity:
                modes.append("end")

    return modes


def run_checkins(
    modes: list[str],
    guard_state: dict[str, object],
    cooldown_minutes: int,
    no_prompt: bool,
    notify_only: bool,
    now: datetime,
) -> dict[str, object]:
    """Execute due check-ins and update guard state."""
    updated_state = dict(guard_state)
    for mode in modes:
        if not should_prompt(mode, guard_state, cooldown_minutes, now):
            continue
        if notify_only:
            run_attention_notice()
        else:
            run_daily_checkin(mode, no_prompt)
        updated_state = mark_prompted(updated_state, mode, now)
    return updated_state


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Automatically run daily check-ins based on time windows."
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run continuously.",
    )
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=5,
        help="Loop interval in minutes (default: 5).",
    )
    parser.add_argument(
        "--config",
        default="",
        help="Optional path to a JSON config file.",
    )
    parser.add_argument(
        "--start-window",
        default="06:00-11:30",
        help="Start check-in window (default: 06:00-11:30).",
    )
    parser.add_argument(
        "--mid-window",
        default="12:00-16:00",
        help="Midday check-in window (default: 12:00-16:00).",
    )
    parser.add_argument(
        "--end-window",
        default="18:00-23:30",
        help="End check-in window (default: 18:00-23:30).",
    )
    parser.add_argument(
        "--mid-after-focus",
        type=int,
        default=2,
        help="Trigger mid check-in after this many focus sessions.",
    )
    parser.add_argument(
        "--idle-minutes-for-end",
        type=int,
        default=90,
        help="Trigger end check-in after this many idle minutes.",
    )
    parser.add_argument(
        "--cooldown-minutes",
        type=int,
        default=60,
        help="Minimum minutes between prompts per mode.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip interactive prompts when running check-ins.",
    )
    parser.add_argument(
        "--notify-only",
        action="store_true",
        help="Only notify with attention alert, do not run check-ins.",
    )
    parser.add_argument(
        "--enabled-modes",
        default="",
        help="Comma-separated list of modes to notify/run (e.g. start,mid,end). Defaults to all.",
    )
    parser.add_argument(
        "--start-on-focus-activity",
        action="store_true",
        help="Trigger start check-in after any focus activity (default when unset in config).",
    )
    return parser


def apply_config(
    args: argparse.Namespace,
    config: dict[str, object],
) -> dict[str, object]:
    """Apply config overrides and return config dict."""
    return {
        "start_window": config.get("start_window", args.start_window),
        "mid_window": config.get("mid_window", args.mid_window),
        "end_window": config.get("end_window", args.end_window),
        "mid_after_focus": int(config.get("mid_after_focus", args.mid_after_focus)),
        "idle_minutes_for_end": int(
            config.get("idle_minutes_for_end", args.idle_minutes_for_end)
        ),
        "cooldown_minutes": int(config.get("cooldown_minutes", args.cooldown_minutes)),
        "enabled_modes": config.get("enabled_modes", args.enabled_modes),
        "start_on_focus_activity": bool(
            config.get("start_on_focus_activity", args.start_on_focus_activity)
        ),
    }


def normalize_enabled_modes(raw: object) -> set[str] | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, list):
        modes = [str(m).strip().lower() for m in raw if str(m).strip()]
        return set(modes) if modes else None
    if isinstance(raw, str):
        modes = [m.strip().lower() for m in raw.split(",") if m.strip()]
        return set(modes) if modes else None
    return None


def main() -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else get_repo_root() / "operator" / "daily_checkin_config.json"
    config = load_config(config_path)
    settings = apply_config(args, config)
    enabled_modes = normalize_enabled_modes(settings.get("enabled_modes"))
    start_on_focus_activity = bool(settings.get("start_on_focus_activity", True))

    start_window = parse_window(str(settings["start_window"]))
    mid_window = parse_window(str(settings["mid_window"]))
    end_window = parse_window(str(settings["end_window"]))

    interval = max(1, args.interval_minutes)
    guard_state_path = get_guard_state_path()

    while True:
        now = datetime.now().astimezone()
        target_date = now.date()
        guard_state = load_guard_state(guard_state_path)
        if guard_state.get("date") != target_date.isoformat():
            guard_state = {}
        checkins_done = todays_checkins(target_date)
        focus_count, last_focus_end, has_focus_activity = focus_stats(target_date)

        due_modes = evaluate_due_modes(
            now,
            checkins_done,
            focus_count,
            last_focus_end,
            has_focus_activity,
            start_window,
            mid_window,
            end_window,
            int(settings["mid_after_focus"]),
            int(settings["idle_minutes_for_end"]),
            enabled_modes,
            start_on_focus_activity,
        )

        updated_state = run_checkins(
            due_modes,
            guard_state,
            int(settings["cooldown_minutes"]),
            args.no_prompt,
            args.notify_only,
            now,
        )
        if updated_state != guard_state:
            save_guard_state(guard_state_path, updated_state)

        if not args.loop:
            break
        time.sleep(interval * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
