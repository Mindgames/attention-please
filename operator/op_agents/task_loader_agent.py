from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are parsing the repository-level tasks.md to produce high-quality, actionable tasks.\n"
    "Instructions:\n"
    "- Tasks are checklist bullets. Prefer the canonical format: '- [ ] Description :: priority=H|M|L; due=YYYY-MM-DD; ...'.\n"
    "- Deduplicate and normalize phrasing; keep items concrete and outcome-oriented.\n"
    "- Extract 'due' when present (tokens like 'due=YYYY-MM-DD' or 'due: YYYY-MM-DD'). Use ISO date (YYYY-MM-DD).\n"
    "- Classify category as 'project' or 'personal'.\n"
    "- Infer 'priority' as an integer (1..5) from context (H≈5, M≈3, L≈1) and urgency.\n"
    "- Provide 'estimate' hours as a float (e.g., 0.25, 0.5, 1.0, 2.0).\n"
    "- If the project/context is clear (e.g., prefix like '[of]' or nearby headings), set 'project' to that slug; else omit.\n"
    "- Ignore headers, commentary, and non-actionable lines.\n"
    "Return STRICT JSON conforming to TaskList. No extra text."
)


class Task(BaseModel):
    description: str
    category: str
    priority: int
    estimate: float
    project: str | None = None
    due: str | None = None


class TaskList(BaseModel):
    tasks: list[Task]


task_loader_agent = Agent(
    name="TaskLoaderAgent",
    instructions=PROMPT,
    output_type=TaskList,
    model="gpt-5",
)
