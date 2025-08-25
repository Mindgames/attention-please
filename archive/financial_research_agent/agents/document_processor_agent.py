from pydantic import BaseModel

from agents import Agent

# Document processor agent extracts key information from documents
DOCUMENT_PROCESSOR_PROMPT = (
    "You are a document analyst specializing in SEED ROUND investment "
    "documentation. You will be provided with a document and its content. "
    "Your task is to extract and summarize key information relevant to "
    "seed round investment analysis, including market opportunity, "
    "competitive positioning, financial metrics, team information, "
    "technology details, and strategic plans.\n\n"
    "IMPORTANT: Also assess:\n"
    "1. Document relevance to seed round investment (High/Medium/Low)\n"
    "2. Missing information that would strengthen the investment case\n"
    "3. Key data points that are mentioned but lack supporting details\n\n"
    "Structure your response as a concise summary that captures essential "
    "investment insights from the document."
)


class DocumentSummary(BaseModel):
    document_name: str
    """Name of the processed document."""

    relevance_score: str
    """High, Medium, or Low relevance to seed round investment."""

    key_insights: list[str]
    """Key insights extracted from the document."""

    missing_information: list[str]
    """Information mentioned but lacking details or missing entirely."""

    investment_relevance: str
    """How this document relates to the seed round investment thesis."""

    summary: str
    """Concise summary of the document content."""


document_processor_agent = Agent(
    name="SeedRoundDocumentProcessorAgent",
    instructions=DOCUMENT_PROCESSOR_PROMPT,
    model="o3",
    output_type=DocumentSummary,
)
