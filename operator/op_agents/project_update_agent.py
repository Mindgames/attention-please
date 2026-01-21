from __future__ import annotations

from pydantic import BaseModel

from agents import Agent
from operator.tools import (
    read_project_file,
    write_project_file,
    read_repo_file,
    write_repo_file,
    HAS_AGENTS_TOOL,
)

PROMPT = (
    "You are a precise project updater. You receive: a change request and optional context (current PROJECT.md + template/standards). "
    "Your job is to update projects/<slug>/PROJECT.md to reflect the requested focus while staying within repository standards.\n\n"
    "Use tools for I/O:\n"
    "- read_project_file(project_slug, 'PROJECT.md') to load the current document.\n"
    "- write_project_file(project_slug, 'PROJECT.md', updated_markdown) to persist the final document.\n\n"
    "Rules:\n"
    "- Keep front-matter style fields (Status/Owner/Updated/etc.) and set 'Updated:' to today in the body.\n"
    "- If asked to narrow focus (e.g., 'close the deal'), adjust Milestone/Current Milestone accordingly.\n"
    "- Update 'Top Tasks' to include only the next 3–7 aligned items; use checkable list items ('- [ ] ...') with canonical metadata ':: priority=H|M|L; effort=2h; due=YYYY-MM-DD; owner=@x'.\n"
    "- Update 'Plan (next 7 days)' and 'Risks/Blocks' as needed; preserve unrelated sections unless they conflict.\n"
    "- After writing, optionally return a short confirmation like 'OK'. If tools are unavailable, output ONLY the full updated PROJECT.md Markdown (no commentary).\n"
)


class ProjectUpdateResult(BaseModel):
    updated_markdown: str


if HAS_AGENTS_TOOL:
    project_update_agent = Agent(
        name="ProjectUpdateAgent",
        instructions=PROMPT,
        model="gpt-5",
        tools=[
            read_project_file,
            write_project_file,
            read_repo_file,
            write_repo_file,
        ],
    )
else:
    project_update_agent = Agent(
        name="ProjectUpdateAgent",
        instructions=PROMPT,
        model="gpt-5",
    )
