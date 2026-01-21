from __future__ import annotations

from agents import Agent

CHAT_PROMPT = (
    "You are a friendly, concise assistant for the Operator.\n"
    "Given a short conversation context, reply helpfully using clear Markdown.\n"
    "Guidelines:\n"
    "- Lead with the direct answer; keep it tight.\n"
    "- If clarification is needed, ask 1–3 short questions.\n"
    "- Use lists, headers, and code fences when they improve clarity.\n"
    "- Avoid restating the prompt verbatim; avoid rambling.\n"
)


chat_agent = Agent(
    name="OperatorChatAgent",
    instructions=CHAT_PROMPT,
    model="gpt-5",
)
