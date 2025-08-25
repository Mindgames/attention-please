from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

from ..tools import write_file

PROMPT = (
    "Given a JSON list of tasks and the user's available hours, create a "
    "balanced daily schedule. Write a readable version to schedule_tmp.md using "
    "the write_file tool. Output the schedule as JSON with start, end, and "
    "description fields."
)


class ScheduleItem(BaseModel):
    start: str
    end: str
    description: str


class ScheduleDraft(BaseModel):
    items: list[ScheduleItem]


time_allocator_agent = Agent(
    name="TimeAllocatorAgent",
    instructions=PROMPT,
    tools=[write_file],
    output_type=ScheduleDraft,
)
