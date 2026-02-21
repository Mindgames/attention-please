#!/usr/bin/env python3
"""Collect daily check-ins and append incremental notes."""

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


def parse_timestamp(value: str) -> datetime | None:
    """Parse an ISO timestamp into a datetime."""
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def format_duration(seconds: float) -> str:
    """Format seconds into a compact human-readable string."""
    total_seconds = max(0, int(round(seconds)))
    minutes, remainder = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def summarize_time(target_date: date) -> list[str]:
    """Summarize focus time by topic."""
    log_path = get_repo_root() / "operator" / "time_log.jsonl"
    events = load_jsonl(log_path)
    totals: dict[str, float] = {}
    for event in events:
        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        parsed = parse_timestamp(timestamp)
        if not parsed or parsed.date() != target_date:
            continue
        if event.get("event") != "focus_end":
            continue
        elapsed = event.get("elapsed_seconds")
        if not isinstance(elapsed, (int, float)):
            continue
        topic = str(event.get("topic") or "unspecified")
        totals[topic] = totals.get(topic, 0.0) + float(elapsed)
    if not totals:
        return ["No focus time logged yet."]
    lines = []
    for topic, seconds in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"{topic}: {format_duration(seconds)}")
    return lines


def summarize_progress(target_date: date) -> list[str]:
    """Summarize progress log entries."""
    log_path = get_repo_root() / "operator" / "progress_log.jsonl"
    entries = load_jsonl(log_path)
    lines = []
    for entry in entries:
        timestamp = entry.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        parsed = parse_timestamp(timestamp)
        if not parsed or parsed.date() != target_date:
            continue
        project = str(entry.get("project") or "unspecified")
        summary = str(entry.get("summary") or "")
        if summary:
            lines.append(f"{project}: {summary}")
    if not lines:
        return ["No progress logged yet."]
    return lines


def summarize_wellbeing(target_date: date) -> list[str]:
    """Summarize wellbeing log entries."""
    log_path = get_repo_root() / "operator" / "wellbeing_log.jsonl"
    entries = load_jsonl(log_path)
    counts: dict[str, int] = {}
    for entry in entries:
        timestamp = entry.get("timestamp")
        if not isinstance(timestamp, str):
            continue
        parsed = parse_timestamp(timestamp)
        if not parsed or parsed.date() != target_date:
            continue
        activity = str(entry.get("activity") or "unspecified")
        counts[activity] = counts.get(activity, 0) + 1
    if not counts:
        return ["No wellbeing logged yet."]
    return [f"{activity}: {count}x" for activity, count in sorted(counts.items())]


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


def coerce_text(value: object) -> str:
    """Coerce a payload value into a string."""
    if value is None:
        return ""
    return str(value).strip()


def coerce_list(value: object) -> list[str]:
    """Coerce a payload value into a list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return parse_list(value)
    return []


def append_section(path: Path, title: str, lines: list[str]) -> None:
    """Append a markdown section with bullet lines."""
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {title}\n\n")
        if lines:
            for line in lines:
                handle.write(f"- {line}\n")
        else:
            handle.write("- (none)\n")


def ensure_note_header(path: Path, target_date: date) -> None:
    """Ensure a note file exists with a header."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Daily Note: {target_date.isoformat()}\n", encoding="utf-8")


def append_metrics(path: Path, target_date: date) -> None:
    """Append auto metrics to the daily note."""
    append_section(path, "Auto Metrics - Focus Time", summarize_time(target_date))
    append_section(path, "Auto Metrics - Progress", summarize_progress(target_date))
    append_section(path, "Auto Metrics - Wellbeing", summarize_wellbeing(target_date))


def append_state_log(payload: dict[str, object]) -> None:
    """Append a structured state log entry."""
    path = get_repo_root() / "operator" / "state_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def append_wellbeing_entries(activities: list[str]) -> None:
    """Append wellbeing entries for each activity."""
    if not activities:
        return
    path = get_repo_root() / "operator" / "wellbeing_log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().isoformat()
    with path.open("a", encoding="utf-8") as handle:
        for activity in activities:
            entry = {"timestamp": timestamp, "activity": activity}
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def append_experiment_entry(payload: dict[str, object]) -> None:
    """Append an experiment entry."""
    path = get_repo_root() / "operator" / "experiments.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def run_start(
    path: Path,
    target_date: date,
    prompt: bool,
    payload: dict[str, object] | None = None,
) -> None:
    """Run the start-of-day check-in."""
    lines: list[str] = []
    state_payload: dict[str, object] = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "mode": "start",
    }
    if payload is not None:
        sleep_hours = coerce_text(payload.get("sleep_hours"))
        energy = coerce_text(payload.get("energy"))
        focus = coerce_text(payload.get("focus"))
        stress = coerce_text(payload.get("stress"))
        outcomes = coerce_list(payload.get("outcomes"))
        first_project = coerce_text(payload.get("first_project"))
        constraint = coerce_text(payload.get("constraint"))
        journal = coerce_text(payload.get("journal"))
    elif prompt:
        sleep_hours = prompt_text("Sleep hours: ")
        energy = prompt_text("Energy (1-5): ")
        focus = prompt_text("Focus (1-5): ")
        stress = prompt_text("Stress (1-5): ")
        outcomes = prompt_list("Top outcomes (comma-separated): ")
        first_project = prompt_text("First project: ")
        constraint = prompt_text("Main constraint/blocker: ")
        journal = prompt_text("Journal note (optional): ")

        if sleep_hours:
            lines.append(f"Sleep hours: {sleep_hours}")
            state_payload["sleep_hours"] = sleep_hours
        if energy:
            lines.append(f"Energy: {energy}")
            state_payload["energy"] = energy
        if focus:
            lines.append(f"Focus: {focus}")
            state_payload["focus"] = focus
        if stress:
            lines.append(f"Stress: {stress}")
            state_payload["stress"] = stress
        if outcomes:
            lines.append(f"Top outcomes: {', '.join(outcomes)}")
            state_payload["outcomes"] = outcomes
        if first_project:
            lines.append(f"First project: {first_project}")
            state_payload["first_project"] = first_project
        if constraint:
            lines.append(f"Constraint: {constraint}")
            state_payload["constraint"] = constraint
        if journal:
            lines.append(f"Journal: {journal}")
            state_payload["journal"] = journal
    else:
        lines.append("No prompt data collected.")

    append_section(path, "Start Check-in", lines)
    append_state_log(state_payload)


def run_mid(
    path: Path, prompt: bool, payload: dict[str, object] | None = None
) -> None:
    """Run the midday check-in."""
    lines: list[str] = []
    if payload is not None:
        done = coerce_list(payload.get("done"))
        blockers = coerce_list(payload.get("blockers"))
        next_task = coerce_text(payload.get("next_task"))
        correction = coerce_text(payload.get("correction"))
        wellbeing = coerce_list(payload.get("wellbeing"))
    elif prompt:
        done = prompt_list("Done so far (comma-separated): ")
        blockers = prompt_list("Blockers (comma-separated): ")
        next_task = prompt_text("Next immediate task: ")
        correction = prompt_text("Correction if off-track: ")
        wellbeing = prompt_list("Wellbeing done (comma-separated): ")

        if done:
            lines.append(f"Done so far: {', '.join(done)}")
        if blockers:
            lines.append(f"Blockers: {', '.join(blockers)}")
        if next_task:
            lines.append(f"Next task: {next_task}")
        if correction:
            lines.append(f"Correction: {correction}")
        if wellbeing:
            lines.append(f"Wellbeing: {', '.join(wellbeing)}")
            append_wellbeing_entries(wellbeing)
    else:
        lines.append("No prompt data collected.")

    append_section(path, "Midday Check-in", lines)


def run_end(
    path: Path,
    target_date: date,
    prompt: bool,
    include_metrics: bool,
    payload: dict[str, object] | None = None,
) -> None:
    """Run the end-of-day check-in."""
    lines: list[str] = []
    wellbeing: list[str] = []
    experiment_payload: dict[str, object] | None = None
    if payload is not None:
        wins = coerce_list(payload.get("wins"))
        blocks = coerce_list(payload.get("blocks"))
        next_tasks = coerce_list(payload.get("next_tasks"))
        wellbeing = coerce_list(payload.get("wellbeing"))
        friction = coerce_text(payload.get("friction"))
        improvement = coerce_text(payload.get("improvement"))
        experiment_id = coerce_text(payload.get("experiment_id"))
        experiment_effect = coerce_text(payload.get("experiment_effect"))
        experiment_notes = coerce_text(payload.get("experiment_notes"))
        if experiment_id:
            experiment_payload = {
                "timestamp": datetime.now().astimezone().isoformat(),
                "experiment_id": experiment_id,
                "effect": experiment_effect,
                "notes": experiment_notes,
            }
    elif prompt:
        wins = prompt_list("Wins (comma-separated): ")
        blocks = prompt_list("Blocks (comma-separated): ")
        next_tasks = prompt_list("Next tasks (comma-separated): ")
        wellbeing = prompt_list("Wellbeing done (comma-separated): ")
        friction = prompt_text("System friction (1 item): ")
        improvement = prompt_text("System improvement idea: ")
        experiment_id = prompt_text("Experiment id (blank if none): ")
        experiment_effect = ""
        experiment_notes = ""
        if experiment_id:
            experiment_effect = prompt_text("Experiment effect (keep/adjust/stop + why): ")
            experiment_notes = prompt_text("Experiment notes: ")
            experiment_payload = {
                "timestamp": datetime.now().astimezone().isoformat(),
                "experiment_id": experiment_id,
                "effect": experiment_effect,
                "notes": experiment_notes,
            }

        if wins:
            lines.append(f"Wins: {', '.join(wins)}")
        if blocks:
            lines.append(f"Blocks: {', '.join(blocks)}")
        if next_tasks:
            lines.append(f"Next tasks: {', '.join(next_tasks)}")
        if wellbeing:
            lines.append(f"Wellbeing: {', '.join(wellbeing)}")
        if friction:
            lines.append(f"System friction: {friction}")
        if improvement:
            lines.append(f"Improvement idea: {improvement}")
        if experiment_payload:
            effect = experiment_payload.get("effect") or ""
            lines.append(f"Experiment {experiment_id}: {effect}")
    else:
        lines.append("No prompt data collected.")

    append_section(path, "End Check-in", lines)
    if wellbeing:
        append_wellbeing_entries(wellbeing)
    if experiment_payload:
        append_experiment_entry(experiment_payload)
    if include_metrics:
        append_metrics(path, target_date)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Collect daily check-ins and append notes."
    )
    parser.add_argument(
        "--mode",
        choices=["start", "mid", "end"],
        default="end",
        help="Which check-in flow to run (default: end).",
    )
    parser.add_argument(
        "--date",
        default="",
        help="Date for the note (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip interactive prompts and log placeholders.",
    )
    parser.add_argument(
        "--payload-json",
        default="",
        help="Optional JSON string with check-in answers.",
    )
    parser.add_argument(
        "--payload-file",
        default="",
        help="Optional JSON file with check-in answers.",
    )
    parser.add_argument(
        "--include-metrics",
        action="store_true",
        help="Append auto metrics (focus time, progress, wellbeing).",
    )
    return parser


def load_payload(args: argparse.Namespace) -> dict[str, object] | None:
    """Load payload data from JSON string or file."""
    if args.payload_json:
        try:
            payload = json.loads(args.payload_json)
        except json.JSONDecodeError:
            print("Invalid payload JSON.")
            return None
        return payload if isinstance(payload, dict) else None
    if args.payload_file:
        path = Path(args.payload_file)
        if not path.exists():
            print("Payload file not found.")
            return None
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            print("Invalid payload file JSON.")
            return None
        return payload if isinstance(payload, dict) else None
    return None


def main() -> int:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()
    payload = load_payload(args)

    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return 1
    else:
        target_date = datetime.now().astimezone().date()

    note_path = get_note_path(target_date)
    ensure_note_header(note_path, target_date)

    prompt = not args.no_prompt and payload is None
    include_metrics = args.include_metrics or args.mode == "end"

    if args.mode == "start":
        run_start(note_path, target_date, prompt, payload)
    elif args.mode == "mid":
        run_mid(note_path, prompt, payload)
    else:
        run_end(note_path, target_date, prompt, include_metrics, payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
