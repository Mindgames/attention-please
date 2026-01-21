from __future__ import annotations

from pathlib import Path
from typing import Optional

"""Repo-scoped file tools with resilient Agents SDK @tool import.

Some versions of the Agents SDK export a callable `tool` at `agents.tool`,
others as `agents.tools.tool`, and some as `from agents import tool`.
We detect and bind a working decorator; if none is available, we fall back
to a no-op decorator so functions remain usable directly.
"""

_tool_decorator = None
try:  # agents.tool callable
    from agents import tool as _cand  # type: ignore
    if callable(_cand):
        _tool_decorator = _cand
except Exception:
    pass
if _tool_decorator is None:
    try:  # agents.tool:tool
        from agents.tool import tool as _cand  # type: ignore
        if callable(_cand):
            _tool_decorator = _cand
    except Exception:
        pass
if _tool_decorator is None:
    try:  # agents.tools.tool
        from agents.tools import tool as _cand  # type: ignore
        if callable(_cand):
            _tool_decorator = _cand
    except Exception:
        pass

def tool(fn):  # type: ignore
    return _tool_decorator(fn) if callable(_tool_decorator) else fn

# Export whether a real Agents SDK tool decorator is available
HAS_AGENTS_TOOL = bool(callable(_tool_decorator))

# Base directory for all file operations
BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_path(path: str) -> Path:
    """Resolve a repository-relative path and ensure it stays within BASE_DIR."""
    full_path = (BASE_DIR / path).resolve()
    full_path.relative_to(BASE_DIR)  # raises ValueError if outside BASE_DIR
    return full_path


def read_file(path: str) -> str:
    """Return the contents of a text file located at ``path`` relative to the repository root."""
    file_path = _resolve_path(path)
    return file_path.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    """Write ``content`` to ``path`` relative to the repository root and return a confirmation message."""
    file_path = _resolve_path(path)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {file_path}"


# ==== Agents SDK tool wrappers (safe, repo-scoped) ====

@tool
def read_repo_file(path: str) -> str:
    """Read a UTF-8 text file at a repository-relative `path` (safe, repo-scoped)."""
    return read_file(path)


@tool
def write_repo_file(path: str, content: str) -> str:
    """Write UTF-8 `content` to a repository-relative `path` (safe, repo-scoped)."""
    return write_file(path, content)


def _resolve_project_path(project_slug: str, relative_path: Optional[str] = None) -> Path:
    rel = f"projects/{project_slug}"
    if relative_path:
        rel = f"{rel}/{relative_path}"
    return _resolve_path(rel)


@tool
def read_project_file(project_slug: str, relative_path: str = "PROJECT.md") -> str:
    """Read a text file under `projects/<slug>/` (default `PROJECT.md`)."""
    p = _resolve_project_path(project_slug, relative_path)
    return p.read_text(encoding="utf-8")


@tool
def write_project_file(
    project_slug: str,
    relative_path: str,
    content: str,
) -> str:
    """Write a text file under `projects/<slug>/`.

    - project_slug: folder name under `projects/`
    - relative_path: file path under that folder, e.g., `PROJECT.md` or `notes/README.md`
    - content: full file contents to write (UTF-8)
    """
    p = _resolve_project_path(project_slug, relative_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {p}"


# ==== Operator maintenance tools ====

@tool
async def sync_tasks_and_projects() -> str:
    """Synchronize 'tasks.md' with project docs.

    - Marks completed tasks (with 'project=<slug>' meta) as done inside the matching project's PROJECT.md,
      and appends a Recent Activity line.
    - Migrates new Top Tasks from all projects into 'tasks.md' (ensuring 'project=<slug>' is included).
    - Normalizes 'tasks.md' to deduplicate and ensure required metadata.
    Returns a short summary string.
    """
    from .manager import FocusManager

    mgr = FocusManager()
    return await mgr.sync_tasks_and_projects()
