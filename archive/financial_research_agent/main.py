import asyncio

from .manager import InvestmentMemoManager


# Entrypoint for the investment memo compiler.
# Run this as `python -m financial_research_agent.main` to compile your
# investment memo from the docs folder contents.
async def main() -> None:
    print("🔥 Investment Memo Compiler")
    print("Processing documents from docs/ folder...")
    mgr = InvestmentMemoManager()
    await mgr.run()


if __name__ == "__main__":
    asyncio.run(main())
