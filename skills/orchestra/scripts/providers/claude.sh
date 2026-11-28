# Claude models through Claude Code's print mode (outside Claude Code; inside it, use sub-agents).
LANE_BIN=claude
LANE_DEFAULT_MODEL=sonnet
LANE_FAMILY=anthropic
LANE_RO=sandbox            # only Read, Glob and Grep are offered
LANE_EXTRACT=claude
LANE_VERIFIED=2026-11-21
LANE_NOTE="only needed outside Claude Code"
LANE_MAX_COST=yes          # --max-budget-usd is a real per-run spend cap
lane_cmd() {
  local perm=(--tools Read Glob Grep --permission-mode dontAsk)
  # A writing lane must be able to run the check, so Bash is allowed as well as edits. The tool list
  # comes before --permission-mode on purpose: it takes several values and would swallow the prompt.
  [ "$MODE" = rw ] && perm=(--allowedTools Bash --permission-mode acceptEdits)
  CMD=(claude -p --model "$MODEL" --output-format json "${perm[@]}")
  [ -n "$MAX_TURNS" ] && CMD+=(--max-turns "$MAX_TURNS")
  [ -n "$MAX_COST" ] && CMD+=(--max-budget-usd "$MAX_COST")
  CMD+=("$PROMPT")
}
