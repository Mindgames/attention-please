# attention-ping

Codex skill that plays a macOS alert sound and says "Project NAME needs your attention."

## Requirements

- macOS for `afplay` and `say` (falls back to printing the message if `say` is unavailable).

## Install

Clone into your Codex skills folder:

```bash
git clone https://github.com/OWNER/attention-ping.git ~/.codex/skills/public/attention-ping
```

## Usage

Run from inside a repo so the script can derive the project name from `origin`:

```bash
scripts/attention-ping.sh
```

Override the project name or sound:

```bash
ATTENTION_PING_PROJECT="quiz-juice" scripts/attention-ping.sh
ATTENTION_PING_SOUND="/System/Library/Sounds/Ping.aiff" scripts/attention-ping.sh
```

## How it works

- Uses `git remote get-url origin` to infer the repo name.
- Falls back to the repo folder name or "this project".
- Plays a short sound and speaks the message.
