# iGaming Change Intelligence (Ade JV)

- Status: In Progress
- Owner: Mathias Åsberg
- Updated: 2025-08-25
- North Star Metric: A3 — accepted actionable alerts per operator-week
- ROI Window: 8–10 weeks
- Weekly Time Budget (hours): 12
- Milestone:
  - Name: Design Sprint + Pilot Spec Locked
  - Target: 2025-09-08
  - DoD: Signed MOU; OP-CO set; pilot scope/taxonomy frozen; MVP PRD done; 2 pilots named
- Kill Criteria: If no signed MOU + ≤1 pilot by 2025-09-15 or A3 < 5 by 2025-10-20 → pause/kill
- Cadence:
  - Standup Day: Mon
  - Review Day: Fri

## Summary
Agentic AI that constantly monitors casino sites and public signals (promos, bonuses, game/provider changes, KYC flows, payment rails, geoblocks) and pushes actionable change alerts to operators/affiliates. No integrations needed; browser agents + light enrichment + human approval gates. Built as a JV with Ade.

## Value & Purpose
- Primary value: cost/save + revenue enable (faster reaction to market changes; fewer missed opportunities; less manual monitoring)
- Why now: market is fluid; LLMs + headless browsing make “no-integration” monitoring viable
- Success looks like: ≥2 pilots live and A3 ≥ 5 within 6–8 weeks

## Scope
- In-scope: browser agents; change taxonomy; alerting (Slack/Email); pilot feed UI; light enrichment; audit trail
- Out-of-scope / Guardrails: no credentialed scraping or bypassing protections; respect robots/rate-limits; no personal data; insights are non-legal, require human confirmation
- Dependencies: Ade (partner + access to pilots); pilot operators/affiliates (TBD); LLM provider; storage (Postgres/Timeseries); proxy pool

## Current Milestone
- Name: Design Sprint + Pilot Spec Locked
- Target: 2025-09-08
- Definition of Done: MOU signed; OP-CO operational; pilot casinos chosen; v0 taxonomy + PRD + success criteria frozen

## Top Tasks (next up)
> Format: `- [ ] Title  :: impact=H|M|L; effort=2h; due=YYYY-MM-DD; owner=@x; depends=#id; notes=...`
- [ ] Re-engage Ade: alignment note + book 60-min sprint kickoff  :: impact=H; effort=1h; due=2025-08-26; owner=@mathias; notes=reset cadence & expectations
- [ ] Finalize MOU & payment schedule (30k→Mathias; 20k→OP-CO) + equity 30/70 + IP under OP-CO  :: impact=H; effort=2h; due=2025-08-27; owner=@mathias
- [ ] Design Sprint plan (2 weeks): goals, agenda, artifacts  :: impact=H; effort=2h; due=2025-08-27; owner=@agent
- [ ] Draft change taxonomy v0 (Promos/Bonuses, New/Removed Providers & Games, KYC steps, Payment rails, Geo blocks, T&Cs)  :: impact=H; effort=4h; due=2025-08-28; owner=@agent
- [ ] Pick 30–50 target casinos for pilots (MGA + 1–2 other markets)  :: impact=H; effort=3h; due=2025-08-29; owner=@ade
- [ ] Build headless browsing skeleton w/ rate limits + proxy rotation + robots respect  :: impact=H; effort=6h; due=2025-09-02; owner=@agent
- [ ] Define data model (events, sites, artifacts) + storage (Postgres + timeseries)  :: impact=H; effort=3h; due=2025-09-02; owner:@agent
- [ ] Pilot offer + pricing hypothesis (e.g., €199/site/mo or 1% contract uplift)  :: impact=M; effort=2h; due=2025-09-05; owner=@mathias
- [ ] Draft grant apps (Google for Startups, NVIDIA Inception, Seeds of Bravery)  :: impact=M; effort=4h; due=2025-09-06; owner=@agent

## Plan (next 7 days)
- Close MOU + schedule 2-week design sprint.
- Freeze taxonomy + PRD; choose pilot list; stand up agent skeleton and storage.

## Recent Activity (last 7 days)
- 2025-08-25 — Created Ade JV PROJECT.md; defined NSM, milestone, kill criteria.

## Risks / Blocks
- Communication drift with Ade — mitigation: immediate re-engagement + weekly cadence — owner: @mathias — review: 2025-08-27
- Compliance/scraping risk — mitigation: robots/rate-limits, no auth scraping, legal disclaimer; keep audit trail — owner: @agent
- False positives/alert noise — mitigation: constrained taxonomy, thresholds, human approval gate for outbound alerts — owner: @agent
- Pilot slippage — mitigation: timeboxed outreach via Ade; offer clear pilot terms — owner: @ade

## Decision Log
- 2025-08-25 — JV terms (target): 30/70 equity (Ade 70%), ordinary voting; €30k to Mathias + €20k to OP-CO; IP under OP-CO from day one — why: control + speed; aligns incentives — owner: @mathias
- 2025-08-25 — v0 scope = change intelligence (no forecasting) — why: fastest path to value; reduces complexity

## Open Questions
- [ ] Primary ICP first: operators vs affiliates (or mixed pilots)? — owner: @mathias — needed by: 2025-08-27
- [ ] Initial geographies (MGA + ?) — owner: @ade — needed by: 2025-08-28
- [ ] Pilot casinos list (30–50) — owner: @ade — needed by: 2025-08-29
- [ ] Pricing model (flat per site vs outcome-linked) — owner: @mathias — needed by: 2025-09-05
- [ ] Tooling: Playwright/Browser-Use, proxy provider, timeseries (Timescale?) — owner: @agent — needed by: 2025-08-30

## Links
- MOU draft: <add link>
- MVP PRD (wip): <add link>
- Taxonomy v0 doc: <add link>

---

## Ops & Reflection Log (agent-written)

**Entry format**
