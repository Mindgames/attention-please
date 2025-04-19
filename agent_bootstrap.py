#!/usr/bin/env python3
"""
Bootstrap script to instantiate an OpenAI Agents SDK 0.0.11 Agent
and run the start-of-day routine defined in system/rules.

Usage:
    # Install dependencies:
    pip install openai-agents==0.0.11

    # Run the default start-of-day routine:
    python agent_bootstrap.py

    # Or specify a different action:
    python agent_bootstrap.py --action END-OF-DAY
"""
import glob
import subprocess
import argparse

from agents import Agent, Tool


def read_file(path: str) -> str:
    """Read and return the full contents of a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> str:
    """Overwrite a file with the provided content."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} characters to {path}"


def shell(cmd: str) -> str:
    """Run a shell command and return its standard output."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {cmd}\n{result.stderr}"
        )
    return result.stdout


def build_system_prompt(rules_dir: str) -> str:
    """
    Load all rule files from the system rules directory to compose the agent's system prompt.
    """
    prompt = []

    # Load each rule file in the system/rules directory
    for path in sorted(glob.glob(f"{rules_dir}/*.md")):
        raw = read_file(path)
        prompt.append(f"# Rule: {path}")
        prompt.append(raw.strip())

    return "\n\n".join(prompt)


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap and run a ReplyPilot routine via OpenAI Agents SDK 0.0.11"
    )
    parser.add_argument(
        "--action",
        "-a",
        default="START-OF-DAY",
        help="Name of the routine to run (e.g. START-OF-DAY, END-OF-DAY)",
    )
    args = parser.parse_args()

    # Define toolset
    tools = [
        Tool(
            name="read_file",
            fn=read_file,
            description="Read file contents from disk",
        ),
        Tool(
            name="write_file",
            fn=write_file,
            description="Write contents to a file",
        ),
        Tool(
            name="shell",
            fn=shell,
            description="Run a shell command and return its stdout",
        ),
    ]

    # Build system prompt from system rules only
    system_prompt = build_system_prompt(rules_dir="system/rules")

    # Instantiate the agent
    agent = Agent(
        name="ReplyPilot Agent",
        tools=tools,
        system_message=system_prompt,
        model="gpt-4-1106-preview",  # Use GPT-4.1 model
    )

    # Run the specified routine
    print(f"Running routine: {args.action}\n{'=' * 40}")
    result = agent.run(args.action)
    print(result)


if __name__ == "__main__":
    main()
