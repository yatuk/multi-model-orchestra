# Claude Code on Kimi models through Moonshot's Anthropic-compatible endpoint.
# Anthropic does not support running Claude Code on other vendors' models; Moonshot documents it
# (platform.kimi.ai/docs/guide/claude-code-kimi).
. "$PROVDIR/claude.sh"
LANE_DEFAULT_MODEL=kimi-k3
LANE_FAMILY=moonshot
LANE_VERIFIED=docs         # the claude lane it builds on is run; this endpoint was not
LANE_NOTE="set MOONSHOT_API_KEY; Claude Code runs on Kimi, which Anthropic does not support"
lane_ready() { [ -n "${MOONSHOT_API_KEY:-}" ]; }
lane_env() {
  [ -n "${MOONSHOT_API_KEY:-}" ] || { echo "no API key: set MOONSHOT_API_KEY" >&2; exit 1; }
  export ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic
  export ANTHROPIC_AUTH_TOKEN="$MOONSHOT_API_KEY"
  export ANTHROPIC_API_KEY=""
  export ANTHROPIC_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_FABLE_MODEL="$MODEL"
  export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"
}
