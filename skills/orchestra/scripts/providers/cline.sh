# Cline CLI (cline --json). Never add --zen: it detaches to a daemon and prints nothing.
LANE_BIN=cline
LANE_DEFAULT_MODEL=""      # empty: Cline default; ids depend on the provider (-P)
LANE_FAMILY=any
LANE_RO=throwaway          # plan mode is the nearest thing to read-only, and it is not confirmed to block edits
LANE_EXTRACT=jsonl:text    # the run_result line carries the final text
LANE_VERIFIED=help-3.0.76
LANE_NOTE="npm install -g cline; cline auth, or set a provider key such as ANTHROPIC_API_KEY"
LANE_PROMPT=stdin          # real 3.0.76: --json refuses stdin alone ("requires a prompt argument"), so a short argument goes with it
lane_cmd() {
  CMD=(cline --json -c "$RUNDIR")
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  # One-shot runs are yolo by default, so read-only has to turn approval back on.
  if [ "$MODE" = rw ]; then CMD+=(--yolo); else CMD+=(--plan --auto-approve false); fi
  CMD+=("Follow the instructions given on stdin.")
}
