# Safebuild

- Status: In Progress
- Owner: Mathias Åsberg
- Updated: 2025-08-24
- North Star Metric: SOW<48h rate (%)  — % of new projects where a mutually accepted SOW is produced within 48h of intake
- ROI Window: 6–8 weeks
- Weekly Time Budget (hours): 8
- Milestone:
  - Name: Pilot-ready v0 (Intake→SOW, Change-Order Alerts, Daily Log)
  - Target: 2025-09-15
  - DoD: Two pilot contractors onboarded; Intake→SOW flow produces client+contractor-approved SOW; change-order detector flags diffs; daily site log summary sent.
- Kill Criteria: If <2 paying pilots and SOW<48h rate <60% by 2025-10-15 → pause/kill
- Cadence:
  - Standup Day: Mon
  - Review Day: Fri

## Summary
AI agents for construction contractors that transform messy client comms into clear, mutual expectations: structured SOW with acceptance criteria, automatic change-order detection, and daily progress summaries. Serves contractors and their clients; reduces disputes, delays, and rework.

## Value & Purpose
- Primary value: cost save + revenue enable (fewer disputes, faster close, fewer write-offs)
- Why now: trades are drowning in chat/email; LLMs are finally good enough at extracting/normalizing requirements
- Success looks like: ≥60% SOW<48h rate with 2 pilots in 6–8 weeks

## Scope
- In-scope: Intake of calls/chats/emails; SOW drafting w/ acceptance criteria; change-order detection; daily site log → client update
- Out-of-scope / Guardrails: no binding legal advice; human approval before contract changes; no payment/escrow; respect consent/PII rules
- Dependencies: Henry Chu (product/domain & pilot access); 2 pilot contractors (TBD); LLM provider; simple storage (docs + DB)

## Current Milestone
- Name: Pilot-ready v0
- Target: 2025-09-15
- Definition of Done: Two pilots live; Intake→SOW + change-order alerts + daily summaries working end-to-end with human approval gates

## Top Tasks (next up)
> Format: `- [ ] Title  :: impact=H|M|L; effort=2h; due=YYYY-MM-DD; owner=@x; depends=#id,#id; notes=...`
- [ ] Re-engage Henry: send note + book 45-min alignment call  :: impact=H; effort=1h; due=2025-08-25; owner=@mathias; notes=reset cadence + goals
- [ ] Write 1-pager brief (problem, ICP, NSM, v0 flows)  :: impact=H; effort=2h; due=2025-08-26; owner=@agent; depends=#henry_call
- [ ] Decide ICP + geography (e.g., residential renovations; region TBD)  :: impact=H; effort=1h; due=2025-08-27; owner=@mathias; notes=propose Malta+Poland for pilots
- [ ] Draft SOW template + acceptance-criteria checklist  :: impact=H; effort=3h; due=2025-08-28; owner=@agent
- [ ] Define v0 agent flows (Intake→SOW; Change-order; Daily log)  :: impact=H; effort=4h; due=2025-08-29; owner=@agent
- [ ] Recruit 2 pilot contractors via Henry’s network  :: impact=H; effort=6h; due=2025-09-05; owner=@henry
- [ ] Pricing hypothesis + pilot offer (e.g., €199/site/mo or 1% of contract)  :: impact=M; effort=2h; due=2025-09-05; owner=@mathias

## Plan (next 7 days)
- Reconnect with Henry; lock ICP + NSM; freeze v0 flows and SOW template.
- Line up 2 pilot contractors; define pilot success criteria and pricing.

## Recent Activity (last 7 days)
- 2025-08-24 — Created Safebuild PROJECT.md; set milestone & NSM.

## Risks / Blocks
- Founder comms gap with Henry — mitigation: alignment call in 24h + weekly cadence — owner: @mathias — review: 2025-08-26
- ICP/geography unclear — mitigation: 1-pager + decision on call — owner: @mathias
- Legal/compliance (contracts, consent) — mitigation: disclaimers + human approval; light legal review pre-pilot — owner: @mathias
- LLM reliability — mitigation: constrained templates; require human approval for contract edits — owner: @agent

## Decision Log
- 2025-08-24 — Provisional NSM = SOW<48h rate — why: nearest proxy to “expectation clarity” and sales cycle acceleration — alt: Dispute rate, On-time completion
- 2025-08-24 — Provisional v0 scope set (Intake→SOW; Change-order; Daily log) — why: covers 80% of value fast

## Open Questions
- [ ] Exact ICP (GCs vs specialty trades; residential vs commercial)? — owner: @mathias — needed by: 2025-08-27
- [ ] First geography for pilots? — owner: @mathias — needed by: 2025-08-27
- [ ] Investment structure & IP ownership with Henry? — owner: @mathias — needed by: 2025-08-29
- [ ] Pilot pricing & incentive? — owner: @mathias — needed by: 2025-09-05
- [ ] Tooling stack (LLM, storage, comms integrations)? — owner: @agent — needed by: 2025-08-29

## Links
- <add brief, call notes, pilot candidate list, SOW template once created>

---

## Ops & Reflection Log (agent-written)

**Entry format**
