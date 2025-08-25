from pydantic import BaseModel

from agents import Agent

# Verifier agent reviews the investment memo for quality and completeness
MEMO_VERIFIER_PROMPT = (
    "You are a senior investment analyst specializing in memo review and "
    "quality assurance. You will be provided with a compiled investment "
    "memorandum. Your task is to review it for:\n"
    "1. Completeness - Are all key sections present and comprehensive?\n"
    "2. Consistency - Are facts and figures consistent throughout?\n"
    "3. Persuasiveness - Does it present a compelling investment case?\n"
    "4. Professional Quality - Is it well-structured and clearly written?\n\n"
    "Provide specific feedback on strengths, areas for improvement, "
    "and any missing elements that would strengthen the investment case."
)


class MemoVerificationResult(BaseModel):
    overall_quality_score: int
    """Overall quality score from 1-10."""

    strengths: list[str]
    """Key strengths of the memo."""

    improvement_areas: list[str]
    """Areas that could be improved."""

    missing_elements: list[str]
    """Important elements that are missing."""

    recommendation: str
    """Overall recommendation and next steps."""


memo_verifier_agent = Agent(
    name="MemoVerifierAgent",
    instructions=MEMO_VERIFIER_PROMPT,
    model="o3",
    output_type=MemoVerificationResult,
)
