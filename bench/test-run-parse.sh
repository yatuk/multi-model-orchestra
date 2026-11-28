#!/usr/bin/env bash
# Offline test for how bench/run.sh reads a lane spec (provider:model[:effort]). It goes through
# --dry-run, so no model is called and no results folder is written.
# Run: bash bench/test-run-parse.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Never read the real key file.
export MMO_KEYS_FILE="$(mktemp -u)-none"
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; echo "    got: $got"; fail=1; }
dry() { bash "$HERE/run.sh" --dry-run "$1"; }
check() { # name, spec, provider, model, effort
  got="$(dry "$2")"
  if [ "$(printf '%s
' "$got" | head -1)" = "lane=$2 provider=$3 model=$4 effort=$5" ]      && printf '%s
' "$got" | grep -qx "  bugfix=$6"; then ok "$1"; else bad "$1"; fi
}
check "plain codex lane with effort"       codex:gpt-6.1-sol:medium            codex gpt-6.1-sol medium run
check "effort is optional"                 kimi:kimi-code/k3.1-pro             kimi  kimi-code/k3.1-pro medium run
check "slash model, no effort"             deepseek:deepseek/deepseek-flash    deepseek deepseek/deepseek-flash medium run
check "api model with a free tag"   api:openrouter:google/gemma-4-31b-it:free  api openrouter:google/gemma-4-31b-it:free medium skip
check "api model ends in a size tag"       api:ollama:qwen3:8b                 api ollama:qwen3:8b medium skip
check "api model with an effort"           api:ollama:qwen3:8b:high            api ollama:qwen3:8b high skip
check "xhigh and max are efforts"          codex:gpt-x:xhigh                   codex gpt-x xhigh run
check "minimal and none are efforts"       api:openai:gpt-x:minimal            api openai:gpt-x minimal skip
check "a model named like no effort"       codex:gpt-x:turbo                   codex gpt-x:turbo medium run
check "provider only"                      codex                               codex "" medium run

got="$(DRY=1 bash "$HERE/run.sh" codex:m:low api:o:m)"
if [ "$(printf '%s
' "$got" | grep -c '^lane=')" = 2 ] && printf '%s
' "$got" | grep -q "^lane=api:o:m provider=api model=o:m effort=medium"; then ok "DRY=1 and several lanes"; else bad "DRY=1 and several lanes"; fi

d="$(mktemp -d)"; got="$(BENCH_OUT="$d/never" bash "$HERE/run.sh" --dry-run codex:m)"
if [ ! -e "$d/never" ]; then ok "dry run writes no results folder"; else bad "dry run writes no results folder"; fi
rm -rf "$d"

# BENCH_TASKS selection: only the named tasks are listed; service is opt-in; unknown names are refused
got="$(BENCH_TASKS="service spec" bash "$HERE/run.sh" --dry-run codex:m)"
if [ "$(printf '%s
' "$got" | tail -n +2)" = "$(printf '  service=run
  spec=run')" ]; then ok "BENCH_TASKS selects tasks"; else bad "BENCH_TASKS selects tasks"; fi
got="$(bash "$HERE/run.sh" --dry-run codex:m)"
if ! printf '%s
' "$got" | grep -q service && [ "$(printf '%s
' "$got" | grep -c '^  ')" = 6 ]; then ok "default list has six tasks, no service"; else bad "default list has six tasks, no service"; fi
got="$(BENCH_TASKS="bogus" bash "$HERE/run.sh" --dry-run codex:m 2>&1)"; rc=$?
if [ $rc = 2 ] && printf '%s' "$got" | grep -q "unknown task bogus"; then ok "unknown task is refused"; else bad "unknown task is refused"; fi

# a lane without tools skips every write task and still runs the answer tasks
got="$(BENCH_TASKS="bugfix multifile refactor service reasoning bulk spec" bash "$HERE/run.sh" --dry-run api:ollama:qwen3:8b)"
want_out="$(printf '%s
' '  bugfix=skip' '  reasoning=run' '  bulk=run' '  multifile=skip' '  refactor=skip' '  service=skip' '  spec=run')"
if [ "$(printf '%s
' "$got" | tail -n +2)" = "$want_out" ]; then ok "notools lane skips all write tasks"; else bad "notools lane skips all write tasks"; fi
got="$(BENCH_TASKS="multifile bulk" bash "$HERE/run.sh" --dry-run api:ollama:qwen3:8b)"
if [ "$(printf '%s
' "$got" | tail -n +2)" = "$(printf '  bulk=run
  multifile=skip')" ]; then ok "notools skip combines with BENCH_TASKS"; else bad "notools skip combines with BENCH_TASKS"; fi
exit $fail
