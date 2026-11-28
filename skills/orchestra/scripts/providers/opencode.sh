# OpenCode (anomalyco/opencode), written for the v2 Rust CLI (2.x).
# v1 differences (npm package opencode-ai, 1.x): it also accepts --yolo and --dangerously-skip-permissions
# as aliases of --auto, has --dir to pick the working folder, and its headless default
# auto-rejects every permission request. The flags used below exist in both lines.
LANE_BIN=opencode
LANE_DEFAULT_MODEL=""      # empty: use the model chosen in the user's OpenCode config
LANE_FAMILY=any            # one CLI, many providers; the model id says which (provider/model)
LANE_RO=throwaway          # no confirmed read-only flag for run; --agent plan is not confirmed for run
LANE_EXTRACT=opencode
LANE_VERIFIED=2026-11-28   # run on 2.4.1: read-only, a write in a worktree, an unknown model
LANE_NOTE="install OpenCode 2 and sign in; the desktop app ships the CLI as resources/opencode-cli, put it on PATH as opencode"
LANE_PROMPT=stdin          # a message argument plus piped stdin are both read; the brief can be long
lane_cmd() {
  CMD=(opencode run --format json)
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  # --auto approves what is not explicitly denied. Read-only runs leave it off.
  [ "$MODE" = rw ] && CMD+=(--auto)
  CMD+=("Follow the instructions given on stdin.")
}
