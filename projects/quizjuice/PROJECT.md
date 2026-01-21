---
title: Quizjuice
status: In Progress
owner: Mathias Asberg
updated: 2025-12-28
north_star_metric: TBD
roi_window: TBD
weekly_time_budget_hours: TBD
milestone:
  name: MVP live quiz ready
  target: 2026-01-11
  dod: "Quiz layout/pipeline stable; streaming proxy connected to YouTube, Twitch, TikTok, Facebook, Instagram, Kick."
kill_criteria: TBD
cadence:
  standup_day: Mon
  review_day: Fri
---

# Quizjuice

## Summary

Live-streamed quiz game with a simple puzzle format (animal + animal = ?), capturing chat answers and showing a leaderboard between rounds. Initial version shipped and announced; current focus is UI polish and a first test stream.

## Value & Purpose

- Primary value: audience engagement and recurring income
- Why now: finish MVP and start live runs
- Success looks like: stable multi-platform live stream with active chat participation

## Scope

- In-scope: quiz layout and image pipeline, streaming proxy integration, chat capture and leaderboard display
- Out-of-scope / Guardrails: new game modes or advanced analytics before MVP
- Dependencies: streaming proxy (StreamYard or similar), platform stream keys and chat APIs

## Current Milestone

- **Name**: MVP live quiz ready
- **Target**: TBD
- **Definition of Done**: Layout/pipeline stable; streaming proxy connected to YouTube/Twitch/TikTok/Facebook/Instagram/Kick; MVP run end-to-end

## Top Tasks (next up)

- [ ] Define "finish" checklist for MVP :: impact=H; effort=1h; due=2026-01-05; owner=@mathias
- [ ] Improve UI (bigger animals, better alignment, easier questions) :: impact=H; effort=2h; due=2026-01-06; owner=@mathias
- [ ] Run first test stream :: impact=H; effort=2h; due=2026-01-11; owner=@mathias
- [ ] Connect streaming proxy to YouTube/Twitch/TikTok/Facebook/Instagram/Kick :: impact=H; effort=3h; due=2026-01-11; owner=@mathias

## Plan (next 7 days)

- Improve the UI for quiz readability.
- Define MVP finish checklist.
- Prepare for a first test stream within two weeks.

## Recent Activity (last 7 days)

- 2025-12-28 - Shipped initial version and shared on HN, LinkedIn, and X.
- 2025-12-27 - Completed image generation and improved layout.
- 2025-12-26 - Project added and MVP scope captured.

## Risks / Blocks

- Multi-platform streaming complexity -> mitigation: start with proxy and validate one platform at a time.
- Chat ingestion differences -> mitigation: standardize on proxy chat feed if available.

## Decision Log

- 2025-12-26 - Use a proxy (StreamYard or similar) to reach multiple platforms.

## Open Questions

- [ ] Which proxy service will be used (StreamYard or other)? -- owner: @mathias -- needed by: 2025-12-30
- [ ] Where are images/quizzes sourced and stored? -- owner: @mathias -- needed by: 2025-12-30

## Links

- TBD

---

## Ops & Reflection Log (agent-written)

> One entry per action. First line = facts, second line = evaluation. Keep it terse.

**Entry format**
YYYY-MM-DDThh:mmZ - RUN - - link:<url or -> - result: success|partial|fail - time:<Xm|Xh> - impact:H|M|L
EVAL - value:+|=|- - why:<1 sentence> - risk:low|med|high - confidence:<0.0-1.0> - next:<1 concrete step or ->

**Example**
2025-12-26T10:00Z - RUN - - link:<url or -> - result: success - time:1h - impact:H
EVAL - value:+ - why:<1 sentence> - risk:low - confidence:0.9 - next:<1 concrete step or ->

**Daily Review**

- Summarize the day's work
- Reflect on the results
- Plan the next day's work
- Update the project status, tasks, plan, risks, etc.

---

<!--
AGENT NOTES (keep this comment):
- On every write, update front-matter `updated:`.
- Top Tasks: compute ICE = Impact x Confidence / Effort(hours); append `priority=ICE:x.x` if helpful; keep only 3-7 tasks here.
- If a RUN result is "fail" or "partial", add/adjust a task in Top Tasks and reference it in `next:`.
- When kill_criteria is met or due will slip, add a Risk and a Decision Log entry, and surface in the next Review.
- Keep Recent Activity to last 5 lines; move older entries into a sidecar LOG.md if needed (same folder).
-->
