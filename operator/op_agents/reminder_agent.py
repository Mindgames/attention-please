from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You detect future events/time references in a short user message and normalize them.\n"
    "Input contains 'now_iso' (ISO 8601 with offset). Use this as the reference time to resolve relative phrases like 'tomorrow', 'next Monday', or 'in 2 hours'.\n"
    "Assume times without timezone use the same offset as now_iso.\n"
    "Examples: 'demo Friday 14:00', 'tomorrow at 3pm', 'Oct 5 follow up with Sara'.\n"
    "Return proposals for reminders only when a real future time is implied. Ensure when_iso is strictly in the future relative to now_iso.\n"
    "Use ISO 8601 with timezone offset (e.g., 2025-09-10T14:00:00+02:00). Keep 'event' short (<=80 chars).\n"
    "Output STRICT JSON with schema only. No extra text."
)


class ProposedReminder(BaseModel):
    event: str
    when_iso: str  # ISO 8601 with offset
    ask_confirm: bool = True


class ReminderBatch(BaseModel):
    reminders: list[ProposedReminder]


reminder_agent = Agent(
    name="ReminderAgent",
    instructions=PROMPT,
    output_type=ReminderBatch,
    model="gpt-5",
)
