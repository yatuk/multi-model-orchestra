# Qoder CLI (qoder -p). The npm package is @qoder-ai/qodercli; the docs call the command qoder.
LANE_BIN=qoder
LANE_DEFAULT_MODEL=""      # empty: the account default; --model takes auto, lite, performance or a BYOK key
LANE_FAMILY=any
LANE_RO=throwaway          # --permission-mode plan exists but the docs do not say what it restricts
LANE_EXTRACT=text          # text is the default output; the field of the json answer is not documented
LANE_VERIFIED=docs-1.1.101
LANE_NOTE="npm install -g @qoder-ai/qodercli; run qoder once to sign in, or set QODER_PERSONAL_ACCESS_TOKEN for scripts"
LANE_PROMPT=stdin          # echo "..." | qoder -p is documented
lane_cmd() {
  CMD=(qoder -p --cwd "$RUNDIR")
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  # --yolo is --permission-mode bypass_permissions. accept_edits would still reject shell commands.
  [ "$MODE" = rw ] && CMD+=(--yolo)
}
