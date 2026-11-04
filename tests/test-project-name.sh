#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="${1:-$repo_dir/scripts/attention-please.sh}"
case "$script" in
  /*) ;;
  *) script="$PWD/$script" ;;
esac

sandbox="$(mktemp -d "${TMPDIR:-/tmp}/attention-please-test.XXXXXX")"
trap 'rm -rf "$sandbox"' EXIT
mkdir -p "$sandbox/bin" "$sandbox/home" "$sandbox/worktree" "$sandbox/outside"
touch "$sandbox/sound.aiff"

# Guard against accidentally playing audio, even on a developer's Mac.
for audio_command in say afplay; do
  cat > "$sandbox/bin/$audio_command" <<'AUDIO'
#!/usr/bin/env bash
printf '%s\n' "$0" >> "$TEST_AUDIO_LOG"
exit 99
AUDIO
  chmod +x "$sandbox/bin/$audio_command"
done

# Do not let user Git configuration or inherited overrides affect the fixtures.
clean_env=(env -i "PATH=$sandbox/bin:$PATH" "HOME=$sandbox/home"
  "GIT_CEILING_DIRECTORIES=$sandbox" GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null)
test_git() {
  "${clean_env[@]}" git "$@"
}

test_git -C "$sandbox/worktree" init -q
test_git -C "$sandbox/worktree" remote add origin https://example.com/acme/project.git
test_git init -q --bare "$sandbox/project.git"

failures=0
checks=0
check_message() {
  local label="$1" directory="$2" expected="$3" actual
  shift 3
  checks=$((checks + 1))
  if actual="$(cd "$directory" && "${clean_env[@]}" \
    ATTENTION_PLEASE_NO_SOUND=1 ATTENTION_PLEASE_NO_SAY=1 \
    "ATTENTION_PLEASE_SOUND=$sandbox/sound.aiff" \
    "TEST_AUDIO_LOG=$sandbox/audio.log" "$@" bash "$script")"; then
    if [ "$actual" = "$expected" ]; then
      printf 'PASS %s\n' "$label"
      return
    fi
    printf 'FAIL %s: expected <%s>, got <%s>\n' "$label" "$expected" "$actual" >&2
  else
    printf 'FAIL %s: script exited unsuccessfully\n' "$label" >&2
  fi
  failures=$((failures + 1))
}

check_remote() {
  local remote="$1" expected="$2"
  test_git -C "$sandbox/worktree" remote set-url origin "$remote"
  check_message "$remote" "$sandbox/worktree" "Project $expected needs your attention."
}

check_remote 'https://example.com/acme/project.git' project
check_remote 'https://example.com/acme/project.git/' project
check_remote 'https://example.com/acme/project' project
check_remote 'https://example.com/acme/project/' project
check_remote 'git@example.com:acme/project.git' project
check_remote 'git@example.com:acme/project.git/' project
check_remote 'ssh://git@example.com/acme/project.git' project
check_remote 'ssh://git@example.com/acme/project.git/' project
check_remote 'ssh://git@example.com:2222/acme/project.git/' project
check_remote "file://$sandbox/project.git" project
check_remote "file://$sandbox/project.git/" project
check_remote "$sandbox/project.git" project
check_remote "$sandbox/project.git/" project
check_remote '../project.git' project
check_remote '../project.git/' project
check_remote 'https://example.com/acme/project.git.git/' project.git
check_remote 'https://example.com/acme/my project.git/' 'my project'
check_remote 'https://example.com/acme/project.github/' project.github

# Git also accepts the .git directory inside a non-bare repository as a remote.
test_git init -q "$sandbox/source-project"
check_remote "$sandbox/source-project/.git" source-project
test_git -C "$sandbox/worktree" ls-remote origin >/dev/null
check_remote "$sandbox/source-project/.git/" source-project
test_git -C "$sandbox/worktree" ls-remote origin >/dev/null
check_remote "file://$sandbox/source-project/.git" source-project
check_remote "file://$sandbox/source-project/.git/" source-project

# A trailing slash is usable by Git, not just an accepted remote config string.
# Only contact the temporary local bare repository; no network is required.
test_git -C "$sandbox/worktree" remote set-url origin "$sandbox/project.git/"
test_git -C "$sandbox/worktree" ls-remote origin >/dev/null
check_message 'local bare repository with trailing slash' "$sandbox/worktree" \
  'Project project needs your attention.'

test_git -C "$sandbox/worktree" remote add upstream 'git@example.com:acme/upstream-project.git/'
check_message 'selected remote' "$sandbox/worktree" \
  'Project upstream-project needs your attention.' ATTENTION_PLEASE_REMOTE=upstream
check_message 'explicit project override' "$sandbox/worktree" \
  'Project custom name needs your attention.' 'ATTENTION_PLEASE_PROJECT=custom name'
check_message 'message override' "$sandbox/worktree" \
  'Ready for review.' 'ATTENTION_PLEASE_MESSAGE=Ready for review.'
check_message 'missing selected remote fallback' "$sandbox/worktree" \
  'Project worktree needs your attention.' ATTENTION_PLEASE_REMOTE=missing

test_git -C "$sandbox/worktree" remote remove origin
check_message 'no origin fallback' "$sandbox/worktree" 'Project worktree needs your attention.'
check_message 'outside repository fallback' "$sandbox/outside" 'Project this project needs your attention.'
check_message 'override outside repository' "$sandbox/outside" \
  'Project custom needs your attention.' ATTENTION_PLEASE_PROJECT=custom

if [ -s "$sandbox/audio.log" ]; then
  printf 'FAIL audio commands were invoked\n' >&2
  failures=$((failures + 1))
fi

if [ "$failures" -ne 0 ]; then
  printf '%s failure(s) across %s project-name checks\n' "$failures" "$checks" >&2
  exit 1
fi
printf 'All %s project-name checks passed; no audio commands invoked.\n' "$checks"
