# Attention Please

A Codex and Claude Agent SKILL that notifies you when your attention is needed.

![Support](supported.png)

Attention Please is an Agent SKILL that boosts your productivity by alerting you when a background task finishes or your input is required.

Compatible with macOS today. Windows and Linux are coming soon.

## Install (skills.sh)

Install via `skills.sh`:

```bash
npx skills add Mindgames/attention-please
```

Global install:

```bash
npx skills add Mindgames/attention-please -g -y
```

## Instruct your Agent

Tell your agent when audible alerts are useful:

```text
$attention-please update AGENTS.md to alert only when I explicitly ask, a long-running task needs my input, or a background process finishes and needs attention.
```

## Toggle the alert sound

The short `afplay` alert can be muted or re-enabled persistently:

```bash
scripts/attention-please.sh --sound off
scripts/attention-please.sh --sound on
scripts/attention-please.sh --sound toggle
scripts/attention-please.sh --sound status
```

This controls only the alert sound. Speech remains controlled separately with `ATTENTION_PLEASE_NO_SAY=1`.

By default the preference is stored in `${XDG_CONFIG_HOME:-~/.config}/attention-please/config`. Override the path with `ATTENTION_PLEASE_CONFIG_FILE`.

## Audio sample

MP4 clip (not embedded in repository code):

- Play in browser: [Project john doe needs your attention](https://github.com/Mindgames/attention-please/releases/download/audio-sample-john-doe-20260302/attention-please-john-doe.mp4)
- Download MP4: [Project john doe needs your attention](https://github.com/Mindgames/attention-please/releases/download/audio-sample-john-doe-20260302/attention-please-john-doe.mp4)

Note: GitHub strips video/audio tags from README rendering, so a markdown page player inline control is not supported here.

Issue with the hosted clip: [#5](https://github.com/Mindgames/attention-please/issues/5)

---

Follow me on X: https://x.com/mathiiias123

## Development checks

Run `bash -n scripts/attention-please.sh` and `bash tests/test-sound-toggle.sh`. The tests use temporary config files and audio stubs; they do not change your preferences or play audio.
