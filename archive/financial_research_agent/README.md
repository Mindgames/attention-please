# Seed Round Investment Memo Compiler

This tool compiles a comprehensive **seed round investment memorandum** by
processing all relevant documents in the `docs/` folder. It's designed
specifically for Grais.ai seed round investment materials and outputs
professional markdown files ready for investor presentation.

## ✨ Key Features

- **🎯 Seed Round Focused**: Specifically optimized for early-stage
  investment analysis and documentation
- **🤖 AI-Powered Analysis**: Uses OpenAI's 'o3' model for intelligent
  document processing and synthesis
- **📄 File Output**: Generates clean markdown files instead of console output
- **🔍 Quality Criticism**: Includes professional VC-level criticism and
  improvement suggestions
- **📊 Missing Information Analysis**: Identifies gaps and irrelevant content

## How It Works

The compilation flow consists of five main stages:

1. **Document Processing**: Processes all relevant documents from the docs
   folder, extracting key insights, financial data, market analysis, and
   strategic information relevant to the seed round investment thesis.

2. **Memo Compilation**: A senior investment analyst agent synthesizes all
   processed information into a cohesive, professional seed round investment
   memorandum following standard VC memo structure.

3. **Quality Verification**: A verification agent reviews the compiled memo
   for completeness, consistency, and persuasiveness.

4. **Professional Criticism**: A senior VC partner agent provides detailed
   criticism, improvement suggestions, and identifies potential investor
   concerns.

5. **File Output**: Saves the memo and comprehensive analysis to timestamped
   markdown files in the `output/` directory.

## Usage

Run the seed round memo compiler with:

```bash
python -m financial_research_agent.main
```

The system will automatically:

- Process all documents in `docs/investment/` (highest priority)
- Include core product documents (`product-description.md`, etc.)
- Analyze vision, technical, and roadmap documents
- Compile everything into a professional seed round investment memo
- Provide detailed criticism and improvement suggestions
- Generate two markdown files with timestamped names

## Document Sources

The compiler processes documents from these folders in order of priority:

1. **`docs/investment/`** - Core investment documents (memorandum,
   financial projections, competitive analysis, etc.)
2. **`docs/`** - Core product descriptions and README
3. **`docs/vision/`** - Strategic vision and positioning documents
4. **`docs/technical/`** - Technical architecture and capabilities
5. **`docs/roadmap/`** - Strategic roadmap and milestones

## Output Files

The compiler generates two timestamped markdown files in the `output/` folder:

### 📄 File 1: Seed Round Investment Memo

**Filename**: `grais_seed_round_memo_YYYYMMDD_HHMMSS.md`

A comprehensive seed round investment memorandum including:

- **Executive Summary**: Compelling 3-4 paragraph overview
- **Investment Highlights**: Top 5-7 key points
- **Market Opportunity & Problem Statement**
- **Solution & Product Vision**
- **Competitive Advantage & Technology**
- **Business Model & Path to Revenue**
- **Financial Projections & Unit Economics**
- **Founding Team & Execution Track Record**
- **Go-to-Market Strategy & Early Traction**
- **Use of Funds & Milestones to Series A**
- **Risk Factors & Mitigation Strategies**
- **Investment Terms & Conclusion**

### 📊 File 2: Analysis & Missing Information Report

**Filename**: `memo_analysis_report_YYYYMMDD_HHMMSS.md`

A comprehensive analysis report including:

- **Quality Scores**: Overall memo strength and verification scores
- **Critical Issues**: Must-address weaknesses and concerns
- **Improvement Suggestions**: Specific actionable recommendations
- **Seed Stage Concerns**: Early-stage specific risks and mitigations
- **Document Relevance Analysis**: High/Medium/Low relevance breakdown
- **Missing Information**: Identified gaps and required additional data
- **Professional Criticism**: VC-level feedback and recommendations

## Example Output Structure

```
output/
├── grais_seed_round_memo_20241215_143022.md
└── memo_analysis_report_20241215_143022.md
```

## Key Improvements for Seed Stage

The system specifically focuses on seed round requirements:

- Early traction and validation indicators
- Founding team strength and execution capability
- Market timing and opportunity sizing
- Product-market fit evidence
- Clear path to Series A milestones
- Risk mitigation for early-stage concerns
- Professional VC memo formatting and structure
