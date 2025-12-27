#!/usr/bin/env bash
set -euo pipefail

project_name="${ATTENTION_PING_PROJECT:-}"
sound_path="${ATTENTION_PING_SOUND:-/System/Library/Sounds/Ping.aiff}"

repo_root=""
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  repo_root="$(git rev-parse --show-toplevel)"
fi

if [ -z "$project_name" ] && [ -n "$repo_root" ]; then
  remote_url="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
  if [ -n "$remote_url" ]; then
    clean="${remote_url%.git}"
    path="$clean"
    if [[ "$clean" == *"://"* ]]; then
      path="${clean#*://}"
      path="${path#*@}"
      path="${path#*/}"
    elif [[ "$clean" == *":"* ]]; then
      path="${clean#*:}"
    fi
    path="${path%/}"
    project_name="${path##*/}"
  fi
fi

if [ -z "$project_name" ] && [ -n "$repo_root" ]; then
  project_name="$(basename "$repo_root")"
fi

if [ -z "$project_name" ]; then
  project_name="this project"
fi

message="Project ${project_name} needs your attention."

if command -v afplay >/dev/null 2>&1 && [ -f "$sound_path" ]; then
  afplay "$sound_path" &
fi

if command -v say >/dev/null 2>&1; then
  say "$message"
else
  printf '%s\n' "$message"
fi
