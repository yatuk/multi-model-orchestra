#!/usr/bin/env bash
# Offline test for the group 1 lanes (opencode gemini agy qwen crush goose aider): fake CLIs on PATH.
# Per lane: ro flags reach the CLI and no auto-approve flag does, rw has it, the documented output shape
# gives the right answer, one error string gets the right status. No model, no network.
# Run: bash skills/orchestra/scripts/test-mmo-lanes-1.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0; pass=0; RC=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
bad() { echo "FAIL $1"; [ -f "$T/out" ] && sed 's/^/    /' "$T/out"; fail=1; }
check() { local d="$1"; shift; if "$@"; then ok "$d"; else bad "$d"; fi; }
# run LANE ARGS...: runs mmo-run and keeps its exit code in RC.
run() { PATH="$T/bin:$PATH" bash "$HERE/mmo-run" "$@" --out "$T/out" 2> "$T/log"; RC=$?; }
header() { head -1 "$T/out"; }
has_all() { local x; for x in "$@"; do grep -qxF -- "$x" "$T/args" || return 1; done; }
has_none() { local x; for x in "$@"; do ! grep -qxF -- "$x" "$T/args" || return 1; done; }
ans() { [ "$(sed -n 2p "$T/out")" = "$1" ]; }
status_is() { [ "$RC" -eq "$1" ] && header | grep -q "status=$2"; }
in_stdin() { grep -q "Say PONG" "$T/stdin"; }
throwaway() { [ "$(git worktree list | wc -l)" -eq 2 ]; }
env_has() { grep -q "$1" "$T/env"; }
env_lacks() { ! grep -q "$1" "$T/env"; }

mkdir -p "$T/bin"
# Every fake records its arguments, stdin and environment, then prints the body for FAKE_MODE.
mk() { # name; body on stdin (a case on FAKE_MODE)
  {
    printf '#!/bin/sh\nprintf "%%s\\n" "$@" > "$FAKE_ARGS"\ncat > "$FAKE_STDIN"\nenv > "$FAKE_ENV"\n'
    cat
  } > "$T/bin/$1"
  chmod +x "$T/bin/$1"
}
export FAKE_ARGS="$T/args" FAKE_STDIN="$T/stdin" FAKE_ENV="$T/env"

mk opencode <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo '{"type":"step_start","sessionID":"s"}'
      echo '{"type":"reasoning","part":{"type":"reasoning","text":"thinking about it"}}'
      echo '{"type":"text","part":{"type":"text","text":"early draft"}}'
      echo '{"type":"text","part":{"type":"text","text":"PONG"}}'
      echo '{"type":"step_finish","sessionID":"s"}' ;;
  err) echo '{"type":"error","sessionID":"s","error":{"type":"unknown","message":"Cannot initialize openai/gpt-x: OPENAI_API_KEY is required to resolve the provider endpoint"}}'; exit 1 ;;
esac
X
mk gemini <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo '{"response":"PONG","stats":{"models":{}}}' ;;
  err) echo "Please set an Auth method in your settings or specify one of the following environment variables before running: GEMINI_API_KEY, GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_GENAI_USE_GCA" >&2; exit 41 ;;
  quota) echo "You have exhausted your capacity on this model." >&2; exit 1 ;;
esac
X
mk agy <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo '{"conversation_id":"c1","status":"SUCCESS","response":"PONG","num_turns":1}' ;;
  err) m='error: invalid model selection (--model "nosuch"): model nosuch is not recognized as a known model or custom model in settings'
       echo "$m" >&2; echo '{"conversation_id":"","status":"ERROR","response":"","error":"'"$m"'"}'; exit 1 ;;
esac
X
mk qwen <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo '[{"type":"system","subtype":"session_start"},{"type":"assistant","message":{"content":[{"type":"text","text":"draft"}]}},{"type":"result","subtype":"success","is_error":false,"result":"PONG","usage":{}}]' ;;
  iserr) echo '[{"type":"result","subtype":"error","is_error":true,"result":"boom"}]' ;;
  err) echo "Error: 429 Too Many Requests, rate limit reached" >&2; exit 1 ;;
  noauth) echo '[{"type":"result","subtype":"error_during_execution","is_error":true,"num_turns":0,"error":{"message":"No auth type is selected. Please configure an auth type (e.g. via settings or `--auth-type`) before running in non-interactive mode."}}]'; exit 1 ;;
esac
X
mk crush <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo PONG ;;
  err) echo "no providers configured - please run 'crush' to set up a provider interactively" >&2; exit 1 ;;
esac
X
mk goose <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo PONG ;;
  err) echo "Request failed: 429 Too Many Requests (rate limit)" >&2; exit 1 ;;
esac
X
mk aider <<'X'
case "${FAKE_MODE:-ok}" in
  ok) echo "Aider v0.86.2"; echo "Main model: x with whole edit format"; echo "MMO-ANSWER-BEGIN"; echo "PONG"; echo "MMO-ANSWER-END"; echo "Tokens: 1k sent, 5 received." ;;
  exit0err) echo "litellm.AuthenticationError: AuthenticationError: bad key"; exit 0 ;;
  err) echo "Unable to proceed without an OpenRouter API key for model 'openrouter/x'" >&2; exit 1 ;;
esac
X

git init -q "$T/main"; cd "$T/main" || exit 1
git config user.email t@example.com; git config user.name t; git config core.autocrlf false
echo one > a.txt; git add . && git commit -qm init
git worktree add -q "$T/wt" -b lane/x
echo "Say PONG." > "$T/brief"
RO=(--brief "$T/brief" -C "$T/main"); RW=(--mode rw --brief "$T/brief" -C "$T/wt")

# ---- opencode
run opencode "${RO[@]}" -m openai/gpt-x
check "opencode ro flags" has_all run --format json openai/gpt-x
check "opencode ro has no --auto" has_none --auto
check "opencode ro: brief goes in on stdin" in_stdin
check "opencode answer is the last text event, not reasoning" ans PONG
run opencode "${RW[@]}"
check "opencode rw has --auto" has_all --auto
FAKE_MODE=err run opencode "${RO[@]}"
check "opencode missing key is auth (7)" status_is 7 auth

# ---- gemini
run gemini "${RO[@]}" -m gemini-x
check "gemini ro: plan mode, json, model" has_all --approval-mode plan json gemini-x
check "gemini ro has no yolo" has_none yolo --yolo
check "gemini ro: brief on stdin" in_stdin
check "gemini answer is .response" ans PONG
run gemini "${RW[@]}"
check "gemini rw uses --approval-mode yolo, not plan" has_all --approval-mode yolo
check "gemini rw has no plan" has_none plan
FAKE_MODE=err run gemini "${RO[@]}"
check "gemini auth text (exit 41) is auth (7)" status_is 7 auth
FAKE_MODE=quota run gemini "${RO[@]}"
check "gemini quota text is limit (6)" status_is 6 limit

# ---- agy
run agy "${RO[@]}" -m slug-x
check "agy ro: -p, model, json, plan mode" has_all -p --model slug-x --output-format json --mode plan
check "agy ro has no skip-permissions" has_none --dangerously-skip-permissions
check "agy answer is stdout" ans PONG
check "agy ro leaves no extra worktree behind" throwaway
run agy "${RW[@]}"
check "agy rw has --dangerously-skip-permissions" has_all --dangerously-skip-permissions
FAKE_MODE=err run agy "${RO[@]}"
check "agy unknown model is model (8)" status_is 8 model

# ---- qwen
run qwen "${RO[@]}" --max-turns 5
check "qwen ro: plan mode, json, turn cap" has_all --approval-mode plan json --max-session-turns 5
check "qwen ro has no yolo" has_none yolo --yolo
check "qwen ro: brief on stdin" in_stdin
check "qwen answer is the last result item" ans PONG
check "qwen ro does not silence the yolo warning" env_lacks QWEN_CODE_SUPPRESS_YOLO_WARNING
run qwen "${RW[@]}"
check "qwen rw uses yolo" has_all --approval-mode yolo
check "qwen rw silences the yolo warning" env_has QWEN_CODE_SUPPRESS_YOLO_WARNING=1
FAKE_MODE=iserr run qwen "${RO[@]}"
check "qwen is_error result is a failed lane (3)" [ "$RC" -eq 3 ]
FAKE_MODE=err run qwen "${RO[@]}"
check "qwen rate limit text is limit (6)" status_is 6 limit
FAKE_MODE=noauth run qwen "${RO[@]}"
check "qwen real signed-out output is auth (7)" status_is 7 auth

# ---- crush
run crush "${RO[@]}" -m prov/model-x
check "crush ro: run -q and model" has_all run -q prov/model-x
check "crush ro has no yolo flag" has_none -y --yolo
check "crush ro: brief on stdin" in_stdin
check "crush answer is stdout" ans PONG
check "crush ro leaves no extra worktree behind" throwaway
check "crush turns metrics off" env_has CRUSH_DISABLE_METRICS=1
run crush "${RW[@]}"
check "crush rw is the same command (no approval flag exists)" has_all run -q
FAKE_MODE=err run crush "${RO[@]}"
check "crush no provider is auth (7)" status_is 7 auth

# ---- goose
run goose "${RO[@]}" -m openrouter/vendor/model-x --max-turns 9
check "goose ro: quiet, no session, stdin instructions" has_all -q --no-session -i -
check "goose ro: provider and model are split" has_all --provider openrouter --model vendor/model-x --max-turns 9
check "goose ro: brief on stdin" in_stdin
check "goose answer is stdout" ans PONG
check "goose ro does not set GOOSE_MODE" env_lacks '^GOOSE_MODE='
run goose "${RW[@]}"
check "goose rw sets GOOSE_MODE=auto" env_has '^GOOSE_MODE=auto'
FAKE_MODE=err run goose "${RO[@]}"
check "goose rate limit text is limit (6)" status_is 6 limit

# ---- aider
run aider "${RO[@]}" -m deepseek/deepseek-chat
check "aider ro: ask mode, no auto-commits, model" has_all --chat-mode ask --no-auto-commits --model deepseek/deepseek-chat
check "aider ro has no --yes-always" has_none --yes-always
check "aider answer is the text between the markers" ans PONG
run aider "${RW[@]}"
check "aider rw has --yes-always" has_all --yes-always --no-auto-commits
check "aider rw has no ask mode" has_none ask
FAKE_MODE=exit0err run aider "${RO[@]}"
check "aider exit 0 with a litellm auth error is auth (7)" status_is 7 auth
FAKE_MODE=err run aider "${RO[@]}"
check "aider missing key is auth (7)" status_is 7 auth

echo "passed $pass"
exit $fail
