#!/usr/bin/env bash
# Offline test for mmo-advise: a fake auggie CLI stands in for the advisor lane, no model calls.
# The scripts are copied to a temp folder so a fake mmo-roster can sit next to them.
# Run: bash skills/orchestra/scripts/test-mmo-advise.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; [ -f "$T/stdout" ] && sed 's/^/    out: /' "$T/stdout"; [ -f "$T/stderr" ] && sed 's/^/    err: /' "$T/stderr"; fail=1; }

mkdir -p "$T/orch" "$T/bin" "$T/pathbin"
cp -R "$HERE" "$T/orch/scripts"; cp -R "$HERE/../templates" "$T/orch/templates"
rm -f "$T/orch/scripts/mmo-roster"
S="$T/orch/scripts"

# The fake advisor: records the brief and its arguments, prints FAKE_ANSWER, fails as told.
cat > "$T/bin/auggie" <<'EOF'
#!/bin/sh
printf '%s\n' "$@" > "$FAKE_ARGS"
f="$2"; cp "${f#@}" "$FAKE_PROMPT"
[ -n "${FAKE_SLEEP:-}" ] && sleep "$FAKE_SLEEP"
[ -n "${FAKE_ERR:-}" ] && echo "$FAKE_ERR" >&2
[ -n "${FAKE_ANSWER:-}" ] && cat "$FAKE_ANSWER"
exit "${FAKE_EXIT:-0}"
EOF
chmod +x "$T/bin/auggie"
# A fake llm CLI: the llm lane is READ-ONLY kind notools in mmo-run --list. It reads the prompt from stdin.
cat > "$T/bin/llm" <<'EOF'
#!/bin/sh
printf '%s\n' "$@" > "$FAKE_ARGS"
cat > "$FAKE_PROMPT"
[ -n "${FAKE_ANSWER:-}" ] && cat "$FAKE_ANSWER"
exit "${FAKE_EXIT:-0}"
EOF
chmod +x "$T/bin/llm"
export FAKE_ARGS="$T/args" FAKE_PROMPT="$T/prompt"
unset MMO_ADVISOR MMO_LOG MMO_ADVISE_BUDGET MMO_SESSION MMO_ADVISE_STRICT MMO_ADVISE_MAX_CHARS MMO_ADVISE_BUDGET_CHARS

git init -q "$T/repo"; cd "$T/repo" || exit 1
git config user.email t@example.com; git config user.name t; git config core.autocrlf false
echo one > a.txt; git add . && git commit -qm init

echo "Task: add a retry to the uploader. Approach: wrap upload() in a loop of three tries." > "$T/q"
printf 'PROCEED\nThe loop is bounded (q line 1).\n' > "$T/a-proceed"
printf 'CHANGE: back off between tries\nThree immediate tries hit the same 429.\n' > "$T/a-change"
printf 'STOP: the uploader is not idempotent\nA retry after a timeout uploads twice.\n' > "$T/a-stop"
printf 'Here is my view.\n\n**Verdict: CHANGE: add jitter**\n- reason one\n' > "$T/a-md"
printf 'I think the approach is broadly fine but there are some concerns.\nMore prose.\n' > "$T/a-none"
{ echo PROCEED; for i in $(seq 1 30); do echo "reason $i"; done; } > "$T/a-long"
export FAKE_ANSWER="$T/a-proceed"

# adv ARGS... : run mmo-advise with the fake on PATH; sets rc
adv() { rm -f "$T/prompt" "$T/args"; PATH="$T/bin:$T/pathbin:$PATH" bash "$S/mmo-advise" -C "$T/repo" "$@" > "$T/stdout" 2> "$T/stderr"; rc=$?; }
has() { grep -qF -- "$2" "$1"; }

# Briefs per moment
MMO_SESSION=b adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && has "$T/prompt" "Moment: plan" && has "$T/prompt" "What is wrong with this approach" \
   && has "$T/prompt" "What would you do instead" && has "$T/prompt" "What will bite later" \
   && has "$T/prompt" "wrap upload() in a loop" && has "$T/prompt" "do not ask me questions" \
   && has "$T/prompt" "READ-ONLY LANE"; then ok "plan brief has its sections"; else bad "plan brief has its sections"; fi

{ echo "FIRSTLINE of the log"; for i in $(seq 1 800); do echo "noise line $i padding padding padding"; done; echo "Error: LASTLINE connection reset"; } > "$T/build.log"
MMO_SESSION=b adv --moment stuck --question "$T/q" --evidence "$T/build.log" --lane auggie
if [ $rc -eq 0 ] && has "$T/prompt" "Moment: stuck" && has "$T/prompt" "most likely cause" && has "$T/prompt" "one experiment" \
   && has "$T/prompt" "LASTLINE" && ! has "$T/prompt" "FIRSTLINE" && has "$T/prompt" "the tail is kept"; then
  ok "stuck brief keeps the log tail with a truncation note"; else bad "stuck brief keeps the log tail with a truncation note"; fi

{ echo "SPECSTART the spec"; for i in $(seq 1 800); do echo "spec line $i padding padding padding"; done; echo "SPECEND"; } > "$T/spec.md"
MMO_SESSION=b adv --moment plan --question "$T/q" --evidence "$T/spec.md" --lane auggie
if [ $rc -eq 0 ] && has "$T/prompt" "SPECSTART" && ! has "$T/prompt" "SPECEND" && has "$T/prompt" "the head is kept"; then
  ok "a spec keeps its head"; else bad "a spec keeps its head"; fi

MMO_SESSION=b adv --moment stuck --question "$T/q" --lane auggie
if [ $rc -eq 2 ]; then ok "stuck without the error is refused"; else bad "stuck without the error is refused"; fi

for i in $(seq 1 2000); do echo "changed line $i of the big file"; done > big.txt; git add big.txt
echo two > a.txt
MMO_SESSION=b adv --moment done --question "$T/q" --diff HEAD --lane auggie
if [ $rc -eq 0 ] && has "$T/prompt" "Moment: done" && has "$T/prompt" "strongest reason it is not done" \
   && has "$T/prompt" "git diff HEAD" && has "$T/prompt" "+changed line 1 " && has "$T/prompt" "characters of the diff; the rest was cut"; then
  ok "done attaches a truncated diff"; else bad "done attaches a truncated diff"; fi
git reset -q --hard

# Verdicts
FAKE_ANSWER="$T/a-proceed" MMO_SESSION=v adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && [ "$(head -1 "$T/stdout")" = PROCEED ] && [ "$(wc -l < "$T/stdout")" -eq 2 ]; then ok "PROCEED"; else bad "PROCEED"; fi
FAKE_ANSWER="$T/a-change" MMO_SESSION=v adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && [ "$(head -1 "$T/stdout")" = "CHANGE: back off between tries" ]; then ok "CHANGE"; else bad "CHANGE"; fi
FAKE_ANSWER="$T/a-stop" MMO_SESSION=v adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && [ "$(head -1 "$T/stdout")" = "STOP: the uploader is not idempotent" ]; then ok "STOP"; else bad "STOP"; fi
FAKE_ANSWER="$T/a-md" MMO_SESSION=v adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && [ "$(head -1 "$T/stdout")" = "CHANGE: add jitter" ] && has "$T/stdout" "dropped 1 line(s) before the verdict"; then
  ok "markdown around the verdict is tolerated and noted"; else bad "markdown around the verdict is tolerated and noted"; fi
FAKE_ANSWER="$T/a-none" MMO_SESSION=v2 adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 11 ] && [ ! -s "$T/stdout" ] && has "$T/stderr" "no verdict line"; then ok "no verdict is unusable"; else bad "no verdict is unusable"; fi
FAKE_ANSWER="$T/a-long" MMO_SESSION=v2 adv --moment plan --question "$T/q" --lane auggie --max-lines 5 --out "$T/advice.md"
if [ $rc -eq 0 ] && [ "$(wc -l < "$T/stdout")" -eq 7 ] && has "$T/stdout" "reason 5" && ! has "$T/stdout" "reason 6" \
   && has "$T/stdout" "trimmed 25 line(s) over the limit of 5" && head -1 "$T/advice.md" | grep -q "verdict=PROCEED trimmed=yes"; then
  ok "long answer trimmed to max-lines with a note"; else bad "long answer trimmed to max-lines with a note"; fi

# Budget
okn=0
for i in 1 2 3 4 5 6; do MMO_SESSION=bud adv --moment plan --question "$T/q" --lane auggie; [ $rc -eq 0 ] && okn=$((okn+1)); done
MMO_SESSION=bud adv --moment plan --question "$T/q" --lane auggie
if [ $okn -eq 6 ] && [ $rc -eq 10 ] && [ ! -e "$T/prompt" ] && has "$T/stderr" "budget used up: 6 of 6"; then ok "budget refuses the 7th call with exit 10"; else bad "budget refuses the 7th call with exit 10 (ok=$okn rc=$rc)"; fi
MMO_SESSION=bud MMO_ADVISE_BUDGET=7 adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ]; then ok "MMO_ADVISE_BUDGET raises it"; else bad "MMO_ADVISE_BUDGET raises it"; fi

# Failed lanes pass their status through and never become advice
FAKE_EXIT=1 FAKE_ERR="Error: 429 rate limit exceeded" FAKE_ANSWER="" MMO_SESSION=f adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 6 ] && has "$T/stderr" "status=limit exit=6" && [ ! -s "$T/stdout" ] && grep -q '"f": 0' "$T/repo/.mmo/advise.json"; then
  ok "limit passes through and the call is given back"; else bad "limit passes through and the call is given back"; fi
FAKE_EXIT=1 FAKE_ERR="segfault" FAKE_ANSWER="$T/a-proceed" MMO_SESSION=f adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 3 ] && has "$T/stderr" "status=failed exit=3" && [ ! -s "$T/stdout" ]; then ok "a failed lane gives no advice"; else bad "a failed lane gives no advice"; fi
FAKE_SLEEP=5 MMO_SESSION=f adv --moment plan --question "$T/q" --lane auggie -t 1
if [ $rc -eq 4 ] && has "$T/stderr" "status=timeout"; then ok "timeout passes through"; else bad "timeout passes through"; fi

# Lane resolution
MMO_ADVISOR=nosuch:x MMO_SESSION=l adv --moment plan --question "$T/q" --lane auggie:m0
if [ $rc -eq 0 ] && grep -qx m0 "$T/args"; then ok "--lane beats MMO_ADVISOR"; else bad "--lane beats MMO_ADVISOR"; fi
MMO_ADVISOR=auggie:m1 MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 0 ] && grep -qx m1 "$T/args" && has "$T/stderr" "from MMO_ADVISOR"; then ok "MMO_ADVISOR"; else bad "MMO_ADVISOR"; fi
MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 2 ] && has "$T/stderr" "pass --lane" && has "$T/stderr" "MMO_ADVISOR"; then ok "no lane at all is a clear error"; else bad "no lane at all is a clear error"; fi
printf '#!/usr/bin/env bash\n[ "$1 $2 $3" = "ready --tier strong" ] && echo "auggie m2"\n' > "$T/pathbin/mmo-roster"; chmod +x "$T/pathbin/mmo-roster"
MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 0 ] && grep -qx m2 "$T/args" && has "$T/stderr" "from mmo-roster"; then ok "mmo-roster on PATH, 'provider model' line"; else bad "mmo-roster on PATH, 'provider model' line"; fi
printf '#!/usr/bin/env bash\necho "# ready strong lanes"\necho "auggie:m3"\necho "auggie:m4"\n' > "$S/mmo-roster"
MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 0 ] && grep -qx m3 "$T/args"; then ok "mmo-roster next to the script wins, first line"; else bad "mmo-roster next to the script wins, first line"; fi
printf '#!/usr/bin/env bash\necho "ghost:big"\n' > "$S/mmo-roster"
MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 2 ] && has "$T/stderr" "names no known provider" && [ ! -e "$T/prompt" ]; then ok "stale roster lane is refused"; else bad "stale roster lane is refused"; fi
printf '#!/usr/bin/env bash\nexit 0\n' > "$S/mmo-roster"
MMO_SESSION=l adv --moment plan --question "$T/q"
if [ $rc -eq 2 ] && has "$T/stderr" "pass --lane"; then ok "empty roster is a clear error"; else bad "empty roster is a clear error"; fi
rm -f "$S/mmo-roster" "$T/pathbin/mmo-roster"

# Secrets never leave
printf 'line one\napi_key = "sk-abcdefghijklmnopqrstuvwxyz012345"\nline three\n' > "$T/leak.log"
MMO_SESSION=s adv --moment stuck --question "$T/q" --evidence "$T/leak.log" --lane auggie
if [ $rc -eq 2 ] && [ ! -e "$T/prompt" ] && has "$T/stderr" "leak.log: 1 line(s) look like a secret" && ! has "$T/stderr" "sk-abc"; then
  ok "secret-looking evidence is refused"; else bad "secret-looking evidence is refused"; fi
printf 'commit 0123456789abcdef0123456789abcdef01234567\nid 123e4567-e89b-12d3-a456-426614174000\n' > "$T/ids.log"
MMO_SESSION=s adv --moment stuck --question "$T/q" --evidence "$T/ids.log" --lane auggie
if [ $rc -eq 0 ]; then ok "commit ids and uuids are not secrets"; else bad "commit ids and uuids are not secrets"; fi

# Scoreboard line
MMO_LOG="$T/score.jsonl" FAKE_ANSWER="$T/a-change" MMO_SESSION=g adv --moment plan --question "$T/q" --lane auggie:m9
if [ $rc -eq 0 ] && grep '"kind":"advise"' "$T/score.jsonl" | grep '"moment":"plan"' | grep '"lane":"auggie:m9"' \
   | grep '"verdict":"CHANGE"' | grep -q '"seconds":[0-9]'; then ok "MMO_LOG gets one advise line"; else bad "MMO_LOG gets one advise line"; fi

# Tools: a guarantee for notools lanes, the truth for the others
MMO_SESSION=t adv --moment plan --question "$T/q" --lane llm --out "$T/o-llm.md"
if [ $rc -eq 0 ] && head -1 "$T/o-llm.md" | grep -q 'tools="none"' && has "$T/stderr" "tools=none"; then ok "notools lane says tools=none"; else bad "notools lane says tools=none"; fi
MMO_SESSION=t adv --moment plan --question "$T/q" --lane auggie --out "$T/o-aug.md"
if [ $rc -eq 0 ] && head -1 "$T/o-aug.md" | grep -q 'tools="read-only, empty folder"' && ! head -1 "$T/o-aug.md" | grep -q 'tools="none"'; then
  ok "sandbox lane gets the truthful header"; else bad "sandbox lane gets the truthful header"; fi
MMO_SESSION=t adv --moment plan --question "$T/q" --lane auggie --strict-no-tools
if [ $rc -eq 2 ] && [ ! -e "$T/prompt" ] && has "$T/stderr" "api:<endpoint>:<model>"; then ok "--strict-no-tools refuses a lane with tools"; else bad "--strict-no-tools refuses a lane with tools"; fi
MMO_ADVISE_STRICT=1 MMO_SESSION=t adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 2 ] && [ ! -e "$T/prompt" ]; then ok "MMO_ADVISE_STRICT=1 does the same"; else bad "MMO_ADVISE_STRICT=1 does the same"; fi
MMO_SESSION=t adv --moment plan --question "$T/q" --lane llm --strict-no-tools
if [ $rc -eq 0 ]; then ok "--strict-no-tools lets a notools lane through"; else bad "--strict-no-tools lets a notools lane through"; fi
printf '#!/usr/bin/env bash\necho "auggie:m3"\necho "llm:m5"\n' > "$S/mmo-roster"
MMO_SESSION=t adv --moment plan --question "$T/q"
if [ $rc -eq 0 ] && has "$T/stderr" "advisor llm:m5 (from mmo-roster)" && has "$T/stderr" "tools=none"; then ok "roster preference picks the notools lane"; else bad "roster preference picks the notools lane"; fi
MMO_SESSION=t adv --moment plan --question "$T/q" --lane auggie:m6
if [ $rc -eq 0 ] && has "$T/stderr" "advisor auggie:m6 (from --lane)"; then ok "an explicit --lane is honored over the roster"; else bad "an explicit --lane is honored over the roster"; fi
MMO_ADVISOR=auggie:m7 MMO_SESSION=t adv --moment plan --question "$T/q"
if [ $rc -eq 0 ] && has "$T/stderr" "advisor auggie:m7 (from MMO_ADVISOR)"; then ok "MMO_ADVISOR is honored over the roster"; else bad "MMO_ADVISOR is honored over the roster"; fi
rm -f "$S/mmo-roster"

# Character cap
{ echo "PROCEED"; for i in 1 2 3 4 5 6 7 8; do echo "Reason $i is a sentence of some length that fills the line. And a second sentence follows it."; done; } > "$T/a-chars"
FAKE_ANSWER="$T/a-chars" MMO_SESSION=c adv --moment plan --question "$T/q" --lane auggie --max-chars 300 --out "$T/c.md"
body="$(grep -v '^\[mmo-advise' "$T/stdout")"
if [ $rc -eq 0 ] && [ "${#body}" -le 300 ] && [ "$(head -1 "$T/stdout")" = PROCEED ] && has "$T/stdout" "characters over the limit of 300" \
   && has "$T/stdout" "the full answer is in " && has "$T/stdout" "c.full.md]" && case "$body" in *.) true ;; *) false ;; esac \
   && [ "$(grep -c . "$T/c.full.md")" -eq 9 ] && has "$T/c.full.md" "Reason 8" && ! has "$T/stdout" "Reason 8"; then
  ok "char cap trims at a sentence end, notes it, full answer saved"; else bad "char cap trims at a sentence end, notes it, full answer saved"; fi
FAKE_ANSWER="$T/a-chars" MMO_SESSION=c adv --moment plan --question "$T/q" --lane auggie --max-chars 300
if [ $rc -eq 0 ] && has "$T/repo/.mmo/advise-plan.full.md" "Reason 8"; then ok "full answer goes to the state folder without --out"; else bad "full answer goes to the state folder without --out"; fi
FAKE_ANSWER="$T/a-proceed" MMO_SESSION=c adv --moment plan --question "$T/q" --lane auggie --out "$T/s.md"
if [ $rc -eq 0 ] && ! has "$T/stdout" "limit of" && [ "$(wc -l < "$T/stdout")" -eq 2 ] && has "$T/s.full.md" "The loop is bounded"; then ok "a short answer is untouched"; else bad "a short answer is untouched"; fi
MMO_SESSION=c adv --moment plan --question "$T/q" --lane auggie
if has "$T/prompt" "characters in" && has "$T/prompt" "total, verdict line included"; then ok "the brief tells the advisor the limit"; else bad "the brief tells the advisor the limit"; fi

# Character budget: refused before the lane is called
rm -f "$T/prompt"
MMO_SESSION=cb adv --moment plan --question "$T/q" --lane auggie --budget-chars 500
if [ $rc -eq 10 ] && [ ! -e "$T/prompt" ] && has "$T/stderr" "character budget used up" && has "$T/stderr" "500 left" && has "$T/stderr" "smaller --diff"; then
  ok "character budget refuses with exit 10 before the lane runs"; else bad "character budget refuses with exit 10 before the lane runs"; fi
MMO_SESSION=cb adv --moment plan --question "$T/q" --lane auggie --budget-chars 0
if [ $rc -eq 0 ]; then ok "--budget-chars 0 disables it"; else bad "--budget-chars 0 disables it"; fi
MMO_ADVISE_BUDGET_CHARS=3500 MMO_SESSION=cb2 adv --moment plan --question "$T/q" --lane auggie
n1=$rc; MMO_ADVISE_BUDGET_CHARS=3500 MMO_SESSION=cb2 adv --moment plan --question "$T/q" --lane auggie
n2=$rc; MMO_ADVISE_BUDGET_CHARS=3500 MMO_SESSION=cb2 adv --moment plan --question "$T/q" --lane auggie
if [ $n1 -eq 0 ] && [ $n2 -eq 0 ] && [ $rc -eq 10 ]; then ok "the env budget accumulates brief sizes across calls"; else bad "the env budget accumulates brief sizes across calls ($n1 $n2 $rc)"; fi

# Refund of count and characters when the lane never started
MMO_SESSION=rf adv --moment stuck --question "$T/q" --evidence "$T/build.log" --lane auggie
MMO_SESSION=rf adv status; before="$(grep 'characters sent' "$T/stdout")"
FAKE_EXIT=1 FAKE_ERR="Error: 429 rate limit exceeded" FAKE_ANSWER="" MMO_SESSION=rf adv --moment plan --question "$T/q" --lane auggie
r1=$rc
MMO_SESSION=rf adv status
if [ $r1 -eq 6 ] && has "$T/stdout" "consultations: 1 used of 6" && has "$T/stdout" "moments: plan 0, stuck 1, done 0" \
   && [ "$(grep 'characters sent' "$T/stdout")" = "$before" ]; then ok "a lane limit refunds the count and the characters"; else bad "a lane limit refunds the count and the characters (rc=$r1)"; fi

# status
MMO_SESSION=st adv status
if [ $rc -eq 0 ] && has "$T/stdout" "consultations: 0 used of 6, 6 left" && has "$T/stdout" "characters sent: 0 used of 60000, 60000 left" && has "$T/stdout" "moments: plan 0, stuck 0, done 0"; then
  ok "status on a fresh session"; else bad "status on a fresh session"; fi
MMO_SESSION=st adv --moment plan --question "$T/q" --lane auggie; MMO_SESSION=st adv --moment done --question "$T/q" --evidence "$T/build.log" --lane auggie
MMO_SESSION=st adv status --budget 8
if [ $rc -eq 0 ] && has "$T/stdout" "consultations: 2 used of 8, 6 left" && has "$T/stdout" "moments: plan 1, stuck 0, done 1" && grep -q "characters sent: [1-9][0-9]* used of 60000" "$T/stdout"; then
  ok "status after two consultations"; else bad "status after two consultations"; fi

# Lock: two calls at the same moment with budget 1 make exactly one consultation
rm -f "$T/p1" "$T/p2"
( PATH="$T/bin:$PATH" MMO_SESSION=lk FAKE_SLEEP=1 bash "$S/mmo-advise" -C "$T/repo" --moment plan --question "$T/q" --lane auggie --budget 1 >/dev/null 2>"$T/e1"; echo $? > "$T/p1" ) &
( PATH="$T/bin:$PATH" MMO_SESSION=lk FAKE_SLEEP=1 bash "$S/mmo-advise" -C "$T/repo" --moment plan --question "$T/q" --lane auggie --budget 1 >/dev/null 2>"$T/e2"; echo $? > "$T/p2" ) &
wait
rcs="$(sort "$T/p1" "$T/p2" | tr '\n' ' ')"
if [ "$rcs" = "0 10 " ] && grep -q '"lk": 1' "$T/repo/.mmo/advise.json"; then ok "two parallel calls with budget 1 make one consultation"; else bad "two parallel calls with budget 1 make one consultation ($rcs)"; fi
if [ ! -e "$T/repo/.mmo/advise.json.lock" ]; then ok "the lock folder is gone after a run"; else bad "the lock folder is gone after a run"; fi
mkdir "$T/repo/.mmo/advise.json.lock"; touch -d '3 minutes ago' "$T/repo/.mmo/advise.json.lock"
MMO_SESSION=stale adv --moment plan --question "$T/q" --lane auggie
if [ $rc -eq 0 ] && has "$T/stderr" "stale lock" && [ ! -e "$T/repo/.mmo/advise.json.lock" ]; then ok "a stale lock is broken with a warning"; else bad "a stale lock is broken with a warning"; fi
if "${PYBIN:-python3}" -c 'import json,sys; json.load(open(sys.argv[1]))' "$T/repo/.mmo/advise.json" 2>/dev/null \
   || python -c 'import json,sys; json.load(open(sys.argv[1]))' "$T/repo/.mmo/advise.json"; then
  ok "the state file is valid JSON"; else bad "the state file is valid JSON"; fi
if ls "$T/repo/.mmo" | grep -q '\.tmp$'; then bad "no temp file left behind"; else ok "no temp file left behind"; fi
exit $fail
