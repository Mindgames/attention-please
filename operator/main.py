import asyncio

from .manager import FocusManager


async def main() -> None:
    goals = input("What are your priorities today? ")
    hours = input("How many hours are available? ")
    await FocusManager().run(goals, hours)


if __name__ == "__main__":
    asyncio.run(main())
