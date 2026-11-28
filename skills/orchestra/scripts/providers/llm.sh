# Simon Willison's llm: a plain answer from one model, no tools (it uses tools only when given -T or --functions).
# Binary name warning: `llm` is a generic name; this lane means the Python tool from llm.datasette.io (pipx install llm).
LANE_BIN=llm
LANE_DEFAULT_MODEL=""      # empty: llm's default model (OpenAI, needs OPENAI_API_KEY); other providers are llm plugins
LANE_FAMILY=any
LANE_RO=notools
LANE_EXTRACT=text
LANE_VERIFIED=docs-0.38
LANE_NOTE="pipx install llm; llm keys set openai (or OPENAI_API_KEY); other models need a plugin such as llm-anthropic"
LANE_PROMPT=stdin          # piped text is the prompt; it is documented as coming before any argument
lane_cmd() {
  CMD=(llm --no-stream)
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
}
