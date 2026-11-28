# Augment Auggie (auggie --print).
LANE_BIN=auggie
LANE_DEFAULT_MODEL=""      # empty: the account default; `auggie model list` shows the ids
LANE_FAMILY=any
LANE_RO=throwaway          # --tools leaves only the reading tools (real help), not proven with a signed-in run
LANE_EXTRACT=text          # the JSON event schema is not documented, so use the plain output
LANE_VERIFIED=help-1.2.3
LANE_NOTE="npm install -g @augmentcode/auggie; auggie auth login, or set AUGMENT_SESSION_AUTH"
lane_cmd() {
  # @file makes Auggie read the instruction from the file.
  CMD=(auggie --print "@$PROMPT_FILE" -w "$RUNDIR")
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  if [ "$MODE" = rw ]; then
    CMD+=(--permission bash:allow --permission edit:allow --permission write:allow)
  else
    CMD+=(--tools read,grep,find,ls)
  fi
}
