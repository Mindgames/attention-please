from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

from ..tools import read_file

PROMPT = (
    "Read the repository-level tasks.md file and return a JSON array of tasks. "
    "Each task should include a description, category (project or personal), "
    "priority (1-5), and estimated hours to complete. Use the read_file tool "
    "to access tasks.md."
)


class Task(BaseModel):
    description: str
    category: str
    priority: int
    estimate: float


class TaskList(BaseModel):
    tasks: list[Task]


task_loader_agent = Agent(
    name="TaskLoaderAgent",
    instructions=PROMPT,
    tools=[read_file],
    output_type=TaskList,
)
