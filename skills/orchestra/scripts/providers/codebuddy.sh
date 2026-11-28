# Tencent CodeBuddy Code (codebuddy -p), a Claude Code style CLI.
LANE_BIN=codebuddy
LANE_DEFAULT_MODEL=""      # empty: the account default; --model takes an alias or a full model name
LANE_FAMILY=any
LANE_RO=throwaway          # print mode blocks writes and commands unless -y is given, but no read-only flag is documented
LANE_EXTRACT=field:result  # --output-format json: the final answer is in "result"
LANE_VERIFIED=docs-2.187.0
LANE_NOTE="npm install -g @tencent-ai/codebuddy-code; sign in once in the interactive CLI (or CODEBUDDY_API_KEY, which print mode uses)"
LANE_PROMPT=stdin          # echo "..." | codebuddy -p is documented
lane_cmd() {
  CMD=(codebuddy -p --output-format json)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  [ -n "$MAX_TURNS" ] && CMD+=(--max-turns "$MAX_TURNS")
  # The docs call -y required for edits and commands in print mode, and say a few high-risk commands can
  # still ask. CODEBUDDY_IS_SANDBOX=1 would silence those, but the docs limit it to isolated sandboxes, so it is not set.
  [ "$MODE" = rw ] && CMD+=(-y)
}
