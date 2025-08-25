# Mathias Asberg — Personal Projects

This repository tracks Mathias’s personal projects. Each project lives under `projects/` in its own folder and includes a `PROJECT.md` describing the project, milestones, tasks, and any associated files/code for that project.

## Structure

- `projects/<project-name>/` — One folder per project
  - `PROJECT.md` — Project description, milestones, tasks
  - Other files specific to the project (code, notes, assets)

See `projects/README.md` for the current project index.

## OpenAI Agents SDK

This repo keeps tools that use the OpenAI Agents SDK. The `research_bot` project is an example of a personal tool built on it.

- Run: `python -m projects.research_bot.main`
- Run daily focus assistant: `python -m operator.main`
- Requires Python 3.10+ and a configured `.env` with your API key(s)

## Add a New Project

1. Create a folder: `projects/<your-project-name>/`
2. Add a `PROJECT.md` (use `projects/PROJECT_TEMPLATE.md` as a starting point) with:
   - Purpose and scope
   - Milestones and tasks
   - Notes on any included files
3. Place all project-specific files inside that folder.

For multi-part programs (e.g., iGaming Change Intelligence), create a parent folder with a program-level `PROJECT.md` and put subprojects as subfolders, each with its own `PROJECT.md`.

## Archived Material

Prior company/investor documents and tools have moved to `archive/` to keep this repository focused on personal projects.
