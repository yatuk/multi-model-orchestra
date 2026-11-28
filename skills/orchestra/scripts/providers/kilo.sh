# Kilo Code CLI (kilo run).
LANE_BIN=kilo
LANE_DEFAULT_MODEL=""      # empty: Kilo default; -m takes provider/model, `kilo models` lists them
LANE_FAMILY=any
LANE_RO=throwaway          # without --auto permission requests are rejected, but default permissions may never ask
LANE_EXTRACT=text          # the JSON event shape is not documented
LANE_VERIFIED=help-7.8.40
LANE_NOTE="npm install -g @kilocode/cli; kilo auth login"
lane_cmd() {
  CMD=(kilo run "$PROMPT" --dir "$RUNDIR" --format default)
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  [ "$MODE" = rw ] && CMD+=(--auto)
}
