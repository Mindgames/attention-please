# Repository Guidelines

## Project Structure & Module Organization
- Projects live in `projects/<slug>/` and are driven by a single `PROJECT.md` (see `projects/PROJECT_TEMPLATE.md`, `projects/STANDARDS.md`).
- Code and assets sit inside the project folder (example: `projects/research_bot/`).
- Archived, non‑personal material is under `archive/`.
- Naming: project slugs use kebab‑case (e.g., `igaming-change-intelligence`); Python modules use snake_case.

## Build, Test, and Development Commands
- Run personal research bot: `python -m projects.research_bot.main`
- Python: 3.10+. Create a venv and install your deps as needed (this repo intentionally avoids a global requirements file). Ensure the OpenAI Agents SDK is installed per its docs.
- Formatting (optional but encouraged): `black .` and `ruff .` if available.

## Coding Style & Naming Conventions
- Python: PEP 8, type hints, docstrings for public functions, small focused modules.
- Markdown: one H1 per file, concise sections, bullets for tasks; keep `PROJECT.md` current (status, milestone, top tasks, activity).
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
- This repo keeps the OpenAI Agents SDK in use (e.g., the research bot). Ensure the SDK is installed and available on `PYTHONPATH` so imports like `from agents import Runner` resolve.
