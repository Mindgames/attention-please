---
name: daily-ops
description: Coordinate satcom daily routines by chaining the daily automation loop, gap recovery notes, start/mid/end check-ins, focus/break timers, and attention alerts. Use on the first message of the day, when the user says they missed days/off-grid, when a check-in is pending, when the user asks to start/stop a focus block or break, or whenever you need to prompt for input and must run attention alerts.
---

# Daily Ops

## Overview

Run the daily routine flow for satcom using the existing routine, check-in, timer, and attention skills. Keep prompts minimal and align with the user's rolling schedule preferences.
Prompt style: ask short, conversational questions instead of enumerated lists; keep the journal as a separate, optional flow and fill in the logs in the background.
Break style: rotate break focus to avoid repetition and track daily goals (stretching, breathing, pushups toward 100/day, hydration, hygiene).

## Workflow

1. First message of the day
   - Run the daily routine loop; if a start-of-day check-in is pending, ask if the user is ready and then run it.
2. Daily priority scan (every morning)
   - Review `tasks.md` and `projects/*/PROJECT.md` (Top Tasks/Recent Activity).
   - Propose the top 3 priorities and ask for confirmation before scheduling focus blocks.
   - Ensure each chosen priority has a clear deadline; if missing, propose one and add it to `tasks.md`.
2. Gap recovery (when user missed days/off-grid)
   - Log a gap note and a light restart plan:
     `python3 .codex/skills/private/daily-ops/scripts/gap_reset.py`
   - Keep prompts date-free and minimal; if the user corrects the flow, update the script/runbook immediately and log a reflection.
3. Focus blocks and breaks
   - When the user asks for a focus session or break, start the focus timer (default 60-minute focus, 15-minute break unless overridden).
   - Always set `--volume-boost 0` so system volume stays unchanged.
   - During breaks, pick a different theme than the last break and give a one-sentence instruction. Rotate through: reset (stretch+breath), body (pushups+short walk), recovery (shower/food), environment (tidy/air), admin (one small personal task). Track progress toward daily goals and call out what remains.
4. Midday reset
   - If a midday reset is due or requested, run the midday check-in.
5. End of day
   - When the day wraps or the end window is reached, run the end-of-day check-in (include metrics by default).
6. Assistant reflection
   - After end-of-day check-in or when the user requests internal notes, run:
     `python3 .codex/skills/private/daily-ops/scripts/assistant_reflection.py`
   - When the user flags a failure, log it immediately with a concrete fix to avoid repeat.
7. Attention alerts
   - Before asking for input and at the end of each turn, run the attention alert with `ATTENTION_PLEASE_PROJECT="satcom"`.

## Command Sources

Use these skills for exact commands and scripts:

- Daily routine loop: `.codex/skills/private/daily-routine/SKILL.md`
- Start/mid/end check-ins: `.codex/skills/private/daily-checkin/SKILL.md`
- Focus/break timers: `.codex/skills/private/focus-timer/SKILL.md`
- Attention alerts: `.codex/skills/public/attention-please/SKILL.md`
- Assistant reflections script output:
  - `operator/internal_reflections.md`
  - `operator/assistant_reflections.jsonl`
- Gap reset script output:
  - `operator/daily_notes/YYYY-MM-DD.md` (Gap Note)
  - `operator/state_log.jsonl` (mode=gap)
