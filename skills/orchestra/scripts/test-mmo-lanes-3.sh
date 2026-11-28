#!/usr/bin/env bash
# Offline test for the group 3 lane adapters (devin codebuddy letta qoder gptme llm).
# Fake CLIs on PATH print the documented output shape and record the flags they were given.
# Run: bash skills/orchestra/scripts/test-mmo-lanes-3.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0
ok() { echo "PASS $1"; pass=$((pass + 1)); }
bad() { echo "FAIL $1"; [ -f "$T/out" ] && sed 's/^/    /' "$T/out"; [ -s "$T/log" ] && sed 's/^/    log: /' "$T/log"; fail=$((fail + 1)); }
chk() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }

mkdir -p "$T/bin" "$T/work"
echo "Say PONG." > "$T/brief"

# A fake CLI records its arguments (one per line) and its stdin; the body prints the output.
fake() { # name, body
  printf '#!/bin/sh\nprintf "%%s\\n" "$@" > "$FAKE_ARGS"\ncat > "$FAKE_STDIN"\n%s\n' "$2" > "$T/bin/$1"
  chmod +x "$T/bin/$1"
}
lane() { # provider, then mmo-run options; ro by default
  rm -f "$T/args" "$T/stdin"
  FAKE_ARGS="$T/args" FAKE_STDIN="$T/stdin" PATH="$T/bin:$PATH" \
    bash "$HERE/mmo-run" "$@" --brief "$T/brief" --out "$T/out" -C "$T/work" 2> "$T/log"
}
rwlane() { lane "$@" --mode rw --allow-main; }
has() { grep -qxF -- "$1" "$T/args"; }
lacks() { ! grep -qxF -- "$1" "$T/args"; }
header() { head -1 "$T/out"; }
answer() { sed -n 2p "$T/out"; }
status() { header | grep -q "status=$1"; }

# ---------------------------------------------------------------- devin (prompt after --, plain text)
fake devin 'case "${FAKE_MODE:-ok}" in
  ok) echo "DEVIN-OK" ;;
  trunc) echo "warning: response truncated at the model output token limit" >&2; exit 1 ;;
  edit) echo x > devin-wrote.txt; echo "DEVIN-OK" ;;
esac'
lane devin -m some-model; rc=$?
chk "devin ro: -p, trust check off, --model, prompt after --" '[ $rc -eq 0 ] && has -p && has --respect-workspace-trust && has false && has --model && has some-model && grep -qx -- "--" "$T/args" && grep -q "READ-ONLY LANE" "$T/args"'
chk "devin ro: no --permission-mode" 'lacks --permission-mode && lacks dangerous'
chk "devin: plain answer extracted" 'status ok && [ "$(answer)" = DEVIN-OK ]'
lane devin
chk "devin: no model flag when none given" 'lacks --model'
rwlane devin
chk "devin rw: --permission-mode dangerous" 'has --permission-mode && has dangerous'
FAKE_MODE=edit lane devin; rc=$?
chk "devin ro: a write lands in the throwaway dir and is reported" '[ $rc -eq 0 ] && header | grep -q "ro_violation=yes" && [ ! -e "$T/work/devin-wrote.txt" ]'
FAKE_MODE=trunc lane devin; rc=$?
chk "devin: nonzero exit (truncated response) is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- codebuddy (stdin, json result)
fake codebuddy 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"type\":\"result\",\"result\":\"CODEBUDDY-OK\",\"session_id\":\"s\",\"total_cost_usd\":0}" ;;
  fail) echo "request failed" >&2; exit 1 ;;
esac'
lane codebuddy -m some-alias --max-turns 9; rc=$?
chk "codebuddy ro: -p, --output-format json, model, max turns" '[ $rc -eq 0 ] && has -p && has --output-format && has json && has --model && has some-alias && has --max-turns && has 9'
chk "codebuddy ro: no -y, no skip flag" 'lacks -y && lacks --dangerously-skip-permissions'
chk "codebuddy: the brief reaches the CLI on stdin" 'grep -q "Say PONG" "$T/stdin"'
chk "codebuddy: json result extracted" 'status ok && [ "$(answer)" = CODEBUDDY-OK ]'
rwlane codebuddy
chk "codebuddy rw: -y" 'has -y'
FAKE_MODE=fail lane codebuddy; rc=$?
chk "codebuddy: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- letta (stdin, json result, --tools read-only)
fake letta 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"type\":\"result\",\"result\":\"LETTA-OK\",\"agent_id\":\"a\",\"conversation_id\":\"c\",\"usage\":{}}" ;;
  fail) echo "request failed" >&2; exit 1 ;;
esac'
lane letta -m sonnet; rc=$?
chk "letta ro: -p, --ephemeral, json, model" '[ $rc -eq 0 ] && has -p && has --ephemeral && has --output-format && has json && has --model && has sonnet'
chk "letta ro: --tools Read,Glob,Grep, no --yolo" 'has --tools && has Read,Glob,Grep && lacks --yolo'
chk "letta: the brief reaches the CLI on stdin" 'grep -q "Say PONG" "$T/stdin"'
chk "letta: json result extracted" 'status ok && [ "$(answer)" = LETTA-OK ]'
rwlane letta
chk "letta rw: --yolo, no --tools" 'has --yolo && lacks --tools'
FAKE_MODE=fail lane letta; rc=$?
chk "letta: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- qoder (stdin, plain text)
fake qoder 'case "${FAKE_MODE:-ok}" in
  ok) echo "QODER-OK" ;;
  fail) echo "request failed" >&2; exit 1 ;;
esac'
lane qoder -m performance; rc=$?
chk "qoder ro: -p, --cwd, --model" '[ $rc -eq 0 ] && has -p && has --cwd && has --model && has performance'
chk "qoder ro: no --yolo, no --permission-mode" 'lacks --yolo && lacks --permission-mode'
chk "qoder: the brief reaches the CLI on stdin" 'grep -q "Say PONG" "$T/stdin"'
chk "qoder: plain answer extracted" 'status ok && [ "$(answer)" = QODER-OK ]'
rwlane qoder
chk "qoder rw: --yolo" 'has --yolo'
FAKE_MODE=fail lane qoder; rc=$?
chk "qoder: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- gptme (prompt argument, JSON lines)
fake gptme 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"role\":\"system\",\"content\":\"You are gptme\"}"
      echo "{\"role\":\"user\",\"content\":\"Say PONG.\"}"
      echo "{\"role\":\"assistant\",\"content\":\"GPTME-OK\"}"
      echo "{\"role\":\"system\",\"content\":\"Ran command: ok\"}" ;;
  model) echo "Provider openai requires specifying a model" >&2; exit 1 ;;
  edit) echo x > gptme-wrote.txt
      echo "{\"role\":\"assistant\",\"content\":\"GPTME-OK\"}" ;;
esac'
lane gptme -m groq/some-model; rc=$?
chk "gptme ro: -n, json output, -w, model" '[ $rc -eq 0 ] && has -n && has --output-format && has json && has -w && has -m && has groq/some-model'
chk "gptme: the prompt is an argument" 'grep -q "Say PONG" "$T/args"'
chk "gptme: the last assistant message is the answer, not the trailing system line" 'status ok && [ "$(answer)" = GPTME-OK ]'
lane gptme
chk "gptme: no -m when no model given" 'lacks -m'
FAKE_MODE=edit lane gptme; rc=$?
chk "gptme ro: a write lands in the throwaway dir and is reported" '[ $rc -eq 0 ] && header | grep -q "ro_violation=yes" && [ ! -e "$T/work/gptme-wrote.txt" ]'
rwlane gptme
chk "gptme rw: same flags (-n already approves everything)" 'has -n && lacks -y'
FAKE_MODE=model lane gptme; rc=$?
chk "gptme: requires specifying a model is model (exit 8)" '[ $rc -eq 8 ] && status model'

# ---------------------------------------------------------------- llm (no tools, stdin)
fake llm 'case "${FAKE_MODE:-ok}" in
  ok) echo "LLM-OK" ;;
  fail) echo "Error: request failed" >&2; exit 1 ;;
esac'
lane llm -m some-model; rc=$?
chk "llm ro: --no-stream and -m, brief on stdin" '[ $rc -eq 0 ] && has --no-stream && has -m && has some-model && grep -q "Say PONG" "$T/stdin"'
chk "llm: plain answer extracted" 'status ok && [ "$(answer)" = LLM-OK ]'
lane llm
chk "llm: no -m when none given" 'lacks -m'
rwlane llm; rc=$?
chk "llm rw: refused, it has no tools" '[ $rc -ne 0 ] && grep -q "no tools" "$T/log"'
FAKE_MODE=fail lane llm; rc=$?
chk "llm: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'

echo "lanes-3: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
