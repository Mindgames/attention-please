from pydantic import BaseModel

from agents import Agent  # type: ignore

EXPERT_PROMPT = (
    "You are a senior AI architect. You will receive a list of file reviews "
    "(each with summary, feedback, and issues). Synthesise ONE most valuable "
    "upgrade for the overall system or information base that will deliver the "
    "highest leverage towards Human‑AI Partnership and productivity goals. "
    "Return the upgrade and a short rationale following the schema."
)


class ExpertUpgrade(BaseModel):
    upgrade: str
    """A single highest‑value upgrade suggestion."""

    rationale: str
    """Why this is the most valuable upgrade now (2‑3 sentences)."""


expert_upgrade_agent = Agent(
    name="ExpertUpgradeAgent",
    instructions=EXPERT_PROMPT,
    model="gpt-4o-mini",
    output_type=ExpertUpgrade,
)
