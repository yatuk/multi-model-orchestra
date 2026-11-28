#!/usr/bin/env bash
# Run the bench tasks on every lane in parallel and grade them.
#   bench/run.sh [--dry-run] [lane ...]      lane = provider:model[:effort]
# Results go to bench/results/<date>/: one answer file per lane and task, results.tsv.
#
# Tasks: bugfix, multifile, refactor (write tasks: the lane edits a worktree), reasoning, bulk, spec
# (answer tasks), and service (a large write task, ~2,300 lines, up to 30 min per lane; opt-in, never
# in the default list).
#   BENCH_TASKS="bugfix multifile" bench/run.sh ...   run only those tasks (default: all but service)
#   BENCH_TASKS=service bench/run.sh ...              the large task alone
# Write tasks are graded on the worktree whatever the lane reported (grade.py --lane-out adds what it
# reported); a lane that failed and left the worktree unchanged scores 0.
#
# A lane spec splits like this: the provider is the text before the first colon; the LAST
# colon-separated field is the effort only when it is one of low, medium, high, xhigh, max, minimal,
# none (and something is left to be the model); everything between is the model. So `codex:high`
# reads as model `high`, not effort high, by design: an effort needs a model before it
# (`codex:gpt-6.1-sol:high`). So api lanes work:
#   api:openrouter:google/gemma-4-31b-it:free   provider api, model openrouter:google/gemma-4-31b-it:free
#   api:ollama:qwen3:8b:high                    provider api, model ollama:qwen3:8b, effort high
# Environment:
#   BENCH_OUT=DIR     write the results to DIR instead of bench/results/<date>
#   BENCH_APPEND=1    add rows to an existing results.tsv instead of overwriting it (header only once)
#   DRY=1 or --dry-run  print provider, model and effort per lane, and per wanted task whether it
#                     would run or be skipped, then exit; no model is called, nothing is written
# A lane that has no tools (read-only value "notools" in mmo-run --list, such as api) cannot edit
# files, so every write task is skipped for it and gets a "skipped: lane has no tools" row instead of
# a failed run; the answer tasks still run.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN="$ROOT/skills/orchestra/scripts/mmo-run"
PY="$(command -v python3 || command -v python)"
DRY="${DRY:-0}"; LANES=()
for a in "$@"; do
  case "$a" in --dry-run) DRY=1 ;; *) LANES+=("$a") ;; esac
done
[ ${#LANES[@]} -eq 0 ] && LANES=(
  codex:gpt-6.1-sol:medium codex:gpt-6-astra:medium codex:gpt-6-luna:low
  kimi:kimi-code/k3.1-pro
  deepseek:deepseek/deepseek-v4-pro deepseek:deepseek/deepseek-flash
)

# --- task selection ---
WRITE_TASKS="bugfix multifile refactor service"
ALL_TASKS="bugfix reasoning bulk multifile refactor service spec"   # grading and dry-run order
BENCH_TASKS="${BENCH_TASKS:-bugfix reasoning bulk multifile refactor spec}"
for t in $BENCH_TASKS; do
  case " $ALL_TASKS " in *" $t "*) ;; *) echo "run.sh: unknown task $t" >&2; exit 2 ;; esac
done
want() { case " $BENCH_TASKS " in *" $1 "*) return 0 ;; esac; return 1; }
is_write() { case " $WRITE_TASKS " in *" $1 "*) return 0 ;; esac; return 1; }
# service gets 1800 s, twice the other write tasks: the lane reads some 40 files before it changes
# anything, and a careful lane runs the tests more than once. No --idle: lanes that print only at
# the end would trip it.
rw_timeout() { [ "$1" = service ] && echo 1800 || echo 900; }

# provider:model[:effort] -> PROV MODEL EFFORT (effort is empty when the spec has none)
EFFORTS=" low medium high xhigh max minimal none "
parse_lane() {
  PROV="${1%%:*}"; MODEL=""; EFFORT=""
  case "$1" in *:*) rest="${1#*:}" ;; *) rest="" ;; esac
  case "$rest" in
    *:*) last="${rest##*:}"
         case "$EFFORTS" in *" $last "*) EFFORT="$last"; MODEL="${rest%:*}" ;; *) MODEL="$rest" ;; esac ;;
    *) MODEL="$rest" ;;
  esac
}

# READ-ONLY column of mmo-run --list for one provider (notools = cannot edit files)
LISTING=""
lane_ro() {
  [ -n "$LISTING" ] || LISTING="$(bash "$RUN" --list 2>/dev/null)"
  printf '%s\n' "$LISTING" | awk -v p="$1" '$1==p {print $4}'
}

if [ "$DRY" = 1 ]; then
  for lane in "${LANES[@]}"; do
    parse_lane "$lane"
    printf 'lane=%s provider=%s model=%s effort=%s\n' "$lane" "$PROV" "$MODEL" "${EFFORT:-medium}"
    ro="$(lane_ro "$PROV")"
    for t in $ALL_TASKS; do want "$t" || continue
      act=run; is_write "$t" && [ "$ro" = notools ] && act=skip
      printf '  %s=%s\n' "$t" "$act"
    done
  done
  exit 0
fi

OUT="${BENCH_OUT:-$ROOT/bench/results/$(date +%Y-%m-%d)}"; mkdir -p "$OUT"
want bulk && "$PY" "$ROOT/bench/tasks/bulk/make_task.py"
want spec && "$PY" "$ROOT/bench/tasks/spec/make_task.py"

# A scratch repo for the answer tasks, and for bugfix with one linked worktree per lane.
SCR="$(mktemp -d)"; git -C "$SCR" init -q
cp "$ROOT/bench/tasks/bugfix/durations.py" "$ROOT/bench/tasks/bugfix/test_durations.py" "$SCR/"
git -C "$SCR" add . && git -C "$SCR" -c user.email=bench@local -c user.name=bench commit -qm base

# One scratch repo per other write task, holding only that task's start/ files: the lane never sees
# the hidden tests or the solutions, and the grader later runs its own copies of the tests.
SCRN="$(mktemp -d)"
for t in multifile refactor service; do want "$t" || continue
  git -C "$SCRN" init -q "$t"
  cp -r "$ROOT/bench/tasks/$t/start/." "$SCRN/$t/"
  git -C "$SCRN/$t" add . && git -C "$SCRN/$t" -c user.email=bench@local -c user.name=bench commit -qm base
done

slug() { echo "$1" | tr '/:' '__'; }
# repo and worktree of a write task for a lane slug
wt_repo() { [ "$1" = bugfix ] && echo "$SCR" || echo "$SCRN/$1"; }
wt_dir() { [ "$1" = bugfix ] && echo "$SCR/wt-$2" || echo "$SCRN/wt-$1-$2"; }

pids=()
# start CMD...: run in the background with stderr to the log. The pid is recorded here, only when
# a job was actually started, so a task that was not launched leaves no stale pid.
start() { ( "$@" ) 2>>"$OUT/log.txt" & pids+=($!); }
run_rw() { local rcfile="$1" rc; shift; "$RUN" "$@"; rc=$?; echo "$rc" > "$rcfile"; }

for lane in "${LANES[@]}"; do
  parse_lane "$lane"; prov="$PROV"; model="$MODEL"; effort="${EFFORT:-medium}"; s="$(slug "$prov:$model")"
  ro="$(lane_ro "$prov")"
  # 900 s for the write tasks (the slowest lane on 2026-11-28 needed 94 s for bugfix), 600 s for the answer tasks.
  for t in $WRITE_TASKS; do want "$t" || continue
    [ "$ro" = notools ] && continue
    git -C "$(wt_repo "$t")" worktree add -q "$(wt_dir "$t" "$s")" -b "lane/$s"
    start run_rw "$OUT/$s.$t.rc" "$prov" -m "$model" -e "$effort" --mode rw -C "$(wt_dir "$t" "$s")" -t "$(rw_timeout "$t")" --brief "$ROOT/bench/tasks/$t/brief.md" --out "$OUT/$s.$t.md"
  done
  for t in reasoning bulk spec; do want "$t" || continue
    start "$RUN" "$prov" -m "$model" -e "$effort" --mode ro -C "$SCR" -t 600 --brief "$ROOT/bench/tasks/$t/brief.md" --out "$OUT/$s.$t.md"
  done
done
for p in "${pids[@]}"; do wait "$p"; done

secs() { sed -n 's/.*seconds=\([0-9]*\).*/\1/p' "$1" | head -1; }
if [ "${BENCH_APPEND:-0}" = 1 ] && [ -s "$OUT/results.tsv" ]; then :
else printf 'lane\ttask\tscore\tseconds\tdetail\n' > "$OUT/results.tsv"; fi
for lane in "${LANES[@]}"; do
  parse_lane "$lane"; prov="$PROV"; model="$MODEL"; s="$(slug "$prov:$model")"
  ro="$(lane_ro "$prov")"
  for t in $ALL_TASKS; do want "$t" || continue
    if is_write "$t"; then
      if [ "$ro" = notools ]; then
        printf '%s\t%s\t-\t-\tskipped: lane has no tools\n' "$prov:$model" "$t" >> "$OUT/results.tsv"
        continue
      fi
      # grade.py grades the worktree whatever the lane reported, and says what it reported;
      # a failed lane that left the worktree unchanged scores 0.
      g="$("$PY" "$ROOT/bench/grade.py" "$t" "$(wt_dir "$t" "$s")" --lane-out "$OUT/$s.$t.md")"
      # the diff (new files included) is kept so a reader can see what the lane did
      git -C "$(wt_dir "$t" "$s")" add -A -N 2>/dev/null; git -C "$(wt_dir "$t" "$s")" diff > "$OUT/$s.$t.diff" 2>/dev/null
    else
      g="$("$PY" "$ROOT/bench/grade.py" "$t" "$OUT/$s.$t.md")"
    fi
    printf '%s\t%s\t%s\t%s\n' "$prov:$model" "$t" "$(echo "$g" | cut -f1)" "$(secs "$OUT/$s.$t.md")	$(echo "$g" | cut -f2-)" >> "$OUT/results.tsv"
  done
done
column -t -s $'\t' "$OUT/results.tsv" 2>/dev/null || cat "$OUT/results.tsv"
rm -rf "$SCR" "$SCRN"
