from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
STORE_PATH = REPO_ROOT / "operator" / "reminders.jsonl"


@dataclass
class Reminder:
    id: str  # unique id (timestamp + hash)
    event: str
    when_iso: str  # ISO 8601 with offset
    created_iso: str
    acknowledged: bool = False
    fired: bool = False


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ensure_store() -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text("", encoding="utf-8")


def _gen_id(event: str, when_iso: str) -> str:
    base = f"{_now_iso()}::{event}::{when_iso}"
    return str(abs(hash(base)))


def load_all() -> List[Reminder]:
    _ensure_store()
    out: List[Reminder] = []
    with STORE_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
                out.append(Reminder(**obj))
            except Exception:
                continue
    return out


def save_all(reminders: Iterable[Reminder]) -> None:
    _ensure_store()
    with STORE_PATH.open("w", encoding="utf-8") as f:
        for r in reminders:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")


def add(event: str, when_iso: str) -> Reminder:
    rem = Reminder(id=_gen_id(event, when_iso), event=event, when_iso=when_iso, created_iso=_now_iso())
    items = load_all()
    items.append(rem)
    save_all(items)
    return rem


def mark_fired(rem_id: str) -> None:
    items = load_all()
    changed = False
    for r in items:
        if r.id == rem_id:
            r.fired = True
            changed = True
            break
    if changed:
        save_all(items)


def mark_ack(rem_id: str) -> None:
    items = load_all()
    changed = False
    for r in items:
        if r.id == rem_id:
            r.acknowledged = True
            changed = True
            break
    if changed:
        save_all(items)


def due_within(minutes: int = 5) -> List[Reminder]:
    now = datetime.now().astimezone()
    window_end = now.timestamp() + minutes * 60
    out: List[Reminder] = []
    for r in load_all():
        if r.fired:
            continue
        try:
            t = datetime.fromisoformat(r.when_iso)
        except Exception:
            continue
        if now.timestamp() <= t.timestamp() <= window_end:
            out.append(r)
    return out


def past_due_unfired() -> List[Reminder]:
    now = datetime.now().astimezone().timestamp()
    out: List[Reminder] = []
    for r in load_all():
        if r.fired:
            continue
        try:
            t = datetime.fromisoformat(r.when_iso).timestamp()
        except Exception:
            continue
        if t < now:
            out.append(r)
    return out


def format_reminder_line(r: Reminder) -> str:
    return f"⏰ {r.event} — {r.when_iso} (id={r.id})"

