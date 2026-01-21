# Project Folder Standards

Keep it simple: every project has a single source of truth in `projects/<slug>/PROJECT.md`. That file must capture the current state at a glance.

## Required file
- `PROJECT.md` with these sections:
  - Summary — 2–3 sentences on purpose and outcome
  - Status/Owner/Updated — quick metadata
  - Current Milestone — name, target date, success definition
  - Top Tasks — 3–5 next actions
  - Recent Activity (last 7 days) — dated bullets
  - Plan (next 7 days) — short bullets
  - Risks/Blocks — concise notes
  - Links — references if any

Use `projects/PROJECT_TEMPLATE.md` to start a new project.

## Programs with subprojects
For multi-part programs, create a parent folder with a program-level `PROJECT.md` plus subfolders for each subproject (each with its own `PROJECT.md`). See `projects/quizjuice/`.

## Conventions
- Dates: `YYYY-MM-DD`.
- Status: Planned | In Progress | On Hold | Done.
- Tasks: Use checkable lists for Top Tasks (`- [ ]` when open; `- [x]` when done). The global `tasks.md` must also use checkable bullets; when migrating tasks from projects, add them as `- [ ] ...` and include metadata where known (`:: priority=H|M|L; due=YYYY-MM-DD; owner=@x`).
- Prefer brevity. If a project needs deep history, keep only the last week in “Recent Activity” and summarize older items inline or archive as needed.
