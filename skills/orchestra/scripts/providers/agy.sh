# Google Antigravity CLI (agy), the home of Google AI Pro/Ultra plans since 2026-06-18.
LANE_BIN=agy
LANE_DEFAULT_MODEL=""      # empty: the CLI's own default; agy models lists the slugs
LANE_FAMILY=google
LANE_RO=throwaway          # --mode plan refused writes in tests but is model-enforced, not a sandbox; default mode DID write headlessly
LANE_EXTRACT=field:response
LANE_VERIFIED=2026-11-28   # run on agy 1.5.19 (Windows): read-only, a write in a worktree, an unknown model, 9 models benched
LANE_NOTE="download agy from antigravity.google/download and sign in once"
lane_cmd() {
  CMD=(agy --output-format json)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  if [ "$MODE" = rw ]; then CMD+=(--dangerously-skip-permissions); else CMD+=(--mode plan); fi
  CMD+=(-p "$PROMPT")
}
