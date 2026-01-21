#!/usr/bin/env python3
"""Summarize focus timer logs by day and topic."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root based on this module's location."""
    return Path(__file__).resolve().parents[1]


def get_time_log_path() -> Path:
    """Return the path for the focus timer log."""
    return get_project_root() / "operator" / "time_log.jsonl"


def parse_timestamp(value: str) -> datetime | None:
    """Parse an ISO timestamp into a datetime."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_events() -> list[dict[str, object]]:
    """Load log events from disk."""
    path = get_time_log_path()
    if not path.exists():
        return []
    events: list[dict[str, object]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    return events


def format_duration(seconds: float) -> str:
    """Format seconds into a compact human-readable string."""
    total_seconds = max(0, int(round(seconds)))
    minutes, remainder = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def summarize(
    events: list[dict[str, object]],
    target_date: date,
    include_breaks: bool,
) -> dict[tuple[str, str], float]:
    """Aggregate totals by category and topic."""
    totals: dict[tuple[str, str], float] = {}
    for event in events:
        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        parsed = parse_timestamp(timestamp)
        if not parsed or parsed.date() != target_date:
            continue
        event_type = event.get("event")
        if event_type == "focus_end":
            category = "focus"
        elif event_type == "break_end":
            if not include_breaks:
                continue
            category = "break"
        else:
            continue

        elapsed = event.get("elapsed_seconds")
        if not isinstance(elapsed, (int, float)):
            continue
        topic = event.get("topic") or "unspecified"
        key = (category, str(topic))
        totals[key] = totals.get(key, 0.0) + float(elapsed)
    return totals


def render_summary(
    totals: dict[tuple[str, str], float],
    target_date: date,
) -> None:
    """Print a summary report."""
    if not totals:
        print(f"No time entries for {target_date.isoformat()}.")
        return
    print(f"Time summary for {target_date.isoformat()}:")
    sorted_items = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    for (category, topic), seconds in sorted_items:
        print(f"- {category} :: {topic} :: {format_duration(seconds)}")


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Summarize focus timer logs by day and topic."
    )
    parser.add_argument(
        "--date",
        default="",
        help="Date to summarize (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--include-breaks",
        action="store_true",
        help="Include break time in the summary.",
    )
    return parser


def main() -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return 1
    else:
        target_date = datetime.now().astimezone().date()

    totals = summarize(load_events(), target_date, args.include_breaks)
    render_summary(totals, target_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
