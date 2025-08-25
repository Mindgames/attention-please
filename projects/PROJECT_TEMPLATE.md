---
title: <Project Title>
status: Planned | In Progress | On Hold | Done
owner: <@handle or Name>
updated: <YYYY-MM-DD>
north_star_metric: <one metric this project moves>
roi_window: <e.g., 6–8 weeks>
weekly_time_budget_hours: <int>
milestone:
  name: <current milestone>
  target: <YYYY-MM-DD>
  dod: <1–2 lines definition of done>
kill_criteria: <e.g., "If NSM < X by YYYY-MM-DD → pause/kill">
cadence:
  standup_day: Mon
  review_day: Fri
---

## Summary

<2–3 sentences on purpose, outcome, who it serves. Keep tight.>

## Value & Purpose

- Primary value: <revenue | cost save | strategic | learning>
- Why now: <one line>
- Success looks like: <how NSM should change within roi_window>

## Scope

- In-scope: <2–4 bullets>
- Out-of-scope / Guardrails: <2–4 bullets, e.g., “no PII leaves EU”, “respect robots.txt”>
- Dependencies: <brief list of repos/services/people>

## Current Milestone

- **Name**: <milestone>
- **Target**: <YYYY-MM-DD>
- **Definition of Done**: <1–2 lines>

## Top Tasks (next up)

> Format: `- [ ] Title  :: impact=H|M|L; effort=2h; due=YYYY-MM-DD; owner=@x; depends=#id,#id; notes=...`

- [ ] Example: Ship scraper v1 :: impact=H; effort=6h; due=2025-08-28; owner=@dev; depends=#12
- [ ] Example: Draft UX wireframe :: impact=M; effort=3h; due=2025-08-27; owner=@ux

## Plan (next 7 days)

- <brief bullet>
- <brief bullet>

## Recent Activity (last 7 days)

- YYYY-MM-DD — <brief note (link)>
- YYYY-MM-DD — <brief note (link)>

## Risks / Blocks

- <risk> — **mitigation**: <plan> — **owner**: @x — **review**: YYYY-MM-DD

## Decision Log

- YYYY-MM-DD — <decision> — **why**: <reason> — **alt**: <option> — **owner**: @x

## Open Questions

- [ ] <question> — **owner**: @x — **needed by**: YYYY-MM-DD

## Links

- <specs/docs/dashboards/tickets>

---

## Ops & Reflection Log (agent-written)

> One entry per action. First line = facts, second line = evaluation. Keep it terse.

**Entry format**
YYYY-MM-DDThh:mmZ — RUN — — link:<url or -> — result: success|partial|fail — time:<Xm|Xh> — impact:H|M|L
EVAL — value:+|=|− — why:<1 sentence> — risk:low|med|high — confidence:<0.0–1.0> — next:<1 concrete step or ->

**Example**
2025-08-24T10:00Z — RUN — — link:<url or -> — result: success — time:1h — impact:H
EVAL — value:+ — why:<1 sentence> — risk:low — confidence:0.9 — next:<1 concrete step or ->

**Daily Review**

- Summarize the day's work
- Reflect on the results
- Plan the next day's work
- Update the project status, tasks, plan, risks, etc.

---

<!--
AGENT NOTES (keep this comment):
- On every write, update front-matter `updated:`.
- Top Tasks: compute ICE = Impact×Confidence÷Effort(hours); append `priority=ICE:x.x` if helpful; keep only 3–7 tasks here.
- If a RUN result is "fail" or "partial", add/adjust a task in Top Tasks and reference it in `next:`.
- When kill_criteria is met or due will slip, add a Risk and a Decision Log entry, and surface in the next Review.
- Keep Recent Activity to last 5 lines; move older entries into a sidecar LOG.md if needed (same folder).
-->
