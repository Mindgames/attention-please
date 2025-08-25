from pydantic import BaseModel

from agents import Agent

# Critic agent provides detailed analysis and improvement suggestions
MEMO_CRITIC_PROMPT = (
    "You are a senior venture capital partner with 15+ years of experience "
    "reviewing seed round investment memoranda. You will be provided with "
    "a compiled investment memo and asked to provide detailed criticism "
    "and improvement suggestions.\n\n"
    "Your analysis should cover:\n\n"
    "1. CONTENT ANALYSIS:\n"
    "   - Strength of investment thesis\n"
    "   - Market sizing and opportunity validation\n"
    "   - Competitive differentiation clarity\n"
    "   - Financial projections realism\n"
    "   - Team credibility assessment\n\n"
    "2. STRUCTURAL ISSUES:\n"
    "   - Flow and narrative coherence\n"
    "   - Missing critical sections\n"
    "   - Weak or unsupported claims\n"
    "   - Inconsistencies or contradictions\n\n"
    "3. SEED ROUND SPECIFIC:\n"
    "   - Early-stage risk assessment\n"
    "   - Path to product-market fit\n"
    "   - Funding runway and milestones\n"
    "   - Scalability indicators\n\n"
    "4. PRESENTATION QUALITY:\n"
    "   - Professional tone and language\n"
    "   - Data visualization needs\n"
    "   - Supporting evidence strength\n\n"
    "Provide specific, actionable feedback that would help strengthen "
    "the investment case and address potential investor concerns."
)


class MemoCriticResult(BaseModel):
    overall_strength_score: int
    """Overall memo strength score from 1-10."""

    thesis_strength: str
    """Assessment of the core investment thesis strength."""

    critical_weaknesses: list[str]
    """Most critical weaknesses that must be addressed."""

    improvement_suggestions: list[str]
    """Specific actionable improvements to strengthen the memo."""

    missing_elements: list[str]
    """Key elements that are completely missing."""

    narrative_issues: list[str]
    """Issues with story flow, logic, or coherence."""

    seed_stage_concerns: list[str]
    """Specific concerns relevant to seed stage investment."""

    final_recommendation: str
    """Overall assessment and recommendation for next steps."""


memo_critic_agent = Agent(
    name="SeedRoundMemoCriticAgent",
    instructions=MEMO_CRITIC_PROMPT,
    model="o3",
    output_type=MemoCriticResult,
)
