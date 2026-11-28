# xAI Grok through the Grok CLI (grok -p).
LANE_BIN=grok
LANE_DEFAULT_MODEL=grok-4.7
LANE_FAMILY=xai
LANE_RO=sandbox            # --tools leaves only the reading tools
LANE_EXTRACT=field:text
LANE_VERIFIED=2026-11-28   # run on 1.0.92: read-only (a write was refused), a write in a worktree, an unknown model
LANE_NOTE="install the Grok CLI and run grok login"
lane_cmd() {
  CMD=(grok -p "$PROMPT" -m "$MODEL" --cwd "$RUNDIR" --output-format json --reasoning-effort "$EFFORT")
  if [ "$MODE" = rw ]; then CMD+=(--always-approve); else CMD+=(--tools "read_file,grep,list_dir"); fi
  [ -n "$MAX_TURNS" ] && CMD+=(--max-turns "$MAX_TURNS")
}
