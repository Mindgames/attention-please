# Repository Guidelines

## Project Structure & Module Organization
- `scripts/attention-please.sh` is the main executable and contains all bash logic.
- `SKILL.md` defines the Codex skill metadata and expected behavior.
- `README.md` documents install and usage; keep it aligned with script behavior.
- `LICENSE` and `.gitignore` live at the repo root.
- If tests are added, place them under `tests/` to keep the root tidy.

## Build, Test, and Development Commands
This repo has no build step. Run the script directly:
- `scripts/attention-please.sh` — run inside a git repo to infer the project name.
- `ATTENTION_PLEASE_PROJECT="quiz-juice" scripts/attention-please.sh` — override the spoken name.
- `ATTENTION_PLEASE_SOUND="/System/Library/Sounds/Ping.aiff" scripts/attention-please.sh` — override the sound file.
- `bash -n scripts/attention-please.sh` — quick bash syntax check.

## Coding Style & Naming Conventions
- Bash only; keep `#!/usr/bin/env bash` and `set -euo pipefail`.
- Indent with 2 spaces in conditional blocks.
- Environment variables are uppercase with underscores (e.g., `ATTENTION_PLEASE_PROJECT`).
- Script files use kebab-case names with a `.sh` suffix.

## Testing Guidelines
- Run `bash tests/test-sound-toggle.sh` for sound preference and audio-routing regressions with temporary files and audio stubs.
- Manual verification: run `scripts/attention-please.sh` inside a repo and confirm sound, speech, and fallback behavior.
- If you add tests, document the framework and keep fixtures under `tests/`.

## Configuration & Environment
- macOS is required for `afplay` and `say`; the script prints a message if `say` is missing.
- Run from a git repo so `git remote get-url origin` can resolve a project name, or set `ATTENTION_PLEASE_PROJECT`.
- Avoid adding network or destructive operations; this script should remain side-effect light.

## Agent Behavior
- Use the `attention-please` script only when explicitly requested, a long-running task blocks on human input, or a background process finishes and needs attention. Do not alert after ordinary responses.

## Commit & Pull Request Guidelines
- Use short, imperative commit messages; current history shows `Initial attention-please skill`.
- Keep changes scoped; update `README.md` and `SKILL.md` when behavior changes.
- PRs should include a brief description, manual verification steps, and any OS-specific notes.
