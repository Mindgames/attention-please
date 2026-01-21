# CLI Audit Reference for Grais.ai

## Purpose

Consolidated findings from CLI audits (Codex, Gemini CLI, Claude Code, Forge, Aider) to serve as a foundation when updating the Grais.ai system. This focuses on architecture, tool execution, safety, context management, extensibility, and UX signaling.

## Cross-cutting patterns we observed

- **Runtime status signals are separate from model output.** Progress and "starting..." messages are emitted by event streams or tool/UI channels, not by model-generated text (`archive/cli-audit-repos/codex/docs/exec.md`, `archive/cli-audit-repos/codex/sdk/typescript/src/events.ts`, `archive/cli-audit-repos/gemini-cli/packages/a2a-server/src/commands/init.ts`, `archive/cli-audit-repos/forge/crates/forge_domain/src/tools/call/context.rs`, `archive/cli-audit-repos/aider/aider/repomap.py`, `archive/cli-audit-repos/STATUS_UPDATES.md`).
- **Structured output is used for final responses, not progress.** Codex supports JSON schema output for the final message, while progress is event-based (`archive/cli-audit-repos/codex/docs/exec.md`, `archive/cli-audit-repos/STATUS_UPDATES.md`).
- **Tool systems are schema-driven and gated.** CLIs expose tool schemas to models and gate sensitive operations with user approvals or policies (`archive/cli-audit-repos/gemini-cli/docs/tools/index.md`, `archive/cli-audit-repos/gemini-cli/docs/architecture.md`).
- **Context compression is first-class.** Each system compresses/summarizes history using either an LLM prompt or deterministic pipeline; implementation differs by tool (see repo notes below).
- **Extensibility is core.** Plugins, skills, hooks, and custom prompts are first-class mechanisms across CLIs (`archive/cli-audit-repos/claude-code/plugins/README.md`, `archive/cli-audit-repos/gemini-cli/docs/hooks/index.md`, `archive/cli-audit-repos/codex/docs/prompts.md`).
- **Safety/sandboxing is explicit.** Codex and Gemini document sandbox behavior and approvals; Codex adds an execpolicy rules engine for command allow/prompt/deny (`archive/cli-audit-repos/codex/docs/sandbox.md`, `archive/cli-audit-repos/codex/docs/execpolicy.md`, `archive/cli-audit-repos/gemini-cli/docs/tools/index.md`).
- **Session persistence is explicit.** Gemini CLI stores conversation history, tool executions, and token stats with resume support (`archive/cli-audit-repos/gemini-cli/docs/cli/session-management.md`).

## Repo-specific findings

### Codex CLI (openai/codex)

- **Instruction layering via AGENTS.md.** Combines global and project instructions in a deterministic priority order with override support (`archive/cli-audit-repos/codex/docs/agents_md.md`).
- **Sandbox + approvals model.** Read-only by default; trusted workspaces enable workspace-write. Full-access bypass is explicit (`archive/cli-audit-repos/codex/docs/sandbox.md`).
- **Execution policy rules.** Declarative `.rules` allow/deny/prompt policies for command prefixes (`archive/cli-audit-repos/codex/docs/execpolicy.md`).
- **Custom prompts.** Markdown-based prompts with placeholders in `$CODEX_HOME/prompts` (`archive/cli-audit-repos/codex/docs/prompts.md`).
- **Context compaction.** Auto-compaction when token usage exceeds a threshold; uses compaction prompt templates (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).
- **JSONL event stream.** `--json` output includes `item.started/updated/completed` and tool/command status (`archive/cli-audit-repos/codex/docs/exec.md`).

### Gemini CLI (google-gemini/gemini-cli)

- **Two-tier architecture.** CLI front end + core backend; core manages prompt/tool orchestration (`archive/cli-audit-repos/gemini-cli/docs/architecture.md`).
- **Tool catalog + confirmations.** Tools include file, shell, web, memory, todo; sensitive tools require approval and sandboxing (`archive/cli-audit-repos/gemini-cli/docs/tools/index.md`).
- **Hooks across lifecycle.** Synchronous hook system with Before/After Tool, Model, Agent, compression, and notification events (`archive/cli-audit-repos/gemini-cli/docs/hooks/index.md`).
- **Memory tool.** Persistent facts saved into `~/.gemini/GEMINI.md` (`archive/cli-audit-repos/gemini-cli/docs/tools/memory.md`).
- **Session persistence.** Auto-saved sessions with resume, listing, deletion, and retention controls (`archive/cli-audit-repos/gemini-cli/docs/cli/session-management.md`).
- **System prompt override.** `GEMINI_SYSTEM_MD` fully replaces core prompt; default can be exported (`archive/cli-audit-repos/gemini-cli/docs/cli/system-prompt.md`).
- **Context compression.** Compresses history beyond threshold and preserves recent context (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).
- **Status updates.** Event bus emits `status-update` with `state` lifecycle values (`archive/cli-audit-repos/gemini-cli/packages/a2a-server/src/commands/init.ts`, `archive/cli-audit-repos/STATUS_UPDATES.md`).

### Claude Code (anthropics/claude-code)

- **Plugin system.** Plugins can define commands, agents, skills, hooks, and MCP servers; standardized plugin layout (`archive/cli-audit-repos/claude-code/plugins/README.md`).
- **Multi-agent workflows.** Example plugins use parallel specialized agents for code review and PR analysis (`archive/cli-audit-repos/claude-code/plugins/README.md`).
- **Context compression not surfaced.** No compaction prompt found in repo; changelog references `/context` and `/resume` (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).

### Forge (antinomyhq/forge)

- **Tool-call format.** Enforces a single JSON tool call wrapped in `<forge_tool_call>` tags per message (`archive/cli-audit-repos/forge/templates/forge-partial-tool-use-example.md`).
- **Tool descriptions matter.** Detailed tool descriptions with <1024 char limit; tools must be registered in the registry (`archive/cli-audit-repos/forge/docs/tool-guidelines.md`).
- **Tool UI context.** Tool calls can emit titles/messages via `ToolCallContext` (separate from model output) (`archive/cli-audit-repos/forge/crates/forge_domain/src/tools/call/context.rs`).
- **Agents as tools.** Agents can be exposed as tools (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).
- **Context compaction.** Deterministic transformer pipeline and summary frame template, not LLM-based (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).

### Aider

- **Repo map.** Builds a map of the codebase to improve context in larger repos (`archive/cli-audit-repos/aider/README.md`).
- **Progress updates in long tasks.** Repo map updates emit progress messages via CLI callbacks (`archive/cli-audit-repos/aider/aider/repomap.py`, `archive/cli-audit-repos/STATUS_UPDATES.md`).
- **Context compression.** Summarizes history once token limits are exceeded; summary inserted as a user message (`archive/cli-audit-repos/AUDIT_SUMMARY.md`).
- **Core workflow features.** Git integration, lint/test integration, and support for multiple LLM providers (`archive/cli-audit-repos/aider/README.md`).

## Design implications for Grais.ai

- **Emit structured status events.** Separate progress/status signaling from final model responses (JSONL or internal event bus).
- **Keep tool UI separate from model output.** Provide a tool context channel for progress messages and titles.
- **Adopt explicit safety gates.** Combine sandboxing + approval policy + command allow/deny rules for sensitive actions.
- **Make prompts and instructions modular.** Support layered instructions (global + project) and customizable prompts.
- **Provide hooks/plugins for extensibility.** Lifecycle hooks allow validation and policy enforcement without core changes.
- **Plan for context compression.** Support both LLM summarization and deterministic compaction paths.
- **Persist sessions and memory.** Store full conversation history, tool usage, and optional user memory for continuity.

## Key references (starting points)

- Codex: `archive/cli-audit-repos/codex/docs/exec.md`, `archive/cli-audit-repos/codex/docs/sandbox.md`, `archive/cli-audit-repos/codex/docs/agents_md.md`
- Gemini CLI: `archive/cli-audit-repos/gemini-cli/docs/architecture.md`, `archive/cli-audit-repos/gemini-cli/docs/tools/index.md`, `archive/cli-audit-repos/gemini-cli/docs/hooks/index.md`
- Claude Code: `archive/cli-audit-repos/claude-code/plugins/README.md`
- Forge: `archive/cli-audit-repos/forge/docs/tool-guidelines.md`, `archive/cli-audit-repos/forge/templates/forge-partial-tool-use-example.md`
- Aider: `archive/cli-audit-repos/aider/README.md`, `archive/cli-audit-repos/aider/aider/repomap.py`
