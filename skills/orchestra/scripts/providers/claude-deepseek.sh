# Claude Code on DeepSeek models through DeepSeek's Anthropic-compatible endpoint.
# Anthropic does not support running Claude Code on other vendors' models; DeepSeek documents it
# (api-docs.deepseek.com/quick_start/agent_integrations/claude_code).
. "$PROVDIR/claude.sh"
LANE_DEFAULT_MODEL=deepseek-v4-pro
LANE_FAMILY=deepseek
LANE_VERIFIED=docs         # the claude lane it builds on is run; this endpoint was not
LANE_NOTE="set DEEPSEEK_API_KEY; Claude Code runs on DeepSeek, which Anthropic does not support"
lane_ready() { [ -n "${DEEPSEEK_API_KEY:-}" ]; }
lane_env() {
  [ -n "${DEEPSEEK_API_KEY:-}" ] || { echo "no API key: set DEEPSEEK_API_KEY" >&2; exit 1; }
  export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
  export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
  export ANTHROPIC_API_KEY=""   # empty so a saved claude.ai login is not used
  export ANTHROPIC_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
  export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"
}
