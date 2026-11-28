# Claude Code on MiniMax models through MiniMax's Anthropic-compatible endpoint.
# Anthropic does not support running Claude Code on other vendors' models; MiniMax documents it
# (platform.minimax.io/docs/m-plan/claude-code). The docs name no key variable: MINIMAX_API_KEY is
# this lane's own choice.
. "$PROVDIR/claude.sh"
LANE_DEFAULT_MODEL=MiniMax-M3.1-Flash
LANE_FAMILY=any
LANE_VERIFIED=docs         # the claude lane it builds on is run; this endpoint was not
LANE_NOTE="set MINIMAX_API_KEY; Claude Code runs on MiniMax, which Anthropic does not support"
lane_ready() { [ -n "${MINIMAX_API_KEY:-}" ]; }
lane_env() {
  [ -n "${MINIMAX_API_KEY:-}" ] || { echo "no API key: set MINIMAX_API_KEY" >&2; exit 1; }
  export ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
  export ANTHROPIC_AUTH_TOKEN="$MINIMAX_API_KEY"
  export ANTHROPIC_API_KEY=""
  export ANTHROPIC_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
}
