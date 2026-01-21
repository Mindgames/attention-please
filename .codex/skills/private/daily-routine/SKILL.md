---
name: daily-routine
description: Start or refresh satcom's daily automation loop, including background auto-checkins and a pending start-of-day check-in flag. Use at the first user message of the day, or whenever you need to restart the daily routine or verify auto-checkin status.
---

# Daily Routine

## Overview

Start the daily automation loop for satcom, keep a per-day routine state, and ensure auto-checkins are running in the background with attention alerts.

## Quick Start

- First message of the day (notify-only auto-checkins):
  `python3 scripts/daily_routine.py`
- Force restart the auto-checkin loop:
  `python3 scripts/daily_routine.py --force`
- Run the start-of-day check-in now:
  `python3 scripts/daily_routine.py --start-checkin`
- Run the start-of-day check-in without prompts:
  `python3 scripts/daily_routine.py --start-checkin --no-prompt`
- Run auto-checkins with prompts (only when interactive):
  `python3 scripts/daily_routine.py --prompt-checkins`
- Status only:
  `python3 scripts/daily_routine.py --status`

## Workflow

1. Run the script on the first user message of the day.
2. It starts (or confirms) the background auto-checkin loop (notify-only by default).
3. If a start-of-day check-in is pending, ask the user when ready and run:
   `python3 .codex/skills/private/daily-checkin/scripts/daily_checkin.py --mode start`
4. Auto-checkins will continue to alert based on the configured time windows.

## Outputs

- Routine state: `operator/daily_routine_state.json`
- Auto-checkin PID: `operator/auto_checkin.pid`
- Auto-checkin log: `operator/auto_checkin.log`

## Notes

- Run inside the satcom repo so paths resolve correctly.
- This skill is private to this project and should not be used elsewhere.

## Resources

### scripts/
- `scripts/daily_routine.py` - start or refresh the daily automation loop.
