#!/bin/bash
# Run the Grais agent in SYSTEM-REVIEW mode automatically

set -e

# Activate your Python environment if needed
# source /path/to/venv/bin/activate

python agent_bootstrap.py --action SYSTEM-REVIEW
