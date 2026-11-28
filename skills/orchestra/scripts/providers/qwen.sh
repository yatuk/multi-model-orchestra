# Qwen Code (QwenLM/qwen-code), binary qwen. A fork of Gemini CLI with its own exit codes (41 auth,
# 53 turn limit, 55 budget); mmo-run classifies by error text only, not by exit code.
LANE_BIN=qwen
LANE_DEFAULT_MODEL=qwen3-coder-plus
LANE_FAMILY=alibaba
LANE_RO=throwaway          # --approval-mode plan is documented as read-only analysis; not proven with a signed-in run
LANE_EXTRACT=qwen
LANE_VERIFIED=help-0.29.0
LANE_NOTE="npm i -g @qwen-code/qwen-code; sign in with /auth once, or set OPENAI_API_KEY and OPENAI_BASE_URL"
LANE_PROMPT=stdin
lane_env() {
  # --yolo prints a warning without a sandbox; this documented variable silences it.
  [ "$MODE" = rw ] && export QWEN_CODE_SUPPRESS_YOLO_WARNING=1
  return 0
}
lane_cmd() {
  CMD=(qwen -m "$MODEL" --output-format json)
  if [ "$MODE" = rw ]; then CMD+=(--approval-mode yolo); else CMD+=(--approval-mode plan); fi
  [ -n "$MAX_TURNS" ] && CMD+=(--max-session-turns "$MAX_TURNS")
  CMD+=(-p "Follow the instructions given on stdin.")
}
