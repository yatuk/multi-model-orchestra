# Cognition's Devin CLI, the local agent (devin -p). Windsurf's CLI became this one, so there is no separate windsurf lane.
# Not the cloud Devin: that one is reached through mmo-cloud.
LANE_BIN=devin
LANE_DEFAULT_MODEL=""      # empty: the account default (DEVIN_MODEL or `devin models`)
LANE_FAMILY=any
LANE_RO=throwaway          # no read-only flag; plan mode is a slash command, not a flag
LANE_EXTRACT=text          # -p prints the response and exits; no JSON shape is documented
LANE_VERIFIED=docs-3000.15.14
LANE_NOTE="install Devin CLI (curl -fsSL https://cli.devin.ai/install.sh | bash) and run devin auth login"
lane_cmd() {
  # Print mode cannot show the workspace-trust prompt and fails in an untrusted folder, so skip that check:
  # the folder is the run directory the runner made.
  CMD=(devin -p --respect-workspace-trust false)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  # dangerous (aliases yolo, bypass) approves every tool call. Read-only runs keep the default,
  # where print mode denies what would need approval and goes on to an answer.
  [ "$MODE" = rw ] && CMD+=(--permission-mode dangerous)
  # The documented form is `devin -p -- <prompt>`; the -- keeps a prompt that starts with a dash from being read as a flag.
  CMD+=(-- "$PROMPT")
}
