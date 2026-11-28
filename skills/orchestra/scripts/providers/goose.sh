# Goose (aaif-goose/goose, formerly block/goose), goose run.
# -m takes provider/model (split at the first slash, so openrouter/x/y is provider openrouter, model x/y);
# a bare model id uses the provider from GOOSE_PROVIDER or the user's config.
LANE_BIN=goose
LANE_DEFAULT_MODEL=""
LANE_FAMILY=any
LANE_RO=throwaway          # no native read-only mode; the default GOOSE_MODE=auto approves every tool
LANE_EXTRACT=text
LANE_VERIFIED=docs-1.61.1
LANE_NOTE="install goose (see goose docs), run goose configure once or set provider env keys"
LANE_PROMPT=stdin
lane_env() {
  # Say it explicitly for rw lanes; read-only lanes run in a discarded worktree and keep the user's setting.
  [ "$MODE" = rw ] && export GOOSE_MODE=auto
  return 0
}
lane_cmd() {
  CMD=(goose run -q --no-session -i -)
  if [ -n "$MODEL" ]; then
    case "$MODEL" in
      */*) CMD+=(--provider "${MODEL%%/*}" --model "${MODEL#*/}") ;;
      *) CMD+=(--model "$MODEL") ;;
    esac
  fi
  [ -n "$MAX_TURNS" ] && CMD+=(--max-turns "$MAX_TURNS")
}
