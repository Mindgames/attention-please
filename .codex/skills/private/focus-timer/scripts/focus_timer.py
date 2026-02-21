#!/usr/bin/env python3
"""Run focus and break timers with spoken prompts and pip alerts."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

DEFAULT_FOCUS_MINUTES = 90
DEFAULT_BREAK_MINUTES = 15
DEFAULT_SOUND = "/System/Library/Sounds/Ping.aiff"
DEFAULT_VOLUME = 1.0
DEFAULT_VOLUME_BOOST = 80
DEFAULT_PIP_COUNT = 1
DEFAULT_PIP_PAUSE_SECONDS = 0.25


def get_state_path() -> Path:
    """Return the path for the session state file."""
    env_path = os.getenv("FOCUS_TIMER_STATE_PATH")
    if env_path:
        return Path(env_path).expanduser()
    digest = hashlib.sha256(str(Path(__file__).resolve()).encode("utf-8")).hexdigest()
    suffix = digest[:10]
    return Path(tempfile.gettempdir()) / f"focus_timer_{suffix}.json"


def get_log_path() -> Path:
    """Return the path for the background session log file."""
    return get_state_path().with_suffix(".log")


def get_project_root() -> Path:
    """Return the repository root based on the .codex directory when possible."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == ".codex":
            return parent.parent
    return Path.cwd()


def get_activity_log_path() -> Path:
    """Return the path for the daily activity log."""
    return get_project_root() / "operator" / "time_log.jsonl"


def get_pending_checkins_path() -> Path:
    """Return the path for pending focus check-ins."""
    return get_project_root() / "operator" / "pending_checkins.json"


def load_pending_checkins() -> list[dict[str, object]]:
    """Load pending check-ins from disk."""
    path = get_pending_checkins_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def save_pending_checkins(checkins: list[dict[str, object]]) -> None:
    """Persist pending check-ins to disk."""
    path = get_pending_checkins_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(checkins, ensure_ascii=True, indent=2))


def enqueue_checkin(entry: dict[str, object]) -> None:
    """Append a pending check-in entry."""
    try:
        checkins = load_pending_checkins()
        checkins.append(entry)
        save_pending_checkins(checkins)
    except Exception:
        return


def log_event(event: str, payload: dict[str, object]) -> None:
    """Append a JSONL entry for time tracking without interrupting the timer."""
    try:
        log_path = get_activity_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "event": event,
        }
        entry.update(payload)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")
    except Exception:
        return


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value to a range."""
    return max(minimum, min(value, maximum))


def play_pip(sound_path: str, volume: float) -> None:
    """Play a single pip sound if possible, otherwise fall back to a beep."""
    if sound_path:
        path = Path(sound_path)
        if path.exists() and shutil.which("afplay"):
            volume = clamp(volume, 0.0, 1.0)
            subprocess.run(["afplay", "-v", f"{volume:.2f}", str(path)], check=False)
            return

    if shutil.which("osascript"):
        subprocess.run(["osascript", "-e", "beep 1"], check=False)
        return

    print("\a", end="", flush=True)


def play_pips(
    sound_path: str,
    volume: float,
    count: int = DEFAULT_PIP_COUNT,
    pause_seconds: float = DEFAULT_PIP_PAUSE_SECONDS,
) -> None:
    """Play a short pip sequence for audible emphasis."""
    if count <= 0:
        return
    for index in range(count):
        play_pip(sound_path, volume)
        if index < count - 1:
            time.sleep(pause_seconds)


def run_attention_notice() -> None:
    """Trigger the attention-please alert for satcom."""
    script = (
        Path.home()
        / ".codex"
        / "skills"
        / "public"
        / "attention-please"
        / "scripts"
        / "attention-please.sh"
    )
    if not script.exists():
        return
    subprocess.run(
        ["env", "ATTENTION_PLEASE_PROJECT=satcom", str(script)],
        check=False,
    )


def start_nag(mode: str, session_id: str, started_at: str, interval_minutes: int = 5) -> None:
    """Start a background alert loop until the user responds."""
    script = Path(__file__).resolve().parent / "nag_until_response.py"
    if not script.exists():
        return
    command = [
        sys.executable,
        str(script),
        "--mode",
        mode,
        "--session-id",
        session_id,
        "--started-at",
        started_at,
        "--interval-minutes",
        str(interval_minutes),
    ]
    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        return


def speak(message: str, voice: str | None) -> None:
    """Speak a message using the system TTS if available."""
    if not message:
        return
    if shutil.which("say"):
        command = ["say"]
        if voice:
            command.extend(["-v", voice])
        command.append(message)
        subprocess.run(command, check=False)


def announce(
    message: str,
    speech_enabled: bool,
    voice: str | None,
    sound_path: str,
    volume: float,
    volume_boost: int,
) -> None:
    """Print, speak, and add pip cues around the message."""
    print(message)
    previous_volume = None
    volume_changed = False
    if volume_boost > 0:
        previous_volume = get_system_volume()
        if previous_volume is not None:
            target_volume = int(clamp(volume_boost, 0, 100))
            if previous_volume < target_volume:
                set_system_volume(target_volume)
                volume_changed = True
    try:
        play_pips(sound_path, volume)
        if speech_enabled:
            speak(message, voice)
    finally:
        if volume_changed and previous_volume is not None:
            set_system_volume(previous_volume)


def build_child_args(argv: list[str]) -> list[str]:
    """Build arguments for a background child process."""
    cleaned: list[str] = []
    for arg in argv:
        if arg == "--background":
            continue
        cleaned.append(arg)
    return cleaned


def launch_background(command: list[str], log_path: Path) -> int:
    """Launch the timer in the background and return the PID."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    return process.pid


def get_system_volume() -> int | None:
    """Return the current system output volume (0-100) if available."""
    if not shutil.which("osascript"):
        return None
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    try:
        return int(output)
    except ValueError:
        return None


def set_system_volume(volume: int) -> None:
    """Set the system output volume (0-100)."""
    volume = int(clamp(volume, 0, 100))
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {volume}"], check=False
    )


def write_state(
    start_time: float,
    focus_minutes: float,
    break_minutes: float,
    topic: str,
    mode: str,
    session_id: str,
) -> None:
    """Persist the active session for status checks."""
    state_path = get_state_path()
    state = {
        "pid": os.getpid(),
        "start_time": start_time,
        "focus_minutes": focus_minutes,
        "break_minutes": break_minutes,
        "topic": topic,
        "mode": mode,
        "session_id": session_id,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2))


def clear_state() -> None:
    """Remove the state file if present."""
    state_path = get_state_path()
    if state_path.exists():
        state_path.unlink()


def is_pid_running(pid: int) -> bool:
    """Return True if the PID exists."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def format_duration(total_seconds: float) -> str:
    """Format seconds as Xm Ys."""
    total_seconds = max(0, int(round(total_seconds)))
    minutes, seconds = divmod(total_seconds, 60)
    if minutes and seconds:
        return f"{minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m"
    return f"{seconds}s"


def show_status() -> None:
    """Print the remaining time for the active session."""
    state_path = get_state_path()
    if not state_path.exists():
        print("No active focus session.")
        return
    try:
        state = json.loads(state_path.read_text())
    except json.JSONDecodeError:
        print("No active focus session.")
        return

    pid = state.get("pid")
    if not isinstance(pid, int) or not is_pid_running(pid):
        clear_state()
        print("No active focus session.")
        return

    start_time = state.get("start_time", 0)
    focus_minutes = state.get("focus_minutes", DEFAULT_FOCUS_MINUTES)
    break_minutes = state.get("break_minutes", DEFAULT_BREAK_MINUTES)
    topic = state.get("topic") or "unspecified"
    mode = state.get("mode", "focus")

    now = time.time()
    elapsed = max(0.0, now - float(start_time))
    focus_seconds = max(1, round(float(focus_minutes) * 60))
    break_seconds = max(0, round(float(break_minutes) * 60))

    if mode == "break":
        if break_seconds <= 0:
            clear_state()
            print("No active focus session.")
            return
        if elapsed < break_seconds:
            remaining = break_seconds - elapsed
            print(f"Break: {format_duration(remaining)} remaining.")
            return
        clear_state()
        print("No active focus session.")
        return

    if elapsed < focus_seconds:
        remaining = focus_seconds - elapsed
        print(f"Focus: {format_duration(remaining)} remaining. Topic: {topic}.")
        return
    if break_seconds and elapsed < focus_seconds + break_seconds:
        remaining = focus_seconds + break_seconds - elapsed
        print(f"Break: {format_duration(remaining)} remaining.")
        return

    clear_state()
    print("No active focus session.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run focus and break timers with spoken prompts and an alert."
    )
    parser.add_argument(
        "-m",
        "--minutes",
        type=float,
        default=DEFAULT_FOCUS_MINUTES,
        help="Focus duration in minutes (default: 90).",
    )
    parser.add_argument(
        "-b",
        "--break-minutes",
        type=float,
        default=DEFAULT_BREAK_MINUTES,
        help="Break duration in minutes after focus (default: 15).",
    )
    parser.add_argument(
        "-t",
        "--topic",
        default="",
        help="Focus topic to include in the spoken prompt.",
    )
    parser.add_argument(
        "--mode",
        choices=["focus", "break"],
        default="focus",
        help="Run focus+break or break-only mode.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show remaining time for the active session and exit.",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run the timer in the background and exit immediately.",
    )
    parser.add_argument(
        "--log-path",
        default="",
        help="Optional log file path for background runs.",
    )
    parser.add_argument(
        "--no-speech",
        action="store_true",
        help="Disable spoken prompts.",
    )
    parser.add_argument(
        "--voice",
        default="",
        help="Voice name for the macOS 'say' command.",
    )
    parser.add_argument(
        "-s",
        "--sound",
        default=DEFAULT_SOUND,
        help="Sound file to play when time is up.",
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=DEFAULT_VOLUME,
        help="Pip volume for afplay (0.0 to 1.0).",
    )
    parser.add_argument(
        "--volume-boost",
        type=int,
        default=DEFAULT_VOLUME_BOOST,
        help="Temporarily raise system output volume (0-100) during prompts; 0 disables.",
    )
    args = parser.parse_args()

    if args.status:
        show_status()
        return
    if args.background:
        child_args = build_child_args(sys.argv[1:])
        child_command = [
            sys.executable,
            str(Path(__file__).resolve()),
            *child_args,
        ]
        log_path = (
            Path(args.log_path).expanduser()
            if args.log_path
            else get_log_path()
        )
        pid = launch_background(child_command, log_path)
        print(f"Focus session started in background (pid {pid}).")
        return

    if args.minutes <= 0:
        raise SystemExit("minutes must be greater than 0")
    if args.break_minutes < 0:
        raise SystemExit("break-minutes must be 0 or greater")
    if not (0.0 <= args.volume <= 1.0):
        raise SystemExit("volume must be between 0.0 and 1.0")
    if args.volume_boost < 0 or args.volume_boost > 100:
        raise SystemExit("volume-boost must be between 0 and 100")

    speech_enabled = not args.no_speech
    voice = args.voice or None
    topic = args.topic.strip()

    start_time = time.time()
    session_id = uuid.uuid4().hex
    mode = args.mode
    if mode == "break":
        break_minutes = args.minutes
        write_state(start_time, 0.0, break_minutes, topic, mode, session_id)
        try:
            break_start = f"Now start a {break_minutes:g} minute break."
            announce(
                break_start,
                speech_enabled,
                voice,
                args.sound,
                args.volume,
                args.volume_boost,
            )
            log_event(
                "break_start",
                {
                    "session_id": session_id,
                    "mode": "break",
                    "topic": topic,
                    "planned_minutes": break_minutes,
                    "source": "break_only",
                },
            )
            break_seconds = max(1, round(break_minutes * 60))
            break_started_at = time.time()
            time.sleep(break_seconds)
            log_event(
                "break_end",
                {
                    "session_id": session_id,
                    "mode": "break",
                    "topic": topic,
                    "elapsed_seconds": max(0.0, time.time() - break_started_at),
                },
            )
            announce(
                "Break is over. Quick note: what did you do during the break and what's next?",
                speech_enabled,
                voice,
                args.sound,
                args.volume,
                args.volume_boost,
            )
            run_attention_notice()
            start_nag(
                "break",
                session_id,
                datetime.fromtimestamp(break_started_at)
                .astimezone()
                .isoformat(),
                interval_minutes=5,
            )
        finally:
            clear_state()
        return

    write_state(start_time, args.minutes, args.break_minutes, topic, mode, session_id)

    try:
        focus_start = f"New {args.minutes:g} minute focus session starting."
        if topic:
            focus_start = f"{focus_start} Focus on {topic}."
        announce(
            focus_start,
            speech_enabled,
            voice,
            args.sound,
            args.volume,
            args.volume_boost,
        )
        log_event(
            "focus_start",
            {
                "session_id": session_id,
                "mode": "focus",
                "topic": topic,
                "planned_focus_minutes": args.minutes,
                "planned_break_minutes": args.break_minutes,
            },
        )

        focus_seconds = max(1, round(args.minutes * 60))
        time.sleep(focus_seconds)
        log_event(
            "focus_end",
            {
                "session_id": session_id,
                "mode": "focus",
                "topic": topic,
                "elapsed_seconds": max(0.0, time.time() - start_time),
            },
        )
        enqueue_checkin(
            {
                "session_id": session_id,
                "topic": topic,
                "planned_focus_minutes": args.minutes,
                "planned_break_minutes": args.break_minutes,
                "started_at": datetime.fromtimestamp(start_time)
                .astimezone()
                .isoformat(),
                "ended_at": datetime.now().astimezone().isoformat(),
            }
        )
        run_attention_notice()
        start_nag(
            "focus",
            session_id,
            datetime.now().astimezone().isoformat(),
            interval_minutes=5,
        )
        if args.break_minutes > 0:
            break_start = (
                "Focus session complete. "
                "Please share what you did and the next task. "
                f"Now start a {args.break_minutes:g} minute break."
            )
            announce(
                break_start,
                speech_enabled,
                voice,
                args.sound,
                args.volume,
                args.volume_boost,
            )
            log_event(
                "break_start",
                {
                    "session_id": session_id,
                    "mode": "break",
                    "topic": topic,
                    "planned_minutes": args.break_minutes,
                    "source": "focus",
                },
            )
            break_seconds = max(1, round(args.break_minutes * 60))
            break_started_at = time.time()
            time.sleep(break_seconds)
            log_event(
                "break_end",
                {
                    "session_id": session_id,
                    "mode": "break",
                    "topic": topic,
                    "elapsed_seconds": max(0.0, time.time() - break_started_at),
                },
            )
            announce(
                "Break is over. Quick note: what did you do during the break and what's next?",
                speech_enabled,
                voice,
                args.sound,
                args.volume,
                args.volume_boost,
            )
            run_attention_notice()
            start_nag(
                "break",
                session_id,
                datetime.fromtimestamp(break_started_at)
                .astimezone()
                .isoformat(),
                interval_minutes=5,
            )
        else:
            announce(
                "Focus session complete. Please share what you did and the next task.",
                speech_enabled,
                voice,
                args.sound,
                args.volume,
                args.volume_boost,
            )
            run_attention_notice()
            start_nag(
                "focus",
                session_id,
                datetime.now().astimezone().isoformat(),
                interval_minutes=5,
            )
    finally:
        clear_state()


if __name__ == "__main__":
    main()
