---
name: deadline-guard
description: Enforce deadline discipline in this repo by scanning tasks and project docs for due dates, surfacing overdue and due-soon items, and escalating schedule changes. Use when tracking deadlines, reviewing priorities, preventing slips, or running daily start/end routines.
---

# Deadline Guard

## Overview

Scan satcom tasks and project milestones for due dates, highlight risk, and push due-soon items into the next focus block.

## Quick Start

- Run a scan with default windows (3-day due-soon, 7-day this week):
  `python3 scripts/deadline_scan.py`
- Use a wider escalation window:
  `python3 scripts/deadline_scan.py --window-days 5`
- Include tasks missing due dates:
  `python3 scripts/deadline_scan.py --include-missing`

## Workflow

1. Run `scripts/deadline_scan.py` from the repo root.
2. Report results in this order: Overdue, Due soon (next N days), Due this week, Missing due dates (if requested).
3. Escalate:
   - Overdue or due-soon items must be scheduled before any new work.
   - If a due date is missing or unrealistic, propose a new due date and update `tasks.md` or the project doc.
4. Confirm a short list of next focus blocks that directly address the due-soon items.
5. If a deadline slips, log a failure note via the daily-ops assistant reflection with cause and fix.

## Decision Rules

- Default escalation window is 3 days unless the user sets a different window.
- Any item due within the window is treated as top priority.
- Never let due dates slip silently; explicitly confirm reschedule or de-scope.

## Files Scanned

- `tasks.md`
- `projects/*/PROJECT.md`

## Output Format

Use concise bullet lists with file references, for example:
- `Overdue: <title> (due YYYY-MM-DD) -- tasks.md`
- `Due soon: <title> (due YYYY-MM-DD) -- projects/<slug>/PROJECT.md`

## Resources

### scripts/

- `scripts/deadline_scan.py` - scan due dates and milestones, print overdue and due-soon items.
