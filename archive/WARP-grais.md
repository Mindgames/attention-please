# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is the **Grais Investment Materials** repository, containing all materials for preparing comprehensive seed round investment documentation. Grais is "Cursor.sh but for communication" - AI agents that integrate directly into chat communication channels to provide strategic conversation assistance.

## Key Commands

### Research & Analysis Tools

Generate investment memo from docs:
```bash
python -m financial_research_agent.main
```

Run general research bot (interactive):
```bash
python -m research_bot.main
```

### Daily Workflow Commands

Check TODO list status (should be done daily):
```bash
cat TODO.md
```

Update daily log:
```bash
echo "$(date): Checked TODO.md and reviewed priorities" >> daily_log.md
```

### File Operations

Find specific document types:
```bash
find docs/ -name "*.md" -type f | grep -E "(investment|financial|competitive)"
```

Search for specific terms across all documents:
```bash
grep -r "seed round\|Series A\|valuation" docs/
```

## Architecture & Code Structure

### Multi-Agent AI System

The repository contains two main AI agent systems:

**1. Financial Research Agent** (`financial_research_agent/`)
- **Purpose**: Compiles comprehensive seed round investment memorandums
- **Architecture**: 5-stage pipeline with specialized agents:
  - Document processor → Memo compiler → Quality verifier → Professional critic → File output
- **Key Agents**: 
  - `memo_compiler_agent.py` - Senior investment analyst synthesis
  - `memo_critic_agent.py` - VC-level criticism and improvement suggestions
  - `memo_verifier_agent.py` - Quality verification and completeness checks
- **Output**: Timestamped markdown files in `output/` directory

**2. Research Bot** (`research_bot/`)
- **Purpose**: Multi-agent web research and report generation
- **Architecture**: 3-stage pipeline:
  - Planner → Parallel search agents → Writer synthesis
- **Usage**: Interactive tool for general research topics

### Document Hierarchy

The repository follows a structured documentation hierarchy optimized for investment presentation:

```
docs/
├── investment/           # Core investment documents (highest priority)
│   ├── investment-memorandum.md
│   ├── financial-projections.md
│   ├── competitive-landscape.md
│   └── team-and-validation.md
├── product-description.md    # Core product overview
├── vision/               # Strategic positioning
├── technical/            # Technical architecture
└── roadmap/              # Development timeline
```

## Important Terminology & Philosophy

### Preferred Terms (from .cursorrules)
- **"AI Augmentation"** - Core philosophy, preferred over "automation"
- **"Human-in-the-Loop"** - Fundamental design approach where humans maintain control
- **"Human-AI Partnership"** - The relationship between users and AI in Grais

### Avoid These Terms
- "AI Automation" (implies removing humans from the process)
- "Replacement" (AI is not meant to replace human communication)

## Daily Procedures

### Required Daily Check
Every development session should start with:
1. Review `TODO.md` for current priorities and gaps
2. Update `daily_log.md` with the date and priorities reviewed
3. Focus on "Critical Missing Information" items first

### Priority Order for Tasks
1. **Critical Missing Information** (team details, funding amounts, real metrics)
2. **Data & Validation Gaps** (customer validation, market research)
3. **Pitch Deck Completion** (visual assets, demo screenshots)
4. **Business Model Refinement** (pricing strategy, go-to-market)

## Output File Management

### Generated Files Location
- **Investment memos**: `output/grais_seed_round_memo_YYYYMMDD_HHMMSS.md`
- **Analysis reports**: `output/memo_analysis_report_YYYYMMDD_HHMMSS.md`

### File Naming Convention
All generated outputs use timestamp format: `YYYYMMDD_HHMMSS`

## Development Context

### Investment Stage Focus
- **Current Stage**: Seed round preparation ($3-5M target, $12-18M post-money valuation)
- **Next Milestone**: Series A readiness (18-month timeline)
- **Key Metrics**: Path to $1M ARR and 10K DAU within 18 months

### Critical Data Gaps
The TODO.md file contains comprehensive lists of missing information required for investor presentations. Always reference this file before making assumptions about company details, team information, or financial metrics.

### Confidentiality
This repository contains confidential and proprietary information of Grais. All work should maintain appropriate confidentiality standards for investment materials.

## Agent System Dependencies

Both agent systems appear to use:
- OpenAI API (specifically 'o3' model mentioned in financial_research_agent)
- Async Python patterns
- Modular agent architecture with specialized roles

Note: No requirements.txt or dependency files were found - dependencies may be managed elsewhere or require setup.
