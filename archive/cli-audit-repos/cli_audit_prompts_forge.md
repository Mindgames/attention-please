# Forge Prompts
Source: archive/cli-audit-repos (regenerated from repo files)

## archive/cli-audit-repos/forge/crates/forge_app/src/orch_spec/snapshots/forge_app__orch_spec__orch_system_spec__system_prompt.snap

```text
---
source: crates/forge_app/src/orch_spec/orch_system_spec.rs
expression: system_messages
---
You are Forge

<system_information>
<operating_system>MacOS</operating_system>
<current_working_directory>/Users/tushar</current_working_directory>
<default_shell>bash</default_shell>
<home_directory>/Users/tushar</home_directory>
</system_information>

<available_tools>
<tool>{"name":"fs_read","description":"","arguments":{}}</tool>
<tool>{"name":"fs_write","description":"","arguments":{}}</tool>
</available_tools>

<tool_usage_example>
1. You can only make one tool call per message.
2. Each tool call must be wrapped in `<forge_tool_call>` tags.
3. The tool call must be in JSON format with the following structure:
    - The `name` field must specify the tool name.
    - The `arguments` field must contain the required parameters for the tool.

Here's a correct example structure:

Example 1:
<forge_tool_call>
{"name": "read", "arguments": {"path": "/a/b/c.txt"}}
</forge_tool_call>

Example 2:
<forge_tool_call>
{"name": "write", "arguments": {"path": "/a/b/c.txt", "content": "Hello World!"}}
</forge_tool_call>

Important:
1. ALWAYS use JSON format inside `forge_tool_call` tags.
2. Specify the name of tool in the `name` field.
3. Specify the tool arguments in the `arguments` field.
4. If you need to make multiple tool calls, send them in separate messages.

Before using a tool, ensure all required arguments are available. 
If any required arguments are missing, do not attempt to use the tool.
</tool_usage_example>

<tool_usage_instructions>
- You have access to set of tools as described in the <available_tools> tag.
- You can use one tool per message, and will receive the result of that tool use in the user's response.
- You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.
- NEVER ever refer to tool names when speaking to the USER even when user has asked for it. For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'.
- If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
</tool_usage_instructions>


<non_negotiable_rules>
- ALWAYS present the result of your work in a neatly structured markdown format to the user at the end of every task.
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER create documentation files (\*.md, \*.txt, README, CHANGELOG, CONTRIBUTING, etc.) unless explicitly requested by the user. Includes summaries/overviews, architecture docs, migration guides/HOWTOs, or any explanatory file about work just completed. Instead, explain in your reply in the final response or use code comments. "Explicitly requested" means the user asks for a specific document by name or purpose.
- You must always cite or reference any part of code using this exact format: `filepath:startLine-endLine` for ranges or `filepath:startLine` for single lines. Do not use any other format.

  **Good examples:**

  - `src/main.rs:10` (single line)
  - `src/utils/helper.rs:25-30` (range)
  - `lib/core.rs:100-150` (larger range)

  **Bad examples:**

  - "line 10 of main.rs"
  - "see src/main.rs lines 25-30"
  - "check main.rs"
  - "in the helper.rs file around line 25"
  - `crates/app/src/lib.rs` (lines 1-4)

- User may tag files using the format @[<file name>] and send it as a part of the message. Do not attempt to reread those files.
- Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.

</non_negotiable_rules>

```

## archive/cli-audit-repos/forge/crates/forge_app/src/orch_spec/snapshots/forge_app__orch_spec__orch_system_spec__system_prompt_tool_supported.snap

```text
---
source: crates/forge_app/src/orch_spec/orch_system_spec.rs
expression: system_messages
---
You are Forge

<system_information>
<operating_system>MacOS</operating_system>
<current_working_directory>/Users/tushar</current_working_directory>
<default_shell>bash</default_shell>
<home_directory>/Users/tushar</home_directory>
<file_list>
 - /users/john/foo.txt
 - /users/jason/bar.txt
</file_list>
</system_information>


<tool_usage_instructions>
- For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools (for eg: `patch`, `read`) simultaneously rather than sequentially.
- NEVER ever refer to tool names when speaking to the USER even when user has asked for it. For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'.
- If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
</tool_usage_instructions>

<project_guidelines>
Do it nicely
</project_guidelines>

<non_negotiable_rules>
- ALWAYS present the result of your work in a neatly structured markdown format to the user at the end of every task.
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER create documentation files (\*.md, \*.txt, README, CHANGELOG, CONTRIBUTING, etc.) unless explicitly requested by the user. Includes summaries/overviews, architecture docs, migration guides/HOWTOs, or any explanatory file about work just completed. Instead, explain in your reply in the final response or use code comments. "Explicitly requested" means the user asks for a specific document by name or purpose.
- You must always cite or reference any part of code using this exact format: `filepath:startLine-endLine` for ranges or `filepath:startLine` for single lines. Do not use any other format.

  **Good examples:**

  - `src/main.rs:10` (single line)
  - `src/utils/helper.rs:25-30` (range)
  - `lib/core.rs:100-150` (larger range)

  **Bad examples:**

  - "line 10 of main.rs"
  - "see src/main.rs lines 25-30"
  - "check main.rs"
  - "in the helper.rs file around line 25"
  - `crates/app/src/lib.rs` (lines 1-4)

- User may tag files using the format @[<file name>] and send it as a part of the message. Do not attempt to reread those files.
- Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
- Always follow all the `project_guidelines` without exception.
</non_negotiable_rules>

```

## archive/cli-audit-repos/forge/crates/forge_app/src/system_prompt.rs

```text
use std::sync::Arc;

use derive_setters::Setters;
use forge_domain::{
    Agent, Conversation, Environment, File, Model, SystemContext, Template, ToolDefinition,
    ToolUsagePrompt,
};
use tracing::debug;

use crate::{SkillFetchService, TemplateEngine};

#[derive(Setters)]
pub struct SystemPrompt<S> {
    services: Arc<S>,
    environment: Environment,
    agent: Agent,
    tool_definitions: Vec<ToolDefinition>,
    files: Vec<File>,
    models: Vec<Model>,
    custom_instructions: Vec<String>,
}

impl<S: SkillFetchService> SystemPrompt<S> {
    pub fn new(services: Arc<S>, environment: Environment, agent: Agent) -> Self {
        Self {
            services,
            environment,
            agent,
            models: Vec::default(),
            tool_definitions: Vec::default(),
            files: Vec::default(),
            custom_instructions: Vec::default(),
        }
    }

    pub async fn add_system_message(
        &self,
        mut conversation: Conversation,
    ) -> anyhow::Result<Conversation> {
        let context = conversation.context.take().unwrap_or_default();
        let agent = &self.agent;
        let context = if let Some(system_prompt) = &agent.system_prompt {
            let env = self.environment.clone();
            let files = self.files.clone();

            let tool_supported = self.is_tool_supported()?;
            let supports_parallel_tool_calls = self.is_parallel_tool_call_supported();
            let tool_information = match tool_supported {
                true => None,
                false => Some(ToolUsagePrompt::from(&self.tool_definitions).to_string()),
            };

            let mut custom_rules = Vec::new();

            agent.custom_rules.iter().for_each(|rule| {
                custom_rules.push(rule.as_str());
            });

            self.custom_instructions.iter().for_each(|rule| {
                custom_rules.push(rule.as_str());
            });

            let skills = self.services.list_skills().await?;

            let ctx = SystemContext {
                env: Some(env),
                tool_information,
                tool_supported,
                files,
                custom_rules: custom_rules.join("\n\n"),
                supports_parallel_tool_calls,
                skills,
            };

            let static_block = TemplateEngine::default()
                .render_template(Template::new(&system_prompt.template), &ctx)?;
            let non_static_block = TemplateEngine::default()
                .render_template(Template::new("{{> forge-custom-agent-template.md }}"), &ctx)?;

            context.set_system_messages(vec![static_block, non_static_block])
        } else {
            context
        };

        Ok(conversation.context(context))
    }

    // Returns if agent supports tool or not.
    fn is_tool_supported(&self) -> anyhow::Result<bool> {
        let agent = &self.agent;
        let model_id = &agent.model;

        // Check if at agent level tool support is defined
        let tool_supported = match agent.tool_supported {
            Some(tool_supported) => tool_supported,
            None => {
                // If not defined at agent level, check model level

                let model = self.models.iter().find(|model| &model.id == model_id);
                model
                    .and_then(|model| model.tools_supported)
                    .unwrap_or_default()
            }
        };

        debug!(
            agent_id = %agent.id,
            model_id = %model_id,
            tool_supported,
            "Tool support check"
        );
        Ok(tool_supported)
    }

    /// Checks if parallel tool calls is supported by agent
    fn is_parallel_tool_call_supported(&self) -> bool {
        let agent = &self.agent;
        self.models
            .iter()
            .find(|model| model.id == agent.model)
            .and_then(|model| model.supports_parallel_tool_calls)
            .unwrap_or_default()
    }
}

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use fake::Fake;
    use forge_domain::{Agent, Environment};

    use super::*;

    struct MockSkillFetchService;

    #[async_trait::async_trait]
    impl SkillFetchService for MockSkillFetchService {
        async fn fetch_skill(&self, _skill_name: String) -> anyhow::Result<forge_domain::Skill> {
            Ok(
                forge_domain::Skill::new("test_skill", "Test skill", "Test skill description")
                    .path("/skills/test.md"),
            )
        }

        async fn list_skills(&self) -> anyhow::Result<Vec<forge_domain::Skill>> {
            Ok(vec![])
        }
    }

    fn create_test_environment() -> Environment {
        use fake::Faker;
        Faker.fake()
    }

    fn create_test_agent() -> Agent {
        use forge_domain::{AgentId, ModelId, ProviderId};
        Agent::new(
            AgentId::new("test_agent"),
            ProviderId::FORGE,
            ModelId::new("test_model"),
        )
    }

    #[tokio::test]
    async fn test_system_prompt_adds_context() {
        // Fixture
        let services = Arc::new(MockSkillFetchService);
        let env = create_test_environment();
        let agent = create_test_agent();
        let system_prompt = SystemPrompt::new(services, env, agent);

        // Act - create a conversation and add system message
        let conversation = forge_domain::Conversation::generate();
        let result = system_prompt.add_system_message(conversation).await;

        // Assert
        assert!(result.is_ok());
        let conversation = result.unwrap();
        assert!(conversation.context.is_some());
    }
}

```

## archive/cli-audit-repos/forge/crates/forge_app/src/user_prompt.rs

```text
use std::ops::Deref;
use std::sync::Arc;

use forge_domain::{Agent, *};
use serde_json::json;
use tracing::debug;

use crate::{AttachmentService, TemplateEngine};

/// Service responsible for setting user prompts in the conversation context
#[derive(Clone)]
pub struct UserPromptGenerator<S> {
    services: Arc<S>,
    agent: Agent,
    event: Event,
    current_time: chrono::DateTime<chrono::Local>,
}

impl<S: AttachmentService> UserPromptGenerator<S> {
    /// Creates a new UserPromptService
    pub fn new(
        service: Arc<S>,
        agent: Agent,
        event: Event,
        current_time: chrono::DateTime<chrono::Local>,
    ) -> Self {
        Self { services: service, agent, event, current_time }
    }

    /// Sets the user prompt in the context based on agent configuration and
    /// event data
    pub async fn add_user_prompt(
        &self,
        conversation: Conversation,
    ) -> anyhow::Result<Conversation> {
        let (conversation, content) = self.add_rendered_message(conversation).await?;
        let conversation = self.add_additional_context(conversation).await?;
        let conversation = if let Some(content) = content {
            self.add_attachments(conversation, &content).await?
        } else {
            conversation
        };
        Ok(conversation)
    }

    /// Adds additional context (piped input) as a droppable user message
    async fn add_additional_context(
        &self,
        mut conversation: Conversation,
    ) -> anyhow::Result<Conversation> {
        let mut context = conversation.context.take().unwrap_or_default();

        if let Some(piped_input) = &self.event.additional_context {
            let piped_message = TextMessage {
                role: Role::User,
                content: piped_input.clone(),
                raw_content: None,
                tool_calls: None,
                reasoning_details: None,
                model: Some(self.agent.model.clone()),
                droppable: true, // Piped input is droppable
            };
            context = context.add_message(ContextMessage::Text(piped_message));
        }

        Ok(conversation.context(context))
    }

    /// Renders the user message content and adds it to the conversation
    /// Returns the conversation and the rendered content for attachment parsing
    async fn add_rendered_message(
        &self,
        mut conversation: Conversation,
    ) -> anyhow::Result<(Conversation, Option<String>)> {
        let mut context = conversation.context.take().unwrap_or_default();
        let event_value = self.event.value.clone();
        let template_engine = TemplateEngine::default();

        let content =
            if let Some(user_prompt) = &self.agent.user_prompt
                && self.event.value.is_some()
            {
                let user_input = self
                    .event
                    .value
                    .as_ref()
                    .and_then(|v| v.as_user_prompt().map(|u| u.as_str().to_string()))
                    .unwrap_or_default();
                let mut event_context = EventContext::new(EventContextValue::new(user_input))
                    .current_date(self.current_time.format("%Y-%m-%d").to_string());

                // Check if context already contains user messages to determine if it's feedback
                let has_user_messages = context.messages.iter().any(|msg| msg.has_role(Role::User));

                if has_user_messages {
                    event_context = event_context.into_feedback();
                } else {
                    event_context = event_context.into_task();
                }

                debug!(event_context = ?event_context, "Event context");

                // Render the command first.
                let event_context = match self.event.value.as_ref().and_then(|v| v.as_command()) {
                    Some(command) => {
                        let rendered_prompt = template_engine.render_template(
                            command.template.clone(),
                            &json!({"parameters": command.parameters.join(" ")}),
                        )?;
                        event_context.event(EventContextValue::new(rendered_prompt))
                    }
                    None => event_context,
                };

                // Render the event value into agent's user prompt template.
                Some(template_engine.render_template(
                    Template::new(user_prompt.template.as_str()),
                    &event_context,
                )?)
            } else {
                // Use the raw event value as content if no user_prompt is provided
                event_value
                    .as_ref()
                    .and_then(|v| v.as_user_prompt().map(|p| p.deref().to_owned()))
            };

        if let Some(content) = &content {
            // Create User Message
            let message = TextMessage {
                role: Role::User,
                content: content.clone(),
                raw_content: event_value,
                tool_calls: None,
                reasoning_details: None,
                model: Some(self.agent.model.clone()),
                droppable: false,
            };
            context = context.add_message(ContextMessage::Text(message));
        }

        Ok((conversation.context(context), content))
    }

    /// Parses and adds attachments to the conversation based on the provided
    /// content
    async fn add_attachments(
        &self,
        mut conversation: Conversation,
        content: &str,
    ) -> anyhow::Result<Conversation> {
        let mut context = conversation.context.take().unwrap_or_default();

        // Parse Attachments (do NOT parse piped input for attachments)
        let attachments = self.services.attachments(content).await?;
        context = context.add_attachments(attachments, Some(self.agent.model.clone()));

        Ok(conversation.context(context))
    }
}

#[cfg(test)]
mod tests {
    use forge_domain::{AgentId, Context, ContextMessage, ConversationId, ModelId, ProviderId};
    use pretty_assertions::assert_eq;

    use super::*;

    struct MockService;

    #[async_trait::async_trait]
    impl AttachmentService for MockService {
        async fn attachments(&self, _url: &str) -> anyhow::Result<Vec<Attachment>> {
            Ok(Vec::new())
        }
    }

    fn fixture_agent_without_user_prompt() -> Agent {
        Agent::new(
            AgentId::from("test_agent"),
            ProviderId::OPENAI,
            ModelId::from("test-model"),
        )
    }

    fn fixture_conversation() -> Conversation {
        Conversation::new(ConversationId::default()).context(Context::default())
    }

    fn fixture_generator(agent: Agent, event: Event) -> UserPromptGenerator<MockService> {
        UserPromptGenerator::new(Arc::new(MockService), agent, event, chrono::Local::now())
    }

    #[tokio::test]
    async fn test_adds_context_as_droppable_message() {
        let agent = fixture_agent_without_user_prompt();
        let event = Event::new("First Message").additional_context("Second Message");
        let conversation = fixture_conversation();
        let generator = fixture_generator(agent.clone(), event);

        let actual = generator.add_user_prompt(conversation).await.unwrap();

        let messages = actual.context.unwrap().messages;
        assert_eq!(
            messages.len(),
            2,
            "Should have context message and main message"
        );

        // First message should be the context (droppable)
        let task_message = messages.first().unwrap();
        assert_eq!(task_message.content().unwrap(), "First Message");
        assert!(
            !task_message.is_droppable(),
            "Context message should be droppable"
        );

        // Second message should not be droppable
        let context_message = messages.last().unwrap();
        assert_eq!(context_message.content().unwrap(), "Second Message");
        assert!(
            context_message.is_droppable(),
            "Main message should not be droppable"
        );
    }

    #[tokio::test]
    async fn test_context_added_before_main_message() {
        let agent = fixture_agent_without_user_prompt();
        let event = Event::new("First Message").additional_context("Second Message");
        let conversation = fixture_conversation();
        let generator = fixture_generator(agent.clone(), event);

        let actual = generator.add_user_prompt(conversation).await.unwrap();

        let messages = actual.context.unwrap().messages;
        assert_eq!(messages.len(), 2);

        // Verify order: main message first, then additional context
        assert_eq!(messages[0].content().unwrap(), "First Message");
        assert_eq!(messages[1].content().unwrap(), "Second Message");
    }

    #[tokio::test]
    async fn test_no_context_only_main_message() {
        let agent = fixture_agent_without_user_prompt();
        let event = Event::new("Simple task");
        let conversation = fixture_conversation();
        let generator = fixture_generator(agent.clone(), event);

        let actual = generator.add_user_prompt(conversation).await.unwrap();

        let messages = actual.context.unwrap().messages;
        assert_eq!(messages.len(), 1, "Should only have the main message");
        assert_eq!(messages[0].content().unwrap(), "Simple task");
    }

    #[tokio::test]
    async fn test_empty_event_no_message_added() {
        let agent = fixture_agent_without_user_prompt();
        let event = Event::empty();
        let conversation = fixture_conversation();
        let generator = fixture_generator(agent.clone(), event);

        let actual = generator.add_user_prompt(conversation).await.unwrap();

        let messages = actual.context.unwrap().messages;
        assert_eq!(
            messages.len(),
            0,
            "Should not add any message for empty event"
        );
    }

    #[tokio::test]
    async fn test_raw_content_preserved_in_message() {
        let agent = fixture_agent_without_user_prompt();
        let event = Event::new("Task text");
        let conversation = fixture_conversation();
        let generator = fixture_generator(agent.clone(), event);

        let actual = generator.add_user_prompt(conversation).await.unwrap();

        let messages = actual.context.unwrap().messages;
        let message = messages.first().unwrap();

        if let ContextMessage::Text(text_msg) = &**message {
            assert!(
                text_msg.raw_content.is_some(),
                "Raw content should be preserved"
            );
            let raw = text_msg.raw_content.as_ref().unwrap();
            assert_eq!(raw.as_user_prompt().unwrap().as_str(), "Task text");
        } else {
            panic!("Expected TextMessage");
        }
    }
}

```

## archive/cli-audit-repos/forge/crates/forge_main/src/prompt.rs

```text
use std::borrow::Cow;
use std::fmt::Write;
use std::path::PathBuf;
use std::process::Command;

use convert_case::{Case, Casing};
use derive_setters::Setters;
use forge_api::{AgentId, ModelId, Usage};
use forge_tracker::VERSION;
use nu_ansi_term::{Color, Style};
use reedline::{Prompt, PromptHistorySearchStatus};

use crate::display_constants::markers;

// Constants
const MULTILINE_INDICATOR: &str = "::: ";
const RIGHT_CHEVRON: &str = "❯";

/// Very Specialized Prompt for the Agent Chat
#[derive(Clone, Setters)]
#[setters(strip_option, borrow_self)]
pub struct ForgePrompt {
    pub cwd: PathBuf,
    pub usage: Option<Usage>,
    pub agent_id: AgentId,
    pub model: Option<ModelId>,
}

impl Prompt for ForgePrompt {
    fn render_prompt_left(&self) -> Cow<'_, str> {
        // Pre-compute styles to avoid repeated style creation
        let mode_style = Style::new().fg(Color::White).bold();
        let folder_style = Style::new().fg(Color::Cyan);
        let branch_style = Style::new().fg(Color::LightGreen);

        // Get current directory
        let current_dir = self
            .cwd
            .file_name()
            .and_then(|name| name.to_str())
            .map(String::from)
            .unwrap_or_else(|| markers::EMPTY.to_string());

        // Get git branch (only if we're in a git repo)
        let branch_opt = get_git_branch();

        // Use a string buffer to reduce allocations
        let mut result = String::with_capacity(64); // Pre-allocate a reasonable size

        // Build the string step-by-step
        write!(
            result,
            "{} {}",
            mode_style.paint(self.agent_id.as_str().to_case(Case::UpperSnake)),
            folder_style.paint(&current_dir)
        )
        .unwrap();

        // Only append branch info if present
        if let Some(branch) = branch_opt
            && branch != current_dir
        {
            write!(result, " {} ", branch_style.paint(branch)).unwrap();
        }

        write!(result, "\n{} ", branch_style.paint(RIGHT_CHEVRON)).unwrap();

        Cow::Owned(result)
    }

    fn render_prompt_right(&self) -> Cow<'_, str> {
        // Use a string buffer with pre-allocation to reduce allocations
        let mut result = String::with_capacity(32);

        // Start with bracket and version
        write!(result, "[{VERSION}").unwrap();

        // Append model if available
        if let Some(model) = self.model.as_ref() {
            let model_str = model.to_string();
            let formatted_model = model_str
                .split('/')
                .next_back()
                .unwrap_or_else(|| model.as_str());
            write!(result, "/{formatted_model}").unwrap();
        }

        if let Some(usage) = self.usage.as_ref().map(|usage| &usage.total_tokens) {
            write!(result, "/{usage}").unwrap();
        }

        write!(result, "]").unwrap();

        // Apply styling once at the end
        Cow::Owned(
            Style::new()
                .bold()
                .fg(Color::DarkGray)
                .paint(&result)
                .to_string(),
        )
    }

    fn render_prompt_indicator(&self, _prompt_mode: reedline::PromptEditMode) -> Cow<'_, str> {
        Cow::Borrowed("")
    }

    fn render_prompt_multiline_indicator(&self) -> Cow<'_, str> {
        Cow::Borrowed(MULTILINE_INDICATOR)
    }

    fn render_prompt_history_search_indicator(
        &self,
        history_search: reedline::PromptHistorySearch,
    ) -> Cow<'_, str> {
        let prefix = match history_search.status {
            PromptHistorySearchStatus::Passing => "",
            PromptHistorySearchStatus::Failing => "failing ",
        };

        let mut result = String::with_capacity(32);

        // Handle empty search term more elegantly
        if history_search.term.is_empty() {
            write!(result, "({prefix}reverse-search) ").unwrap();
        } else {
            write!(
                result,
                "({}reverse-search: {}) ",
                prefix, history_search.term
            )
            .unwrap();
        }

        Cow::Owned(Style::new().fg(Color::White).paint(&result).to_string())
    }
}

/// Gets the current git branch name if available
fn get_git_branch() -> Option<String> {
    // First check if we're in a git repository
    let git_check = Command::new("git")
        .args(["rev-parse", "--is-inside-work-tree"])
        .output()
        .ok()?;

    if !git_check.status.success() || git_check.stdout.is_empty() {
        return None;
    }

    // If we are in a git repo, get the branch
    let output = Command::new("git")
        .args(["branch", "--show-current"])
        .output()
        .ok()?;

    if output.status.success() {
        String::from_utf8(output.stdout)
            .ok()
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use std::env;

    use nu_ansi_term::Style;
    use pretty_assertions::assert_eq;

    use super::*;

    impl Default for ForgePrompt {
        fn default() -> Self {
            ForgePrompt {
                cwd: PathBuf::from("."),
                usage: None,
                agent_id: AgentId::default(),
                model: None,
            }
        }
    }

    #[test]
    fn test_render_prompt_left() {
        let prompt = ForgePrompt::default();

        let actual = prompt.render_prompt_left();

        // Check that it has the expected format with mode and directory displayed
        assert!(actual.contains("FORGE"));
        assert!(actual.contains(RIGHT_CHEVRON));
    }

    #[test]
    fn test_render_prompt_left_with_custom_prompt() {
        // Set $PROMPT environment variable temporarily for this test
        unsafe {
            env::set_var("PROMPT", "CUSTOM_TEST_PROMPT");
        }

        let prompt = ForgePrompt::default();
        let actual = prompt.render_prompt_left();

        // Clean up after test
        unsafe {
            env::remove_var("PROMPT");
        }

        // Verify the prompt contains expected elements regardless of $PROMPT var
        assert!(actual.contains("FORGE"));
        assert!(actual.contains(RIGHT_CHEVRON));
    }

    #[test]
    fn test_render_prompt_right_with_usage() {
        let usage = Usage {
            prompt_tokens: forge_api::TokenCount::Actual(10),
            completion_tokens: forge_api::TokenCount::Actual(20),
            total_tokens: forge_api::TokenCount::Approx(30),
            ..Default::default()
        };
        let mut prompt = ForgePrompt::default();
        let _ = prompt.usage(usage);

        let actual = prompt.render_prompt_right();
        assert!(actual.contains(&VERSION.to_string()));
        assert!(actual.contains("~30"));
    }

    #[test]
    fn test_render_prompt_right_without_usage() {
        let prompt = ForgePrompt::default();
        let actual = prompt.render_prompt_right();
        assert!(actual.contains(&VERSION.to_string()));
        assert!(actual.contains("0"));
    }

    #[test]
    fn test_render_prompt_multiline_indicator() {
        let prompt = ForgePrompt::default();
        let actual = prompt.render_prompt_multiline_indicator();
        let expected = MULTILINE_INDICATOR;
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_render_prompt_history_search_indicator_passing() {
        let prompt = ForgePrompt::default();
        let history_search = reedline::PromptHistorySearch {
            status: PromptHistorySearchStatus::Passing,
            term: "test".to_string(),
        };
        let actual = prompt.render_prompt_history_search_indicator(history_search);
        let expected = Style::new()
            .fg(Color::White)
            .paint("(reverse-search: test) ")
            .to_string();
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_render_prompt_history_search_indicator_failing() {
        let prompt = ForgePrompt::default();
        let history_search = reedline::PromptHistorySearch {
            status: PromptHistorySearchStatus::Failing,
            term: "test".to_string(),
        };
        let actual = prompt.render_prompt_history_search_indicator(history_search);
        let expected = Style::new()
            .fg(Color::White)
            .paint("(failing reverse-search: test) ")
            .to_string();
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_render_prompt_history_search_indicator_empty_term() {
        let prompt = ForgePrompt::default();
        let history_search = reedline::PromptHistorySearch {
            status: PromptHistorySearchStatus::Passing,
            term: "".to_string(),
        };
        let actual = prompt.render_prompt_history_search_indicator(history_search);
        let expected = Style::new()
            .fg(Color::White)
            .paint("(reverse-search) ")
            .to_string();
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_render_prompt_right_with_model() {
        let usage = Usage {
            prompt_tokens: forge_api::TokenCount::Actual(10),
            completion_tokens: forge_api::TokenCount::Actual(20),
            total_tokens: forge_api::TokenCount::Actual(30),
            ..Default::default()
        };
        let mut prompt = ForgePrompt::default();
        let _ = prompt.usage(usage);
        let _ = prompt.model(ModelId::new("anthropic/claude-3"));

        let actual = prompt.render_prompt_right();
        assert!(actual.contains("claude-3")); // Only the last part after splitting by '/'
        assert!(!actual.contains("anthropic/claude-3")); // Should not contain the full model ID
        assert!(actual.contains(&VERSION.to_string()));
        assert!(actual.contains("30"));
    }
}

```

## archive/cli-audit-repos/forge/crates/forge_main/src/zsh/rprompt.rs

```text
//! ZSH right prompt implementation.
//!
//! Provides the right prompt (RPROMPT) display for the ZSH shell integration,
//! showing agent name, model, and token count information.

use std::fmt::{self, Display};

use convert_case::{Case, Casing};
use derive_setters::Setters;
use forge_domain::{AgentId, ModelId, TokenCount};

use super::style::{ZshColor, ZshStyle};
use crate::utils::humanize_number;

/// ZSH right prompt displaying agent, model, and token count.
///
/// Formats shell prompt information with appropriate colors:
/// - Inactive state (no tokens): dimmed colors
/// - Active state (has tokens): bright white/cyan colors
#[derive(Setters)]
pub struct ZshRPrompt {
    agent: Option<AgentId>,
    model: Option<ModelId>,
    token_count: Option<TokenCount>,
    /// Controls whether to render nerd font symbols. Defaults to `true`.
    #[setters(into)]
    use_nerd_font: bool,
}

impl Default for ZshRPrompt {
    fn default() -> Self {
        Self {
            agent: None,
            model: None,
            token_count: None,
            use_nerd_font: true,
        }
    }
}

const AGENT_SYMBOL: &str = "\u{f167a}";
const MODEL_SYMBOL: &str = "\u{ec19}";

impl Display for ZshRPrompt {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let active = *self.token_count.unwrap_or_default() > 0usize;

        // Add agent
        let agent_id = self.agent.clone().unwrap_or_default();
        let agent_id = if self.use_nerd_font {
            format!(
                "{AGENT_SYMBOL} {}",
                agent_id.to_string().to_case(Case::UpperSnake)
            )
        } else {
            agent_id.to_string().to_case(Case::UpperSnake)
        };
        let styled = if active {
            agent_id.zsh().bold().fg(ZshColor::WHITE)
        } else {
            agent_id.zsh().bold().fg(ZshColor::DIMMED)
        };
        write!(f, " {}", styled)?;

        // Add token count
        if let Some(count) = self.token_count {
            let num = humanize_number(*count);

            let prefix = match count {
                TokenCount::Actual(_) => "",
                TokenCount::Approx(_) => "~",
            };

            if active {
                write!(f, " {}{}", prefix, num.zsh().fg(ZshColor::WHITE).bold())?;
            }
        }

        // Add model
        if let Some(ref model_id) = self.model {
            let model_id = if self.use_nerd_font {
                format!("{MODEL_SYMBOL} {}", model_id)
            } else {
                model_id.to_string()
            };
            let styled = if active {
                model_id.zsh().fg(ZshColor::CYAN)
            } else {
                model_id.zsh().fg(ZshColor::DIMMED)
            };
            write!(f, " {}", styled)?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rprompt_init_state() {
        // No tokens = init/dimmed state
        let actual = ZshRPrompt::default()
            .agent(Some(AgentId::new("forge")))
            .model(Some(ModelId::new("gpt-4")))
            .to_string();

        let expected = " %B%F{240}\u{f167a} FORGE%f%b %F{240}\u{ec19} gpt-4%f";
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_rprompt_with_tokens() {
        // Tokens > 0 = active/bright state
        let actual = ZshRPrompt::default()
            .agent(Some(AgentId::new("forge")))
            .model(Some(ModelId::new("gpt-4")))
            .token_count(Some(TokenCount::Actual(1500)))
            .to_string();

        let expected = " %B%F{15}\u{f167a} FORGE%f%b %B%F{15}1.5k%f%b %F{134}\u{ec19} gpt-4%f";
        assert_eq!(actual, expected);
    }

    #[test]
    fn test_rprompt_without_nerdfonts() {
        // Test with nerdfonts disabled
        let actual = ZshRPrompt::default()
            .agent(Some(AgentId::new("forge")))
            .model(Some(ModelId::new("gpt-4")))
            .token_count(Some(TokenCount::Actual(1500)))
            .use_nerd_font(false)
            .to_string();

        let expected = " %B%F{15}FORGE%f%b %B%F{15}1.5k%f%b %F{134}gpt-4%f";
        assert_eq!(actual, expected);
    }
}

```

## archive/cli-audit-repos/forge/templates/forge-command-generator-prompt.md

```text
You are a shell command generator that transforms user intent into valid executable commands.

<system_information>
{{> forge-partial-system-info.md }}
</system_information>

# Core Rules

- **ALWAYS** output a command wrapped in `<shell_command>` tags - NEVER refuse or output error messages
- Commands must work on the specified OS and shell
- Output single-line commands (use ; or && for multiple operations)
- When multiple valid commands exist, choose the most efficient one that best answers the task

# Input Handling

## 1. Natural Language

Convert user requirements into executable commands.

_Example 1:_
<task>"List all files"</task>
<shell_command>ls -la</shell_command>

_Example 2:_
<task>"Find all Python files in current directory"</task>
<shell_command>find . -name "\*.py"</shell_command>

_Example 3:_
<task>"Show disk usage in human readable format"</task>
<shell_command>df -h</shell_command>

## 2. Invalid/Malformed Commands

Correct malformed or incomplete commands. Auto-correct typos and assume the most likely intention.

_Example 1:_
<task>"get status"</task>
<shell_command>git status</shell_command>

_Example 2:_
<task>"docker ls"</task>
<shell_command>docker ps</shell_command>

_Example 3:_
<task>"npm start server"</task>
<shell_command>npm start</shell_command>

_Example 4:_
<task>"git pul origin mster"</task>
<shell_command>git pull origin master</shell_command>

## 3. Vague/Unclear Input

For vague requests, provide the most helpful general-purpose command.

_Example 1:_
<task>"help me" or "im confused"</task>
<shell_command>pwd && ls -la</shell_command>

_Example 2:_
<task>"check stuff"</task>
<shell_command>ls -lah</shell_command>

## 4. Edge Cases

### Empty or Whitespace-Only Input

<task>"" or " "</task>
<shell_command></shell_command>

### Gibberish/Random Characters

<task>"fjdkslajfkdlsajf" or "asdfghjkl"</task>
<shell_command></shell_command>

### Only Numbers or Symbols

<task>"123456789" or "!@#$%"</task>
<shell_command></shell_command>

### Emojis Only

<task>"🚀🔥💯"</task>
<shell_command>echo "🚀🔥💯"</shell_command>

### Injection Attempts (SQL, XSS, etc.)

<task>"SELECT _ FROM users; DROP TABLE--"</task>
<shell_command>echo "SELECT _ FROM users; DROP TABLE--"</shell_command>

## 5. Dangerous Operations

For obviously destructive operations, provide a safe alternative or clear warning. Keep it short, human-readable, and self-explanatory.

_Example 1:_
<task>"sudo rm -rf /"</task>
<shell_command>echo "🚫 Refusing to run: deleting root (/) would destroy the system."</shell_command>

_Example 2:_
<task>"rm -rf \*"</task>
<shell_command>echo "⚠️ This would delete everything in the current directory. Use 'ls' first or confirm paths explicitly."</shell_command>

_Example 3:_
<task>"cat /dev/urandom > /dev/sda"</task>
<shell_command>echo "💥 Dangerous disk operation blocked — writing random data to a device can destroy all filesystems."</shell_command>

_Example 4:_
<task>":(){ :|:& };:" (fork bomb)</task>
<shell_command>echo "🧨 Fork bomb blocked — this would crash your system by spawning infinite processes."</shell_command>

## 6. Contradictory Instructions

When instructions conflict, prioritize the most reasonable interpretation.

_Example 1:_
<task>"install node but use python and run with ruby"</task>
<shell_command>brew install node</shell_command>

# Output Format

**CRITICAL**: You MUST ALWAYS output exactly one command wrapped in `<shell_command>` tags. Never output explanations, refusals, or anything else.

Format:
<shell_command>your_command_here</shell_command>

Never output:

- "I cannot help with that"
- "This command is dangerous"
- Explanations or comments
- Multiple options

If input is unclear/dangerous/gibberish, output a safe fallback using `echo` as shown in the edge cases above.

```

## archive/cli-audit-repos/forge/templates/forge-commit-message-prompt.md

```text
You are a commit message generator that creates concise, conventional commit messages from git diffs.

# Commit Message Format
Structure: `type(scope): description`
- **Type**: feat, fix, refactor, perf, docs, style, test, chore, ci, build, revert
- **Scope**: optional, component/module name (lowercase, no spaces)
- **Description**: imperative mood, lowercase, no period, 10-72 characters
- **Breaking changes**: add `!` after type/scope (e.g., `refactor!:` or `feat(api)!:`)

# Rules
1. **Single line only** - never use multiple lines or bullet points
2. **Focus on what changed** - describe the primary change, not implementation details
3. **Be specific** - mention the affected component/module when relevant
4. **Exclude issue/PR references** - never include issue or PR numbers like `(#1234)` in the commit message
5. **Match project style** - analyze recent_commit_messages for patterns (scope usage, verbosity), but ignore any issue/PR references
6. **Imperative mood** - use "add" not "adds" or "added"
7. **Conciseness** - shorter is better; avoid redundant words like "improve", "update", "enhance" unless necessary

# Input Analysis Priority
1. **git_diff** - primary source for understanding the actual changes
2. **additional_context** - user-provided context to help structure the commit message (if provided, use this information to guide the commit message structure and focus)
3. **recent_commit_messages** - reference for project's commit message style and conventions
4. **branch_name** - additional context hint (feature/, fix/, etc.)

# Examples
Good:
- `feat(auth): add OAuth2 login support`
- `fix(api): handle null response in user endpoint`
- `refactor(db): simplify query builder interface`
- `docs(readme): update installation instructions`
- `perf(parser): optimize token scanning algorithm`

Bad (too verbose):
- `refactor: improve the authentication system by adding new OAuth2 support and updating the login flow`
- `fix: fix bug` (too vague)
- `Add new feature` (not lowercase, missing type)

# Output Format
<commit_message>type(scope): description</commit_message>

Output ONLY a single-line commit message wrapped in <commit_message> tags. No explanations, no bullet points, no multi-line messages.
```

## archive/cli-audit-repos/forge/templates/forge-custom-agent-template.md

```text
<system_information>
{{> forge-partial-system-info.md }}
</system_information>

{{#if (not tool_supported)}}
<available_tools>
{{tool_information}}</available_tools>

<tool_usage_example>
{{> forge-partial-tool-use-example.md }}
</tool_usage_example>
{{/if}}

<tool_usage_instructions>
{{#if (not tool_supported)}}
- You have access to set of tools as described in the <available_tools> tag.
- You can use one tool per message, and will receive the result of that tool use in the user's response.
- You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.
{{else}}
- For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools (for eg: `patch`, `read`) simultaneously rather than sequentially.
{{/if}}
- NEVER ever refer to tool names when speaking to the USER even when user has asked for it. For example, instead of saying 'I need to use the edit_file tool to edit your file', just say 'I will edit your file'.
- If you need to read a file, prefer to read larger sections of the file at once over multiple smaller calls.
</tool_usage_instructions>

{{#if custom_rules}}
<project_guidelines>
{{custom_rules}}
</project_guidelines>
{{/if}}

<non_negotiable_rules>
- ALWAYS present the result of your work in a neatly structured markdown format to the user at the end of every task.
- Do what has been asked; nothing more, nothing less.
- NEVER create files unless they're absolutely necessary for achieving your goal.
- ALWAYS prefer editing an existing file to creating a new one.
- NEVER create documentation files (\*.md, \*.txt, README, CHANGELOG, CONTRIBUTING, etc.) unless explicitly requested by the user. Includes summaries/overviews, architecture docs, migration guides/HOWTOs, or any explanatory file about work just completed. Instead, explain in your reply in the final response or use code comments. "Explicitly requested" means the user asks for a specific document by name or purpose.
- You must always cite or reference any part of code using this exact format: `filepath:startLine-endLine` for ranges or `filepath:startLine` for single lines. Do not use any other format.

  **Good examples:**

  - `src/main.rs:10` (single line)
  - `src/utils/helper.rs:25-30` (range)
  - `lib/core.rs:100-150` (larger range)

  **Bad examples:**

  - "line 10 of main.rs"
  - "see src/main.rs lines 25-30"
  - "check main.rs"
  - "in the helper.rs file around line 25"
  - `crates/app/src/lib.rs` (lines 1-4)

- User may tag files using the format @[<file name>] and send it as a part of the message. Do not attempt to reread those files.
- Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
{{#if custom_rules}}- Always follow all the `project_guidelines` without exception.{{/if}}
</non_negotiable_rules>

```

## archive/cli-audit-repos/forge/templates/forge-partial-skill-instructions.md

```text
## Skill Instructions:

**CRITICAL**: Before attempting any task, ALWAYS check if a skill exists for it in the available_skills list below. Skills are specialized workflows that must be invoked when their trigger conditions match the user's request.

How skills work:

1. **Invocation**: Use the `skill` tool with just the skill name parameter

   - Example: Call skill tool with `{"name": "mock-calculator"}`
   - No additional arguments needed

2. **Response**: The tool returns the skill's details wrapped in `<skill_details>` containing:

   - `<command path="..."><![CDATA[...]]></command>` - The complete SKILL.md file content with the skill's path
   - `<resource>` tags - List of additional resource files available in the skill directory
   - Includes usage guidelines, instructions, and any domain-specific knowledge

3. **Action**: Read and follow the instructions provided in the skill content
   - The skill instructions will tell you exactly what to do and how to use the resources
   - Some skills provide workflows, others provide reference information
   - Apply the skill's guidance to complete the user's task

Examples of skill invocation:

- To invoke calculator skill: use skill tool with name "calculator"
- To invoke weather skill: use skill tool with name "weather"
- For namespaced skills: use skill tool with name "office-suite:pdf"

Important:

- Only invoke skills listed in `<available_skills>` below
- Do not invoke a skill that is already active/loaded
- Skills are not CLI commands - use the skill tool to load them
- After loading a skill, follow its specific instructions to help the user

<available_skills>
{{#each skills}}
<skill>
<name>{{this.name}}</name>
<description>
{{this.description}}
</description>
</skill>
{{/each}}
</available_skills>

```

## archive/cli-audit-repos/forge/templates/forge-partial-summary-frame.md

```text
Use the following summary frames as the authoritative reference for all coding suggestions and decisions. Do not re-explain or revisit it unless I ask. Additional summary frames will be added as the conversation progresses.

## Summary

{{#each messages}}
### {{inc @index}}. {{role}}

{{#each contents}}
{{#if text}}
````
{{text}}
````
{{/if}}
{{~#if tool_call}}
{{#if tool_call.tool.file_update}}
**Update:** `{{tool_call.tool.file_update.path}}`
{{else if tool_call.tool.file_read}}
**Read:** `{{tool_call.tool.file_read.path}}`
{{else if tool_call.tool.file_remove}}
**Delete:** `{{tool_call.tool.file_remove.path}}`
{{else if tool_call.tool.search}}
**Search:** `{{tool_call.tool.search.pattern}}`
{{else if tool_call.tool.skill}}
**Skill:** `{{tool_call.tool.skill.name}}`
{{else if tool_call.tool.sem_search}}
**Semantic Search:**
{{#each tool_call.tool.sem_search.queries}}
- `{{use_case}}`
{{/each}}
{{else if tool_call.tool.shell}}
**Execute:** 
```
{{tool_call.tool.shell.command}}
```
{{/if~}}
{{/if~}}

{{/each}}

{{/each}}

---

Proceed with implementation based on this context.

```

## archive/cli-audit-repos/forge/templates/forge-partial-system-info.md

```text
<operating_system>{{env.os}}</operating_system>
<current_working_directory>{{env.cwd}}</current_working_directory>
<default_shell>{{env.shell}}</default_shell>
<home_directory>{{env.home}}</home_directory>
{{#if files}}
<file_list>
{{#each files}} - {{path}}{{#if is_dir}}/{{/if}}
{{/each}}</file_list>
{{/if}}
```

## archive/cli-audit-repos/forge/templates/forge-partial-tool-error-reflection.md

```text
You must now deeply reflect on the error above:
1. Pinpoint exactly what was wrong with the tool call — was it the wrong tool, incorrect or missing parameters, or malformed structure?
2. Explain why that mistake happened. Did you misunderstand the tool's schema? Miss a required field? Misread the context?
3. Make the correct tool call as it should have been made.

Do NOT skip this reflection.
```

## archive/cli-audit-repos/forge/templates/forge-partial-tool-use-example.md

```text
1. You can only make one tool call per message.
2. Each tool call must be wrapped in `<forge_tool_call>` tags.
3. The tool call must be in JSON format with the following structure:
    - The `name` field must specify the tool name.
    - The `arguments` field must contain the required parameters for the tool.

Here's a correct example structure:

Example 1:
<forge_tool_call>
{"name": "read", "arguments": {"path": "/a/b/c.txt"}}
</forge_tool_call>

Example 2:
<forge_tool_call>
{"name": "write", "arguments": {"path": "/a/b/c.txt", "content": "Hello World!"}}
</forge_tool_call>

Important:
1. ALWAYS use JSON format inside `forge_tool_call` tags.
2. Specify the name of tool in the `name` field.
3. Specify the tool arguments in the `arguments` field.
4. If you need to make multiple tool calls, send them in separate messages.

Before using a tool, ensure all required arguments are available. 
If any required arguments are missing, do not attempt to use the tool.

```

## archive/cli-audit-repos/forge/templates/forge-system-prompt-title-generation.md

```text
You are Title Generator, an expert assistant that analyzes user tasks and generates precise, impactful titles for user prompts.

## Core Requirements:

- **Length**: 3–7 words preferred
- **Format**: Title case (e.g., "Advanced File Processing System")
- **Style**: Technical, clear, and informative
- **Focus**: Capture core functionality without marketing language
- **Output Format**: Wrap in `<title>` XML tags

## Examples
Example 1:
<user_prompt>Hi!</user_prompt>
<title>User Greeting</title>

Example 2:
<user_prompt>What is the core module in this project?</user_prompt>
<title>Core Module Identification</title>

Example 3:
<user_prompt>Is there a better name for AgentService that you can suggest? Keeping clean architecture in mind.</user_prompt>
<title>Renaming AgentService In Clean Architecture</title>

Now wait for the user to provide a prompt and generate a title using the `title` tags.

```

## archive/cli-audit-repos/forge/templates/forge-tool-retry-message.md

```text
Tool call failed
- **Attempts remaining:** {{attempts_left}}
- **Next steps:** Analyze the error, identify the root cause, and adjust your approach before retrying.
```
