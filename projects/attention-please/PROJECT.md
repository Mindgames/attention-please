---
title: Attention Please
status: In Progress
owner: Mathias
updated: 2025-12-27
north_star_metric: Awesome-skill repo PRs merged
roi_window: 2-4 weeks
weekly_time_budget_hours: 2
milestone:
  name: Publish skill to awesome skill repos
  target: 2026-01-03
  dod: PRs opened to target repos with the skill listed
kill_criteria: If no repo accepts by 2026-01-31, pause and reassess
cadence:
  standup_day: Mon
  review_day: Fri
---

# Attention Please

## Summary

Package and publish the "Attention Please" agent skill that notifies users when runs end or need attention, and distribute it across relevant awesome skills lists.

## Value & Purpose

- Primary value: strategic
- Why now: distribution will make the skill discoverable
- Success looks like: at least one awesome list accepts the skill within roi_window

## Scope

- In-scope: polish skill description; create a short README snippet; submit PRs to awesome skill repos
- Out-of-scope / Guardrails: no new features beyond notification behavior; avoid PII in examples
- Dependencies: existing skill repo, GitHub access

## Current Milestone

- **Name**: Publish skill to awesome skill repos
- **Target**: 2026-01-03
- **Definition of Done**: PRs opened with the skill listed and accepted formatting

## Top Tasks (next up)

> Format: `- [ ] Title  :: impact=H|M|L; effort=2h; due=YYYY-MM-DD; owner=@x; depends=#id,#id; notes=...`

- [ ] Identify 5-8 awesome skill repos to target :: impact=H; effort=1h; due=2025-12-29; owner=@mathias
- [ ] Draft the skill listing snippet (title, summary, link) :: impact=M; effort=30m; due=2025-12-29; owner=@mathias
- [ ] Add Attention Please skill to awesome skills repos (open PRs) :: impact=H; effort=2h; due=2026-01-03; owner=@mathias; notes=after target list is ready

## Plan (next 7 days)

- Build a target list and collect submission guidelines
- Publish the listing snippet and open PRs

## Recent Activity (last 7 days)

- 2025-12-27 - Built initial version, pushed to GitHub, posted on Hacker News, LinkedIn, and X.
- 2025-12-27 - Project initialized with milestone and tasks

## Risks / Blocks

- Maintainers may reject or delay PRs - **mitigation**: widen target list and follow repo conventions - **owner**: @mathias - **review**: 2026-01-03

## Decision Log

- 2025-12-27 - Prioritize distribution over new features - **why**: discoverability first - **alt**: add features first - **owner**: @mathias

## Open Questions

- [ ] Which awesome skill lists are the best fit? - **owner**: @mathias - **needed by**: 2025-12-29

## Links

- TBD

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
