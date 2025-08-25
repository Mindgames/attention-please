from __future__ import annotations

import asyncio
import time
from pathlib import Path
from collections.abc import Sequence
from datetime import datetime

from rich.console import Console

from agents import Runner, gen_trace_id, trace

from .agents.document_processor_agent import (
    DocumentSummary,
    document_processor_agent,
)
from .agents.memo_compiler_agent import (
    MemoCompilerData,
    memo_compiler_agent,
)
from .agents.memo_verifier_agent import (
    MemoVerificationResult,
    memo_verifier_agent,
)
from .agents.memo_critic_agent import (
    MemoCriticResult,
    memo_critic_agent,
)
from .printer import Printer


class InvestmentMemoManager:
    """
    Orchestrates the seed round investment memo compilation flow:
    1. Document Processing: Reads and processes all relevant docs
    2. Memo Compilation: Compiles a cohesive seed round investment memo
    3. Verification: Verifies the memo for completeness and accuracy
    4. Criticism: Provides detailed criticism and improvement suggestions
    5. File Output: Saves memo, analysis and logs to markdown files
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)
        self.docs_path = Path("docs")
        self.output_path = Path("output")
        self.requested_path = Path("requested_material")
        self.logs_path = Path("logs")

        # Ensure directories exist
        self.output_path.mkdir(exist_ok=True)
        self.requested_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    async def run(self) -> None:
        trace_id = gen_trace_id()
        with trace(
            "Seed round memo compilation trace", trace_id=trace_id
        ):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/"
                f"trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item(
                "start",
                "Starting seed round investment memo compilation...",
                is_done=True,
            )

            # Process all relevant documents
            processed_docs = await self._process_documents()

            # Compile the investment memo
            compiled_memo = await self._compile_memo(processed_docs)

            # Verify the memo
            verification = await self._verify_memo(compiled_memo)

            # Get detailed criticism
            criticism = await self._criticize_memo(compiled_memo)

            # Generate missing information report
            missing_info_report = (
                await self._generate_missing_info_report(
                    processed_docs
                )
            )

            # Save to files
            memo_file, analysis_file = await self._save_to_files(
                compiled_memo,
                verification,
                criticism,
                missing_info_report,
            )

            self.printer.update_item(
                "complete",
                f"✅ Seed round memo saved to {memo_file}",
                is_done=True,
            )
            self.printer.update_item(
                "analysis",
                f"📊 Analysis report saved to {analysis_file}",
                is_done=True,
            )

            self.printer.end()

        # Print summary to console
        print("\n🚀 SEED ROUND INVESTMENT MEMO COMPILATION COMPLETE")
        print(f"📄 Investment Memo: {memo_file}")
        print(f"📊 Analysis Report: {analysis_file}")
        print(
            f"⭐ Overall Quality Score: {criticism.overall_strength_score}/10"
        )
        print("\n" + "=" * 60)

    async def _process_documents(self) -> Sequence[DocumentSummary]:
        """Process all relevant documents from the docs folder"""
        self.printer.update_item(
            "processing", "Processing documents..."
        )

        # Get all relevant document paths
        doc_paths = self._get_document_paths()

        # Process documents in parallel
        tasks = [
            asyncio.create_task(self._process_single_document(path))
            for path in doc_paths
        ]
        processed_docs: list[DocumentSummary] = []
        num_completed = 0

        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                processed_docs.append(result)
            num_completed += 1
            self.printer.update_item(
                "processing",
                f"Processing... {num_completed}/{len(tasks)} documents completed",
            )

        self.printer.mark_item_done("processing")
        return processed_docs

    def _get_document_paths(self) -> list[Path]:
        """Get all relevant document paths for the investment memo"""
        paths: list[Path] = []

        # Investment documents (highest priority)
        investment_dir = self.docs_path / "investment"
        if investment_dir.exists():
            paths.extend(investment_dir.glob("*.md"))

        # Core product documents
        core_docs = [
            "product-description.md",
            "product-description-v2.md",
            "README.md",
        ]
        for doc in core_docs:
            doc_path = self.docs_path / doc
            if doc_path.exists():
                paths.append(doc_path)

        # Vision documents
        vision_dir = self.docs_path / "vision"
        if vision_dir.exists():
            paths.extend(vision_dir.glob("*.md"))

        # Technical documents
        technical_dir = self.docs_path / "technical"
        if technical_dir.exists():
            paths.extend(technical_dir.glob("*.md"))

        # Roadmap documents
        roadmap_dir = self.docs_path / "roadmap"
        if roadmap_dir.exists():
            paths.extend(roadmap_dir.glob("*.md"))

        return paths

    async def _process_single_document(
        self, doc_path: Path
    ) -> DocumentSummary | None:
        """Process a single document and extract key information"""
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read()

            input_data = (
                f"Document: {doc_path.name}\nContent:\n{content}"
            )
            result = await Runner.run(
                document_processor_agent, input_data
            )
            return result.final_output_as(DocumentSummary)
        except Exception as e:
            print(f"Error processing {doc_path}: {e}")
            return None

    async def _compile_memo(
        self, processed_docs: Sequence[DocumentSummary]
    ) -> MemoCompilerData:
        """Compile all processed documents into a cohesive seed round memo"""
        self.printer.update_item(
            "compiling", "Compiling seed round memo..."
        )

        input_data = (
            "Processed Documents for Seed Round Investment Memo:\n\n"
        )
        for doc in processed_docs:
            input_data += f"## {doc.document_name}\n"
            input_data += f"**Relevance:** {doc.relevance_score}\n"
            input_data += f"**Summary:** {doc.summary}\n"
            input_data += (
                f"**Key Insights:** {', '.join(doc.key_insights)}\n\n"
            )

        result = Runner.run_streamed(memo_compiler_agent, input_data)
        update_messages = [
            "Analyzing market opportunity...",
            "Compiling financial projections...",
            "Structuring competitive analysis...",
            "Finalizing executive summary...",
        ]
        last_update = time.time()
        next_message = 0

        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(
                update_messages
            ):
                self.printer.update_item(
                    "compiling", update_messages[next_message]
                )
                next_message += 1
                last_update = time.time()

        self.printer.mark_item_done("compiling")
        return result.final_output_as(MemoCompilerData)

    async def _verify_memo(
        self, memo: MemoCompilerData
    ) -> MemoVerificationResult:
        """Verify the compiled memo for completeness and accuracy"""
        self.printer.update_item(
            "verifying", "Verifying seed round memo..."
        )

        result = await Runner.run(memo_verifier_agent, memo.full_memo)
        self.printer.mark_item_done("verifying")
        return result.final_output_as(MemoVerificationResult)

    async def _criticize_memo(
        self, memo: MemoCompilerData
    ) -> MemoCriticResult:
        """Get detailed criticism and improvement suggestions"""
        self.printer.update_item(
            "criticizing", "Analyzing memo quality..."
        )

        result = await Runner.run(memo_critic_agent, memo.full_memo)
        self.printer.mark_item_done("criticizing")
        return result.final_output_as(MemoCriticResult)

    async def _generate_missing_info_report(
        self, processed_docs: Sequence[DocumentSummary]
    ) -> str:
        """Generate a report on missing information and document relevance"""
        report = (
            "# Missing Information & Document Analysis Report\n\n"
        )
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Document relevance analysis
        high_relevance = [
            d for d in processed_docs if d.relevance_score == "High"
        ]
        medium_relevance = [
            d for d in processed_docs if d.relevance_score == "Medium"
        ]
        low_relevance = [
            d for d in processed_docs if d.relevance_score == "Low"
        ]

        report += "## Document Relevance Summary\n\n"
        report += (
            f"- **High Relevance:** {len(high_relevance)} documents\n"
        )
        report += f"- **Medium Relevance:** {len(medium_relevance)} documents\n"
        report += (
            f"- **Low Relevance:** {len(low_relevance)} documents\n\n"
        )

        if low_relevance:
            report += "### Low Relevance Documents\n\n"
            for doc in low_relevance:
                report += f"- **{doc.document_name}**: {doc.investment_relevance}\n"
            report += "\n"

        # Missing information compilation
        all_missing_info = []
        for doc in processed_docs:
            all_missing_info.extend(doc.missing_information)

        if all_missing_info:
            report += "## Missing Information Identified\n\n"
            # Remove duplicates while preserving order
            unique_missing = list(dict.fromkeys(all_missing_info))
            for info in unique_missing:
                report += f"- {info}\n"
            report += "\n"

        # Document-specific missing information
        report += "## Document-Specific Missing Information\n\n"
        for doc in processed_docs:
            if doc.missing_information:
                report += f"### {doc.document_name}\n"
                for info in doc.missing_information:
                    report += f"- {info}\n"
                report += "\n"

        return report

    async def _save_to_files(
        self,
        memo: MemoCompilerData,
        verification: MemoVerificationResult,
        criticism: MemoCriticResult,
        missing_info_report: str,
    ) -> tuple[Path, Path]:
        """Save the memo and analysis to markdown files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # File 1: Investment Memo
        memo_filename = f"grais_seed_round_memo_{timestamp}.md"
        memo_file = self.output_path / memo_filename

        with open(memo_file, "w", encoding="utf-8") as f:
            f.write(memo.full_memo)

        # File 2: Analysis Report (missing info + criticism)
        analysis_filename = f"memo_analysis_report_{timestamp}.md"
        analysis_file = self.output_path / analysis_filename

        analysis_content = "# Investment Memo Analysis Report\n\n"
        analysis_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        analysis_content += "## Executive Summary\n\n"
        analysis_content += f"**Overall Quality Score:** {criticism.overall_strength_score}/10\n"
        analysis_content += (
            f"**Thesis Strength:** {criticism.thesis_strength}\n\n"
        )

        analysis_content += "## Critical Issues to Address\n\n"
        for weakness in criticism.critical_weaknesses:
            analysis_content += f"- {weakness}\n"
        analysis_content += "\n"

        analysis_content += "## Improvement Suggestions\n\n"
        for suggestion in criticism.improvement_suggestions:
            analysis_content += f"- {suggestion}\n"
        analysis_content += "\n"

        analysis_content += "## Seed Stage Specific Concerns\n\n"
        for concern in criticism.seed_stage_concerns:
            analysis_content += f"- {concern}\n"
        analysis_content += "\n"

        analysis_content += "## Verification Results\n\n"
        analysis_content += f"**Quality Score:** {verification.overall_quality_score}/10\n\n"
        analysis_content += "**Strengths:**\n"
        for strength in verification.strengths:
            analysis_content += f"- {strength}\n"
        analysis_content += "\n"

        analysis_content += "**Areas for Improvement:**\n"
        for area in verification.improvement_areas:
            analysis_content += f"- {area}\n"
        analysis_content += "\n"

        analysis_content += "---\n\n"
        analysis_content += missing_info_report

        analysis_content += "---\n\n"
        analysis_content += "## Final Recommendation\n\n"
        analysis_content += criticism.final_recommendation

        with open(analysis_file, "w", encoding="utf-8") as f:
            f.write(analysis_content)

        return memo_file, analysis_file


# Keep the old class for backwards compatibility but mark as deprecated
class FinancialResearchManager:
    """
    DEPRECATED: Use InvestmentMemoManager instead.
    This class is kept for backwards compatibility only.
    """

    def __init__(self) -> None:
        raise DeprecationWarning(
            "FinancialResearchManager is deprecated. "
            "Use InvestmentMemoManager instead."
        )
