from typing import List

from pydantic import BaseModel

from agents import Agent  # type: ignore

FILE_SUMMARIZER_PROMPT = (
    "You are a senior code reviewer. Given the path and contents of a single project file, "
    "produce: (1) a concise summary of the file's purpose; (2) constructive feedback on "
    "clarity, style, and maintainability; and (3) a list of concrete issues or TODOs that "
    "should be addressed (bugs, missing docs, refactor opportunities, etc.). "
    "Output MUST follow the schema exactly."
)


class FileReview(BaseModel):
    file: str
    """Relative path of the reviewed file."""

    summary: str
    """Concise summary of the file's purpose and behavior (2‑4 sentences)."""

    feedback: str
    """Constructive feedback on code quality and maintainability."""

    issues: List[str]
    """List of specific issues / TODOs detected in the file."""


file_summarizer_agent = Agent(
    name="FileSummarizerAgent",
    instructions=FILE_SUMMARIZER_PROMPT,
    model="gpt-4.1",
    output_type=FileReview,
)
