# CLI Audit Summary

This file captures the key findings requested: how each CLI compresses context, which prompt is used (if any), and whether it uses a single agent or agents-as-tools.

## Snapshot (quick compare)

- Aider
  - Context compression: LLM summarization when chat history exceeds token budget.
  - Prompt: `aider/aider/prompts.py` (`summarize`, `summary_prefix`).
  - Agents/tools: Single interactive assistant; no agents-as-tools.
- Codex CLI (openai/codex)
  - Context compression: Auto-compact when total tokens exceed model auto-compact limit.
  - Prompt: `codex/codex-rs/core/templates/compact/prompt.md` with prefix `codex/codex-rs/core/templates/compact/summary_prefix.md`.
  - Agents/tools: Single assistant with tools; no agents-as-tools.
- Gemini CLI (google-gemini/gemini-cli)
  - Context compression: Auto-compress when history exceeds threshold fraction of model token limit.
  - Prompt: `gemini-cli/packages/core/src/core/prompts.ts` (`getCompressionPrompt`).
  - Agents/tools: Single assistant with hooks/commands; no agents-as-tools.
- Claude Code (anthropics/claude-code)
  - Context compression: Prompt not found in repo; changelog references /context and /resume.
  - Prompt: not located in repo search.
  - Agents/tools: Supports multiple agents in plugins (code review plugin uses parallel agents).
- Forge (antinomyhq/forge)
  - Context compression: Deterministic summary transformer pipeline (non-LLM).
  - Prompt: Template-driven summary frame `forge/templates/forge-partial-summary-frame.md`.
  - Agents/tools: Agents can be exposed as tools (`Agent::tool_definition`).

## Details by repo

### Aider

Compression trigger and flow:
- Chat history is summarized when `ChatSummary.too_big()` detects total tokens > `max_tokens` (`aider/aider/history.py`).
- `base_coder` spins up a background summarizer thread when `done_messages` exceeds the limit (`aider/aider/coders/base_coder.py`).

Prompt used:
- System prompt string in `aider/aider/prompts.py` (`summarize`).
- Summary is prefixed with `summary_prefix` and inserted as a user message (`aider/aider/history.py`).

Agents/tools:
- Interactive single assistant; Aider explicitly avoids agentic behavior (see `aider/aider/website/_posts/2024-06-02-main-swe-bench.md`).
- No agents-as-tools in core flow.

Key files:
- `archive/cli-audit-repos/aider/aider/history.py`
- `archive/cli-audit-repos/aider/aider/prompts.py`
- `archive/cli-audit-repos/aider/aider/coders/base_coder.py`

### Codex CLI

Compression trigger and flow:
- Auto-compaction runs when total usage tokens exceed the model auto-compact limit (`codex/codex-rs/core/src/codex.rs`).
- Compaction runs a dedicated summarization task and then replaces history with summary + recent items (`codex/codex-rs/core/src/compact.rs`).
- Uses local compaction or remote compaction for OpenAI providers (`codex/codex-rs/core/src/compact_remote.rs`).

Prompt used:
- Compaction prompt is `codex/codex-rs/core/templates/compact/prompt.md`.
- Summary prefix is `codex/codex-rs/core/templates/compact/summary_prefix.md`.

Agents/tools:
- Single assistant that can call tools; skills are injected into the prompt.
- No explicit agents-as-tools pattern.

Key files:
- `archive/cli-audit-repos/codex/codex-rs/core/src/codex.rs`
- `archive/cli-audit-repos/codex/codex-rs/core/src/compact.rs`
- `archive/cli-audit-repos/codex/codex-rs/core/src/compact_remote.rs`
- `archive/cli-audit-repos/codex/codex-rs/core/templates/compact/prompt.md`
- `archive/cli-audit-repos/codex/codex-rs/core/templates/compact/summary_prefix.md`

### Gemini CLI

Compression trigger and flow:
- Compression runs when history token count exceeds a threshold (default 0.5 of model limit) (`gemini-cli/packages/core/src/services/chatCompressionService.ts`).
- Preserves last 30% of history and summarizes earlier messages into a `<state_snapshot>` block.

Prompt used:
- `getCompressionPrompt()` returns a structured XML summary prompt in `gemini-cli/packages/core/src/core/prompts.ts`.
- Tool output summarization uses `packages/core/src/utils/summarizer.ts` and is called from shell tool when enabled (`packages/core/src/tools/shell.ts`).

Agents/tools:
- Single assistant with hooks and commands; no agents-as-tools found in code search.

Key files:
- `archive/cli-audit-repos/gemini-cli/packages/core/src/services/chatCompressionService.ts`
- `archive/cli-audit-repos/gemini-cli/packages/core/src/core/prompts.ts`
- `archive/cli-audit-repos/gemini-cli/packages/core/src/utils/summarizer.ts`

### Claude Code

Compression trigger and prompt:
- No explicit compaction prompt found in this repo search.
- Changelog references `/context` and `/resume` (see `claude-code/CHANGELOG.md`), suggesting internal or closed-source compaction behavior.

Agents/tools:
- Multi-agent capabilities exist via plugins (for example, PR/code review uses parallel agents).
- See plugin docs and agent definitions:
  - `archive/cli-audit-repos/claude-code/plugins/README.md`
  - `archive/cli-audit-repos/claude-code/plugins/pr-review-toolkit/agents/`
  - `archive/cli-audit-repos/claude-code/plugins/code-review/`

### Forge

Compression trigger and flow:
- Compaction is deterministic: build a `ContextSummary`, run transformer pipeline, render a summary frame, replace a sequence in the context (`forge/crates/forge_app/src/compact.rs`).
- Compaction thresholds are configured by token/turn/message counts or end-of-turn in `forge_domain/src/compact/compact_config.rs` and `forge_domain/src/compact/strategy.rs`.
- `TrimContextSummary` deduplicates tool calls to reduce context size (`forge/crates/forge_app/src/transformers/trim_context_summary.rs`).

Prompt used:
- Summary frame template: `forge/templates/forge-partial-summary-frame.md`.
- This is a deterministic template, not an LLM prompt.

Agents/tools:
- Agents can be exposed as tools via `Agent::tool_definition` (`forge/crates/forge_domain/src/agent.rs`), enabling agents-as-tools.

Key files:
- `archive/cli-audit-repos/forge/crates/forge_app/src/compact.rs`
- `archive/cli-audit-repos/forge/crates/forge_app/src/transformers/trim_context_summary.rs`
- `archive/cli-audit-repos/forge/crates/forge_domain/src/compact/compact_config.rs`
- `archive/cli-audit-repos/forge/crates/forge_domain/src/compact/strategy.rs`
- `archive/cli-audit-repos/forge/templates/forge-partial-summary-frame.md`
