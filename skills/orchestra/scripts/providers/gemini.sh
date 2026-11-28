# Google Gemini CLI (google-gemini/gemini-cli). Since 2026-06 it serves Code Assist Standard/Enterprise
# and API or Vertex keys; personal Google AI plans moved to the agy lane.
LANE_BIN=gemini
LANE_DEFAULT_MODEL=""      # empty: the CLI's own default (auto)
LANE_FAMILY=google
LANE_RO=throwaway          # --approval-mode plan is documented as read-only, but no signed-in run has proven it; keep the discarded copy
LANE_EXTRACT=field:response
LANE_VERIFIED=help-0.71.1
LANE_NOTE="npm i -g @google/gemini-cli; sign in once with gemini, or set GEMINI_API_KEY"
LANE_PROMPT=stdin          # -p text is appended to what arrives on stdin
lane_cmd() {
  CMD=(gemini -o json --skip-trust)
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  # --yolo is deprecated; --approval-mode yolo is the documented replacement.
  if [ "$MODE" = rw ]; then CMD+=(--approval-mode yolo); else CMD+=(--approval-mode plan); fi
  CMD+=(-p "Follow the instructions given on stdin.")
}
