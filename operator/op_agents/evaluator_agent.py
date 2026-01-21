from __future__ import annotations

from pydantic import BaseModel

from agents import Agent

PROMPT = (
    "You are an exacting schedule evaluator. Given Goals, Available hours (H), and a Schedule JSON, verify the plan is feasible and impact-focused.\n"
    "Approve only if ALL of the following hold:\n"
    "1) Total scheduled time <= H; 2) No overlaps; 3) Deep-work blocks exist for top tasks;\n"
    "4) Breaks and a lunch are reasonable; 5) High-leverage work scheduled early; 6) 15–30 min buffer near the end;\n"
    "7) Descriptions are specific/actionable; 8) If key info is missing, early 'clarify' blocks exist for critical tasks;\n"
    "9) At least one quick win (<= 30 min) is included when possible; 10) Optional 10–15 min improvement/reflection near the end is reasonable.\n"
    "Respond only with JSON: {approved: boolean, reason: string}. If not approved, the reason MUST include precise corrections (times, items to add/remove/move)."
)


class Evaluation(BaseModel):
    approved: bool
    reason: str


evaluator_agent = Agent(
    name="EvaluatorAgent",
    instructions=PROMPT,
    output_type=Evaluation,
    model="gpt-5",
)
