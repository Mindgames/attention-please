import os
import asyncio
import logging
from dotenv import load_dotenv

try:
    from .manager import AgenticSystemManager  # type: ignore
except ImportError:  # Fallback if running as script
    from agentic_system.manager import AgenticSystemManager  # type: ignore

# Load environment variables from .env
load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(__file__),
        "..",
        ".env",
    )
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentic_system")


async def run_manager() -> None:
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    manager = AgenticSystemManager(project_root=project_root)
    await manager.run()


def main() -> None:
    logger.info("Starting Agentic System 2.0...")
    asyncio.run(run_manager())


if __name__ == "__main__":
    main()
