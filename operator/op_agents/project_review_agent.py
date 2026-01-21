from __future__ import annotations

from pydantic import BaseModel

from agents import Agent
from operator.tools import read_project_file, read_repo_file, HAS_AGENTS_TOOL

PROMPT = (
    "You are a pragmatic project review assistant focused on impact.\n"
    "Input: ONE project document in the format '=== <path> ===\\n<contents>'.\n"
    "Goals:\n"
    "- Surface the most valuable next actions (concrete, high-leverage, unblocked).\n"
    "- Identify missing info and ask concise questions to the user.\n"
    "- Flag risks/blockers and suggest the smallest step to unblock.\n"
    "Output STRICT JSON with fields: {project: string, summary: string, migrated_tasks: string[], completed_task_queries?: string[], questions_for_user?: string[], risks?: string[]}.\n"
    "- migrated_tasks: actionable items suitable for the global tasks list; write in imperative voice, formatted as checkable items (e.g., '- [ ] Title :: priority=H|M|L; due=YYYY-MM-DD; ...'). Do not include project prefixes; the operator will infer project context.\n"
    "- completed_task_queries: short phrases to fuzzy-match tasks in tasks.md that appear completed in this project's doc (e.g., marked '[x]' or annotated as done). Keep each to 3–8 words.\n"
    "- questions_for_user: at most 3 brief questions if info is missing or decisions are needed.\n"
    "- risks: optional, short phrases highlighting blockers or uncertainties."
)


class ProjectReportItem(BaseModel):
    project: str
    summary: str
    migrated_tasks: list[str]
    questions_for_user: list[str] = []
    risks: list[str] = []
    completed_task_queries: list[str] = []


if HAS_AGENTS_TOOL:
    project_review_agent = Agent(
        name="ProjectReviewAgent",
        instructions=PROMPT,
        output_type=ProjectReportItem,
        model="gpt-5",
        tools=[read_project_file, read_repo_file],
    )
else:
    project_review_agent = Agent(
        name="ProjectReviewAgent",
        instructions=PROMPT,
        output_type=ProjectReportItem,
        model="gpt-5",
    )
