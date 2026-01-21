import asyncio
import argparse

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass

from .manager import FocusManager
from .terminal import terminal


async def _chat_loop(manager: FocusManager) -> None:
    print(terminal.welcome())
    while True:
        try:
            msg = input(terminal.prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{terminal.goodbye()}")
            return
        if not msg:
            continue
        if msg.lower() in {"exit", "quit"}:
            print(terminal.goodbye())
            return
        if msg.lower() in {"help", "?"}:
            print(terminal.welcome())
            continue
        reply = await manager.run(note=msg)
        if reply:
            print(reply)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Daily focus operator"
    )
    parser.add_argument(
        "--goals",
        type=str,
        default=None,
        help="Override default goals",
    )
    parser.add_argument(
        "--hours",
        type=str,
        default=None,
        help="Available hours, e.g., 6",
    )
    parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="One-shot instruction to execute",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Only review projects; skip scheduling",
    )
    args = parser.parse_args()

    manager = FocusManager()

    # If any one-shot flags are provided, perform a single run; else start chat
    if any([args.goals, args.hours, args.message, args.status_only]):
        reply = await manager.run(
            goals=args.goals,
            hours=args.hours,
            note=args.message,
            status_only=args.status_only,
        )
        if reply:
            print(reply)
    else:
        await _chat_loop(manager)


if __name__ == "__main__":
    asyncio.run(main())
