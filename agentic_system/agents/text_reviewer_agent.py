from typing import List

from pydantic import BaseModel

from agents import Agent  # type: ignore
from . import DEFAULT_MODEL

TEXT_REVIEW_PROMPT = (
    "You are an expert technical writer and editor. Given the path and contents "
    "of a documentation or text file, provide: (1) a concise summary of its "
    "purpose and key points; (2) constructive feedback on clarity, tone, and "
    "completeness, considering Human‑AI Partnership messaging; and (3) a list "
    "of concrete issues or TODOs (missing sections, outdated info, emotional "
    "tone improvements, etc.). Follow the schema exactly."
)


class TextFileReview(BaseModel):
    file: str
    """Relative path of the reviewed file."""

    summary: str
    """Concise summary (2‑4 sentences)."""

    feedback: str
    """Constructive feedback on clarity, tone, completeness."""

    issues: List[str]
    """List of specific issues / TODOs detected."""


text_reviewer_agent = Agent(
    name="TextReviewerAgent",
    instructions=TEXT_REVIEW_PROMPT,
    model=DEFAULT_MODEL,
    output_type=TextFileReview,
)
