#!/usr/bin/env bash
# Offline test for mmo-run itself: fake CLIs on PATH, a tiny git repo, no model calls.
# Run: bash skills/orchestra/scripts/test-mmo-run.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; [ -f "$T/out" ] && sed 's/^/    /' "$T/out"; fail=1; }
run() { PATH="$T/bin:$PATH" bash "$HERE/mmo-run" "$@" --out "$T/out" 2> "$T/log"; }
header() { head -1 "$T/out"; }
# Never read the real key file; tests that need one point MMO_KEYS_FILE at a temp file.
export MMO_KEYS_FILE="$T/no-such-keys.env"

mkdir -p "$T/bin"
# A fake CLI that behaves as FAKE_MODE says. It answers in the shape of the lane it stands in for.
fake() { # name, body
  printf '#!/bin/sh\n%s\n' "$2" > "$T/bin/$1"; chmod +x "$T/bin/$1"
}
fake grok 'case "${FAKE_MODE:-ok}" in
  ok) echo "{\"text\": \"PONG\", \"sessionId\": \"s1\"}" ;;
  hang) sleep 60 ;;
  quiet) echo starting; sleep 60 ;;
  edit) echo changed > lane-file.txt; echo "{\"text\": \"DONE\"}" ;;
  commit) echo c > c.txt; git add c.txt; git -c user.email=l@example.com -c user.name=lane commit -qm lane; echo "{\"text\": \"DONE\"}" ;;
  args) printf "%s\n" "$@" > "$FAKE_ARGS"; echo "{\"text\": \"ok\"}" ;;
  keycheck) if [ -n "${MMO_TEST_KEY:-}" ]; then k=present; else k=absent; fi; echo "{\"text\": \"KEY=$k\"}" ;;
  loop) i=0; while [ $i -lt 6 ]; do i=$((i+1)); echo "{\"type\":\"tool_call\",\"name\":\"read\",\"input\":{\"path\":\"a\"},\"id\":$i,\"ts\":$i}"; done; sleep 60 ;;
  alt) i=0; while [ $i -lt 6 ]; do i=$((i+1)); echo "{\"type\":\"tool_call\",\"name\":\"read\",\"input\":{\"path\":\"a\"},\"id\":$i}"; echo "{\"type\":\"tool_call\",\"name\":\"read\",\"input\":{\"path\":\"b\"},\"id\":$i}"; done; sleep 60 ;;
  texts) i=0; while [ $i -lt 6 ]; do i=$((i+1)); echo "{\"type\":\"text\",\"text\":\"thinking\",\"id\":$i}"; done; sleep 60 ;;
  jsonerr) echo "{\"error\": {\"message\": \"boom\"}}" ;;
esac'
fake kimi 'echo x > sneaky.txt; echo "{\"role\": \"assistant\", \"content\": \"read it\"}"'

git init -q "$T/main"; cd "$T/main" || exit 1
git config user.email t@example.com; git config user.name t; git config core.autocrlf false
echo one > a.txt; git add . && git commit -qm init
git worktree add -q "$T/wt" -b lane/x
echo "Say PONG." > "$T/brief"

run grok --brief "$T/brief" -C "$T/main"
if [ $? -eq 0 ] && header | grep -q "status=ok" && sed -n 2p "$T/out" | grep -qx PONG; then ok "json answer extracted"; else bad "json answer extracted"; fi

FAKE_MODE=jsonerr run grok --brief "$T/brief" -C "$T/main"
if [ $? -eq 3 ] && header | grep -q "status=failed"; then ok "error inside JSON is a failed lane"; else bad "error inside JSON is a failed lane"; fi

FAKE_MODE=hang run grok --brief "$T/brief" -C "$T/main" -t 2
if [ $? -eq 4 ] && header | grep -q "status=timeout"; then ok "timeout"; else bad "timeout"; fi

FAKE_MODE=quiet run grok --brief "$T/brief" -C "$T/main" -t 60 --idle 5
if [ $? -eq 4 ] && header | grep -q "status=stalled"; then ok "idle lane is stalled"; else bad "idle lane is stalled"; fi

run grok --mode rw --brief "$T/brief" -C "$T/main"
if [ $? -eq 2 ]; then ok "rw refused outside a worktree"; else bad "rw refused outside a worktree"; fi

FAKE_MODE=edit run grok --mode rw --brief "$T/brief" -C "$T/wt" --base lane/x
if [ $? -eq 0 ] && header | grep -q "changed=1" && header | grep -q "base=" && ! header | grep -q committed; then ok "rw header has base and changed"; else bad "rw header has base and changed"; fi

FAKE_MODE=commit run grok --mode rw --brief "$T/brief" -C "$T/wt"
if header | grep -q "committed=yes"; then ok "a lane that commits is flagged"; else bad "a lane that commits is flagged"; fi

echo two > a.txt; git commit -qam "conductor moved on"
run grok --mode rw --brief "$T/brief" -C "$T/wt" --base master 2>/dev/null || run grok --mode rw --brief "$T/brief" -C "$T/wt" --base main
if [ $? -eq 9 ] && header | grep -q "status=base"; then ok "stale worktree refused by --base"; else bad "stale worktree refused by --base"; fi

FAKE_ARGS="$T/args" FAKE_MODE=args run grok --brief "$T/brief" -C "$T/main" --max-turns 7 -m grok-x
if grep -qx -- "--max-turns" "$T/args" && grep -qx 7 "$T/args" && grep -qx "read_file,grep,list_dir" "$T/args" && ! grep -qx -- "--always-approve" "$T/args"; then ok "read-only flags and max turns reach the CLI"; else bad "read-only flags and max turns reach the CLI"; fi

# The claude adapter: a writing lane must be able to run commands (Bash allowed), and the prompt must stay the
# last argument (the tool list takes several values and would swallow it). Read-only offers no Bash.
fake claude 'printf "%s\n" "$@" > "$FAKE_ARGS"; echo "{\"result\": \"ok\"}"'
echo "Say PONG." > "$T/brief"
git -C "$T/wt" checkout -q -- . 2>/dev/null; git -C "$T/wt" merge -q --ff-only master >/dev/null 2>&1 || git -C "$T/wt" merge -q --ff-only main >/dev/null 2>&1
FAKE_ARGS="$T/cargs" run claude --mode rw --brief "$T/brief" -C "$T/wt" -m sonnet
if grep -qx -- "--allowedTools" "$T/cargs" && grep -qx "Bash" "$T/cargs" && grep -qx -- "--permission-mode" "$T/cargs" \
   && grep -qx "acceptEdits" "$T/cargs" && [ "$(tail -n +$(( $(wc -l < "$T/cargs") - 0 )) "$T/cargs" | head -1)" != "" ] \
   && [ "$(tail -n 1 "$T/cargs")" = "$(cat "$T/brief")" ]; then ok "claude rw: Bash and acceptEdits offered, prompt still last"; else bad "claude rw arguments"; sed 's/^/    /' "$T/cargs"; fi
FAKE_ARGS="$T/cargs" run claude --mode ro --brief "$T/brief" -C "$T/main" -m sonnet
if ! grep -qx "Bash" "$T/cargs" && ! grep -qx -- "--allowedTools" "$T/cargs" && grep -qx -- "--tools" "$T/cargs" && grep -qx "Grep" "$T/cargs"; then ok "claude ro: no Bash offered"; else bad "claude ro arguments"; fi

run kimi --brief "$T/brief" -C "$T/main"
if [ $? -eq 0 ] && header | grep -q "ro_violation=yes" && [ ! -e "$T/main/sneaky.txt" ] && [ "$(git worktree list | wc -l)" -eq 2 ]; then ok "throwaway read-only run discards writes"; else bad "throwaway read-only run discards writes"; fi

run nosuchlane --brief "$T/brief"
if [ $? -eq 2 ]; then ok "unknown provider"; else bad "unknown provider"; fi
run ../codex --brief "$T/brief"
if [ $? -eq 2 ]; then ok "provider name cannot be a path"; else bad "provider name cannot be a path"; fi

listing="$(PATH="$T/bin:$PATH" bash "$HERE/mmo-run" --list)"
if printf '%s
' "$listing" | grep -q "^grok "; then ok "--list"; else bad "--list"; fi

# --- key file: every lane sees the keys, the out file never holds the value ---
printf 'MMO_TEST_KEY=sk-fake-VALUE-9876
OTHER=x
' > "$T/keys.env"
MMO_KEYS_FILE="$T/keys.env" FAKE_MODE=keycheck run grok --brief "$T/brief" -C "$T/main"
if [ $? -eq 0 ] && sed -n 2p "$T/out" | grep -q "^KEY=present" && ! grep -q "sk-fake-VALUE" "$T/out" "$T/log"; then ok "a lane sees a key from the key file"; else bad "a lane sees a key from the key file"; fi
FAKE_MODE=keycheck run grok --brief "$T/brief" -C "$T/main"
if sed -n 2p "$T/out" | grep -q "^KEY=absent"; then ok "no key file, no key"; else bad "no key file, no key"; fi
MMO_KEYS_FILE="$T/keys.env" PATH="$T/bin:$PATH" bash "$HERE/mmo-run" --list > "$T/list.txt" 2>&1
if ! grep -q "sk-fake-VALUE" "$T/list.txt" && [ -z "${MMO_TEST_KEY:-}" ]; then ok "--list neither prints nor exports a key"; else bad "--list leaks a key"; fi
# A key file that exists but does not source: one warning naming the file, never its contents; the run goes on.
printf 'MMO_TEST_KEY=sk-secret-SYNTAX-1111
if then ((( fi
' > "$T/badkeys.env"
MMO_KEYS_FILE="$T/badkeys.env" FAKE_MODE=ok run grok --brief "$T/brief" -C "$T/main"; rc=$?
if [ $rc -eq 0 ] && [ "$(grep -c 'could not load key file' "$T/log")" -eq 1 ] && grep -q "badkeys.env" "$T/log"    && ! grep -q "SYNTAX-1111\|if then" "$T/log" "$T/out"; then ok "unsourceable key file: one warning, no contents, run continues"; else bad "unsourceable key file warning"; fi

# --- --list layout ---
PATH="$T/bin:$PATH" bash "$HERE/mmo-run" --list > "$T/list.txt" 2>&1
hdr="$(head -1 "$T/list.txt")"
row="$(grep "^claude-deepseek " "$T/list.txt")"
if [ "$(printf '%s' "$hdr" | awk '{print index($0,"CLI")}')" = 18 ] && [ "$(printf '%s' "$hdr" | awk '{print index($0,"FAMILY")}')" = 26 ]    && [ "$(printf '%s' "$hdr" | awk '{print index($0,"DEFAULT MODEL")}')" = 61 ]    && [ "$(printf '%s' "$row" | cut -c17)" = " " ] && [ "$(printf '%s' "$row" | cut -c18-24 | tr -d ' ')" != "" ]    && [ "$(printf '%s' "$row" | cut -c25)" = " " ] && [ "$(printf '%s' "$row" | cut -c26-33)" = "deepseek" ]; then ok "--list columns line up"; else bad "--list columns line up"; fi
PATH="$T/bin:$PATH" bash "$HERE/mmo-run" --list 2> "$T/pipe.err" | head -1 > /dev/null
if [ ! -s "$T/pipe.err" ]; then ok "--list into head prints no error text"; else bad "--list into head prints no error text"; fi

# --- --loop ---
FAKE_MODE=loop run grok --brief "$T/brief" -C "$T/main" -t 60 --loop 5
if [ $? -eq 4 ] && header | grep -q "status=looping"; then ok "the same tool call 6 times is looping at --loop 5"; else bad "looping detected"; fi
FAKE_MODE=alt run grok --brief "$T/brief" -C "$T/main" -t 12 --loop 5
if header | grep -q "status=timeout"; then ok "alternating calls are not a loop"; else bad "alternating calls are not a loop"; fi
FAKE_MODE=texts run grok --brief "$T/brief" -C "$T/main" -t 12 --loop 5
if header | grep -q "status=timeout"; then ok "identical text events are not a loop"; else bad "identical text events are not a loop"; fi
FAKE_MODE=loop run grok --brief "$T/brief" -C "$T/main" -t 12 --loop 0
if header | grep -q "status=timeout"; then ok "--loop 0 never fires"; else bad "--loop 0 never fires"; fi
run grok --brief "$T/brief" -C "$T/main" --loop x
if [ $? -eq 2 ]; then ok "--loop needs a number"; else bad "--loop needs a number"; fi

# mmo_loop.py normalizer, on its own
norm() { printf '%s
' "$1" | "$PY" "$HERE/mmo_loop.py" norm; }
n1="$(norm '{"type":"tool_call","name":"read","input":{"p":"a"},"id":1,"ts":5,"duration_ms":7}')"
n2="$(norm '{"ts":9,"id":2,"input":{"p":"a"},"name":"read","type":"tool_call","duration_ms":99}')"
if [ -n "$n1" ] && [ "$n1" = "$n2" ]; then ok "normalizer drops ids, times and key order"; else bad "normalizer drops ids"; fi
n3="$(norm '{"type":"tool_call","name":"read","input":{"p":"b"},"id":1}')"
if [ -n "$n3" ] && [ "$n3" != "$n1" ]; then ok "normalizer keeps a different argument"; else bad "normalizer different argument"; fi
if [ -z "$(norm '{"type":"text","text":"hi"}')" ] && [ -z "$(norm 'plain text line')" ] && [ -z "$(norm '{"type":"thinking","thinking":"x"}')" ] && [ -z "$(norm '{broken')" ]; then ok "normalizer ignores text, thinking, plain and broken lines"; else bad "normalizer ignores non-actions"; fi
if [ -n "$(norm '{"error":{"message":"boom"}}')" ] && [ -n "$(norm '{"type":"error","message":"x"}')" ] && [ -n "$(norm '{"tool_name":"bash","arguments":"ls"}')" ] && [ -n "$(norm '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"t1","name":"Read","input":{"f":"a"}}]}}')" ]; then ok "normalizer recognizes errors and tool calls"; else bad "normalizer recognizes actions"; fi
printf '%s
' '{"type":"tool_call","name":"r","input":{},"id":1}' '{"type":"text","text":"x"}' '{"type":"tool_call","name":"r","input":{},"id":2}' '{"type":"tool_call","name":"r","input":{},"id":3}' > "$T/stream"
"$PY" "$HERE/mmo_loop.py" 3 "$T/stream"; a=$?; "$PY" "$HERE/mmo_loop.py" 4 "$T/stream"; b=$?
if [ $a -eq 10 ] && [ $b -eq 0 ]; then ok "text between identical calls does not reset the count"; else bad "count across text events ($a $b)"; fi
exit $fail
