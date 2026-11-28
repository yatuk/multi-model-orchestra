# Letta Code (letta -p). It keeps a stateful agent with memory per folder; --ephemeral makes the lane stateless.
LANE_BIN=letta
LANE_DEFAULT_MODEL=""      # empty: the agent's own model; --model takes an alias such as sonnet, or auto
LANE_FAMILY=any
LANE_RO=sandbox            # --tools "Read,Glob,Grep" is the documented way to restrict a run to read-only operations
LANE_EXTRACT=field:result  # --output-format json: one object, the answer is "result"
LANE_VERIFIED=docs-0.34.72
LANE_NOTE="npm install -g @letta-ai/letta-code and sign in once by running letta; the docs read did not name the API key variable"
LANE_PROMPT=stdin          # echo "..." | letta -p is documented
lane_cmd() {
  # --ephemeral: no agent, memory or MemFS is created or resumed, so lanes do not share state.
  CMD=(letta -p --ephemeral --output-format json)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  if [ "$MODE" = rw ]; then CMD+=(--yolo); else CMD+=(--tools "Read,Glob,Grep"); fi
}
