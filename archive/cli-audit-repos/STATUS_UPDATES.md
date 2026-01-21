# Task Start and Status Updates in CLI Agents

## Summary

- Most CLIs surface "starting/working" signals via runtime event streams or tool-context UI channels, not via model-authored text.
- Structured output (JSON schema) is typically used for the final response, not for progress updates.

## Evidence by repo

### Codex CLI (openai/codex)

- `codex exec --json` streams JSONL events like `item.started` with `command_execution` or `mcp_tool_call` items that carry `status: "in_progress"` before completion and before the final `agent_message`.
- Event types are defined in `archive/cli-audit-repos/codex/sdk/typescript/src/events.ts`.
- Item statuses are defined in `archive/cli-audit-repos/codex/sdk/typescript/src/items.ts`.
- Example JSONL stream with `item.started`/`item.completed` is documented in `archive/cli-audit-repos/codex/docs/exec.md`.

### Gemini CLI (google-gemini/gemini-cli)

- The A2A server publishes `kind: "status-update"` events with `status.state` and a message payload, allowing UI to show progress before final content (`archive/cli-audit-repos/gemini-cli/packages/a2a-server/src/commands/init.ts`).
- Task persistence includes `status.state: "working"` during execution (`archive/cli-audit-repos/gemini-cli/packages/a2a-server/src/persistence/gcs.test.ts`), indicating a lifecycle separate from final output.

### Forge (antinomyhq/forge)

- Tools can emit UI updates directly via `ToolCallContext.send_text` and `ToolCallContext.send_title`, enabling "starting ..." messages during tool execution (not model output): `archive/cli-audit-repos/forge/crates/forge_domain/src/tools/call/context.rs`.
- Tool call context is treated as UI-only and kept separate from business logic in tooling plans (see `archive/cli-audit-repos/forge/plans/2025-06-07-tool-service-migration-v1.md`).

### Aider

- Long-running operations emit progress updates from the CLI itself via a `progress` callback (e.g., repo-map updates show "Updating repo map: ...") in `archive/cli-audit-repos/aider/aider/repomap.py`.

## Answer to "structured output?"

- Some CLIs support structured output for the final response (for example, Codex `--output-schema`), but the "starting task" indicators are typically separate, structured *events* or UI messages emitted by the runtime or tool layer.
- These are not the same as model-level structured output; they are system- or tool-generated status/progress signals.
