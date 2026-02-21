#!/usr/bin/env python3
"""Interactive daily journal with rotating prompts."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Prompt:
    id: str
    text: str


PROMPTS: dict[str, list[Prompt]] = {
    "start": [
        Prompt("start_outcome", "What is the single most important outcome today?"),
        Prompt("start_first_block", "What is the exact first deep-work block you will do?"),
        Prompt("start_win", "What would make today feel like a win?"),
        Prompt("start_risk", "What is the main risk or distraction, and how will you handle it?"),
        Prompt("start_no", "What will you say no to today?"),
        Prompt("start_support", "What support or input do you need to move faster today?"),
    ],
    "mid": [
        Prompt("mid_progress", "What have you completed since the start of the day?"),
        Prompt("mid_next_block", "What is the next exact block you will run?"),
        Prompt("mid_blocker", "What is the biggest blocker right now?"),
        Prompt("mid_adjust", "What should you stop, start, or change to stay on track?"),
        Prompt("mid_energy", "How is your energy right now, and what will you do about it?"),
    ],
    "end": [
        Prompt("end_win", "What was the biggest win today?"),
        Prompt("end_next", "What is the single most important task for tomorrow?"),
        Prompt("end_learn", "What did you learn today that changes how you work?"),
        Prompt("end_gratitude", "What are you grateful for today?"),
        Prompt("end_fix", "What was off-track, and what is the fix for tomorrow?"),
    ],
    "free": [
        Prompt("free_thought", "What is on your mind right now?"),
        Prompt("free_question", "What question do you need to answer next?"),
        Prompt("free_worry", "What is the smallest next step to reduce your biggest worry?"),
        Prompt("free_gratitude", "What is one thing you appreciate today?"),
    ],
}

CORE_PROMPTS = {
    "start": ["start_outcome", "start_first_block"],
    "mid": ["mid_progress", "mid_next_block"],
    "end": ["end_win", "end_next"],
}

PROMPT_COUNTS = {
    "start": 4,
    "mid": 3,
    "end": 4,
    "free": 3,
}

LOOKBACK_DAYS = 7


def get_repo_root() -> Path:
    """Return repository root based on the .codex directory when possible."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def get_journal_dir() -> Path:
    return get_repo_root() / "operator" / "journal"


def get_log_path() -> Path:
    return get_repo_root() / "operator" / "journal_log.jsonl"


def parse_time(value: str) -> dt_time:
    return datetime.strptime(value.strip(), "%H:%M").time()


def in_window(now: dt_time, start: str, end: str) -> bool:
    start_t = parse_time(start)
    end_t = parse_time(end)
    if start_t <= end_t:
        return start_t <= now <= end_t
    return now >= start_t or now <= end_t


def determine_mode(now: datetime) -> str:
    current = now.time()
    if in_window(current, "06:00", "11:30"):
        return "start"
    if in_window(current, "12:00", "16:00"):
        return "mid"
    if in_window(current, "18:00", "23:30"):
        return "end"
    return "free"


def load_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    out: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            out.append(payload)
    return out


def recent_prompt_ids(target_date: date) -> set[str]:
    entries = load_jsonl(get_log_path())
    cutoff = target_date - timedelta(days=LOOKBACK_DAYS)
    ids: set[str] = set()
    for entry in entries:
        ts = entry.get("timestamp")
        if not isinstance(ts, str):
            continue
        try:
            parsed = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if parsed.date() < cutoff or parsed.date() >= target_date:
            continue
        prompts = entry.get("prompts")
        if isinstance(prompts, list):
            for item in prompts:
                if isinstance(item, dict):
                    pid = item.get("id")
                    if isinstance(pid, str):
                        ids.add(pid)
    return ids


def sanitize_text(value: str, limit: int = 140) -> str:
    """Clean and truncate text for prompts."""
    cleaned = " ".join(value.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def latest_response(target_date: date) -> tuple[str, str, str] | None:
    """Return the most recent (prompt id, prompt text, response) before target date."""
    entries = load_jsonl(get_log_path())
    if not entries:
        return None
    for entry in reversed(entries):
        ts = entry.get("timestamp")
        if not isinstance(ts, str):
            continue
        try:
            parsed = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if parsed.date() > target_date:
            continue
        prompts = entry.get("prompts")
        if not isinstance(prompts, list):
            continue
        for item in reversed(prompts):
            if not isinstance(item, dict):
                continue
            response = item.get("response")
            if not isinstance(response, str):
                continue
            response = response.strip()
            if not response:
                continue
            pid = item.get("id")
            text = item.get("text")
            if isinstance(pid, str) and isinstance(text, str):
                return pid, text, response
    return None


def select_prompts(mode: str, target_date: date, quick: bool) -> list[Prompt]:
    prompts = PROMPTS.get(mode) or PROMPTS["free"]
    core_ids = CORE_PROMPTS.get(mode, [])
    core = [p for p in prompts if p.id in core_ids]
    pool = [p for p in prompts if p.id not in core_ids]
    count = 2 if quick else PROMPT_COUNTS.get(mode, 3)
    recent_ids = recent_prompt_ids(target_date)

    rng = random.Random(f"{target_date.isoformat()}::{mode}")
    follow_up = None
    if not quick:
        latest = latest_response(target_date)
        if latest:
            pid, text, response = latest
            snippet = sanitize_text(response)
            prompt_text = (
                f'Last time you wrote: "{snippet}". Any update or action today?'
            )
            follow_up = Prompt(f"followup::{pid}", prompt_text)
    fresh = [p for p in pool if p.id not in recent_ids]
    rng.shuffle(fresh)
    picked = list(core)
    if follow_up and follow_up.id not in {p.id for p in picked}:
        picked.append(follow_up)
    needed = max(0, count - len(picked))
    picked.extend(fresh[:needed])
    if len(picked) < count:
        fallback = [p for p in pool if p not in picked]
        rng.shuffle(fallback)
        picked.extend(fallback[: count - len(picked)])
    return picked


def prompt_text(question: str) -> str:
    print(question)
    return input("> ").strip()


def ensure_header(path: Path, target_date: date) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Journal: {target_date.isoformat()}\n", encoding="utf-8")


def append_section(path: Path, title: str, lines: list[str]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {title}\n\n")
        for line in lines:
            handle.write(f"{line}\n")


def log_entry(payload: dict[str, object]) -> None:
    log_path = get_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")

def coerce_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def coerce_prompt_entries(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    out: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        pid = coerce_text(item.get("id"))
        text = coerce_text(item.get("text"))
        response = coerce_text(item.get("response"))
        out.append({"id": pid, "text": text, "response": response})
    return out


def load_payload(args: argparse.Namespace) -> dict[str, object] | None:
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


def run_journal(
    mode: str,
    target_date: date,
    quick: bool,
    no_prompt: bool,
    payload: dict[str, object] | None = None,
) -> None:
    now = datetime.now().astimezone()
    responses: list[dict[str, str]] = []
    lines: list[str] = []

    if payload is not None:
        payload_mode = coerce_text(payload.get("mode"))
        if payload_mode:
            mode = payload_mode
        responses = coerce_prompt_entries(payload.get("prompts"))
        if not responses:
            lines.append("- (no prompt data collected)")
        else:
            for entry in responses:
                question = entry.get("text") or ""
                answer = entry.get("response") or ""
                lines.append(f"- Q: {question}")
                lines.append(f"  - A: {answer if answer else '(skipped)'}")
    elif no_prompt:
        lines.append("- (no prompt data collected)")
    else:
        prompts = select_prompts(mode, target_date, quick)
        for prompt in prompts:
            answer = prompt_text(prompt.text)
            responses.append({"id": prompt.id, "text": prompt.text, "response": answer})
            lines.append(f"- Q: {prompt.text}")
            lines.append(f"  - A: {answer if answer else '(skipped)'}")

    journal_path = get_journal_dir() / f"{target_date.isoformat()}.md"
    ensure_header(journal_path, target_date)
    stamp = now.strftime("%H:%M")
    append_section(journal_path, f"{stamp} {mode}", lines)

    payload_out = {
        "timestamp": now.isoformat(),
        "mode": mode,
        "prompts": responses,
    }
    log_entry(payload_out)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a smart daily journal.")
    parser.add_argument(
        "--mode",
        choices=["start", "mid", "end", "free", "auto"],
        default="auto",
        help="Journal mode (default: auto by time of day).",
    )
    parser.add_argument(
        "--date",
        default="",
        help="Override date (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Short journal with fewer prompts.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip prompts and log placeholders.",
    )
    parser.add_argument(
        "--payload-json",
        default="",
        help="Optional JSON string with journal answers.",
    )
    parser.add_argument(
        "--payload-file",
        default="",
        help="Optional JSON file with journal answers.",
    )
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="Print selected prompts as JSON and exit.",
    )
    return parser


def main() -> int:
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

    mode = args.mode
    if mode == "auto":
        mode = determine_mode(datetime.now().astimezone())

    if args.list_prompts:
        prompts = select_prompts(mode, target_date, args.quick)
        payload = {
            "mode": mode,
            "prompts": [{"id": prompt.id, "text": prompt.text} for prompt in prompts],
        }
        print(json.dumps(payload, ensure_ascii=True))
        return 0

    payload = load_payload(args)
    no_prompt = args.no_prompt and payload is None
    run_journal(mode, target_date, args.quick, no_prompt, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
