#!/usr/bin/env bash
# A/B: does the orchestra skill beat "Use subagents for implementation."?
#   bench/ab/run_ab.sh [RUN_SPEC ...]      RUN_SPEC = A1, B1, C1, A2, ... (default: A1 B1 A2 B2)
#   ARMS="C" RUNS=2 bench/ab/run_ab.sh     same as C1 C2 (ARMS and RUNS are used only when no RUN_SPEC is given;
#                                          order is run 1 of every arm, then run 2, ...)
# Arms: A = "Use subagents for implementation."; B = A plus "Follow the orchestra skill." and the skill;
#       C = A with one line saying "Use Sonnet subagents ... name the model explicitly on every sub-agent call."
# Runs are sequential. Each gets a fresh temp git repo with a copy of bench/ab/taskrepo.
# Env: MODEL (default claude-fable-5-2), CAP_USD per run (default 25), TIMEOUT_S (default 3600),
#      FABLE_SKILL_DIR (optional extra routing skill copied into arm B, e.g. fable-orchestration).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="$(command -v python3 || command -v python)"
MODEL="${MODEL:-claude-fable-5-2}"; CAP_USD="${CAP_USD:-25}"; TIMEOUT_S="${TIMEOUT_S:-3600}"
OUT="$HERE/results/$(date +%Y-%m-%d)"; mkdir -p "$OUT"
SPECS=("$@")
if [ ${#SPECS[@]} -eq 0 ]; then
  if [ -n "${ARMS:-}" ] || [ -n "${RUNS:-}" ]; then
    for ((r=1; r<=${RUNS:-2}; r++)); do for a in ${ARMS:-A B}; do SPECS+=("$a$r"); done; done
  else SPECS=(A1 B1 A2 B2); fi
fi

BASE_PROMPT='Do the four tasks in TASKS.md in this repository. Run the visible tests with `python -m unittest`. Do not edit or delete the existing test files. Do not commit. Use subagents for implementation.'

# Least permission that lets it work: file edits inside the repo (acceptEdits); python (tests and
# scratch checks; tests are code anyway), git, cd/ls/cp through Bash or PowerShell, so sub-agents in
# their own worktrees can test and the main loop can merge. No web tools. Anything else that would
# prompt is denied (--permission-prompts none). User settings, user skills, hooks and MCP servers are
# not loaded (--setting-sources project --strict-mcp-config), so arm A sees no routing skill.
ALLOW=("Bash(python *)" "Bash(python3 *)" "Bash(git *)" "Bash(cd *)" "Bash(ls *)" "Bash(cp *)"
       "PowerShell(python *)" "PowerShell(git *)" "PowerShell(cd *)" "PowerShell(ls *)" "PowerShell(Copy-Item *)")

SONNET_LINE='Use Sonnet subagents for implementation, and name the model explicitly on every sub-agent call.'
if [ -n "${PRINT_PROMPTS:-}" ]; then
  echo "A: $BASE_PROMPT"; echo "B: $BASE_PROMPT Follow the orchestra skill."
  echo "C: ${BASE_PROMPT/Use subagents for implementation./$SONNET_LINE}"; exit 0
fi

for spec in "${SPECS[@]}"; do
  arm="${spec:0:1}"; n="${spec:1}"
  D="$(mktemp -d)"; M="$(mktemp -d)"; cp "$HERE"/taskrepo/* "$D/"
  prompt="$BASE_PROMPT"
  if [ "$arm" = B ]; then
    mkdir -p "$D/.claude/skills"; cp -r "$ROOT/skills/orchestra" "$D/.claude/skills/"
    [ -n "${FABLE_SKILL_DIR:-}" ] && [ -d "$FABLE_SKILL_DIR" ] && cp -r "$FABLE_SKILL_DIR" "$D/.claude/skills/"
    prompt="$prompt Follow the orchestra skill."
  fi
  if [ "$arm" = C ]; then prompt="${BASE_PROMPT/Use subagents for implementation./$SONNET_LINE}"; fi
  git -C "$D" init -q && git -C "$D" add -A && git -C "$D" -c user.email=bench@local -c user.name=bench commit -qm base 2>/dev/null
  echo "run $spec, model $MODEL, cap \$$CAP_USD" >&2
  t0=$(date +%s)
  ( cd "$D" && timeout -k 10 "$TIMEOUT_S" claude -p "$prompt" --model "$MODEL" \
      --setting-sources project --strict-mcp-config \
      --permission-mode acceptEdits --permission-prompts none \
      --allowedTools "${ALLOW[@]}" --disallowedTools WebFetch WebSearch \
      --max-budget-usd "$CAP_USD" --output-format json --no-session-persistence \
      </dev/null > "$M/raw.json" 2> "$M/err.txt" )
  rc=$?; wall=$(( $(date +%s) - t0 )); echo "exit $rc, ${wall}s" >&2
  # Grade only what landed in the main checkout; sub-agent worktrees under .claude/ do not count.
  git -C "$D" add -A -- . ':!.claude' 2>/dev/null
  git -C "$D" diff --cached > "$OUT/$spec.diff"
  "$PY" "$HERE/grade_ab.py" "$D" > "$M/grade.json"
  "$PY" "$HERE/collect.py" "$arm" "$n" "$M/raw.json" "$M/grade.json" "$D" "$OUT/$spec.json" "$wall" "$rc"
  "$PY" "$HERE/collect.py" --scrub-file "$OUT/$spec.diff" "$D"
  cat "$M/grade.json" >&2
  rm -rf "$D" "$M"
done
"$PY" "$HERE/summarize_ab.py" "$OUT"
