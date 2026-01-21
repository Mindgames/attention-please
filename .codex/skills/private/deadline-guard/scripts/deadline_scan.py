#!/usr/bin/env python3
"""
Scan satcom tasks and project docs for due dates and milestones.

Outputs categories: overdue, due soon, due this week, and optional missing due dates.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
DUE_RE = re.compile(r"\bdue=([^\s;]+)")
PROJECT_RE = re.compile(r"\bproject=([a-z0-9-]+)")
TARGET_RE = re.compile(r"\b(?:Target|target):\s*(\d{4}-\d{2}-\d{2})")
NAME_RE = re.compile(r"\b(?:Name|name):\s*(.+)")


@dataclass(frozen=True)
class Entry:
    kind: str
    title: str
    due: Optional[dt.date]
    raw_due: Optional[str]
    project: Optional[str]
    source: Path


def parse_due(raw: Optional[str], today: dt.date) -> Optional[dt.date]:
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in {"unset", "tbd", "none", "null"}:
        return None
    if value == "today":
        return today
    if DATE_RE.fullmatch(value):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def infer_project_slug(path: Path) -> Optional[str]:
    parts = list(path.parts)
    if "projects" in parts:
        index = parts.index("projects")
        if index + 1 < len(parts):
            return parts[index + 1]
    return None


def parse_task_line(
    line: str,
    source: Path,
    project_hint: Optional[str],
    today: dt.date,
) -> Optional[Entry]:
    if not line.lstrip().startswith("- [ ]"):
        return None
    title = line.split("::", 1)[0].replace("- [ ]", "").strip()
    raw_due = None
    due_match = DUE_RE.search(line)
    if due_match:
        raw_due = due_match.group(1)
    project = project_hint
    project_match = PROJECT_RE.search(line)
    if project_match:
        project = project_match.group(1)
    return Entry(
        kind="task",
        title=title,
        due=parse_due(raw_due, today),
        raw_due=raw_due,
        project=project,
        source=source,
    )


def extract_tasks(path: Path, today: dt.date) -> List[Entry]:
    entries: List[Entry] = []
    project_hint = infer_project_slug(path)
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = parse_task_line(line, path, project_hint, today)
        if entry:
            entries.append(entry)
    return entries


def extract_milestones(path: Path, today: dt.date) -> List[Entry]:
    entries: List[Entry] = []
    project_hint = infer_project_slug(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    last_name: Optional[str] = None
    last_name_index: Optional[int] = None
    for index, line in enumerate(lines):
        name_match = NAME_RE.search(line)
        if name_match:
            last_name = name_match.group(1).strip()
            last_name_index = index
        target_match = TARGET_RE.search(line)
        if not target_match:
            continue
        raw_due = target_match.group(1)
        due = parse_due(raw_due, today)
        if due is None:
            continue
        title = "Milestone target"
        if last_name_index is not None and last_name and index - last_name_index <= 5:
            title = f"Milestone: {last_name}"
        entries.append(
            Entry(
                kind="milestone",
                title=title,
                due=due,
                raw_due=raw_due,
                project=project_hint,
                source=path,
            )
        )
    return entries


def dedupe(entries: Iterable[Entry]) -> List[Entry]:
    seen = set()
    unique: List[Entry] = []
    for entry in entries:
        key = (entry.kind, entry.title, entry.due, entry.project)
        if key in seen:
            continue
        seen.add(key)
        unique.append(entry)
    return unique


def format_entry(entry: Entry, label: str) -> str:
    project = f"{entry.project} - " if entry.project else ""
    due_value = entry.due.isoformat() if entry.due else "missing"
    source = str(entry.source)
    return f"- {label}: {project}{entry.title} (due {due_value}) -- {source}"


def print_section(title: str, entries: List[Entry], label: str) -> None:
    print(title)
    if not entries:
        print("- none")
        return
    for entry in entries:
        print(format_entry(entry, label))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan for due dates in satcom tasks.")
    parser.add_argument("--root", default=".", help="Repo root path")
    parser.add_argument("--window-days", type=int, default=3, help="Due-soon window")
    parser.add_argument("--week-days", type=int, default=7, help="Due-this-week window")
    parser.add_argument("--include-missing", action="store_true", help="Include missing due dates")
    parser.add_argument("--today", help="Override today's date (YYYY-MM-DD)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    window_days = max(args.window_days, 0)
    week_days = max(args.week_days, window_days)

    task_paths = [root / "tasks.md"]
    task_paths.extend(root.glob("projects/*/PROJECT.md"))

    entries: List[Entry] = []
    for path in task_paths:
        if not path.exists():
            continue
        entries.extend(extract_tasks(path, today))
        if path.name == "PROJECT.md":
            entries.extend(extract_milestones(path, today))

    entries = dedupe(entries)

    overdue: List[Entry] = []
    due_soon: List[Entry] = []
    due_week: List[Entry] = []
    missing_due: List[Entry] = []

    for entry in entries:
        if entry.due is None:
            if args.include_missing:
                missing_due.append(entry)
            continue
        if entry.due < today:
            overdue.append(entry)
        elif entry.due <= today + dt.timedelta(days=window_days):
            due_soon.append(entry)
        elif entry.due <= today + dt.timedelta(days=week_days):
            due_week.append(entry)

    overdue.sort(key=lambda item: item.due or today)
    due_soon.sort(key=lambda item: item.due or today)
    due_week.sort(key=lambda item: item.due or today)
    missing_due.sort(key=lambda item: (item.project or "", item.title))

    print_section("Overdue", overdue, "Task")
    print("")
    print_section(f"Due soon (next {window_days} days)", due_soon, "Task")
    print("")
    print_section(f"Due this week (next {week_days} days)", due_week, "Task")
    if args.include_missing:
        print("")
        print_section("Missing due dates", missing_due, "Task")


if __name__ == "__main__":
    main()
