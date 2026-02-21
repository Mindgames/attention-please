---
name: focus-timer
description: Run a focus timer with optional break or start a break-only timer, speak start/break prompts, and play a single pip alert at transitions. Use when the user asks to start a focus block, start a break, set a 90-minute session, check remaining time, or wants spoken timers with breaks.
---

# Focus Timer

## Overview

Run a focus timer with optional break or a break-only timer, spoken prompts, and a single pip alert.

## Quick Start

- Run `python3 scripts/focus_timer.py --topic "layout alignment" --background` to start a 90-minute focus session without blocking the terminal.
- Run `python3 scripts/focus_timer.py --mode break --minutes 15 --background` to start a 15-minute break-only timer.
- Pass `--minutes` to override the focus duration.
- Pass `--break-minutes` to change the break length or set `0` to skip it.
- Pass `--mode break` to run a break-only timer using `--minutes` as the break length.
- Pass `--background` to run the timer in the background and return immediately.
- Pass `--log-path` to capture background output in a specific file.
- Pass `--no-speech` to disable spoken prompts.
- Pass `--sound` to override the alert sound file path.
- Pass `--volume` to adjust pip volume (0.0 to 1.0).
- Pass `--status` to show remaining time for the active session.
- Pass `--volume-boost 0` to avoid temporarily raising system volume during prompts.
- Time tracking events append to `operator/time_log.jsonl` on start and end of focus/break segments.
- Focus completion appends a pending check-in entry to `operator/pending_checkins.json` for progress capture.
- After focus or break ends, an attention loop will repeat alerts every few minutes until you respond (complete the pending check-in or start a new focus session).

## Behavior

- Default focus duration is 90 minutes with a 15-minute break.
- Speak prompts with macOS `say` when available.
- Play a single pip cue before spoken prompts; fall back to a system beep if needed.
- Temporarily raise system volume during prompts for louder cues (disable with `--volume-boost 0`).
- Background runs log to the temp file derived from the session state path unless `--log-path` is provided.
- Focus/break starts and completions append JSONL entries to `operator/time_log.jsonl`.
- Focus completion queues a pending check-in entry in `operator/pending_checkins.json`.

## Examples

- "Start a 90 minute focus session with focus on layout, then a 15 minute break."
- "Run a 45 minute focus block with no break and play a sound."
- "Start a 15 minute break."
- "Set a focus timer and speak the start and break prompts."
- "How much time is left on the focus session?"

## Resources

### scripts/

- `scripts/focus_timer.py` - Start the timer and play the alert.
