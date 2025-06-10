import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded so agents can read LLM_MODEL
root_dir = (
    Path(__file__).resolve().parent.parent.parent
)  # project root
load_dotenv(root_dir / ".env")

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4.1")
