from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

from ..tools import read_file, write_file

PROMPT = (
    "You are a project review assistant. Given a list of project paths "
    "containing PROJECT.md files, read each file using the read_file tool. "
    "Summarize the project's health and extract any tasks that should be "
    "migrated to the global tasks.md. Append tasks using write_file. "
    "Return a JSON report summarizing findings for each project."
)


class ProjectReportItem(BaseModel):
    project: str
    summary: str
    migrated_tasks: list[str]


class ProjectReport(BaseModel):
    reports: list[ProjectReportItem]


project_review_agent = Agent(
    name="ProjectReviewAgent",
    instructions=PROMPT,
    tools=[read_file, write_file],
    output_type=ProjectReport,
)
