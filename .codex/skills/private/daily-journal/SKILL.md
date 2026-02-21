---
name: daily-journal
description: Guided daily journaling with rotating prompts and time-of-day modes (start, mid, end, free). Use when the user wants to journal, reflect, capture thoughts, debrief a day, set intentions, or requests a daily/weekly reflection flow.
---

# Daily Journal

## Overview

Lead a short, non-repetitive journaling flow each day. Prompts rotate to avoid repeats and adapt to the time of day (start, mid, end, or free mode).

## Quick Start

- Run an auto-selected journal session:
  - `python3 scripts/journal.py`
- Morning intent:
  - `python3 scripts/journal.py --mode start`
- Midday reset:
  - `python3 scripts/journal.py --mode mid`
- End-of-day reflection:
  - `python3 scripts/journal.py --mode end`
- Short version:
  - `python3 scripts/journal.py --quick`

## How It Stays Fresh

- Rotates prompts by mode and avoids prompts used in the last 7 days.
- Uses a deterministic daily seed so the prompt set is stable for the day but changes day-to-day.

## Where Entries Are Stored

- Markdown log: `operator/journal/YYYY-MM-DD.md`
- Structured log: `operator/journal_log.jsonl`

## Daily Flow

- Morning: `python3 scripts/journal.py --mode start`
- End of day: `python3 scripts/journal.py --mode end`
- Use `--quick` when short on time.

## Chat-first flow (human, one-by-one)

Use this when interactive CLI prompts are unavailable or the user wants a more human chat flow.

1. Fetch prompts:
   - `python3 scripts/journal.py --mode start --list-prompts`
2. Ask the prompts one by one in chat.
3. Write answers to a payload JSON and run:
   - `python3 scripts/journal.py --payload-file /tmp/journal_payload.json`

Payload shape:
`{"mode":"start","prompts":[{"id":"...", "text":"...", "response":"..."}]}`

## Options

- `--mode auto|start|mid|end|free` (default: auto)
- `--quick` for fewer prompts
- `--no-prompt` to log placeholders without interaction
- `--payload-json` or `--payload-file` to log chat-collected answers
- `--list-prompts` to print selected prompts as JSON
