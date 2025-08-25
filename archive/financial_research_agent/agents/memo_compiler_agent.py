from pydantic import BaseModel

from agents import Agent

# Memo compiler agent synthesizes processed documents into seed round memo
MEMO_COMPILER_PROMPT = (
    "You are a senior investment analyst specializing in SEED ROUND "
    "investment memoranda. You will be provided with processed documents "
    "containing key insights about Grais.ai. Your task is to synthesize "
    "this information into a comprehensive, professional SEED ROUND "
    "investment memorandum that tells a compelling early-stage investment "
    "story.\n\n"
    "CRITICAL: This is for a SEED ROUND - focus on:\n"
    "- Early traction and validation\n"
    "- Founding team strength and execution capability\n"
    "- Market timing and opportunity size\n"
    "- Product-market fit indicators\n"
    "- Clear path to Series A milestones\n"
    "- Risk mitigation for early-stage concerns\n\n"
    "Structure your memo to include:\n"
    "1. Executive Summary (compelling 3-4 paragraph overview)\n"
    "2. Investment Highlights (top 5-7 key points)\n"
    "3. Market Opportunity & Problem Statement\n"
    "4. Solution & Product Vision\n"
    "5. Competitive Advantage & Technology\n"
    "6. Business Model & Path to Revenue\n"
    "7. Financial Projections & Unit Economics\n"
    "8. Founding Team & Execution Track Record\n"
    "9. Go-to-Market Strategy & Early Traction\n"
    "10. Use of Funds & Milestones to Series A\n"
    "11. Risk Factors & Mitigation Strategies\n"
    "12. Investment Terms & Conclusion\n\n"
    "Focus on creating a narrative that demonstrates why Grais.ai represents "
    "an exceptional SEED ROUND investment opportunity in the AI augmentation "
    "space. Use data and insights from the provided documents to support "
    "your thesis. Write in professional VC memo style."
)


class MemoCompilerData(BaseModel):
    executive_summary: str
    """A compelling 3-4 paragraph executive summary."""

    full_memo: str
    """The complete seed round investment memorandum in markdown format."""

    key_highlights: list[str]
    """Top 5-7 investment highlights as bullet points."""

    investment_thesis: str
    """Core investment thesis in 2-3 sentences."""

    seed_round_focus: str
    """Specific reasons why this is attractive for seed stage."""


memo_compiler_agent = Agent(
    name="SeedRoundMemoCompilerAgent",
    instructions=MEMO_COMPILER_PROMPT,
    model="o3",
    output_type=MemoCompilerData,
)
