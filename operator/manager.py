from __future__ import annotations

from pathlib import Path

from agents import Runner

from .agents import (
    ProjectReport,
    TaskList,
    evaluator_agent,
    project_review_agent,
    task_loader_agent,
    time_allocator_agent,
)
from .tools import read_file, write_file


class FocusManager:
    """Coordinates agents to produce a daily schedule."""

    MAX_ATTEMPTS = 3

    async def run(self, goals: str, hours: str) -> None:
        """Run the daily focus workflow."""
        await self._review_projects()

        tasks_result = await Runner.run(task_loader_agent, "")
        tasks = tasks_result.final_output_as(TaskList)

        base_context = (
            f"Goals: {goals}\nAvailable hours: {hours}\nTasks: {tasks.model_dump_json()}"
        )
        context = base_context
        for attempt in range(self.MAX_ATTEMPTS):
            draft_result = await Runner.run(time_allocator_agent, context)
            draft = draft_result.final_output

            review_result = await Runner.run(evaluator_agent, draft_result.final_output)
            review = review_result.final_output

            if review.approved:
                schedule_text = read_file("schedule_tmp.md")
                write_file("schedule.md", schedule_text)
                return
            context = base_context + f"\nFeedback: {review.reason}"

    async def _review_projects(self) -> None:
        """Run the project review agent across all project directories."""
        projects_dir = Path(__file__).resolve().parent.parent / "projects"
        project_files = [
            str(p / "PROJECT.md")
            for p in projects_dir.iterdir()
            if (p / "PROJECT.md").exists()
        ]
        if project_files:
            await Runner.run(project_review_agent, "\n".join(project_files))
