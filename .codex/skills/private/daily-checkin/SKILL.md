---
name: daily-checkin
description: Collect a daily personal state/journal check-in and incremental notes for satcom. Use at start-of-day, midday reset, or end-of-day to capture energy/focus/stress, outcomes, blockers, wellbeing actions, and system friction. Writes to operator daily notes and JSONL logs.
---

# Daily Checkin

## Overview

Collect daily state, journal, and productivity signals with minimal friction, and append incremental notes so the system can improve over time.

## Quick Start

- Start-of-day:
  `python3 scripts/daily_checkin.py --mode start`
- Midday reset:
  `python3 scripts/daily_checkin.py --mode mid`
- End-of-day (includes metrics by default):
  `python3 scripts/daily_checkin.py --mode end`
- Skip prompts (placeholders only):
  `python3 scripts/daily_checkin.py --mode end --no-prompt`
- Auto-run (checks every 5 minutes, prompts when due):
  `python3 scripts/auto_checkin.py --loop`
- Auto-run notifications only (no prompts):
  `python3 scripts/auto_checkin.py --loop --notify-only`

## Workflow (Daily Routine)

1. Start-of-day check-in:
   - Sleep, energy, focus, stress
   - Top outcomes, first project, constraint
   - Optional journal line
2. Midday reset:
   - Done so far, blockers, next task
   - Correction if off-track
   - Wellbeing done (stretch/breathe/pushups)
3. End-of-day check-in:
   - Wins, blocks, next tasks
   - Wellbeing done
   - System friction + improvement idea
   - Optional experiment feedback (keep/adjust/stop)

## Chat-first check-in (batch for morning, brief for others)

Use this when interactive CLI prompts are unavailable.

1. **Start-of-day**: collect the core fields in a single batch message to reduce friction.
2. **Midday/end**: short, human prompts are fine (one by one if needed).
3. Build a payload JSON with the answers.
4. Write payload to a temp file and run:
   - Start: `python3 scripts/daily_checkin.py --mode start --payload-file /tmp/daily_checkin_payload.json`
   - Midday: `python3 scripts/daily_checkin.py --mode mid --payload-file /tmp/daily_checkin_payload.json`
   - End: `python3 scripts/daily_checkin.py --mode end --payload-file /tmp/daily_checkin_payload.json`

### Expected payload keys

- **start**: `sleep_hours`, `energy`, `focus`, `stress`, `outcomes` (list), `first_project`, `constraint`, `journal`
- **mid**: `done` (list), `blockers` (list), `next_task`, `correction`, `wellbeing` (list)
- **end**: `wins` (list), `blocks` (list), `next_tasks` (list), `wellbeing` (list), `friction`, `improvement`, `experiment_id`, `experiment_effect`, `experiment_notes`

## Outputs

- Daily note appended at:
  - `operator/daily_notes/YYYY-MM-DD.md`
- Structured logs:
  - `operator/state_log.jsonl` (state + journal)
  - `operator/wellbeing_log.jsonl` (wellbeing actions)
  - `operator/experiments.jsonl` (experiment feedback)

## Auto Metrics (optional)

- When `--include-metrics` is set (or at end-of-day by default), append:
  - Focus time by topic from `operator/time_log.jsonl`
  - Progress summaries from `operator/progress_log.jsonl`
  - Wellbeing counts from `operator/wellbeing_log.jsonl`

## Auto Check-in Rules

- Start check-in triggers when within the start window or after the first focus activity.
- Midday check-in triggers after 2 focus sessions or inside the midday window.
- End check-in triggers inside the end window or after 90 minutes of focus idle time.
- Defaults (override with `operator/daily_checkin_config.json`):
  - start_window: `06:00-11:30`
  - mid_window: `12:00-16:00`
  - end_window: `18:00-23:30`
  - mid_after_focus: `2`
  - idle_minutes_for_end: `90`
  - cooldown_minutes: `60`

## Notes

- Run inside the satcom repo so paths resolve correctly.
- This skill is private to this project and should not be used elsewhere.

## Resources

### scripts/
- `scripts/daily_checkin.py` - collect check-ins and append daily notes/logs.
- `scripts/auto_checkin.py` - check time windows and run check-ins automatically.
