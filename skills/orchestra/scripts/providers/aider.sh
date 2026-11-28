# Aider (Aider-AI/aider). Plain text output mixed with banners, so the brief gets two marker lines
# and the extractor keeps what is between them. Models are litellm ids (deepseek/deepseek-chat).
LANE_BIN=aider
LANE_DEFAULT_MODEL=""
LANE_FAMILY=any
LANE_RO=throwaway          # --chat-mode ask never edits, but aider has no sandbox; keep a throwaway copy too
LANE_EXTRACT=aider
LANE_VERIFIED=docs-0.86.2
LANE_NOTE="pip install aider-chat (or aider-install) and set the provider API key env var"
lane_cmd() {
  local pf="$PROMPT_FILE.aider"
  { cat "$PROMPT_FILE"; printf '\n\nFormat: put the line MMO-ANSWER-BEGIN on its own line before your final answer and the line MMO-ANSWER-END on its own line after it.\n'; } > "$pf"
  CMD=(aider --message-file "$pf" --no-auto-commits --no-suggest-shell-commands --no-check-update --no-analytics --no-show-release-notes --no-gitignore --no-pretty --no-stream)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  # Unattended edits need every confirmation answered yes; read-only runs use ask mode and answer nothing.
  if [ "$MODE" = rw ]; then CMD+=(--yes-always); else CMD+=(--chat-mode ask); fi
}
