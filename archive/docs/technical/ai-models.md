# AI Models for the Agentic System

This document lists the latest and recommended AI models available for use in the agentic system. It should be updated as new models are released or adopted.

---

## Policy: Model Names and API Calls

> **Do not arbitrarily change model names or API call names.**
>
> - All model names and API endpoints must remain consistent with official documentation and codebase references.
> - Any change to a model name or API call must be documented, justified, and reviewed. Random or ad-hoc changes can break compatibility, reproducibility, and system integrity.
> - When upgrading or switching models, update this file and reference the change in `system-upgrade-ideas.log`.

---

## OpenAI GPT-4.1 Model Family (2025)

- **GPT-4.1** (`gpt-4.1`)
  - The latest OpenAI model as of 2025.
  - High performance, advanced reasoning, and strong context handling.
  - 1 million token context window (approx. 750,000 words).
  - Multimodal (text, image, video input; text output).
  - Optimized for coding, instruction following, and agentic workflows.
  - Used for all core agentic routines, including SYSTEM-REVIEW.
  - Available via OpenAI API (not ChatGPT UI).
  - **Variants:**
    - **GPT-4.1 mini**: More efficient, faster, lower cost, slightly less accurate.
    - **GPT-4.1 nano**: Fastest and cheapest, for high-throughput/low-latency use cases.
  - **Pricing (2025):**
    - GPT-4.1: $2/million input tokens, $8/million output tokens
    - GPT-4.1 mini: $0.40/$1.60
    - GPT-4.1 nano: $0.10/$0.40
  - **Key Features:**
    - Enhanced coding and instruction following
    - 1M token context window
    - Tool calling, structured outputs
    - Fine-tuning support (for GPT-4.1 and mini)
    - Outperforms previous OpenAI models on coding and reasoning benchmarks
    - Limitations: Reliability drops with very large input sizes; more literal than GPT-4o

---

## Google Gemini 2.5 Model Family (2025)

- **Gemini 2.5 Pro (Experimental/Preview)**
  - Best for coding, complex prompts, advanced reasoning
  - 1 million token context window (2 million coming soon)
  - Native multimodality: text, image, video, audio input; text output
  - State-of-the-art on math, science, reasoning, and agentic coding benchmarks
  - Tool use: function calling, code execution, structured output, search
  - Available via Google AI Studio, Gemini App (Advanced), Vertex AI (soon)
- **Gemini 2.5 Flash (Preview)**
  - Fast, cost-efficient, with "thinking budget" to control reasoning depth
  - Nearly matches Pro on hard prompts, lower cost/latency
  - API support for fine-grained reasoning control
- **Gemini 2.0 Flash-Lite (General Availability)**
  - High-volume, cost-sensitive applications
  - 1M token context, multimodal input

**Key Features:**

- "Thinking" models: internal reasoning before output
- Agentic coding: can write, modify, debug, and refine code
- Massive context: 1M–2M tokens
- Tool use: API calls, code execution, structured data
- Fine-grained reasoning control (Flash)

---

## Model Comparison Table (2025)

| Model Family   | Variants         | Context Window | Modalities          | Best For                 | Notable Strengths                 | Limitations/Notes                       |
| -------------- | ---------------- | -------------- | ------------------- | ------------------------ | --------------------------------- | --------------------------------------- |
| OpenAI GPT-4.1 | 4.1, mini, nano  | 1M tokens      | Text, Image, Video  | Coding, reasoning, LLMs  | Coding, instruction, API support  | Reliability drops at 1M tokens          |
| Gemini 2.5     | Pro, Flash, Lite | 1M–2M tokens   | Text, Img, Vid, Aud | Reasoning, coding, agent | Multimodal, agentic, long context | Slightly behind in code gen (vs OpenAI) |

---

## Guidance for Future Updates

- Always document the model name, version, and a brief description.
- Note any special capabilities, limitations, or configuration requirements.
- When upgrading, update this file and reference the change in `system-upgrade-ideas.log`.

---

_This file is for the agentic system's own reference and should be maintained as models evolve._
