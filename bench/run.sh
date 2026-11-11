#!/usr/bin/env bash
# Run the three bench tasks on every lane in parallel and grade them.
#   bench/run.sh [lane ...]      lane = provider:model:effort  (effort optional)
# Results go to bench/results/<date>/: one answer file per lane and task, results.tsv.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$ROOT/skills/orchestra/scripts/mmo-run"
PY="$(command -v python3 || command -v python)"
LANES=("$@")
[ ${#LANES[@]} -eq 0 ] && LANES=(
  codex:gpt-6.1-sol:medium codex:gpt-6-astra:medium codex:gpt-6-luna:low
  kimi:kimi-code/k3.1-pro
  deepseek:deepseek/deepseek-v4-pro deepseek:deepseek/deepseek-flash
)
OUT="$ROOT/bench/results/$(date +%Y-%m-%d)"; mkdir -p "$OUT"
"$PY" "$ROOT/bench/tasks/bulk/make_task.py"

# A scratch repo with one linked worktree per lane for the write task.
SCR="$(mktemp -d)"; git -C "$SCR" init -q
cp "$ROOT/bench/tasks/bugfix/durations.py" "$ROOT/bench/tasks/bugfix/test_durations.py" "$SCR/"
git -C "$SCR" add . && git -C "$SCR" -c user.email=bench@local -c user.name=bench commit -qm base

slug() { echo "$1" | tr '/:' '__'; }
pids=()
for lane in "${LANES[@]}"; do
  IFS=: read -r prov model effort <<< "$lane"; effort="${effort:-medium}"; s="$(slug "$prov:$model")"
  git -C "$SCR" worktree add -q "$SCR/wt-$s" -b "lane/$s"
  ( "$RUN" "$prov" -m "$model" -e "$effort" --mode rw -C "$SCR/wt-$s" -t 900 --brief "$ROOT/bench/tasks/bugfix/brief.md" --out "$OUT/$s.bugfix.md"; echo $? > "$OUT/$s.bugfix.rc" ) 2>>"$OUT/log.txt" &
  pids+=($!)
  ( "$RUN" "$prov" -m "$model" -e "$effort" --mode ro -C "$SCR" -t 600 --brief "$ROOT/bench/tasks/reasoning/brief.md" --out "$OUT/$s.reasoning.md" ) 2>>"$OUT/log.txt" &
  pids+=($!)
  ( "$RUN" "$prov" -m "$model" -e "$effort" --mode ro -C "$SCR" -t 600 --brief "$ROOT/bench/tasks/bulk/brief.md" --out "$OUT/$s.bulk.md" ) 2>>"$OUT/log.txt" &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done

secs() { sed -n 's/.*seconds=\([0-9]*\).*/\1/p' "$1" | head -1; }
printf 'lane\ttask\tscore\tseconds\tdetail\n' > "$OUT/results.tsv"
for lane in "${LANES[@]}"; do
  IFS=: read -r prov model effort <<< "$lane"; s="$(slug "$prov:$model")"
  if grep -q 'status=ok' "$OUT/$s.bugfix.md" 2>/dev/null; then g="$("$PY" "$ROOT/bench/grade.py" bugfix "$SCR/wt-$s")"
  else g="$(printf '0.00\tlane failed: %s' "$(sed -n 's/.*status=\([a-z]*\).*/\1/p' "$OUT/$s.bugfix.md" | head -1)")"; fi
  git -C "$SCR/wt-$s" diff > "$OUT/$s.bugfix.diff" 2>/dev/null
  printf '%s\tbugfix\t%s\t%s\n' "$prov:$model" "$(echo "$g" | cut -f1)" "$(secs "$OUT/$s.bugfix.md")	$(echo "$g" | cut -f2-)" >> "$OUT/results.tsv"
  for t in reasoning bulk; do
    g="$("$PY" "$ROOT/bench/grade.py" "$t" "$OUT/$s.$t.md")"
    printf '%s\t%s\t%s\t%s\n' "$prov:$model" "$t" "$(echo "$g" | cut -f1)" "$(secs "$OUT/$s.$t.md")	$(echo "$g" | cut -f2-)" >> "$OUT/results.tsv"
  done
done
column -t -s $'\t' "$OUT/results.tsv" 2>/dev/null || cat "$OUT/results.tsv"
rm -rf "$SCR"
