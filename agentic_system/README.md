# Agentic System 2.0

This directory contains the implementation of the next-generation agentic system for Grais, based on the design in `docs/technical/agentic-system-2.0.md`.

## Overview

- Multi-agent orchestration using OpenAI Agents SDK 0.0.11
- Modular agent roles (summarizer, reviewer, upgrade recommender, etc.)
- Hybrid memory and extensible tool layer
- Automated project file review, summarization, and upgrade suggestion workflow
- Strict Human-in-the-Loop and AI Augmentation philosophy

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure your `.env` file is present at the project root with all required API keys and configuration.

3. Run the main agentic system:
   ```bash
   python main.py
   ```

## Files

- `main.py`: Entry point for the agentic system
- `orchestrator.py`: Multi-agent orchestration logic
- `agents/`: Specialized agent implementations
- `memory/`: Memory and context modules
- `tools/`: Tool interface modules

## Philosophy

- All outputs are suggestions for human review (never direct actions)
- Transparent reasoning and logging
- Continuous improvement and easy onboarding for new contributors

For full technical rationale and design, see `../docs/technical/agentic-system-2.0.md`.
