---
title: Grais Website
status: In Progress
owner: Mathias Asberg
updated: 2026-01-16
north_star_metric: TBD
roi_window: TBD
weekly_time_budget_hours: TBD
milestone:
  name: 0.7 website update
  target: 2026-01-16
  dod: "Changelog updated for 0.7 and published on site."
kill_criteria: TBD
cadence:
  standup_day: Mon
  review_day: Fri
---

# Grais Website

## Summary

Public-facing website for Grais; keeps product messaging and changelog up to date. Current focus is the 0.7 milestone update.

## Value & Purpose

- Primary value: marketing and product communication
- Why now: 0.7 milestone needs a website update
- Success looks like: changelog reflects 0.7 and is visible on site

## Scope

- In-scope: changelog updates, minor copy edits, release notes
- Out-of-scope / Guardrails: redesigns or new pages before 0.7 is published
- Dependencies: Replypilot/grais-website repo, release notes from API/Chrome

## Current Milestone

- **Name**: 0.7 website update
- **Target**: 2026-01-16
- **Definition of Done**: Changelog updated for 0.7 and published on site

## Top Tasks (next up)

- [ ] Update website changelog for 0.7 :: impact=H; effort=1h; due=2026-01-16; owner=@mathias
- [ ] Gather 0.7 release notes from API/Chrome issues :: impact=H; effort=1h; due=2026-01-16; owner=@mathias
- [ ] Publish website update and verify live changelog :: impact=M; effort=0.5h; due=2026-01-16; owner=@mathias

## Plan (next 7 days)

- Collect 0.7 release notes.
- Update the changelog and publish.
- Verify the live site reflects the update.

## Recent Activity (last 7 days)

- 2026-01-16 - Project added; aligned milestone with 0.7.

## Risks / Blocks

- Release notes incomplete -> mitigation: confirm with API/Chrome owners.

## Decision Log

- 2026-01-16 - Track website updates as a dedicated project.

## Open Questions

- [ ] Where is the canonical changelog source (repo file vs CMS)? -- owner: @mathias -- needed by: 2026-01-16

## Links

- https://github.com/Replypilot/grais-website
- https://github.com/Replypilot/grais-website/issues/145

---

## Ops & Reflection Log (agent-written)

> One entry per action. First line = facts, second line = evaluation. Keep it terse.

**Entry format**
YYYY-MM-DDThh:mmZ - RUN - - link:<url or -> - result: success|partial|fail - time:<Xm|Xh> - impact:H|M|L
EVAL - value:+|=|- - why:<1 sentence> - risk:low|med|high - confidence:<0.0-1.0> - next:<1 concrete step or ->

**Example**
2025-08-24T10:00Z - RUN - - link:<url or -> - result: success - time:1h - impact:H
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
