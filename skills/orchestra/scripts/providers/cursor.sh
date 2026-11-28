# Cursor CLI in headless mode. Its binary is now called `agent`, a name other tools also install
# (the Grok CLI ships one), so this lane calls the `cursor-agent` name the installer still creates.
LANE_BIN=cursor-agent
LANE_DEFAULT_MODEL=""      # empty: the CLI picks; `cursor-agent --list-models` shows the ids
LANE_FAMILY=any
LANE_RO=throwaway          # --mode ask is asked for, but the docs say -p grants all tools, so do not trust it alone
LANE_EXTRACT=claude        # json output is one result object: {"type":"result","is_error":..,"result":".."}
LANE_VERIFIED=2026-11-28   # cursor-agent 2026.11.22 on Windows: ro PONG, ro write refused, rw write in a worktree, unknown model, bugfix+reasoning+bulk bench
LANE_NOTE="install the Cursor CLI, then cursor-agent login (or set CURSOR_API_KEY)"
lane_cmd() {
  # --trust: headless runs otherwise stop at the workspace-trust prompt.
  CMD=(cursor-agent -p "$PROMPT" --output-format json --workspace "$RUNDIR" --trust)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  if [ "$MODE" = rw ]; then CMD+=(--force); else CMD+=(--mode ask); fi
}
