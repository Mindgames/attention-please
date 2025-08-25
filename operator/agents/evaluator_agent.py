from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "Review a proposed schedule for time conflicts, workload balance, and "
    "inclusion of personal time. Respond with JSON {approved: bool, reason: str}."
)


class Evaluation(BaseModel):
    approved: bool
    reason: str


evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=PROMPT,
    output_type=Evaluation,
)
