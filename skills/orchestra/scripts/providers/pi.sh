# Pi coding agent in print mode (pi -p). The repo and package moved to earendil-works.
LANE_BIN=pi
LANE_DEFAULT_MODEL=""      # empty: the configured default; `pi --list-models` shows the ids
LANE_FAMILY=any
LANE_RO=throwaway          # the tool allowlist is the guard (real help), not proven with a signed-in run
LANE_EXTRACT=text          # -p prints only the final assistant text
LANE_VERIFIED=help-1.7.0
LANE_NOTE="npm install -g --ignore-scripts @earendil-works/pi-coding-agent; pi auth login <provider> or a provider key env"
lane_cmd() {
  CMD=(pi --print --no-session)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  # --no-mcp: --tools does not remove MCP tools, which could write.
  [ "$MODE" = ro ] && CMD+=(--tools read,grep,find,ls --no-mcp)
  CMD+=(-- "$PROMPT")
}
