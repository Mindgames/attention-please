---
title: Grais.ai
status: In Progress
owner: Mathias Asberg
updated: 2026-01-21
north_star_metric: TBD
roi_window: TBD
weekly_time_budget_hours: TBD
milestone:
  name: 0.8
  target: TBD
  dod: "0.8 plan mapped with owners, dates, and acceptance gates."
kill_criteria: TBD
cadence:
  standup_day: Mon
  review_day: Fri
---

# Grais.ai

## Summary

Grais is "Cursor for communication": an AI agent integrated into chat channels that provides strategic suggestions and context in the flow of conversation. Current focus is executing the 0.8 plan that has been mapped in the release project.

## Value & Purpose

- Primary value: AI augmentation for high-stakes communication
- Why now: preparing beta for testers
- Success looks like: beta ships to testers with core flows stable and feedback loop active

## Scope

- In-scope: 0.8 execution across API/Chrome/Website/tasks, acceptance gates, beta rollout readiness
- Out-of-scope / Guardrails: new product lines or major feature expansion before 0.8 scope ships
- Dependencies: TBD

## Current Milestone

- **Name**: 0.8
- **Target**: TBD
- **Definition of Done**: 0.8 scope delivered across repos with acceptance gates passed and release notes ready

## Top Tasks (next up)

- [ ] Chrome permissions workstream (Replypilot/grais-chrome#379) :: impact=H; effort=2h; due=unset; owner=@Mindgames
- [ ] PostHog backend analytics (Replypilot/grais-api#350) :: impact=H; effort=3h; due=unset; owner=@skanderkaroui
- [ ] Ignore label-only drafts in external history (Replypilot/grais-chrome#436) :: impact=H; effort=2h; due=unset; owner=@skanderkaroui
- [ ] Emails / onboarding / loops (Replypilot/grais-tasks#10) :: impact=H; effort=3h; due=unset; owner=@skanderkaroui
- [ ] Chrome extension public release prep (Replypilot/grais-chrome#429) :: impact=H; effort=2h; due=unset; owner=@unassigned

## Plan (next 7 days)

- Drive 0.8 execution across API/Chrome/Website workstreams.
- Clear blockers for in-progress items and move backlog to Ready.
- Align sequencing, dependencies, and acceptance gates for release.

## Recent Activity (last 7 days)

- 2026-01-21 - 0.8 plan mapped in GitHub project; execution started on in-progress items.
- 2026-01-16 - Shifted milestone focus to 0.7 and aligned with GitHub project tracking.
- 2025-12-28 - Set beta rollout deadline for end of week; queued fundraising prep for early 2026.
- 2025-12-28 - Routed all models through LiteLLM.
- 2025-12-26 - Project added and scoped for beta readiness.

## Risks / Blocks

- 0.8 scope expansion -> mitigation: keep to mapped items in the release project and gate new asks.

## Decision Log

- 2026-01-21 - Move from 0.8 planning to execution based on mapped project scope.
- 2025-12-26 - Focus on beta readiness before fundraising or social presence.

## Open Questions

- [ ] Confirm 0.8 target date and success criteria. -- owner: @mathias -- needed by: 2026-01-22

## Links

- https://github.com/orgs/Replypilot/projects/3
- https://github.com/Replypilot/grais-api
- https://github.com/Replypilot/grais-chrome

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
