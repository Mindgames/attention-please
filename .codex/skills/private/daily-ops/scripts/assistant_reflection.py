#!/usr/bin/env python3
"""Capture assistant reflections on daily behavior and performance."""

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


def get_markdown_path() -> Path:
    """Return the markdown reflections path."""
    return get_repo_root() / "operator" / "internal_reflections.md"


def get_jsonl_path() -> Path:
    """Return the JSONL reflections path."""
    return get_repo_root() / "operator" / "assistant_reflections.jsonl"


def ensure_markdown_header(path: Path) -> None:
    """Ensure the reflections markdown file exists with a header."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Internal Reflections\n", encoding="utf-8")


def parse_list(value: str) -> list[str]:
    """Parse a comma/semicolon separated list."""
    if not value.strip():
        return []
    raw = value.replace(";", ",").split(",")
    return [item.strip() for item in raw if item.strip()]


def prompt_text(label: str) -> str:
    """Prompt for a single line of text."""
    return input(label).strip()


def prompt_list(label: str) -> list[str]:
    """Prompt for a list."""
    return parse_list(prompt_text(label))


def append_markdown_entry(
    path: Path,
    timestamp: datetime,
    behaviors: list[str],
    interpretation: str,
    improvement: str,
    self_rating: str,
    self_critique: str,
) -> None:
    """Append a markdown reflection entry."""
    timestamp_label = timestamp.strftime("%Y-%m-%d %H:%M")
    behavior_text = ", ".join(behaviors) if behaviors else "(none)"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {timestamp_label}\n\n")
        handle.write(f"- Behavior: {behavior_text}\n")
        handle.write(f"- Interpretation: {interpretation or '(none)'}\n")
        handle.write(f"- Improvement: {improvement or '(none)'}\n")
        if self_rating:
            handle.write(f"- Self rating: {self_rating}/5\n")
        else:
            handle.write("- Self rating: (none)\n")
        handle.write(f"- Self critique: {self_critique or '(none)'}\n")


def append_jsonl_entry(
    path: Path,
    timestamp: datetime,
    behaviors: list[str],
    interpretation: str,
    improvement: str,
    self_rating: str,
    self_critique: str,
) -> None:
    """Append a structured JSONL reflection entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": timestamp.astimezone().isoformat(),
        "date": timestamp.astimezone().date().isoformat(),
        "behavior": behaviors,
        "interpretation": interpretation,
        "improvement": improvement,
        "self_rating": self_rating,
        "self_critique": self_critique,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Capture assistant reflections on daily behavior and performance."
    )
    parser.add_argument(
        "--date",
        default="",
        help="Date for the reflection (YYYY-MM-DD). Defaults to today.",
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
        timestamp = datetime.combine(target_date, datetime.now().time()).astimezone()
    else:
        timestamp = datetime.now().astimezone()

    if args.no_prompt:
        behaviors = []
        interpretation = ""
        improvement = ""
        self_rating = ""
        self_critique = ""
    else:
        behaviors = prompt_list("Behavior observed (comma-separated): ")
        interpretation = prompt_text("Interpretation/meaning: ")
        improvement = prompt_text("Change to improve: ")
        self_rating = prompt_text("Self rating (1-5): ")
        self_critique = prompt_text("Self critique: ")

    markdown_path = get_markdown_path()
    ensure_markdown_header(markdown_path)
    append_markdown_entry(
        markdown_path,
        timestamp,
        behaviors,
        interpretation,
        improvement,
        self_rating,
        self_critique,
    )
    append_jsonl_entry(
        get_jsonl_path(),
        timestamp,
        behaviors,
        interpretation,
        improvement,
        self_rating,
        self_critique,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
