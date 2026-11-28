#!/usr/bin/env bash
# Offline test for mmo-score: hand-written JSONL logs in a temp dir, no model calls.
# Run: bash skills/orchestra/scripts/test-mmo-score.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }
S() { bash "$HERE/mmo-score" "$@"; }
has() { case "$3" in *"$2"*) ok "$1";; *) bad "$1"; printf '    wanted to contain: %s\n    got:\n%s\n' "$2" "$3";; esac; }
hasnt() { case "$3" in *"$2"*) bad "$1"; printf '    must not contain: %s\n' "$2";; *) ok "$1";; esac; }
eq() { [ "$2" = "$3" ] && ok "$1" || { bad "$1"; printf '    wanted: %s\n    got:    %s\n' "$2" "$3"; }; }
run() { printf '{"ts":"t","kind":"run","provider":"%s","model":"%s","status":"%s","seconds":%s,"task":"%s"}\n' "$@"; }
chk() { printf '{"ts":"t","kind":"check","status":"%s","seconds":1,"task":"%s"}\n' "$@"; }

# default output: the table, unchanged
L="$T/a.jsonl"
{ run codex gpt-6.1-sol ok 10 t1; chk pass t1; run deepseek deepseek-v4-pro ok 20 t2; chk fail t2; } > "$L"
out="$(S "$L")"
has "default table header" "LANE" "$out"
has "default table lane row" "codex/gpt-6.1-sol" "$out"
hasnt "default output has no share block" "FAMILY" "$out"

# log-agent
export MMO_LOG="$T/b.jsonl"
S log-agent --model sonnet --task t9 --seconds 30
S log-agent --model haiku --task t9 --status failed
eq "log-agent appends two lines" "2" "$(wc -l < "$MMO_LOG" | tr -d ' ')"
has "log-agent line shape" '"kind":"run","provider":"claude-agent","model":"sonnet"' "$(head -1 "$MMO_LOG")"
has "log-agent shows in the table" "claude-agent/sonnet" "$(S)"
S log-agent --task t9 2>/dev/null; eq "log-agent needs --model" "2" "$?"
unset MMO_LOG

# share + drift sentence
L="$T/share.jsonl"
{ for i in 1 2 3 4 5 6 7 8 9; do run claude-agent sonnet ok 10 s$i; done; run claude haiku ok 5 s10
  run codex gpt-6.1-sol ok 40 s11; run codex gpt-6.1-sol failed 10 s12; } > "$L"
out="$(S "$L" --share)"
has "share groups Claude" "Claude" "$out"
has "share counts Claude runs 10 of 12" "10" "$out"
has "share lists codex" "codex" "$out"
has "drift sentence" "Most work went to Claude although these lanes answered: codex." "$out"
{ for i in 1 2 3 4 5; do run claude-agent sonnet ok 10 s$i; done; run codex gpt-6.1-sol ok 40 s11; } > "$T/small.jsonl"
hasnt "no drift sentence under 10 runs" "Most work went" "$(S "$T/small.jsonl" --share)"
{ for i in 1 2 3 4 5 6 7 8 9 10 11; do run claude-agent sonnet ok 10 s$i; done; run codex gpt-6.1-sol failed 4 s12; } > "$T/nolane.jsonl"
hasnt "no drift sentence when external lanes never answered" "Most work went" "$(S "$T/nolane.jsonl" --share)"

# task history and escalation advice
L="$T/task.jsonl"
{ run claude-agent haiku ok 10 a; chk fail a
  run claude-agent haiku ok 10 b; chk fail b; run claude-agent haiku ok 10 b; chk fail b
  run codex gpt-6.1-sol limit 3 c
  run mystery-cli x ok 3 d; chk fail d; chk fail d
  run claude-agent opus ok 9 e; chk fail e; chk fail e
  run deepseek deepseek-v4-pro base 1 f; } > "$L"
out="$(S "$L" --task a)"
has "task lists the run" "claude-agent/haiku" "$out"
has "task counts failed checks" "failed checks: 1" "$out"
has "1 failed check: retry same tier" "retry on the same tier" "$out"
out="$(S "$L" --task b)"
has "2 failed checks: tier up" "one tier up (cheap)" "$out"
has "2 failed checks counted" "failed checks: 2" "$out"
out="$(S "$L" --task c)"
has "limit: another lane of the same tier" "another lane of the same tier (middle)" "$out"
hasnt "limit: no tier up" "one tier up" "$out"
has "unknown tier: no tier advice" "unknown tier" "$(S "$L" --task d)"
hasnt "unknown tier: no tier up" "one tier up" "$(S "$L" --task d)"
has "top tier: no tier above" "already the top tier" "$(S "$L" --task e)"
has "base: recreate the worktree" "recreate the worktree" "$(S "$L" --task f)"
has "unknown task id" "no history for task zz" "$(S "$L" --task zz)"

# routes: only lanes with >= 5 checked tasks are ranked
L="$T/routes.jsonl"
{ for i in 1 2 3 4 5; do run codex gpt-6.1-sol ok 1 x$i; chk pass x$i; done
  for i in 1 2 3 4 5; do run claude-agent sonnet ok 1 y$i; if [ $i -le 2 ]; then chk pass y$i; else chk fail y$i; fi; done
  for i in 1 2 3; do run deepseek deepseek-v4-pro ok 1 z$i; chk pass z$i; done; } > "$L"
out="$(S "$L" --routes)"
has "routes: tier heading" "middle:" "$out"
has "routes: rank 1 is codex at 5/5" "1. codex/gpt-6.1-sol" "$out"
has "routes: rank 2 is sonnet at 2/5" "2. claude-agent/sonnet" "$out"
has "routes: thin data is not ranked" "not enough data (n=3)" "$out"
hasnt "routes: thin lane has no percentage" "deepseek/deepseek-v4-pro                 3/3" "$out"

# councils
L="$T/council.jsonl"
{ for i in 1 2 3 4 5 6; do printf '{"kind":"council","lanes":3,"answered":3,"task":"c%s"}\n' $i; done; } > "$L"
S council-note --task c1 --agreed --log "$L"; S council-note --task c2 --agreed --log "$L"
S council-note --task c3 --agreed --log "$L"; S council-note --task c4 --agreed --log "$L"
out="$(S "$L" --councils)"
has "councils: counts" "councils run: 6, noted: 4 agreed, 0 split" "$out"
hasnt "councils: no advice under 5 notes" "could be used less" "$out"
S council-note --task c5 --split --log "$L"
has "councils: 4 of 5 agreed is 80%, advice appears" "could be used less" "$(S "$L" --councils)"
S council-note --task c6 --split --log "$L"
has "councils: 4 of 6 agreed, no advice" "4 agreed, 2 split" "$(S "$L" --councils)"
hasnt "councils: under 80% gives no advice" "could be used less" "$(S "$L" --councils)"
has "share includes the council line" "councils run: 6" "$(S "$L" --share)"
S council-note --task c7 --log "$L" 2>/dev/null; eq "council-note needs agreed or split" "2" "$?"

# reports
D="$T/out"; mkdir -p "$D"
{ echo '<!-- mmo provider=kimi model=k3 mode=ro status=ok exit=0 seconds=5 -->'; seq 1 60; } > "$D/long.md"
{ echo '<!-- mmo provider=codex model=gpt-6.1-sol mode=ro status=ok exit=0 seconds=5 -->'; seq 1 10; } > "$D/short.md"
{ echo '# my own notes'; seq 1 90; } > "$D/notes.md"
out="$(S --reports "$D")"
has "reports: long lane listed with lane" "kimi/k3" "$out"
has "reports: line count" "60 lines" "$out"
hasnt "reports: short lane not listed" "codex" "$out"
hasnt "reports: non-header file ignored" "notes.md" "$out"
has "reports: --lines raises the bar" "no lane output longer than 80 lines" "$(S --reports "$D" --lines 80)"

# bad input
S "$T/missing.jsonl" >/dev/null 2>&1; eq "missing log exits 2" "2" "$?"

[ $fail -eq 0 ] && echo "all passed" || { echo "FAILED"; exit 1; }
