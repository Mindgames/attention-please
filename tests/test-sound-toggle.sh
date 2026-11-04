#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
script="${1:-$repo_dir/scripts/attention-please.sh}"
sandbox="$(mktemp -d "${TMPDIR:-/tmp}/attention-sound-test.XXXXXX")"
trap 'rm -rf "$sandbox"' EXIT
mkdir -p "$sandbox/bin" "$sandbox/home" "$sandbox/config with spaces"
touch "$sandbox/sound.aiff"
for audio_command in say afplay; do
  cat > "$sandbox/bin/$audio_command" <<'AUDIO'
#!/usr/bin/env bash
printf '%s\n' "${0##*/}" >> "$TEST_AUDIO_LOG"
AUDIO
  chmod +x "$sandbox/bin/$audio_command"
done
config="$sandbox/config with spaces/settings"
clean_env=(env -i "PATH=$sandbox/bin:$PATH" "HOME=$sandbox/home"
  "TEST_AUDIO_LOG=$sandbox/audio.log" "ATTENTION_PLEASE_CONFIG_FILE=$config"
  "ATTENTION_PLEASE_SOUND=$sandbox/sound.aiff" ATTENTION_PLEASE_PROJECT=test)
run() { "${clean_env[@]}" /bin/bash "$script" "$@"; }
checks=0
expect() {
  local expected="$1" actual
  shift
  actual="$(run "$@")"
  [ "$actual" = "$expected" ] || { printf 'Expected <%s>, got <%s>\n' "$expected" "$actual" >&2; exit 1; }
  checks=$((checks + 1))
}
expect 'attention-please sound is on' --sound status
[ ! -e "$config" ]
expect 'attention-please sound is off' --sound off
expect 'attention-please sound is off' --sound status
expect 'attention-please sound is on' --sound toggle
expect 'attention-please sound is off' --sound=off
expect 'attention-please sound is on' --sound ON
expect 'attention-please sound is off' --sound disabled
# Preserve unrelated text without executing it; remove duplicate preferences.
printf '# preserved\nother=$(touch %s)\nsound_enabled=on\nsound_enabled=off' "$sandbox/executed" > "$config"
expect 'attention-please sound is off' --sound off
[ "$(cat "$config")" = "$(printf '# preserved\nother=$(touch %s)\nsound_enabled=off' "$sandbox/executed")" ]
[ ! -e "$sandbox/executed" ]
[ ! -e "$sandbox/audio.log" ]
# Invalid arguments must fail without changing config or invoking audio.
cp "$config" "$sandbox/before"
for value in '' invalid; do
  for spelling in separate equals; do
    args=("--sound=$value")
    if [ "$spelling" = separate ]; then args=(--sound "$value"); fi
    result=0
    run "${args[@]}" > "$sandbox/stdout" 2> "$sandbox/stderr" || result=$?
    [ "$result" -eq 2 ]
    [ ! -s "$sandbox/stdout" ]
    cmp "$config" "$sandbox/before"
    checks=$((checks + 1))
  done
done
for argument in --sound --unknown; do
  result=0
  run "$argument" >/dev/null 2>&1 || result=$?
  [ "$result" -eq 2 ]
  checks=$((checks + 1))
done
[ ! -e "$sandbox/audio.log" ]
# Muting sound preserves speech; stubs record routing without playing audio.
run
[ "$(cat "$sandbox/audio.log")" = say ]
rm "$sandbox/audio.log"
# Environment override still mutes an enabled persisted preference.
expect 'attention-please sound is on' --sound on
"${clean_env[@]}" ATTENTION_PLEASE_NO_SOUND=1 /bin/bash "$script"
[ "$(cat "$sandbox/audio.log")" = say ]
rm "$sandbox/audio.log"
# Exercise enabled sound; wait briefly for the asynchronous afplay stub.
run > "$sandbox/notification"
for attempt in {1..100}; do
  if [ "$(wc -l < "$sandbox/audio.log")" -eq 2 ]; then break; fi
  sleep 0.01
done
[ "$(sort "$sandbox/audio.log")" = "$(printf 'afplay\nsay')" ]
rm "$sandbox/audio.log"
# Config directories must fail without moving temporary files inside them.
mkdir "$sandbox/config-directory"
result=0
"${clean_env[@]}" "ATTENTION_PLEASE_CONFIG_FILE=$sandbox/config-directory" /bin/bash "$script" --sound off > "$sandbox/stdout" 2> "$sandbox/stderr" || result=$?
[ "$result" -ne 0 ]
[ ! -s "$sandbox/stdout" ]
[ -z "$(ls -A "$sandbox/config-directory")" ]
# A failed rename must clean up its temporary file.
cat > "$sandbox/bin/mv" <<'FAIL'
#!/usr/bin/env bash
exit 1
FAIL
chmod +x "$sandbox/bin/mv"
result=0
run --sound off >/dev/null 2>&1 || result=$?
[ "$result" -ne 0 ]
[ -z "$(find "$sandbox/config with spaces" -name '*.tmp.*' -print)" ]
rm "$sandbox/bin/mv"
# Default path resolution is isolated from actual user configuration.
"${clean_env[@]}" ATTENTION_PLEASE_CONFIG_FILE= "XDG_CONFIG_HOME=$sandbox/xdg" /bin/bash "$script" --sound off >/dev/null
[ "$(cat "$sandbox/xdg/attention-please/config")" = sound_enabled=off ]
"${clean_env[@]}" ATTENTION_PLEASE_CONFIG_FILE= /bin/bash "$script" --sound off >/dev/null
[ "$(cat "$sandbox/home/.config/attention-please/config")" = sound_enabled=off ]
printf 'Passed %s CLI assertions plus config safety and stubbed audio-routing checks.\n' "$checks"
