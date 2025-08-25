from __future__ import annotations

from pathlib import Path

from agents import tool

# Base directory for all file operations
BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(path: str) -> Path:
    """Resolve a repository-relative path and ensure it stays within BASE_DIR."""
    full_path = (BASE_DIR / path).resolve()
    full_path.relative_to(BASE_DIR)  # raises ValueError if outside BASE_DIR
    return full_path


@tool()
def read_file(path: str) -> str:
    """Return the contents of a text file located at ``path`` relative to the repository root."""
    file_path = _resolve_path(path)
    return file_path.read_text(encoding="utf-8")


@tool()
def write_file(path: str, content: str) -> str:
    """Write ``content`` to ``path`` relative to the repository root and return a confirmation message."""
    file_path = _resolve_path(path)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {file_path}"
