# Repository Guidelines

## Project Structure & Module Organization
- Projects live in `projects/<slug>/` and are driven by a single `PROJECT.md` (see `projects/PROJECT_TEMPLATE.md`, `projects/STANDARDS.md`).
- Code and assets sit inside the project folder (example: `projects/research_bot/`).
- Archived, non‑personal material is under `archive/`.
- Naming: project slugs use kebab‑case (e.g., `igaming-change-intelligence`); Python modules use snake_case.

## Build, Test, and Development Commands
- Use the `satcom` conda env for Python: `conda activate satcom`.
- Install deps (Python 3.10+): `pip install -r requirements.txt`
- Run research bot: `python -m projects.research_bot.main`
- Run operator (daily focus): `python -m operator.main`
- Record focus session check-ins: `python -m operator.checkins list` and `python -m operator.checkins complete --latest --summary "..." --next-task "..."`.
- Summarize time logs: `python -m operator.time_report` (add `--date YYYY-MM-DD` or `--include-breaks`).
- Formatting (optional): `black .` and `ruff .` if available.

## Coding Style & Naming Conventions
- Python: PEP 8, type hints, docstrings for public functions, small focused modules.
- Markdown: one H1 per file, concise sections. For tasks, use checkable lists (`- [ ]` / `- [x]`). Keep `PROJECT.md` current (status, milestone, Top Tasks, Recent Activity).
- Avoid one‑letter variables; keep changes minimal and scoped to a single project.

## Testing Guidelines
- Prefer `pytest` if tests are added: place under `projects/<slug>/tests/`, name files `test_*.py`.
- For agent flows, add lightweight offline tests (mock network, sample inputs). Keep runs deterministic.
- Run: `pytest -q` (if a test suite exists).

## Commit & Pull Request Guidelines
- Commits: imperative present, include the “why” and the project path. Example: `projects/of: add pilot playbook summary`.
- PRs: clear description, scope limited to one project, screenshots or sample output when UI/agent behavior changes, and links to the edited `PROJECT.md`.

## Security & Configuration Tips
- Configure API keys via `.env` (never commit secrets). Respect platform ToS and privacy; avoid logging PII. For long‑running agents, add guardrails and human‑in‑the‑loop where needed.

## Agent‑Specific Notes
- Uses the OpenAI Agents SDK (`openai-agents` on PyPI). Imports like `from agents import Agent, Runner, tool` should resolve after installing requirements.
- Agents should optimize for daily progress: prefer actions that unblock and move priority projects forward (review → migrate tasks → schedule → completion). When generating or migrating tasks, emit checkable items in the canonical format: `- [ ] Title :: priority=H|M|L; due=YYYY-MM-DD; ...`.

## Skills
- attention-please: play an alert sound and speak "Project NAME needs your attention"; run at the end of each turn, and also right before asking for input/confirmation if that happens earlier, with `ATTENTION_PLEASE_PROJECT="satcom"` (path: `.codex/skills/public/attention-please/SKILL.md`).
- daily-ops: orchestrate daily routines (daily automation loop, check-ins, focus/break timers, attention alerts); use on first message of the day, check-in requests, or focus/break requests (path: `.codex/skills/private/daily-ops/SKILL.md`).
- deadline-guard: scan tasks and project docs for due dates, surface overdue/due-soon items, and escalate scheduling; use during daily start/end routines or when deadlines are mentioned (path: `.codex/skills/private/deadline-guard/SKILL.md`).
- focus-timer: project-only focus timer with spoken prompts and pip alerts (path: `.codex/skills/private/focus-timer/SKILL.md`).
- daily-checkin: project-only daily check-in to capture state, journal, wellbeing, and metrics (path: `.codex/skills/private/daily-checkin/SKILL.md`).
- daily-routine: project-only daily automation loop that ensures auto-checkins run and tracks first-message-of-day state (path: `.codex/skills/private/daily-routine/SKILL.md`).
- daily-journal: private daily journaling with rotating prompts and time-of-day modes (path: `.codex/skills/private/daily-journal/SKILL.md`).

## Daily Ops Runbook
- First message of the day: run daily routine; if start-of-day check-in is pending, ask if the user is ready and then run it.
- After start-of-day check-in: run a journal entry with `python3 scripts/journal.py --mode start`.
- Daily priority scan (every morning): review `tasks.md` and `projects/*/PROJECT.md` (Top Tasks/Recent Activity), propose top 3 priorities before scheduling focus blocks.
- Daily priority scan: ensure each chosen priority has a deadline; propose and add one if missing.
- Daily deadline scan (morning + shutdown): run `python3 scripts/deadline_scan.py`; escalate overdue or due-soon items (default 3-day window unless overridden).
- Missed days/off-grid: run `python3 scripts/gap_reset.py` to log a gap note and light restart plan (keep prompts date-free).
- Focus blocks or breaks: start a focus timer (default 60-minute focus, 15-minute break unless specified).
- Midday reset: run the midday check-in when due or requested.
- End of day: run the end-of-day check-in (include metrics by default).
- After end-of-day check-in: run a journal entry with `python3 scripts/journal.py --mode end`.
- Assistant reflections: after end-of-day check-in or when requested, run `python3 scripts/assistant_reflection.py` to append to `operator/internal_reflections.md` and `operator/assistant_reflections.jsonl`.
- Failure handling: when the user flags a miss, log it immediately with a concrete fix.
- Prompt style: avoid enumerated lists; ask brief questions and fill logs in the background; journal is a separate optional flow.
- Break instruction: rotate break focus (reset/body/recovery/environment/admin), avoid repeating the same routine, and track daily goals (stretching, breathing, pushups toward 100/day, hydration, hygiene).
- Focus timer volume: always pass `--volume-boost 0` so volume stays unchanged.
- Before asking for input and at the end of each turn: run attention-please with `ATTENTION_PLEASE_PROJECT="satcom"`.


---
# Migration Task
Use docs in /var/folders/05/ds2vn7657bs5vjhzl6n_x_f40000gn/T/tmp.zdTRrtP4KW; migrate OpenAI completions→responses using model gpt-5.

- Do not preserve backward compatibility wrappers; adopt the Responses output shape across the codebase.
- Do not leave tombstone comments or backup files in the repo.
- If migrating to gpt-5, ensure 'temperature' is omitted or set to 1 to avoid errors.

## Operator Agents (current)

- `CoordinatorAgent`: routes intents — chat, show, review, schedule, update, complete, delete.
- `CoachAgent`: conversational coach; replies in Markdown, proposes 1–3 next tasks (canonical format), asks brief questions, and can suggest routing.
- `TaskLoaderAgent`: parses `tasks.md` into structured tasks.
- `TimeAllocatorAgent`: produces a JSON schedule for the day.
- `EvaluatorAgent`: validates the schedule against constraints/principles.
- `ProjectReviewAgent`: reviews `projects/<slug>/PROJECT.md`, migrates tasks, suggests completions.
- `ProjectUpdateAgent`: applies natural-language updates to project docs via tools.
- `ReminderAgent`: detects future events in chat and proposes normalized reminders (ISO with TZ).

Reminders are stored in `operator/reminders.jsonl`, surfaced when due, and can be confirmed inline in chat.

## User Notes (Personal Task Manager)

- 2025-12-26 - Timezone: CET.
- 2025-12-26 - Work start time varies; fixed schedule does not work.
- 2025-12-26 - Daily capacity: 10-16 hours (rough range).
- 2025-12-26 - Focus peak varies; context switching is the main drain.
- 2025-12-26 - This week's must-move projects: Grais.ai and Quizjuice.
- 2025-12-26 - Grais.ai goals mentioned: roll out new beta to testers; start raising next round; start building social media presence.
- 2025-12-26 - Grais.ai is the main company; Quizjuice is intended to be a self-running income stream.
- 2025-12-26 - Grais.ai top priority this week: get ready for beta.
- 2025-12-26 - "Beta ready" for Grais.ai includes: update how the system determines conversation type; review prompts and tools.
- 2025-12-26 - Grais.ai beta focus: exploratory; dating is the lowest-hanging fruit segment.
- 2025-12-26 - Wants structure in place before starting work; otherwise keeps thinking about everything else.
- 2025-12-26 - Quizjuice weekly outcome: finish it.
- 2025-12-26 - Quizjuice "finish" bullets: fix layout and pipeline of images/quizzes; connect streaming service.
- 2025-12-26 - Quizjuice streaming: use a proxy (e.g., StreamYard) to broadcast to multiple platforms; live quiz format with animal + animal = ?, capture chat answers and show a leaderboard between rounds.
- 2025-12-26 - Quizjuice streaming MVP target: YouTube, Twitch, TikTok, Facebook, Instagram, Kick.
- 2025-12-26 - Wants well-being, focus sessions, and break sessions included in the system.
- 2025-12-26 - Struggles with consistent well-being habits; has ADHD.
- 2025-12-26 - Unsure what well-being actions feel good; most options feel like pain.
- 2025-12-26 - Well-being preferences: stretching, 100 pushups daily, breathing exercises.
- 2025-12-27 - Uses stretching and breathing during breaks; wants to keep the routine.
- 2025-12-26 - 100 pushups can be split across the day.
- 2025-12-26 - Prefers rolling "start-now" schedules instead of fixed start times.
- 2025-12-26 - Wants updates communicated proactively.
- 2025-12-26 - Prefers dynamic daily hours (no fixed cap); work on a rolling basis.
- 2025-12-26 - Preferred focus block length: 90 minutes.
- 2025-12-26 - Fixed break length between focus blocks: 15 minutes.
- 2025-12-26 - Rolling schedule default: 2 blocks per check-in.
- 2025-12-26 - Prefers minimal questions to avoid overwhelm.
