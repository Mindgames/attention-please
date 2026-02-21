"""Rich terminal output utilities for the operator.

Provides consistent, beautiful terminal formatting with colors, emojis, and structure.
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

# Rich terminal formatting


class Colors:
    """ANSI color codes for terminal output."""

    # Basic colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class Emojis:
    """Emojis for visual enhancement."""

    # Status indicators
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    LOADING = "⏳"
    DONE = "🎯"

    # Actions
    SCHEDULE = "📅"
    TASK = "📝"
    PROJECT = "📁"
    REVIEW = "🔍"
    UPDATE = "🔄"
    DELETE = "🗑️"
    COMPLETE = "✔️"
    PLAN = "🎯"

    # Time
    CLOCK = "🕐"
    CALENDAR = "📆"
    TIMER = "⏱️"

    # Communication
    CHAT = "💬"
    COACH = "🎓"
    HELP = "❓"
    EXIT = "👋"

    # Progress
    ARROW = "➤"
    BULLET = "•"
    CHECK = "✓"
    CROSS = "✗"


class TerminalFormatter:
    """Rich terminal formatting utilities."""

    def __init__(
        self, use_colors: bool = True, use_emojis: bool = True
    ):
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_emojis = use_emojis

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_colors:
            return text
        return f"{color}{text}{Colors.RESET}"

    def _emoji(self, emoji: str) -> str:
        """Add emoji if emojis are enabled."""
        if not self.use_emojis:
            return ""
        return f"{emoji} "

    def header(self, text: str, emoji: str = "") -> str:
        """Create a prominent header."""
        emoji_str = self._emoji(emoji) if emoji else ""
        return self._colorize(
            f"\n{emoji_str}{text.upper()}", Colors.BOLD + Colors.CYAN
        )

    def subheader(self, text: str, emoji: str = "") -> str:
        """Create a subheader."""
        emoji_str = self._emoji(emoji) if emoji else ""
        return self._colorize(
            f"\n{emoji_str}{text}", Colors.BOLD + Colors.BLUE
        )

    def success(self, text: str, emoji: str = Emojis.SUCCESS) -> str:
        """Success message."""
        emoji_str = self._emoji(emoji)
        return self._colorize(f"{emoji_str}{text}", Colors.GREEN)

    def error(self, text: str, emoji: str = Emojis.ERROR) -> str:
        """Error message."""
        emoji_str = self._emoji(emoji)
        return self._colorize(f"{emoji_str}{text}", Colors.RED)

    def warning(self, text: str, emoji: str = Emojis.WARNING) -> str:
        """Warning message."""
        emoji_str = self._emoji(emoji)
        return self._colorize(f"{emoji_str}{text}", Colors.YELLOW)

    def info(self, text: str, emoji: str = Emojis.INFO) -> str:
        """Info message."""
        emoji_str = self._emoji(emoji)
        return self._colorize(f"{emoji_str}{text}", Colors.CYAN)

    def highlight(self, text: str) -> str:
        """Highlight important text."""
        return self._colorize(text, Colors.BOLD + Colors.YELLOW)

    def muted(self, text: str) -> str:
        """Muted text for less important information."""
        return self._colorize(text, Colors.DIM)

    def bullet(self, text: str, level: int = 0) -> str:
        """Create a bullet point with proper indentation."""
        indent = "  " * level
        bullet = self._emoji(Emojis.BULLET) if level == 0 else "  "
        return f"{indent}{bullet}{text}"

    def checkbox(self, text: str, checked: bool = False) -> str:
        """Create a checkbox item."""
        check = self._emoji(Emojis.CHECK if checked else "☐")
        return f"{check} {text}"

    def progress_bar(
        self, current: int, total: int, width: int = 30
    ) -> str:
        """Create a simple progress bar."""
        if total == 0:
            return ""

        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int((current / total) * 100)
        return f"[{bar}] {percentage}% ({current}/{total})"

    def timestamp(self) -> str:
        """Get current timestamp string."""
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def time_of_day_label(self, now: Optional[datetime] = None) -> str:
        """Return a human-friendly time-of-day label for a datetime."""
        current = now or datetime.now()
        hour = current.hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 23:
            return "evening"
        return "night"

    def separator(self, char: str = "─", length: int = 50) -> str:
        """Create a visual separator."""
        return self._colorize(char * length, Colors.DIM)

    def code_block(self, text: str, language: str = "") -> str:
        """Format code block."""
        lines = text.split("\n")
        formatted = []
        for line in lines:
            formatted.append(
                self._colorize(f"  {line}", Colors.BRIGHT_BLACK)
            )
        return "\n".join(formatted)

    def table_row(
        self, *columns: str, widths: Optional[list[int]] = None
    ) -> str:
        """Create a table row with proper spacing."""
        if not columns:
            return ""

        if widths is None:
            # Auto-calculate widths
            max_width = 80
            col_width = max_width // len(columns)
            widths = [col_width] * len(columns)

        formatted_cols = []
        for i, col in enumerate(columns):
            width = widths[i] if i < len(widths) else 20
            formatted_cols.append(col.ljust(width)[:width])

        return " │ ".join(formatted_cols)

    def table_header(
        self, *columns: str, widths: Optional[list[int]] = None
    ) -> str:
        """Create a table header with separator."""
        header = self.table_row(*columns, widths=widths)
        separator = self.table_row(
            *[
                "─" * (widths[i] if i < len(widths) else 20)
                for i in range(len(columns))
            ]
        )
        return f"{self._colorize(header, Colors.BOLD)}\n{self._colorize(separator, Colors.DIM)}"


class ProgressIndicator:
    """Animated progress indicator for long-running operations."""

    def __init__(
        self,
        message: str = "Working...",
        formatter: Optional[TerminalFormatter] = None,
    ):
        self.message = message
        self.formatter = formatter or TerminalFormatter()
        self.running = False
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.current_char = 0

    def start(self):
        """Start the progress indicator."""
        self.running = True
        self._print_status()

    def stop(self, final_message: str = ""):
        """Stop the progress indicator."""
        self.running = False
        if final_message:
            print(f"\r{self.formatter.success(final_message)}")
        else:
            print()  # Clear the line

    def _print_status(self):
        """Print current status with spinner."""
        if not self.running:
            return

        char = self.spinner_chars[self.current_char]
        status = f"{char} {self.message}"
        print(
            f"\r{self.formatter.info(status, emoji='')}",
            end="",
            flush=True,
        )

        self.current_char = (self.current_char + 1) % len(
            self.spinner_chars
        )

        # Schedule next update
        import threading

        timer = threading.Timer(0.1, self._print_status)
        timer.daemon = True
        timer.start()


class OperatorTerminal:
    """Main terminal interface for the operator."""

    def __init__(self):
        self.formatter = TerminalFormatter()
        self._session_start = datetime.now()

    # Convenience pass-throughs to the formatter so call sites can use
    # terminal.info()/warning()/error()/success() directly.
    def info(self, text: str, emoji: str = Emojis.INFO) -> str:  # type: ignore[override]
        return self.formatter.info(text, emoji)

    def warning(self, text: str, emoji: str = Emojis.WARNING) -> str:  # type: ignore[override]
        return self.formatter.warning(text, emoji)

    def error(self, text: str, emoji: str = Emojis.ERROR) -> str:  # type: ignore[override]
        return self.formatter.error(text, emoji)

    def success(self, text: str, emoji: str = Emojis.SUCCESS) -> str:  # type: ignore[override]
        return self.formatter.success(text, emoji)

    def welcome(self) -> str:
        """Display welcome message."""
        now = datetime.now()
        daypart = self.formatter.time_of_day_label(now)
        lines = [
            self.formatter.header("GRAIS OPERATOR", Emojis.COACH),
            self.formatter.info("AI-Augmented Daily Focus System"),
            self.formatter.muted(
                f"Session started: {self._session_start.strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            self.formatter.muted(
                f"Local time: {now.strftime('%Y-%m-%d %H:%M')} ({daypart})"
            ),
            "",
            self.formatter.subheader(
                "Available Commands", Emojis.HELP
            ),
            self.formatter.bullet("'status' - Review project health"),
            self.formatter.bullet(
                "'show schedule' - View current plan"
            ),
            self.formatter.bullet(
                "'plan my day' - Generate impact-first schedule"
            ),
            self.formatter.bullet("'help' - Show this help"),
            self.formatter.bullet("'exit' - Quit operator"),
            "",
            self.formatter.info(
                "Chat freely - I'll coach with next steps and capture tasks."
            ),
            self.formatter.separator(),
        ]
        return "\n".join(lines)

    def prompt(self) -> str:
        """Display input prompt."""
        now = datetime.now()
        daypart = self.formatter.time_of_day_label(now)
        timestamp = now.strftime("%H:%M")
        return (
            f"{self.formatter.muted(f'[{timestamp} {daypart}]')} "
            f"{self.formatter.highlight('operator')} ➤ "
        )

    def goodbye(self) -> str:
        """Display goodbye message."""
        duration = datetime.now() - self._session_start
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        lines = [
            "",
            self.formatter.header("SESSION COMPLETE", Emojis.DONE),
            self.formatter.info(
                f"Duration: {int(hours)}h {int(minutes)}m"
            ),
            self.formatter.success("Keep making impact! 🚀"),
            "",
        ]
        return "\n".join(lines)

    def show_schedule(self, schedule_text: str) -> str:
        """Display schedule in a formatted way."""
        lines = [
            self.formatter.header(
                "TODAY'S SCHEDULE", Emojis.SCHEDULE
            ),
            "",
            self.formatter.code_block(schedule_text),
            "",
            self.formatter.info("Schedule saved to schedule.md"),
        ]
        return "\n".join(lines)

    def show_tasks(
        self, tasks: list[dict], project: Optional[str] = None
    ) -> str:
        """Display tasks in a formatted way."""
        if project:
            header = f"TASKS FOR {project.upper()}"
        else:
            header = "CURRENT TASKS"

        lines = [self.formatter.header(header, Emojis.TASK)]

        if not tasks:
            lines.append(self.formatter.muted("No tasks found."))
            return "\n".join(lines)

        # Group by project
        by_project: dict[str, list[dict]] = {}
        for task in tasks:
            proj = task.get("project", "General")
            if proj not in by_project:
                by_project[proj] = []
            by_project[proj].append(task)

        for proj, proj_tasks in by_project.items():
            if (
                not project
            ):  # Only show project headers if not filtering
                lines.append(
                    self.formatter.subheader(proj, Emojis.PROJECT)
                )

            for task in proj_tasks:
                desc = task.get("description", "")
                priority = task.get("priority", "M")
                due = task.get("due", "unset")
                checked = task.get("completed", False)

                # Priority color coding
                if priority == "H":
                    priority_color = Colors.RED
                elif priority == "M":
                    priority_color = Colors.YELLOW
                else:
                    priority_color = Colors.GREEN

                # Format task line
                task_line = self.formatter.checkbox(desc, checked)
                if due != "unset":
                    task_line += (
                        f" {self.formatter.muted(f'(due: {due})')}"
                    )

                task_line += f" {self.formatter._colorize(f'[{priority}]', priority_color)}"

                lines.append(f"  {task_line}")

        return "\n".join(lines)

    def show_projects(self, projects: list[dict]) -> str:
        """Display projects in a formatted way."""
        lines = [
            self.formatter.header("PROJECT STATUS", Emojis.PROJECT)
        ]

        if not projects:
            lines.append(self.formatter.muted("No projects found."))
            return "\n".join(lines)

        # Table header
        header = self.formatter.table_header(
            "Project",
            "Status",
            "Tasks",
            "Updated",
            widths=[20, 12, 8, 12],
        )
        lines.append(header)

        for project in projects:
            name = project.get("name", "Unknown")
            status = project.get("status", "Active")
            task_count = project.get("task_count", 0)
            updated = project.get("updated", "Unknown")

            # Status color coding
            if status.lower() == "active":
                status_color = Colors.GREEN
            elif status.lower() == "paused":
                status_color = Colors.YELLOW
            else:
                status_color = Colors.RED

            status_colored = self.formatter._colorize(
                status, status_color
            )
            row = self.formatter.table_row(
                name,
                status_colored,
                str(task_count),
                updated,
                widths=[20, 12, 8, 12],
            )
            lines.append(row)

        return "\n".join(lines)

    def operation_result(
        self, operation: str, success: bool, details: str = ""
    ) -> str:
        """Display operation result."""
        if success:
            return self.formatter.success(
                f"{operation} completed successfully", Emojis.DONE
            )
        else:
            return self.formatter.error(
                f"{operation} failed: {details}", Emojis.ERROR
            )

    def loading(self, message: str) -> ProgressIndicator:
        """Start a loading indicator."""
        return ProgressIndicator(message, self.formatter)


# Global instance for easy access
terminal = OperatorTerminal()
