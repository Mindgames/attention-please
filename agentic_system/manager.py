from __future__ import annotations

import os
from typing import List

from rich.console import Console

# Agent runner from OpenAI Agents SDK
from agents import Runner  # type: ignore

from .agents.file_summarizer_agent import (  # type: ignore
    FileReview,
    file_summarizer_agent,
)
from .agents.text_reviewer_agent import (
    TextFileReview,
    text_reviewer_agent,
)  # type: ignore
from .agents.expert_upgrade_agent import expert_upgrade_agent  # type: ignore
from .printer import Printer  # type: ignore


class AgenticSystemManager:
    def __init__(self, project_root: str):
        self.console = Console()
        self.printer = Printer(self.console)
        self.project_root = project_root

    async def run(self) -> None:
        self.printer.update_item(
            "starting",
            f"Scanning project files in: {self.project_root}",
            is_done=True,
            hide_checkmark=True,
        )
        # Step 1: List all files in the project directory
        file_paths = self._list_project_files()
        file_count_msg = f"Found {len(file_paths)} files to review."
        self.printer.update_item(
            "file_count",
            file_count_msg,
            is_done=True,
        )
        # Step 2: Summarize and review each file, classified by type
        code_exts = {".py", ".js", ".ts", ".tsx"}
        code_reviews: list[FileReview] = []
        for file_path in file_paths:
            self.printer.update_item(
                f"summarizing_{file_path}",
                f"Summarizing {file_path}...",
            )
            contents = self._read_file_contents(file_path)
            _, ext = os.path.splitext(file_path)
            input_payload = (
                "File path: "
                f"{file_path}\n\nFile contents:\n{contents}"
            )
            try:
                if ext.lower() in code_exts:
                    res = await Runner.run(
                        file_summarizer_agent,
                        input_payload,
                    )
                    review = res.final_output_as(FileReview)
                    code_reviews.append(review)
                else:
                    res = await Runner.run(
                        text_reviewer_agent,
                        input_payload,
                    )
                    review = res.final_output_as(TextFileReview)
            except Exception:
                if ext.lower() in code_exts:
                    review = FileReview(
                        file=file_path,
                        summary="Error generating summary.",
                        feedback="",
                        issues=[],
                    )
                    code_reviews.append(review)
                else:
                    review = TextFileReview(
                        file=file_path,
                        summary="Error generating summary.",
                        feedback="",
                        issues=[],
                    )
            self.printer.mark_item_done(f"summarizing_{file_path}")

        # Step 3: Expert upgrade agent suggestion
        all_reviews = code_reviews
        try:
            expert_result = await Runner.run(
                expert_upgrade_agent,
                str([r.model_dump() for r in all_reviews]),
            )
            expert_upgrade = expert_result.final_output["upgrade"]
            expert_rationale = expert_result.final_output["rationale"]
        except Exception:
            expert_upgrade = "Error generating expert upgrade."
            expert_rationale = ""

        # Output results to console
        print("\n\n===== CODE FILE REVIEWS =====\n\n")
        for review in code_reviews:
            print(
                f"File: {review.file}\n"
                f"Summary: {review.summary}\n"
                f"Feedback: {review.feedback}\n"
                f"Issues: {review.issues}\n"
            )
        print("\n\n===== TOP EXPERT UPGRADE RECOMMENDATION =====\n\n")
        print(
            f"Upgrade: {expert_upgrade}\nRationale: {expert_rationale}\n"
        )
        self.printer.end()

        # Write output to markdown file
        output_path = os.path.join(
            os.path.dirname(__file__), "project_file_reviews.md"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Project File Reviews\n\n")
            f.write("## Code Reviews\n\n")
            for review in code_reviews:
                f.write(f"### {review.file}\n\n")
                f.write(f"**Summary:** {review.summary}\n\n")
                f.write(f"**Feedback:** {review.feedback}\n\n")
                if review.issues:
                    f.write("**Issues / TODOs:**\n")
                    for issue in review.issues:
                        f.write(f"- {issue}\n")
                    f.write("\n")
            f.write("# Top Expert Upgrade Recommendation\n\n")
            f.write(f"**Upgrade:** {expert_upgrade}\n\n")
            f.write(f"**Rationale:** {expert_rationale}\n\n")
        print(f"\nMarkdown output written to: {output_path}\n")

    def _list_project_files(self) -> List[str]:
        """
        Return a list of project files to review, based on extension and
        directory filters.
        """
        ALLOWED_EXTENSIONS = {
            ".md",
            ".markdown",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".json",
            ".yml",
            ".yaml",
            ".txt",
            ".env",
        }
        EXCLUDE_DIRS = {
            ".git",
            "node_modules",
            ".mypy_cache",
            "__pycache__",
        }

        file_paths: list[str] = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [
                d
                for d in dirs
                if d not in EXCLUDE_DIRS and not d.startswith(".")
            ]

            for file in files:
                # Skip hidden files
                if file.startswith("."):
                    continue
                _, ext = os.path.splitext(file)
                if ext.lower() not in ALLOWED_EXTENSIONS:
                    continue
                joined_path = os.path.join(root, file)
                rel_path = os.path.relpath(
                    joined_path,
                    self.project_root,
                )
                file_paths.append(rel_path)

        return sorted(file_paths)

    def _read_file_contents(
        self, relative_path: str, max_chars: int = 4000
    ) -> str:
        abs_path = os.path.join(self.project_root, relative_path)
        try:
            with open(
                abs_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                content = f.read(max_chars)
            if len(content) == max_chars:
                content += "\n...[truncated]"
            return content
        except Exception as exc:
            return f"[Error reading file: {exc}]"
