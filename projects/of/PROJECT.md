# OF

- Status: On Hold (Decision Pending)
- Owner: Mathias
- Updated: 2025-08-25

## Summary
Research the feasibility and ROI of using AI agents to replace human chat operators ("sexters") for an OF-style agency. Focus on value, compliance, ethics, and quality: can AI maintain or improve conversion and retention while reducing operator hours, without violating platform policies or safety standards?

## Current Milestone
- Name: Go/No-Go Decision (Feasibility + ROI v1)
- Target: 2025-09-07
- Success: Guardrails defined, baseline metrics plan ready, evaluation plan drafted, compliance scan complete, and go/no-go decision recorded

## Top Tasks (next up)
- [ ] Define ICP and guardrails (allowed topics, tone, escalation)  :: impact=H; effort=2h; due=2025-08-27; owner=@mathias
- [ ] Compliance scan (platform ToS, jurisdictional rules, consent + moderation workflow)  :: impact=H; effort=2h; due=2025-08-29; owner=@agent
- [ ] Draft evaluation plan (A/B with anonymized logs; safety filters; escalation to human)  :: impact=H; effort=3h; due=2025-09-01; owner=@agent
- [ ] Baseline metrics plan (what to measure, how to collect)  :: impact=H; effort=2h; due=2025-09-01; owner=@agent

## Recent Activity (last 7 days)
- 2025-08-24 — Project scaffolded

## Plan (next 7 days)
- Lock scope + guardrails; gather baseline metrics and ToS constraints; draft evaluation plan.

## Risks / Blocks
- Platform policy violations and safety — mitigation: strict guardrails + human-in-the-loop; pre-review ToS; automated moderation
- Ethical concerns and reputational risk — mitigation: explicit disclosures; opt-in consent; avoid explicit content generation
- Data access for evaluation — mitigation: use anonymized/redacted logs with consent

## Links
- Research: `projects/of/market_competitor_landscape.md` — Landscape of agencies/automation vendors, ToS constraints; moats: persona/memory packs, guardrails, whale detection.
- Pilot Playbook: `projects/of/pilot_playbook.md` — 3–4 week hybrid AI inbox pilot (cohorts A/B/C), KPIs and runbook, success/stop thresholds.
- Creator Offer: `projects/of/creator_offer.md` — Hybrid AI + human chat offer; 60/40 Creator/Agency rev-share; whale escalation; 24–72h onboarding.
- Investor Offer: `projects/of/investor_offer.md` — $100–250k raise one-pager: use of funds, milestones (GM≥55%, payback≤3mo), structures (Rev-Share Note/SAFE/SPV), risks.
- Exec Memo: `projects/of/exec_memo.md` — Exec rationale and unit economics; ToS policy risk; viability thresholds and base creator model.
