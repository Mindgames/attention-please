from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

from agents import Runner

from .op_agents import (
    TaskList,
    evaluator_agent,
    project_review_agent,
    project_update_agent,
    task_loader_agent,
    time_allocator_agent,
    CoordinatorDecision,
    coordinator_agent,
)
from .tools import read_file, write_file
from .terminal import terminal


class FocusManager:
    """Coordinates agents to produce a daily schedule."""

    MAX_ATTEMPTS = 3

    def __init__(self) -> None:
        # Rolling conversation history as list of (role, text)
        self._history: list[tuple[str, str]] = []
        # Best-effort integration with Agents SDK context (if available)
        self._runner_kwargs: dict[str, object] = {}
        try:
            # Lazily import context from Agents SDK, then create a chat/thread context if exposed.
            from agents import context as agents_context  # type: ignore

            # Attempt common factory APIs; ignore if unavailable.
            ctx = None
            if hasattr(agents_context, "thread"):
                # e.g., agents.context.thread("Operator Chat")
                ctx = agents_context.thread("Operator Chat")  # type: ignore[attr-defined]
            elif hasattr(agents_context, "Conversation"):
                ctx = agents_context.Conversation("Operator Chat")  # type: ignore[attr-defined]
            elif hasattr(agents_context, "Context"):
                ctx = agents_context.Context()

            if ctx is not None:
                # Runner.run may accept 'context' kwarg in recent SDKs
                self._runner_kwargs["context"] = ctx
        except Exception:
            # Context integration is optional; fall back to local history only.
            self._runner_kwargs = {}
        # Pending destructive actions awaiting confirmation
        self._pending_delete_slug: str | None = None

    async def run(
        self,
        goals: str | None = None,
        hours: str | None = None,
        note: str | None = None,
        status_only: bool = False,
        only_project: str | None = None,
    ) -> str | None:
        """Run the daily focus workflow without interactive prompts.

        - goals: optional focus statement; if None, uses a professional, impact-first default.
        - hours: optional available hours; if None, uses env FOCUS_HOURS or 6.
        """
        goals = goals or (
            "Maximize impact today: execute top-priority, high-leverage tasks; unblock dependencies; "
            "deliver tangible outcomes; protect deep-work time; include short breaks and a buffer."
        )
        # Default to 996-style day (12h) unless overridden
        hours = hours or os.getenv("FOCUS_HOURS", "12")
        # Track user message in history for coordinator context.
        if note:
            self._history.append(("user", note))
        # Handle pending confirmations first
        if self._pending_delete_slug and note:
            decision = note.strip().lower()
            if decision in {"yes", "y", "confirm", "ok"}:
                reply = self._delete_project(
                    self._pending_delete_slug
                )
                self._pending_delete_slug = None
                self._history.append(("assistant", reply))
                return reply
            if decision in {"no", "n", "cancel"}:
                reply = "Canceled. Project was not deleted."
                self._pending_delete_slug = None
                self._history.append(("assistant", reply))
                return reply
        # Decide what to do based on request flags / note
        # Quick time query handling
        if note and note.strip().lower() in {
            "now",
            "time",
            "date",
            "what time is it",
            "what's the time",
        }:
            reply = terminal.info(f"Now: {self._now_string()}")
            self._history.append(("assistant", reply))
            return reply

        intent = self._infer_intent(note, status_only)
        if intent is None:
            # Use the lightweight coordinator to decide how to respond without loading tasks/projects.
            coordinator_input = self._compose_coordinator_input(
                note or ""
            )
            decision_result = await Runner.run(
                coordinator_agent,
                coordinator_input,
                **self._runner_kwargs,
            )
            decision = decision_result.final_output_as(
                CoordinatorDecision
            )
            if decision.action == "delete":
                query = decision.project_query or (note or "")
                reply = self._handle_delete_request(
                    query, decision.confirm
                )
                self._history.append(("assistant", reply))
                return reply
            if decision.action == "complete":
                if not decision.task_query:
                    reply = "Which task should I mark complete? Please specify a short name."
                    self._history.append(("assistant", reply))
                    return reply
                reply = self._complete_task(
                    decision.task_query, decision.project
                )
                self._history.append(("assistant", reply))
                return reply
            if decision.action == "show":
                # If coordinator didn't set a project, try to infer from the note
                only_proj = decision.project or decision.project_query
                if not only_proj and note:
                    repo_root = Path(__file__).resolve().parent.parent
                    projs_dir = repo_root / "projects"
                    lowered = note.lower()
                    candidates = []
                    for p in projs_dir.iterdir():
                        if (p / "PROJECT.md").exists():
                            slug = p.name
                            hay = f"{slug} {slug.replace('-', ' ')} {slug.replace('_', ' ')}".lower()
                            score = sum(
                                1
                                for w in lowered.split()
                                if w and w in hay
                            )
                            if score > 0:
                                candidates.append((score, slug))
                    if candidates:
                        candidates.sort(reverse=True)
                        only_proj = candidates[0][1]
                reply = await self._show_schedule_or_tasks(
                    only_project=only_proj
                )
                self._history.append(("assistant", reply))
                return reply
            if decision.action == "chat":
                reply = (
                    decision.message
                    or "Hello! Say 'status' to review projects or 'plan' to schedule."
                )
                self._history.append(("assistant", reply))
                return reply
            if decision.action == "review":
                print(
                    terminal.info(
                        "Reviewing projects (per coordinator)...",
                        terminal.formatter._emoji("🔍"),
                    )
                )
                await self._review_projects(
                    only_project=decision.project
                    or decision.project_query
                )
                print(terminal.success("Project review complete."))
                self._history.append(
                    ("assistant", "Project review complete.")
                )
                return None
            if decision.action == "update":
                proj_query = (
                    decision.project or decision.project_query or ""
                ).strip()
                # Smart handling: bulk maintenance requests like "all projects" or
                # "go over projects" should run a review/sync across all projects.
                lowered = (note or "").lower()
                wants_bulk = (
                    not proj_query
                    or proj_query
                    in {
                        "all",
                        "all projects",
                        "projects",
                        "everything",
                    }
                    or "all projects" in lowered
                    or "go over projects" in lowered
                    or "sync" in lowered
                    or "migrate" in lowered
                    or "move new tasks" in lowered
                )
                if wants_bulk:
                    print(
                        terminal.info(
                            "Bulk sync across projects: scanning tasks.md and project docs…",
                            terminal.formatter._emoji("🔄"),
                        )
                    )
                    reply = await self.sync_tasks_and_projects()
                    self._history.append(("assistant", reply))
                    return reply
                # Single-project update path
                reply = await self._update_project(
                    proj_query, note or ""
                )
                self._history.append(("assistant", reply))
                return reply
            if decision.action == "schedule":
                # Fall through to scheduling path with potential overrides
                goals = decision.goals or goals
                hours = decision.hours or hours
                intent = "schedule"
        if intent == "review":
            # For bulk maintenance requests like "sync/migrate tasks across projects",
            # run the synchronization workflow instead of a plain review.
            lowered = (note or "").lower()
            if any(
                k in lowered
                for k in [
                    "sync tasks",
                    "sync task",
                    "migrate tasks",
                    "move new tasks",
                    "update completed tasks",
                    "sync projects",
                    "sync tasks and projects",
                    "go over projects",
                ]
            ):
                print(
                    terminal.info(
                        "Synchronizing tasks and projects (per request)...",
                        terminal.formatter._emoji("🔄"),
                    )
                )
                reply = await self.sync_tasks_and_projects()
                print(terminal.success("Sync complete."))
                return reply
            print(
                terminal.info(
                    "Reviewing projects (per request)...",
                    terminal.formatter._emoji("🔍"),
                )
            )
            await self._review_projects(only_project=only_project)
            print(terminal.success("Project review complete."))
            return
        if intent == "delete" and note:
            reply = self._handle_delete_request(note, None)
            self._history.append(("assistant", reply))
            return reply
        if intent == "complete" and note:
            # naive extraction if coordinator didn't fire
            reply = self._complete_task(note, None)
            self._history.append(("assistant", reply))
            return reply
        if intent == "show":
            # Try to scope to a project mentioned in the note
            only_proj = None
            if note:
                repo_root = Path(__file__).resolve().parent.parent
                projs_dir = repo_root / "projects"
                lowered = note.lower()
                candidates = []
                for p in projs_dir.iterdir():
                    if (p / "PROJECT.md").exists():
                        slug = p.name
                        hay = f"{slug} {slug.replace('-', ' ')} {slug.replace('_', ' ')}".lower()
                        score = sum(
                            1
                            for w in lowered.split()
                            if w and w in hay
                        )
                        if score > 0:
                            candidates.append((score, slug))
                if candidates:
                    candidates.sort(reverse=True)
                    only_proj = candidates[0][1]
            reply = await self._show_schedule_or_tasks(
                only_project=only_proj
            )
            self._history.append(("assistant", reply))
            return reply
        # If the user is asking to view today's schedule, show existing schedule if available.
        if intent == "schedule" and note:
            lowered = note.lower()
            if any(
                key in lowered
                for key in [
                    "what's my schedule",
                    "what is my schedule",
                    "show schedule",
                    "schedule today",
                    "tasks schedule today",
                    "what's my tasks schedule",
                    "what is my tasks schedule",
                ]
            ):
                repo_root = Path(__file__).resolve().parent.parent
                sched_path = repo_root / "schedule.md"
                if sched_path.exists():
                    schedule_text = sched_path.read_text(
                        encoding="utf-8"
                    )
                    reply = (
                        "Here is your current schedule:\n\n"
                        + schedule_text
                    )
                    self._history.append(("assistant", reply))
                    return reply

        # Load tasks.md contents and have the agent parse it
        print(
            terminal.info(
                "Loading tasks.md and parsing tasks...",
                terminal.formatter._emoji("📝"),
            )
        )
        # Normalize tasks.md to checklist format with priority and due fields
        self._normalize_tasks_file()
        tasks_md = read_file("tasks.md")
        tasks_result = await Runner.run(
            task_loader_agent, tasks_md, **self._runner_kwargs
        )
        tasks = tasks_result.final_output_as(TaskList)
        print(terminal.success(f"Parsed {len(tasks.tasks)} tasks."))

        now_str = self._now_string()
        base_context = (
            "You are a professional focus operator optimizing for impact.\n"
            f"Today: {now_str}\n"
            f"Goals: {goals}\n"
            f"Available hours: {hours}\n"
            "Preferences: Workday window 09:00–21:00 (996). Schedule H hours within this window. "
            "Prioritize deep-work blocks (60–90 min) for high-value tasks; reduce context switching; "
            "add 10–15 min breaks between blocks; include a ~30 min lunch around 12:30 and a ~30 min dinner around 18:30; "
            "reserve a 15–30 min buffer near the end.\n"
            + (f"User note: {note}\n" if note else "")
            + f"Tasks: {tasks.model_dump_json()}"
        )
        context = base_context
        for attempt in range(self.MAX_ATTEMPTS):
            print(
                terminal.info(
                    f"Scheduling attempt {attempt + 1}/{self.MAX_ATTEMPTS}...",
                    terminal.formatter._emoji("⏳"),
                )
            )
            draft_result = await Runner.run(
                time_allocator_agent, context, **self._runner_kwargs
            )
            draft = draft_result.final_output
            # Ensure evaluator receives a textual/JSON representation
            schedule_json = (
                draft.model_dump_json()
                if hasattr(draft, "model_dump_json")
                else str(draft)
            )
            eval_input = f"Today: {now_str}\nGoals: {goals}\nAvailable hours: {hours}\nSchedule: {schedule_json}"
            review_result = await Runner.run(
                evaluator_agent, eval_input, **self._runner_kwargs
            )
            review = review_result.final_output

            if review.approved:
                # Render a simple markdown schedule, persist it, and return it to the user
                lines = ["# Schedule"]
                for item in getattr(draft, "items", []):
                    lines.append(
                        f"- {item.start}–{item.end}: {item.description}"
                    )
                schedule_text = "\n".join(lines) + "\n"
                write_file("schedule.md", schedule_text)
                print(
                    terminal.success(
                        "Schedule approved. Wrote schedule.md"
                    )
                )
                reply = terminal.show_schedule(schedule_text)
                self._history.append(("assistant", reply))
                return reply
            print(terminal.warning(f"Not approved: {review.reason}"))
            context = base_context + f"\nFeedback: {review.reason}"
        # If we reach here, attempts exhausted
        failure_msg = terminal.error(
            "Unable to produce an approved schedule after several attempts. "
            "Try refining goals or hours, or say 'show schedule' or 'status'."
        )
        self._history.append(("assistant", failure_msg))
        return failure_msg

    async def _review_projects(
        self, only_project: str | None = None
    ) -> None:
        """Run the project review agent across all project directories."""
        # Use repository-relative paths
        repo_root = Path(__file__).resolve().parent.parent
        projects_dir = repo_root / "projects"
        # Normalize generic selectors to None (means: all projects)
        if only_project and only_project.lower().strip() in {
            "all",
            "all projects",
            "projects",
            "everything",
            "all tasks and projects",
        }:
            only_project = None
        project_paths = []
        for p in projects_dir.iterdir():
            project_md = p / "PROJECT.md"
            if project_md.exists():
                if only_project:
                    slug = p.name.lower()
                    if only_project.lower() in slug:
                        project_paths.append(project_md)
                else:
                    project_paths.append(project_md)

        # Process one project at a time using a while-loop
        i = 0
        total = len(project_paths)
        print(
            terminal.info(
                f"Found {total} project(s) with PROJECT.md.",
                terminal.formatter._emoji("📁"),
            )
        )

        # Create progress indicator
        progress = terminal.loading("Reviewing projects...")
        progress.start()

        try:
            while i < len(project_paths):
                project_md = project_paths[i]
                rel = project_md.relative_to(repo_root)
                content = project_md.read_text(encoding="utf-8")
                section = f"=== {rel} ===\n{content}"
                result = await Runner.run(
                    project_review_agent,
                    section,
                    **self._runner_kwargs,
                )
                item = result.final_output
                # Append migrated tasks to tasks.md if any
                if getattr(item, "migrated_tasks", None):
                    existing = (
                        read_file("tasks.md")
                        if Path(repo_root / "tasks.md").exists()
                        else ""
                    )
                    # Ensure migrated tasks are added as checkable items
                    slug = project_md.parent.name
                    appended_items: list[str] = []
                    for raw in item.migrated_tasks:
                        line = str(raw).strip()
                        # Normalize to checkbox format
                        if not line.lstrip().startswith(
                            ("- [", "* [")
                        ):
                            line = f"- [ ] {line}"
                        # Ensure project meta is included
                        if "project=" not in line:
                            sep = " :: " if "::" in line else " :: "
                            line = f"{line}{sep}project={slug}"
                        appended_items.append(line)
                    appended = (
                        existing.rstrip()
                        + "\n"
                        + "\n".join(appended_items)
                        + "\n"
                    )
                    write_file("tasks.md", appended)

                # Show project review result
                summary = item.summary[:80] + (
                    "..." if len(item.summary) > 80 else ""
                )
                print(
                    f"\n{terminal.formatter.bullet(f'Reviewed {rel}: {summary}')}"
                )

                # If the agent surfaced completed task queries, mark them done in tasks.md
                completed_qs = (
                    getattr(item, "completed_task_queries", []) or []
                )
                if completed_qs:
                    for q in completed_qs[
                        :20
                    ]:  # cap to avoid runaway edits
                        try:
                            msg = self._complete_task(q, None)
                            if (
                                msg
                                and "I couldn't find" not in msg
                                and "multiple matching" not in msg
                            ):
                                print(
                                    terminal.success(
                                        f"Marked complete: {q}"
                                    )
                                )
                        except Exception:
                            pass
                # If the agent requested missing info, surface it to the user immediately
                questions = (
                    getattr(item, "questions_for_user", []) or []
                )
                if questions:
                    print(
                        terminal.warning("Info needed to progress:")
                    )
                    for q in questions[:3]:
                        print(f"  {terminal.formatter.bullet(q)}")
                i += 1
        finally:
            progress.stop()
        # After processing projects, normalize tasks file to avoid duplicates
        try:
            self._normalize_tasks_file()
        except Exception:
            pass

    async def sync_tasks_and_projects(self) -> str:
        """Synchronize tasks between the global tasks.md and project PROJECT.md files.

        - Reads tasks.md and finds completed items ("[x]") that include a project meta (project=<slug>).
        - For each completed item, marks the corresponding Top Task complete in that project's PROJECT.md
          and appends a Recent Activity line.
        - Reviews all projects to migrate any new Top Tasks into tasks.md, ensuring project meta is included.
        - Normalizes tasks.md format.

        Returns a short summary string.
        """
        repo_root = Path(__file__).resolve().parent.parent
        tasks_path = repo_root / "tasks.md"
        completed = 0
        migrated = 0

        # 1) Normalize tasks ahead of time
        try:
            self._normalize_tasks_file()
        except Exception:
            pass

        # 2) Propagate completed tasks with project meta to project docs
        if tasks_path.exists():
            lines = tasks_path.read_text(
                encoding="utf-8"
            ).splitlines()
            for ln in lines:
                s = ln.strip()
                if not s.startswith(("- ", "* ")):
                    continue
                # Only consider explicit completed items
                if "[x]" not in s.lower():
                    continue
                # Extract description up to meta separator and parse meta
                content = s.lstrip("-* ").strip()
                # Strip checkbox token
                if content.startswith("[x]") or content.startswith(
                    "[X]"
                ):
                    content = content[3:].strip()
                # Split description vs meta
                if "::" in content:
                    desc_part, meta_part = content.split("::", 1)
                else:
                    desc_part, meta_part = content, ""
                desc = desc_part.strip()
                project_slug = None
                if meta_part:
                    # meta tokens separated by ';'
                    for tok in meta_part.split(";"):
                        t = tok.strip()
                        if t.lower().startswith("project="):
                            project_slug = t.split("=", 1)[1].strip()
                            break
                if project_slug:
                    msg = self._complete_task(desc, project_slug)
                    if msg and (
                        "Updated projects/" in msg
                        or "Project '" in msg
                        or "Top Task" in msg
                    ):
                        completed += 1

        # 3) Review projects to migrate new tasks and include project meta in tasks.md
        before = 0
        if tasks_path.exists():
            before = sum(
                1
                for ln in tasks_path.read_text(
                    encoding="utf-8"
                ).splitlines()
                if ln.strip().startswith(("- ", "* "))
            )
        await self._review_projects(only_project=None)
        after = 0
        if tasks_path.exists():
            after = sum(
                1
                for ln in tasks_path.read_text(
                    encoding="utf-8"
                ).splitlines()
                if ln.strip().startswith(("- ", "* "))
            )
        migrated = max(0, after - before)

        # 4) Normalize again
        try:
            self._normalize_tasks_file()
        except Exception:
            pass

        return terminal.success(
            f"Synced tasks. Marked {completed} completed item(s) in project docs and migrated {migrated} new task(s) to tasks.md."
        )

    async def _update_project(
        self, project_query: str, change_request: str
    ) -> str:
        """Update a single project's PROJECT.md based on a natural language request.

        - Finds a matching project by slug substring.
        - Runs ProjectUpdateAgent to produce a new Markdown and writes it.
        """
        repo_root = Path(__file__).resolve().parent.parent
        projects_dir = repo_root / "projects"
        matches = []
        q = project_query.lower().strip()
        for p in projects_dir.iterdir():
            md = p / "PROJECT.md"
            if md.exists() and q in p.name.lower():
                matches.append(md)
        if not matches:
            return terminal.error(
                f"I couldn't find a project matching '{project_query}'."
            )
        if len(matches) > 1:
            names = ", ".join(m.parent.name for m in matches)
            return terminal.warning(
                f"Multiple projects match '{project_query}': {names}. Please be more specific."
            )
        project_md = matches[0]

        # Build input for the updater agent with tool-first guidance
        template_path = repo_root / "projects" / "PROJECT_TEMPLATE.md"
        standards_path = repo_root / "projects" / "STANDARDS.md"
        guidance = [
            f"PROJECT_SLUG: {project_md.parent.name}",
            "INSTRUCTIONS: Use tools to read the current PROJECT.md, apply the change request, and write the updated doc.",
            f"CHANGE REQUEST:\n{change_request}",
        ]
        if template_path.exists():
            guidance.append(
                f"TEMPLATE:\n{template_path.read_text(encoding='utf-8')}"
            )
        if standards_path.exists():
            guidance.append(
                f"STANDARDS:\n{standards_path.read_text(encoding='utf-8')}"
            )
        updater_input = "\n\n".join(guidance)

        result = await Runner.run(
            project_update_agent, updater_input, **self._runner_kwargs
        )
        # Prefer tool writes; treat any non-empty output as confirmation. Fallback to manager-side write if content returned.
        final = getattr(result, "final_output", None)
        if isinstance(final, str):
            out = final.strip()
            # If the agent chose to return full markdown instead of using tools, persist it
            if (
                out.startswith("# ")
                or out.startswith("---")
                or "## " in out
            ):
                project_md.write_text(out + "\n", encoding="utf-8")
                return terminal.success(
                    f"Updated {project_md.relative_to(repo_root)} (manager write)."
                )
            if out:
                return terminal.success(
                    out
                )  # e.g., 'OK' or tool confirmation text
            return terminal.success("Project update completed.")
        # If model returned an object, stringify and try to detect markdown
        text = str(result.final_output).strip()
        if text:
            if (
                text.startswith("# ")
                or text.startswith("---")
                or "## " in text
            ):
                project_md.write_text(text + "\n", encoding="utf-8")
                return terminal.success(
                    f"Updated {project_md.relative_to(repo_root)} (manager write)."
                )
            return terminal.success(text)
        return terminal.warning(
            "The update agent produced no output; if no file changes appeared, try again or be more specific."
        )

    def _normalize_tasks_file(self) -> None:
        """Normalize and de-duplicate tasks.md with lightweight project inference.

        Goals:
        - Ensure bullets are '- [ ] ...' or '- [x] ...'.
        - Ensure a metadata block exists using '::' with at least 'priority=' and 'due=' tokens.
        - Normalize 'due: YYYY-MM-DD' to 'due=YYYY-MM-DD'. Default to 'due=unset' if missing.
        - If no priority, map from 'impact=H/M/L' when present; else default to 'priority=M'.
        - Heuristically infer 'project=<slug>' if missing by matching project slugs in description.
        - De-duplicate tasks by (normalized description, project) key; prefer: done > project set > more meta.
        - Preserve non-bullet lines as-is.
        """
        repo_root = Path(__file__).resolve().parent.parent
        tasks_path = repo_root / "tasks.md"
        if not tasks_path.exists():
            return
        original = tasks_path.read_text(encoding="utf-8").splitlines()
        out_lines: list[str] = []
        import re

        date_re = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

        # Build simple project inference index
        projs_dir = repo_root / "projects"
        candidates: list[tuple[str, set[str]]] = []  # (slug, tokens)
        try:
            for p in projs_dir.iterdir():
                if not (p / "PROJECT.md").exists():
                    continue
                slug = p.name
                tokens = {
                    slug.lower(),
                    slug.replace("-", " ").lower(),
                    slug.replace("_", " ").lower(),
                }
                # Try to include title words from H1
                try:
                    txt = (p / "PROJECT.md").read_text(
                        encoding="utf-8"
                    )
                    for ln in txt.splitlines():
                        s = ln.strip()
                        if s.startswith("# "):
                            title = s[2:].strip().lower()
                            tokens.add(title)
                            break
                except Exception:
                    pass
                candidates.append((slug, tokens))
        except Exception:
            pass

        # First pass: parse and normalize bullets, collect for de-duplication
        parsed: list[
            tuple[str, str, bool, dict[str, str], list[str]]
        ] = []
        # each item: (original_stripped, desc, done, tokens, other_tokens)

        for line in original:
            s = line.rstrip("\n")
            stripped = s.strip()
            if not stripped.startswith(("- ", "* ", "- [", "* [")):
                out_lines.append(s)
                continue
            content = stripped
            done = False
            if content.startswith(("- [x] ", "* [x] ")):
                done = True
                content = content[6:]
            elif content.startswith(("- [ ] ", "* [ ] ")):
                content = content[6:]
            else:
                content = content[2:].lstrip()

            if "::" in content:
                desc_part, meta_part = content.split("::", 1)
                desc = desc_part.strip()
                meta = meta_part.strip()
            else:
                desc = content.strip()
                meta = ""

            tokens_raw = (
                [t.strip() for t in meta.split(";") if t.strip()]
                if meta
                else []
            )
            tokens: dict[str, str] = {}
            other_tokens: list[str] = []
            for t in tokens_raw:
                if "=" in t:
                    k, v = t.split("=", 1)
                    tokens[k.strip().lower()] = v.strip()
                elif ":" in t:
                    k, v = t.split(":", 1)
                    tokens[k.strip().lower()] = v.strip()
                else:
                    other_tokens.append(t)

            if "due:" in desc.lower() and "due" not in tokens:
                m = date_re.search(desc)
                if m:
                    tokens["due"] = m.group(1)
            if "due" in tokens:
                m2 = (
                    date_re.search(tokens["due"])
                    if tokens["due"]
                    else None
                )
                if m2:
                    tokens["due"] = m2.group(1)
            else:
                tokens["due"] = "unset"

            if "priority" not in tokens:
                imp = tokens.get("impact")
                if imp:
                    imp_norm = imp.strip().upper()[:1]
                    if imp_norm in {"H", "M", "L"}:
                        tokens["priority"] = imp_norm
                if "priority" not in tokens:
                    tokens["priority"] = "M"

            # Heuristic project inference (only if missing)
            if "project" not in tokens and candidates:
                lower_desc = desc.lower()
                scored: list[tuple[int, str]] = []
                for slug, toks in candidates:
                    score = 0
                    for tk in toks:
                        if tk and tk in lower_desc:
                            score += 1
                    if score > 0:
                        scored.append((score, slug))
                if scored:
                    scored.sort(reverse=True)
                    top = scored[0]
                    if len(scored) == 1 or (
                        len(scored) > 1 and top[0] > scored[1][0]
                    ):
                        tokens["project"] = top[1]

            parsed.append(
                (stripped, desc, done, tokens, other_tokens)
            )

        # De-duplicate by (desc.lower(), project)
        seen: dict[
            tuple[str, str | None],
            tuple[str, str, bool, dict[str, str], list[str]],
        ] = {}
        order: list[tuple[str, str | None]] = []
        for item in parsed:
            stripped, desc, done, tokens, other = item
            key = (desc.lower(), tokens.get("project"))
            if key not in seen:
                seen[key] = item
                order.append(key)
            else:
                # Prefer done > not done; then prefer one with project set; then more tokens
                prev = seen[key]
                prev_done = prev[2]
                prev_tokens = prev[3]
                prefer_new = False
                if done and not prev_done:
                    prefer_new = True
                elif done == prev_done:
                    if tokens.get("project") and not prev_tokens.get(
                        "project"
                    ):
                        prefer_new = True
                    elif len(tokens) > len(prev_tokens):
                        prefer_new = True
                if prefer_new:
                    seen[key] = item
                    changed = True

        # Rebuild normalized bullets in original relative order
        new_bullets: list[str] = []
        for key in order:
            _, item = key, seen[key]
            _stripped, desc, done, tokens, other_tokens = item
            # Build metadata with priority, due first, then stable rest
            pr = tokens.pop("priority", "M")
            due = tokens.pop("due", "unset")
            rebuilt_parts = [f"priority={pr}", f"due={due}"]
            for k, v in list(tokens.items()):
                rebuilt_parts.append(f"{k}={v}")
            rebuilt_parts.extend(other_tokens)
            rebuilt_meta = "; ".join(rebuilt_parts)
            new_line = f"- [{'x' if done else ' '}] {desc} :: {rebuilt_meta}".rstrip()
            new_bullets.append(new_line)

        # Merge non-bullet lines (already in out_lines) and bullets; keep original section order
        # Strategy: Replace any previous bullet lines with the new_bullets appended at the end of non-bullets
        # to avoid complex interleaving. This keeps normalization simple and idempotent.
        if new_bullets:
            if out_lines and out_lines[-1] != "":
                out_lines.append("")
            out_lines.extend(new_bullets)

        new_text = "\n".join(out_lines) + "\n"
        if new_text != tasks_path.read_text(encoding="utf-8"):
            tasks_path.write_text(new_text, encoding="utf-8")

    def _infer_intent(
        self, note: str | None, status_only: bool
    ) -> str | None:
        if status_only:
            return "review"
        if not note:
            return None
        lowered = note.lower()
        if any(
            k in lowered
            for k in ["status", "review", "projects", "health"]
        ):
            return "review"
        if any(
            k in lowered
            for k in [
                "show schedule",
                "show tasks",
                "what's my schedule",
                "what is my schedule",
                "my tasks today",
                "tasks today",
                "what are my tasks",
                "today's tasks",
            ]
        ):
            return "show"
        if (
            any(k in lowered for k in ["delete", "remove", "archive"])
            and "project" in lowered
        ):
            return "delete"
        if any(
            k in lowered
            for k in [
                "mark ",
                "done",
                "complete",
                "check off",
                "checked off",
            ]
        ):
            return "complete"
        if any(
            k in lowered
            for k in [
                "schedule",
                "plan",
                "focus",
                "allocate",
                "calendar",
                "plan my day",
            ]
        ):
            return "schedule"
        # If no keywords matched, do not take heavy actions by default.
        return None

    def _compose_coordinator_input(self, user_note: str) -> str:
        # Provide last few turns for coordinator context without heavy artifacts
        history_lines: list[str] = []
        for role, text in self._history[-8:]:
            prefix = "User" if role == "user" else "Assistant"
            history_lines.append(f"{prefix}: {text}")
        history_block = "\n".join(history_lines)
        now_str = self._now_string()
        return f"Now: {now_str}\nConversation so far:\n{history_block}\n\nNew message:\n{user_note}"

    async def _show_schedule_or_tasks(
        self, only_project: str | None = None
    ) -> str:
        """Return a lightweight view of today's plan without heavy workflows.

        - If a project is specified, show its Top Tasks from projects/<slug>/PROJECT.md.
        - Else, if schedule.md exists, show it.
        - Else, provide a quick glance at tasks.md (first few items) with project context if present.
        - Else, guide the user on how to proceed.
        """
        repo_root = Path(__file__).resolve().parent.parent
        # If project specified, show its Top Tasks
        if only_project:
            projs_dir = repo_root / "projects"
            matches: list[tuple[int, Path]] = []
            q = only_project.lower().strip()
            for p in projs_dir.iterdir():
                md = p / "PROJECT.md"
                if md.exists():
                    slug = p.name
                    hay = f"{slug} {slug.replace('-', ' ')} {slug.replace('_', ' ')}".lower()
                    score = sum(
                        1 for w in q.split() if w and w in hay
                    )
                    if score > 0 or q in hay:
                        matches.append(
                            (score + (5 if q in hay else 0), md)
                        )
            if not matches:
                return f"I couldn't find a project matching '{only_project}'."
            matches.sort(reverse=True)
            best_md = matches[0][1]
            lines = best_md.read_text(encoding="utf-8").splitlines()
            # Parse Top Tasks section
            in_top = False
            collected: list[str] = []
            for ln in lines:
                s = ln.strip()
                if s.lower().startswith("## top tasks"):
                    in_top = True
                    continue
                if in_top:
                    if s.startswith("## "):
                        break
                    if s.startswith(("- ", "* ")):
                        collected.append(s)
            if collected:
                return terminal.show_tasks(
                    [
                        {"description": task.strip("- *")}
                        for task in collected
                    ],
                    best_md.parent.name,
                )
            return terminal.warning(
                f"No Top Tasks found in {best_md.relative_to(repo_root)}."
            )
        sched_path = repo_root / "schedule.md"
        if sched_path.exists():
            schedule_text = sched_path.read_text(encoding="utf-8")
            return terminal.show_schedule(schedule_text)
        tasks_path = repo_root / "tasks.md"
        if tasks_path.exists():
            # Normalize before preview to ensure checklist + priority/due present
            try:
                self._normalize_tasks_file()
            except Exception:
                pass
            # Parse tasks via agent to include inferred project context
            from .op_agents import TaskList, task_loader_agent

            try:
                tasks_md = tasks_path.read_text(encoding="utf-8")
                tasks_result = await Runner.run(
                    task_loader_agent, tasks_md, **self._runner_kwargs
                )
                tasks = tasks_result.final_output_as(TaskList)
                lines: list[str] = []
                for t in tasks.tasks[:10]:
                    proj = (
                        f"[{t.project}] "
                        if getattr(t, "project", None)
                        else ""
                    )
                    meta: list[str] = []
                    if getattr(t, "priority", None) is not None:
                        meta.append(f"priority={t.priority}")
                    if getattr(t, "due", None):
                        meta.append(f"due={t.due}")
                    if getattr(t, "estimate", None):
                        meta.append(f"est={t.estimate}h")
                    meta_str = (
                        (" :: " + "; ".join(meta)) if meta else ""
                    )
                    lines.append(f"- {proj}{t.description}{meta_str}")
                if lines:
                    tasks_data = []
                    for line in lines:
                        # Parse the line to extract task info
                        if "[" in line and "]" in line:
                            # Extract project, description, and metadata
                            parts = line.split(" :: ")
                            desc_part = parts[0]
                            meta_part = (
                                parts[1] if len(parts) > 1 else ""
                            )

                            # Extract project from [project] format
                            project = None
                            if desc_part.startswith("- ["):
                                end_bracket = desc_part.find("]")
                                if end_bracket > 0:
                                    project = desc_part[3:end_bracket]
                                    desc_part = desc_part[
                                        end_bracket + 2 :
                                    ].strip()

                            # Parse metadata
                            priority = "M"
                            due = "unset"
                            if meta_part:
                                for meta in meta_part.split(";"):
                                    if "priority=" in meta:
                                        priority = meta.split("=")[
                                            1
                                        ].strip()
                                    elif "due=" in meta:
                                        due = meta.split("=")[
                                            1
                                        ].strip()

                            tasks_data.append(
                                {
                                    "description": desc_part,
                                    "project": project,
                                    "priority": priority,
                                    "due": due,
                                    "completed": False,
                                }
                            )

                    return (
                        terminal.show_tasks(tasks_data)
                        + "\n\n"
                        + terminal.info(
                            "Say 'plan my day' to draft a schedule."
                        )
                    )
            except Exception:
                # Fallback to raw bullets if agent parse fails
                raw = tasks_path.read_text(
                    encoding="utf-8"
                ).splitlines()
                bullets = [
                    line.strip()
                    for line in raw
                    if line.strip().startswith(("- ", "* "))
                ]
                preview = "\n".join(bullets[:10])
                if preview:
                    return (
                        terminal.info(
                            "No schedule yet. Here are some tasks I see:"
                        )
                        + "\n\n"
                        + terminal.formatter.code_block(preview)
                        + "\n\n"
                        + terminal.info(
                            "Say 'plan my day' to draft a schedule."
                        )
                    )
        return terminal.warning(
            "I don't see a schedule or tasks yet. You can create tasks in 'tasks.md' or say 'review projects' to import tasks, "
            "or 'plan my day' to draft a schedule."
        )

    def _complete_task(
        self, task_query: str, project_slug: str | None
    ) -> str:
        """Mark a task complete in tasks.md and update project PROJECT.md if provided.

        - task_query: fuzzy substring used to locate a single task line.
        - project_slug: optional project to update its PROJECT.md Top Tasks and Recent Activity.
        """
        repo_root = Path(__file__).resolve().parent.parent
        date_str = datetime.now().astimezone().strftime("%Y-%m-%d")

        # Update tasks.md
        tasks_path = repo_root / "tasks.md"
        tasks_updated = False
        matched_line = None
        if tasks_path.exists():
            lines = tasks_path.read_text(
                encoding="utf-8"
            ).splitlines()
            lowered_query = task_query.lower().strip()
            candidate_indexes = [
                i
                for i, ln in enumerate(lines)
                if ln.strip().startswith(("- ", "* "))
                and lowered_query in ln.lower()
            ]
            if len(candidate_indexes) == 1:
                idx = candidate_indexes[0]
                matched_line = lines[idx]
                text = matched_line.lstrip("-* ").strip()
                # Convert to checkbox style and mark done
                if "[x]" in matched_line.lower():
                    pass  # already completed
                elif "[ ]" in matched_line:
                    lines[idx] = (
                        matched_line.replace("[ ]", "[x]")
                        + f" (done {date_str})"
                    )
                    tasks_updated = True
                else:
                    # Turn "- Task" into "- [x] Task (done YYYY-MM-DD)"
                    prefix = (
                        "- "
                        if matched_line.strip().startswith("- ")
                        else "* "
                    )
                    content = matched_line.strip()[2:].strip()
                    lines[idx] = (
                        f"{prefix}[x] {content} (done {date_str})"
                    )
                    tasks_updated = True
                if tasks_updated:
                    tasks_path.write_text(
                        "\n".join(lines) + "\n", encoding="utf-8"
                    )
            elif len(candidate_indexes) > 1:
                sample = [
                    lines[i].strip() for i in candidate_indexes[:5]
                ]
                return (
                    terminal.warning(
                        "I found multiple matching tasks in tasks.md. Please be more specific or include the project."
                    )
                    + "\n"
                    + "\n".join(
                        f"  {terminal.formatter.bullet(s)}"
                        for s in sample
                    )
                )
            else:
                # Not found in tasks.md; continue with project update if given
                pass

        # Update project PROJECT.md if a slug was provided
        proj_msg = ""
        if project_slug:
            project_dir = repo_root / "projects" / project_slug
            project_md = project_dir / "PROJECT.md"
            if project_md.exists():
                text = project_md.read_text(encoding="utf-8")
                lines = text.splitlines()
                # Update front-matter updated: date if present (case-insensitive)
                for i in range(min(30, len(lines))):
                    if (
                        lines[i]
                        .strip()
                        .lower()
                        .startswith("updated:")
                    ):
                        lines[i] = f"updated: {date_str}"
                        break
                # Find Top Tasks section and mark [ ] to [x]
                in_top = False
                marked = False
                for i, ln in enumerate(lines):
                    if ln.strip().lower().startswith("## top tasks"):
                        in_top = True
                        continue
                    if in_top:
                        if ln.strip().startswith(
                            "## "
                        ) and not ln.strip().lower().startswith(
                            "## top tasks"
                        ):
                            in_top = False
                        elif (
                            ln.strip().startswith("- ")
                            and task_query.lower() in ln.lower()
                        ):
                            if "[x]" not in ln.lower():
                                lines[i] = (
                                    ln.replace("[ ]", "[x]")
                                    if "[ ]" in ln
                                    else ln.replace("- ", "- [x] ", 1)
                                )
                            marked = True
                            # Add to Recent Activity
                            # Find the Recent Activity header
                            for j, l2 in enumerate(lines):
                                if (
                                    l2.strip()
                                    .lower()
                                    .startswith("## recent activity")
                                ):
                                    insert_at = (
                                        j + 2
                                        if j + 1 < len(lines)
                                        and lines[j + 1].strip() == ""
                                        else j + 1
                                    )
                                    activity_line = f"- {date_str} — Completed: {task_query}"
                                    lines.insert(
                                        insert_at, activity_line
                                    )
                                    break
                            break
                if marked:
                    project_md.write_text(
                        "\n".join(lines) + "\n", encoding="utf-8"
                    )
                    proj_msg = f" Updated projects/{project_slug}/PROJECT.md."
                else:
                    proj_msg = f" Could not find a matching Top Task in projects/{project_slug}/PROJECT.md to mark complete."
            else:
                proj_msg = f" Project '{project_slug}' not found."

        if tasks_updated or proj_msg:
            base = (
                terminal.success("Marked complete in tasks.md.")
                if tasks_updated
                else ""
            )
            return (base + proj_msg).strip() or terminal.success(
                "Done."
            )
        return terminal.error(
            "I couldn't find that task in tasks.md. If it's in a project, try again with the project, e.g., 'mark <task> done in <project-slug>'."
        )

    def _handle_delete_request(
        self, user_query: str, confirmed: bool | None
    ) -> str:
        """Resolve a project by name/slug, ask for confirmation, and archive it if confirmed."""
        repo_root = Path(__file__).resolve().parent.parent
        projects_dir = repo_root / "projects"
        q = user_query.lower().replace("project", "").strip()
        matches: list[tuple[int, str, str]] = []
        for p in projects_dir.iterdir():
            if not p.is_dir():
                continue
            pm = p / "PROJECT.md"
            if not pm.exists():
                continue
            slug = p.name
            title = ""
            try:
                txt = pm.read_text(encoding="utf-8")
                for line in txt.splitlines():
                    s = line.strip()
                    if s.startswith("# "):
                        title = s[2:].strip()
                        break
            except Exception:
                pass
            hay = f"{slug} {slug.replace('_',' ')} {slug.replace('-',' ')} {title}".lower()
            score = sum(1 for w in q.split() if w and w in hay)
            if score > 0:
                matches.append((score, slug, title))
        if not matches:
            return terminal.error(
                "I couldn't find a matching project. Try referencing the exact slug under projects/<slug>."
            )
        matches.sort(reverse=True)
        top_score = matches[0][0]
        tied = [m for m in matches if m[0] == top_score]
        if len(tied) > 1:
            options = "\n".join(
                f"  {terminal.formatter.bullet(f'{s} — {t}')}"
                for _, s, t in tied[:5]
            )
            return (
                terminal.warning(
                    "I found multiple projects. Please specify one by slug:\n"
                )
                + options
            )
        _, slug, title = matches[0]
        if not confirmed:
            self._pending_delete_slug = slug
            title_str = f" ({title})" if title else ""
            return terminal.warning(
                f"About to archive projects/{slug}{title_str}. Reply 'yes' to confirm or 'no' to cancel."
            )
        return self._delete_project(slug)

    def _delete_project(self, slug: str) -> str:
        repo_root = Path(__file__).resolve().parent.parent
        project_dir = repo_root / "projects" / slug
        if not project_dir.exists():
            return terminal.error(f"Project '{slug}' not found.")
        archive_dir = repo_root / "archive"
        archive_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = archive_dir / f"{slug}_{ts}"
        try:
            project_dir.rename(dest)
            return terminal.success(
                f"Archived projects/{slug} → {dest.relative_to(repo_root)}"
            )
        except Exception as e:
            return terminal.error(
                f"Failed to archive projects/{slug}: {e}"
            )

    def _now_string(self) -> str:
        """Return a concise local datetime string with timezone and UTC offset."""
        now = datetime.now().astimezone()
        date = now.strftime("%Y-%m-%d")
        dow = now.strftime("%a")
        t = now.strftime("%H:%M")
        tzname = now.tzname() or "Local"
        offset = now.utcoffset() or None
        if offset is None:
            offset_str = "UTC±00:00"
        else:
            total = int(offset.total_seconds())
            sign = "+" if total >= 0 else "-"
            total = abs(total)
            hh = total // 3600
            mm = (total % 3600) // 60
            offset_str = f"UTC{sign}{hh:02d}:{mm:02d}"
        return f"{date} ({dow}) {t} {tzname} ({offset_str})"
