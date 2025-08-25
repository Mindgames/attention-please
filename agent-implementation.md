# Agent Implementation Tasks

## Environment Setup
- Install the OpenAI Agents SDK and add it to `PYTHONPATH`.
- Configure `OPENAI_API_KEY` via `.env` or shell environment.

## Package Scaffolding
- Add a top-level `operator/` package (outside `projects/`).
- Include `__init__.py`, `main.py`, and an `agents/` subpackage placeholder.
- Store shared artifacts (`tasks.md`, `schedule_tmp.md`, `schedule.md`) alongside the package at the repository root.

## File Tools
- Implement `operator/tools.py` exposing `ReadFileTool` and `WriteFileTool` wrappers.
- Restrict tool paths to the repository root to prevent accidental writes elsewhere.

## ProjectReviewAgent
- Implement `operator/agents/project_review_agent.py` to scan each project directory for `PROJECT.md`.
- Use `ReadFileTool` to extract open tasks and evaluate project status.
- Append prioritized items to the top-level `tasks.md` via `WriteFileTool`.
- Return a `ProjectReport` model with tasks to migrate and notes on project health.

## TaskLoaderAgent
- Implement `operator/agents/task_loader_agent.py` with a Pydantic model representing tasks (name, category, priority, estimate).
- Use `ReadFileTool` to load tasks from `tasks.md` and return structured data.

## TimeAllocatorAgent
- Add `operator/agents/time_allocator_agent.py` to accept the task list and generate a daily schedule.
- Provide a `ScheduleDraft` model and use `WriteFileTool` to output `schedule_tmp.md`.

## EvaluatorAgent
- Implement `operator/agents/evaluator_agent.py` to review the draft schedule for time conflicts and balance.
- Return `{approved: bool, reason: str}` to indicate evaluation result.

## FocusManager Orchestrator
- Create `operator/manager.py` to coordinate agents and run a refinement loop until evaluation passes or the attempt limit is reached.
- Invoke `ProjectReviewAgent` first to refresh `tasks.md` and gather project evaluations.
- Run `TaskLoaderAgent` → `TimeAllocatorAgent` → `EvaluatorAgent` on the updated task list.
- On success, persist the final schedule to `schedule.md`.
- Refinement loop example:
  ```python
  for attempt in range(MAX_ATTEMPTS):
      tasks = await Runner.run(task_loader_agent)
      draft = await Runner.run(time_allocator_agent, tasks.final_output)
      review = await Runner.run(evaluator_agent, draft.final_output)
      if review.final_output.approved:
          break
      tasks_ctx = f"{tasks.final_output}\nFeedback: {review.final_output.reason}"
  ```

## Agent Prompts and Context Flow
- **ProjectReviewAgent prompt**: "Scan each project folder for `PROJECT.md`, summarize open tasks and status, output JSON ready for `tasks.md`."
- **TaskLoaderAgent prompt**: "Read `tasks.md` and return a JSON array of tasks with priority and time estimates."
- **TimeAllocatorAgent prompt**: "Given tasks and a time budget, draft a balanced daily schedule and write to `schedule_tmp.md`."
- **EvaluatorAgent prompt**: "Review the proposed schedule for conflicts, balance, and alignment with goals; respond with `{approved: bool, reason: str}`."
- **Context handoff**: FocusManager feeds each agent only the previous agent's structured output. Evaluation feedback is appended to the next `TimeAllocatorAgent` prompt during refinement loops, while large artifacts are passed via shared files (`tasks.md`, `schedule_tmp.md`).

## CLI & Interactive Chat
- Build `operator/main.py` to launch an interactive terminal chat with `FocusManager` using the Agents SDK.
- Chat loop: prompt the user, send messages to `FocusManager.chat()`, stream replies, and allow commands like `schedule` or `exit`.
- Document usage in `README.md` and update repository-level docs as features evolve.
  ```python
  async def main():
      manager = FocusManager()
      while True:
          user = input("you: ")
          if user.strip() == "exit":
              break
          reply = await manager.chat(user)
          print("agent:", reply)
  ```
- Expose CLI via `python -m operator.main`.

## Future Enhancements
- Add tests under `operator/tests/` for agent interactions and chat flows.
- Consider calendar integration, recurring task support, and persistent conversation history.
