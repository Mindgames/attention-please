#!/usr/bin/env python3
"""Log an off-grid gap and a light restart note."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path


def get_repo_root() -> Path:
    """Return the repository root based on the .codex directory when possible."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def get_notes_dir() -> Path:
    """Return the daily notes directory."""
    return get_repo_root() / "operator" / "daily_notes"


def get_note_path(target_date: date) -> Path:
    """Return the note path for a date."""
    return get_notes_dir() / f"{target_date.isoformat()}.md"


def ensure_note_header(path: Path, target_date: date) -> None:
    """Ensure a note file exists with a header."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Daily Note: {target_date.isoformat()}\n", encoding="utf-8")


def append_section(path: Path, title: str, lines: list[str]) -> None:
    """Append a markdown section with bullet lines."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {title}\n\n")
        if lines:
            for line in lines:
                handle.write(f"- {line}\n")
        else:
            handle.write("- (none)\n")


def append_state_log(payload: dict[str, object]) -> None:
    """Append a structured state log entry."""
    path = get_repo_root() / "operator" / "state_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def prompt_text(label: str) -> str:
    """Prompt for a single line of text."""
    return input(label).strip()


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Log an off-grid gap and a light restart note."
    )
    parser.add_argument(
        "--date",
        default="",
        help="Date for the note (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--days",
        default="",
        help="Approximate days off-grid.",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Short reason for the gap.",
    )
    parser.add_argument(
        "--next-start",
        default="",
        help="Optional next start cue (free text).",
    )
    parser.add_argument(
        "--next-task",
        default="",
        help="Next light task to restart.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Additional notes.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip interactive prompts and log placeholders.",
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

    if args.no_prompt:
        days = args.days
        reason = args.reason
        next_start = args.next_start
        next_task = args.next_task
        notes = args.notes
    else:
        # Keep prompts date-free and minimal to reduce friction.
        days = args.days or prompt_text("Days off-grid (approx): ")
        reason = args.reason or prompt_text("Reason (short): ")
        next_start = args.next_start
        next_task = args.next_task or prompt_text("Next light task: ")
        notes = args.notes or prompt_text("Notes (optional): ")

    lines: list[str] = []
    if days:
        lines.append(f"Days off-grid: {days}")
    if reason:
        lines.append(f"Reason: {reason}")
    if next_start:
        lines.append(f"Next start cue: {next_start}")
    if next_task:
        lines.append(f"Next light task: {next_task}")
    if notes:
        lines.append(f"Notes: {notes}")

    note_path = get_note_path(target_date)
    ensure_note_header(note_path, target_date)
    append_section(note_path, "Gap Note", lines)

    payload = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "mode": "gap",
        "days_off_grid": days,
        "reason": reason,
        "next_start": next_start,
        "next_task": next_task,
        "notes": notes,
    }
    append_state_log(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
