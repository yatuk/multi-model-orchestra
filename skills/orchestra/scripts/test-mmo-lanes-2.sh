#!/usr/bin/env bash
# Offline test for the group 2 lane adapters (cursor copilot amp droid auggie kiro cline kilo vibe pi).
# Fake CLIs on PATH print the documented output shape and record the flags they were given.
# Run: bash skills/orchestra/scripts/test-mmo-lanes-2.sh
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

# ---------------------------------------------------------------- cursor (binary: cursor-agent)
fake cursor-agent 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"CURSOR-OK\",\"session_id\":\"s\"}" ;;
  auth) echo "Error: Authentication required. Please run agent login first, or set CURSOR_API_KEY environment variable." >&2; exit 1 ;;
  usage) echo "ActionRequiredError: Kimi K3 is not included in your weekly usage Buy credits or switch to a Grok model to continue." >&2; exit 1 ;;
  model) echo "Cannot use this model: no-such-model-xyz. Available models: auto, composer-2.5" >&2; exit 1 ;;
esac'
lane cursor -m gpt-5; rc=$?
chk "cursor ro: print, json, workspace, trust, --mode ask, model" '[ $rc -eq 0 ] && has -p && has --output-format && has json && has --workspace && has --trust && has --mode && has ask && has --model && has gpt-5'
chk "cursor ro: no --force" 'lacks --force'
chk "cursor: json result extracted" 'status ok && [ "$(answer)" = CURSOR-OK ]'
lane cursor
chk "cursor: no model flag when none given" 'lacks --model'
rwlane cursor
chk "cursor rw: --force, no --mode ask" 'has --force && lacks --mode'
FAKE_MODE=auth lane cursor; rc=$?
chk "cursor: Authentication required is auth (exit 7)" '[ $rc -eq 7 ] && status auth'
FAKE_MODE=usage lane cursor -m kimi-k3-high; rc=$?
chk "cursor: model not in the weekly usage is limit (exit 6)" '[ $rc -eq 6 ] && status limit'
FAKE_MODE=model lane cursor -m no-such-model-xyz; rc=$?
chk "cursor: Cannot use this model is model (exit 8)" '[ $rc -eq 8 ] && status model'

# ---------------------------------------------------------------- copilot
fake copilot 'case "${FAKE_MODE:-ok}" in
  ok) echo "COPILOT-OK" ;;
  empty) echo "the model returned an empty final response" >&2; exit 1 ;;
  model) echo "Execution failed: Model \"x\" is not available." >&2; exit 1 ;;
esac'
lane copilot -m gpt-6.1-sol; rc=$?
chk "copilot ro: -p, -s, -C, --no-ask-user, --model=" '[ $rc -eq 0 ] && has -p && has -s && has -C && has --no-ask-user && has --model=gpt-6.1-sol'
chk "copilot ro: no allow-all flag" 'lacks --allow-all-tools && lacks --allow-all && lacks --yolo'
chk "copilot: plain answer extracted" 'status ok && [ "$(answer)" = COPILOT-OK ]'
rwlane copilot
chk "copilot rw: --allow-all-tools" 'has --allow-all-tools'
FAKE_MODE=empty lane copilot; rc=$?
chk "copilot: nonzero exit (empty final response) is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=model lane copilot; rc=$?
chk "copilot: real unknown-model text is model (exit 8)" '[ $rc -eq 8 ] && status model'

# ---------------------------------------------------------------- amp (prompt on stdin, stream-json)
fake amp 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"type\":\"system\",\"subtype\":\"init\"}"
      echo "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"text\",\"text\":\"draft\"}]}}"
      echo "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"AMP-OK\",\"session_id\":\"T-1\"}" ;;
  fail) echo "{\"type\":\"result\",\"subtype\":\"error\",\"is_error\":true,\"result\":\"agent stopped on error\"}"; exit 1 ;;
  failzero) echo "{\"type\":\"result\",\"subtype\":\"error\",\"is_error\":true,\"result\":\"agent stopped on error\"}" ;;
  edit) echo x > amp-wrote.txt
      echo "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"AMP-OK\"}" ;;
esac'
lane amp; rc=$?
chk "amp ro: -x and --stream-json, brief on stdin" '[ $rc -eq 0 ] && has -x && has --stream-json && grep -q "Say PONG" "$T/stdin" && grep -q "READ-ONLY LANE" "$T/stdin"'
chk "amp: last result line is the answer" 'status ok && [ "$(answer)" = AMP-OK ]'
chk "amp: no approval flag exists, none sent" 'lacks --dangerously-allow-all'
rwlane amp
chk "amp rw: same flags (Amp has no approval system)" 'has -x && has --stream-json && lacks --dangerously-allow-all'
FAKE_MODE=edit lane amp; rc=$?
chk "amp ro: a write lands in the throwaway dir and is reported" '[ $rc -eq 0 ] && header | grep -q "ro_violation=yes" && [ ! -e "$T/work/amp-wrote.txt" ]'
FAKE_MODE=fail lane amp; rc=$?
chk "amp: exit 1 with is_error result is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=failzero lane amp; rc=$?
chk "amp: is_error result under exit 0 is still failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- droid (prompt via -f)
fake droid 'for a in "$@"; do if [ "$p" = 1 ]; then cp "$a" "$FAKE_STDIN"; p=0; fi; [ "$a" = -f ] && p=1; done
case "${FAKE_MODE:-ok}" in
  ok) echo "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"DROID-OK\",\"session_id\":\"s\"}" ;;
  iserr) echo "{\"type\":\"result\",\"subtype\":\"error\",\"is_error\":true,\"result\":\"action above autonomy level\"}" ;;
  level) echo "error: action requires a higher autonomy level" >&2; exit 1 ;;
esac'
lane droid -m claude-opus-5-5; rc=$?
chk "droid ro: exec, -f, -o json, --cwd, model" '[ $rc -eq 0 ] && has exec && has -f && has -o && has json && has --cwd && has -m && has claude-opus-5-5'
chk "droid ro: no --auto, no --skip-permissions-unsafe" 'lacks --auto && lacks --skip-permissions-unsafe'
chk "droid: the brief reaches the CLI through the -f file" 'grep -q "Say PONG" "$T/stdin"'
chk "droid: json result extracted" 'status ok && [ "$(answer)" = DROID-OK ]'
rwlane droid
chk "droid rw: --auto medium" 'has --auto && has medium && lacks --skip-permissions-unsafe'
FAKE_MODE=iserr lane droid; rc=$?
chk "droid: is_error result under exit 0 is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=level lane droid; rc=$?
chk "droid: nonzero exit above the autonomy level is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- auggie (prompt via @file)
fake auggie 'for a in "$@"; do case "$a" in @*) cp "${a#@}" "$FAKE_STDIN" ;; esac; done
case "${FAKE_MODE:-ok}" in
  ok) echo "AUGGIE-OK" ;;
  fail) echo "request failed" >&2; exit 1 ;;
esac'
lane auggie; rc=$?
chk "auggie ro: --print, -w, --tools read,grep,find,ls" '[ $rc -eq 0 ] && has --print && has -w && has --tools && has read,grep,find,ls'
chk "auggie ro: no --permission allow rules" 'lacks --permission'
chk "auggie: the brief reaches the CLI through the @file" 'grep -q "Say PONG" "$T/stdin"'
chk "auggie: plain answer extracted" 'status ok && [ "$(answer)" = AUGGIE-OK ]'
rwlane auggie
chk "auggie rw: --permission allow rules, no --tools" 'has --permission && has bash:allow && has edit:allow && has write:allow && lacks --tools'
FAKE_MODE=fail lane auggie; rc=$?
chk "auggie: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- kiro (binary: kiro-cli, prompt on stdin)
fake kiro-cli 'case "${FAKE_MODE:-ok}" in
  ok) printf "\033[32mKIRO-OK\033[0m\n" ;;
  mode) echo "mode \"spec\" is not offered by this session, stopping (exit 4)" >&2; exit 4 ;;
esac'
lane kiro; rc=$?
chk "kiro ro: chat --v3 --no-interactive, trust only read tools" '[ $rc -eq 0 ] && has chat && has --v3 && has --no-interactive && has --trust-tools=read_file,grep_search'
chk "kiro ro: no --trust-all-tools; brief on stdin" 'lacks --trust-all-tools && grep -q "Say PONG" "$T/stdin"'
chk "kiro: plain answer extracted, colors removed" 'status ok && [ "$(answer)" = KIRO-OK ]'
rwlane kiro
chk "kiro rw: --trust-all-tools, no --trust-tools" 'has --trust-all-tools && lacks --trust-tools=read_file,grep_search'
FAKE_MODE=mode lane kiro; rc=$?
chk "kiro: exit 4 (mode not offered) is failed and the message is kept" '[ $rc -eq 3 ] && status failed && grep -q "not offered by this session" "$T/out"'

# ---------------------------------------------------------------- cline (stdin, NDJSON)
fake cline 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"ts\":1,\"type\":\"agent_event\",\"event\":{\"type\":\"done\",\"reason\":\"completed\",\"text\":\"inner\",\"iterations\":1}}"
      echo "{\"ts\":2,\"type\":\"run_result\",\"finishReason\":\"completed\",\"iterations\":1,\"text\":\"CLINE-OK\"}" ;;
  aborted) echo "{\"ts\":1,\"type\":\"run_aborted\"}" ;;
  fail) echo "provider error" >&2; exit 1 ;;
  unauth) echo "{\"ts\":1,\"type\":\"error\",\"message\":\"Unauthorized: Please make sure you are using the latest version of Cline and re-authenticate your Cline account.\"}" >&2; exit 1 ;;
esac'
lane cline; rc=$?
chk "cline ro: --json, -c, --plan, --auto-approve false" '[ $rc -eq 0 ] && has --json && has -c && has --plan && has --auto-approve && has false'
chk "cline ro: no --yolo, never --zen; brief on stdin plus a short argument (--json refuses stdin alone)" 'lacks --yolo && lacks -y && lacks --zen && grep -q "Say PONG" "$T/stdin" && has "Follow the instructions given on stdin."'
chk "cline: the run_result text is the answer" 'status ok && [ "$(answer)" = CLINE-OK ]'
rwlane cline
chk "cline rw: --yolo, no --plan" 'has --yolo && lacks --plan && lacks --zen'
FAKE_MODE=aborted lane cline; rc=$?
chk "cline: run_aborted with no text is an empty answer" '[ $rc -eq 5 ] && status empty'
FAKE_MODE=fail lane cline; rc=$?
chk "cline: nonzero exit is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=unauth lane cline; rc=$?
chk "cline: real signed-out text is auth (exit 7)" '[ $rc -eq 7 ] && status auth'

# ---------------------------------------------------------------- kilo
fake kilo 'case "${FAKE_MODE:-ok}" in
  ok) echo "KILO-OK" ;;
  noanswer) echo "run ended without an assistant message; the model returned no output" >&2; exit 1 ;;
  timeout) echo "task exceeded time limit" >&2; exit 124 ;;
esac'
lane kilo -m kilo/some-model; rc=$?
chk "kilo ro: run, --dir, --format default, model" '[ $rc -eq 0 ] && has run && has --dir && has --format && has default && has -m && has kilo/some-model'
chk "kilo ro: no --auto" 'lacks --auto'
chk "kilo: plain answer extracted" 'status ok && [ "$(answer)" = KILO-OK ]'
rwlane kilo
chk "kilo rw: --auto" 'has --auto'
FAKE_MODE=noanswer lane kilo; rc=$?
chk "kilo: run ended without an assistant message is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=timeout lane kilo; rc=$?
chk "kilo: its own exit 124 is a timeout" '[ $rc -eq 4 ] && status timeout'

# ---------------------------------------------------------------- vibe (stdin, -p last)
fake vibe 'case "${FAKE_MODE:-ok}" in
  ok) echo "VIBE-OK" ;;
  limit) echo "turn limit reached" >&2; exit 3 ;;
  usage) echo "usage error: bad arguments" >&2; exit 1 ;;
esac'
lane vibe --max-turns 7 -t 100; rc=$?
chk "vibe ro: --output text, --approval-policy accept-edits" '[ $rc -eq 0 ] && has --output && has text && has --approval-policy && has accept-edits'
chk "vibe ro: no --auto-approve, -p is the last argument, brief on stdin" 'lacks --auto-approve && lacks --yolo && [ "$(tail -n 1 "$T/args")" = -p ] && grep -q "Say PONG" "$T/stdin"'
chk "vibe: --max-turns and --time-limit (timeout minus 20) are wired" 'has --max-turns && has 7 && has --time-limit && has 80'
chk "vibe: plain answer extracted" 'status ok && [ "$(answer)" = VIBE-OK ]'
lane vibe
chk "vibe: no --max-turns unless given" 'lacks --max-turns'
rwlane vibe
chk "vibe rw: --auto-approve, no --approval-policy" 'has --auto-approve && lacks --approval-policy'
FAKE_MODE=limit lane vibe; rc=$?
chk "vibe: exit 3 (stopped without finishing) is failed" '[ $rc -eq 3 ] && status failed'
FAKE_MODE=usage lane vibe; rc=$?
chk "vibe: exit 1 (usage error) is failed" '[ $rc -eq 3 ] && status failed'

# ---------------------------------------------------------------- pi
fake pi 'case "${FAKE_MODE:-ok}" in
  ok) echo "PI-OK" ;;
  fail) echo "no API key for provider" >&2; exit 1 ;;
esac'
lane pi -m sonnet:high; rc=$?
chk "pi ro: --print, --tools read,grep,find,ls, --no-mcp, model" '[ $rc -eq 0 ] && has --print && has --tools && has read,grep,find,ls && has --no-mcp && has --model && has sonnet:high'
chk "pi ro: the prompt follows --" 'grep -qx -- "--" "$T/args" && grep -q "READ-ONLY LANE" "$T/args"'
chk "pi: plain answer extracted" 'status ok && [ "$(answer)" = PI-OK ]'
rwlane pi
chk "pi rw: no --tools allowlist (default tools edit)" 'lacks --tools && lacks --no-mcp'
FAKE_MODE=fail lane pi; rc=$?
chk "pi: a missing key is auth (exit 7)" '[ $rc -eq 7 ] && status auth'

# ---------------------------------------------------------------- all ten are listed
list="$(PATH="$T/bin:$PATH" bash "$HERE/mmo-run" --list)"
for p in amp kiro vibe; do
  chk "--list shows $p, checked from docs" 'printf "%s
" "$list" | grep -E "^$p +" | grep -q "docs-"'
done
for p in droid auggie cline kilo pi; do
  chk "--list shows $p, flags checked against the real help" 'printf "%s
" "$list" | grep -E "^$p +" | grep -q "help-"'
done
chk "--list shows copilot, checked by a real run" 'printf "%s
" "$list" | grep -E "^copilot +" | grep -q "2026-11-28"'

chk "--list shows cursor, checked by a real run" 'printf "%s\n" "$list" | grep -E "^cursor +" | grep -q "2026-11-28"'
echo; echo "$pass passed, $fail failed"
[ $fail -eq 0 ]
