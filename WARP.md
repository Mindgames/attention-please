# WARP.md

Quick commands and structure for this repo.

## Projects

- List projects: `ls projects/`
- Open a project: `ls projects/<project-name>/`
- Each project contains a `PROJECT.md` with scope, milestones, and tasks.

## Run Personal Research Bot

Uses the OpenAI Agents SDK.

- Run: `python -m projects.research_bot.main`
- Configure API keys in `.env`.

## Add a New Project

```bash
mkdir -p projects/my-new-project
cat > projects/my-new-project/PROJECT.md << 'EOF'
# My New Project

- Purpose: ...
- Status: ...

## Milestones
- ...

## Tasks
- [ ] ...

## Contents
- ...
EOF
```

