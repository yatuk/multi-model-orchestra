# OpenAI GPT through the Codex CLI (ChatGPT plan or API key).
LANE_BIN=codex
LANE_DEFAULT_MODEL=gpt-6.1-sol
LANE_FAMILY=openai
LANE_RO=sandbox            # the CLI's own read-only sandbox
LANE_EXTRACT=answer-file   # -o writes the final message itself
LANE_VERIFIED=2026-11-21
LANE_NOTE="install the Codex CLI and sign in with ChatGPT (codex login)"
lane_cmd() {
  local sandbox=(-s read-only)
  [ "$MODE" = rw ] && sandbox=(--approve-for-me)
  CMD=(codex exec --skip-git-repo-check -C "$RUNDIR" -m "$MODEL"
       -c model_reasoning_effort="$EFFORT" "${sandbox[@]}" -o "$ANS" "$PROMPT")
}
