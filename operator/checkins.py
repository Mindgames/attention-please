#!/usr/bin/env python3
"""Record progress and next tasks for completed focus sessions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root based on this module's location."""
    return Path(__file__).resolve().parents[1]


def get_pending_path() -> Path:
    """Return the path for pending check-ins."""
    return get_project_root() / "operator" / "pending_checkins.json"


def get_progress_path() -> Path:
    """Return the path for the progress log."""
    return get_project_root() / "operator" / "progress_log.jsonl"


def load_pending() -> list[dict[str, object]]:
    """Load pending check-ins from disk."""
    path = get_pending_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def save_pending(entries: list[dict[str, object]]) -> None:
    """Persist pending check-ins to disk."""
    path = get_pending_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=True, indent=2))


def append_progress(entry: dict[str, object]) -> None:
    """Append a progress entry to the JSONL log."""
    path = get_progress_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def infer_project(topic: str) -> str:
    """Infer a project label from a topic string."""
    if ":" in topic:
        head = topic.split(":", 1)[0].strip()
        return head
    return ""


def format_pending(entry: dict[str, object]) -> str:
    """Format a pending check-in entry for display."""
    session_id = entry.get("session_id", "unknown")
    topic = entry.get("topic") or "unspecified"
    started_at = entry.get("started_at", "unknown")
    ended_at = entry.get("ended_at", "unknown")
    minutes = entry.get("planned_focus_minutes", "unknown")
    return (
        f"- session_id={session_id} topic={topic} "
        f"planned={minutes}m started={started_at} ended={ended_at}"
    )


def list_pending(entries: list[dict[str, object]]) -> None:
    """Print pending check-ins."""
    if not entries:
        print("No pending check-ins.")
        return
    print("Pending check-ins:")
    for entry in entries:
        print(format_pending(entry))


def select_entry(
    entries: list[dict[str, object]],
    session_id: str,
    latest: bool,
) -> dict[str, object]:
    """Select a pending entry by id or latest."""
    if not entries:
        raise ValueError("No pending check-ins.")
    if latest:
        return entries[-1]
    for entry in entries:
        if entry.get("session_id") == session_id:
            return entry
    raise ValueError(f"Session id not found: {session_id}")


def complete_checkin(args: argparse.Namespace) -> int:
    """Record a completed check-in and remove it from the pending list."""
    entries = load_pending()
    if not entries:
        print("No pending check-ins.")
        return 0
    try:
        entry = select_entry(entries, args.session_id, args.latest)
    except ValueError as exc:
        print(str(exc))
        return 1

    summary = args.summary.strip()
    next_tasks = [task.strip() for task in args.next_task if task.strip()]
    if not summary:
        print("Summary is required.")
        return 1
    if not next_tasks:
        print("At least one next task is required.")
        return 1

    topic = str(entry.get("topic") or "")
    project = args.project.strip() or infer_project(topic)
    progress_entry = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "session_id": entry.get("session_id"),
        "topic": topic,
        "project": project,
        "summary": summary,
        "next_tasks": next_tasks,
        "notes": args.notes.strip() if args.notes else "",
        "planned_focus_minutes": entry.get("planned_focus_minutes"),
        "planned_break_minutes": entry.get("planned_break_minutes"),
        "started_at": entry.get("started_at"),
        "ended_at": entry.get("ended_at"),
    }
    append_progress(progress_entry)

    remaining = [
        item
        for item in entries
        if item.get("session_id") != entry.get("session_id")
    ]
    save_pending(remaining)
    print(f"Recorded progress for session {entry.get('session_id')}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Record progress for completed focus sessions."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List pending check-ins.")

    complete_parser = subparsers.add_parser(
        "complete", help="Complete a pending check-in."
    )
    complete_parser.add_argument(
        "--session-id",
        default="",
        help="Session id to complete.",
    )
    complete_parser.add_argument(
        "--latest",
        action="store_true",
        help="Complete the most recent pending check-in.",
    )
    complete_parser.add_argument(
        "--summary",
        default="",
        help="What was accomplished during the session.",
    )
    complete_parser.add_argument(
        "--next-task",
        action="append",
        default=[],
        help="Next task to plan (repeatable).",
    )
    complete_parser.add_argument(
        "--project",
        default="",
        help="Optional project label override.",
    )
    complete_parser.add_argument(
        "--notes",
        default="",
        help="Optional extra notes.",
    )
    return parser


def main() -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "list"):
        list_pending(load_pending())
        return 0
    if args.command == "complete":
        if not (args.latest or args.session_id):
            print("Provide --latest or --session-id to complete a check-in.")
            return 1
        return complete_checkin(args)

    print("Unknown command.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
