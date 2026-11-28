# Amp (ampcode.com) in execute mode (amp -x).
LANE_BIN=amp
LANE_DEFAULT_MODEL=""      # empty: Amp default mode; --model takes provider/name
LANE_FAMILY=any
LANE_RO=throwaway          # Amp never asks for approval and has no read-only mode
LANE_EXTRACT=result-stream # --stream-json ends with a result line (Claude Code schema)
LANE_VERIFIED=docs-2026-11
LANE_NOTE="install Amp, then amp login; for scripts set AMP_API_KEY (an sgamp_ access token)"
LANE_PROMPT=stdin          # documented: echo "..." | amp -x
lane_cmd() {
  CMD=(amp -x --stream-json)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
}
