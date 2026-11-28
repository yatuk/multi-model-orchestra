# Mistral Vibe in programmatic mode (vibe -p).
LANE_BIN=vibe
LANE_DEFAULT_MODEL=""      # empty: the configured default; --model takes an alias from config.toml
LANE_FAMILY=mistral
LANE_RO=throwaway          # accept-edits still lets the lane edit; the read-only tool ids are not confirmed
LANE_EXTRACT=text
LANE_VERIFIED=docs-3.1.5
LANE_NOTE="uv tool install mistral-vibe; set MISTRAL_API_KEY to skip the first-run wizard"
LANE_MAX_COST=yes          # --max-price is a per-run spend cap
LANE_PROMPT=stdin          # documented: -p with no text reads the prompt from stdin, so -p goes last
lane_cmd() {
  CMD=(vibe --output text)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  [ -n "$MAX_TURNS" ] && CMD+=(--max-turns "$MAX_TURNS")
  [ -n "$MAX_COST" ] && CMD+=(--max-price "$MAX_COST")
  # Stop gracefully a little before the runner hard kill. TIMEOUT is mmo-run's -t value.
  [ "${TIMEOUT:-0}" -gt 40 ] && CMD+=(--time-limit "$((TIMEOUT - 20))")
  # Explicit policy: a user config that says auto-approve must not leak into a read-only run.
  if [ "$MODE" = rw ]; then CMD+=(--auto-approve); else CMD+=(--approval-policy accept-edits); fi
  CMD+=(-p)
}
