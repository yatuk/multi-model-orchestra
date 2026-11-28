# Kimi models through the Kimi Code CLI.
LANE_BIN=kimi
LANE_DEFAULT_MODEL=kimi-code/k3.1-pro
LANE_FAMILY=moonshot
LANE_RO=throwaway          # kimi -p edits without asking and has no read-only sandbox
LANE_EXTRACT=kimi
LANE_VERIFIED=2026-11-21
LANE_NOTE="install Kimi Code and sign in"
lane_cmd() {
  CMD=(kimi -m "$MODEL" -p "$PROMPT" --output-format stream-json)
}
