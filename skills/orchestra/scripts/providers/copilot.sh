# GitHub Copilot CLI in programmatic mode (copilot -p).
LANE_BIN=copilot
LANE_DEFAULT_MODEL=""      # empty: Copilot default; ids depend on the plan
LANE_FAMILY=any
LANE_RO=sandbox            # checked with the real CLI: without an allow flag, headless write and shell calls are denied
LANE_EXTRACT=text          # -s prints only the agent answer
LANE_VERIFIED=2026-11-28
LANE_NOTE="npm install -g @github/copilot; sign in with /login or set COPILOT_GITHUB_TOKEN"
# -p ignores piped stdin, so the prompt has to be an argument.
lane_cmd() {
  CMD=(copilot -p "$PROMPT" -s -C "$RUNDIR" --no-ask-user --no-auto-update)
  [ -n "$MODEL" ] && CMD+=(--model="$MODEL")
  [ "$MODE" = rw ] && CMD+=(--allow-all-tools)
}
