# gptme in non-interactive mode (gptme -n). Python package gptme; the binary is gptme.
LANE_BIN=gptme
LANE_DEFAULT_MODEL=""      # empty: the model from gptme's config; -m takes provider/model (groq/llama-3.3-70b-versatile)
LANE_FAMILY=any
LANE_RO=throwaway          # -n implies --no-confirm, so every tool call is approved; no read-only flag is documented
LANE_EXTRACT=gptme         # --output-format json is one JSON object per message; the answer is the last assistant one
LANE_VERIFIED=docs-0.37.0
LANE_NOTE="pipx install gptme; set OPENAI_API_KEY, ANTHROPIC_API_KEY or OPENROUTER_API_KEY"
lane_cmd() {
  # The same flags in ro and rw: -n cannot be asked to hold back, so the runner's throwaway worktree is the ro guard.
  CMD=(gptme -n --output-format json -w "$RUNDIR")
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  CMD+=("$PROMPT")
}
