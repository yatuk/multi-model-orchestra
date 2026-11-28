# Any OpenAI-compatible chat endpoint, no agent CLI: an opinion or bulk-work lane without tools.
# Pass the model as endpoint:model (mmo-run -m openrouter:deepseek/deepseek-v4-pro); there is no default.
# The lane cannot read the repo, so the brief must carry everything. See docs/lanes/api.md.
LANE_BIN="$(command -v python3 || command -v python || echo python3)"
LANE_DEFAULT_MODEL=""
LANE_FAMILY=any
LANE_RO=notools
LANE_EXTRACT=text
LANE_PROMPT=stdin
LANE_VERIFIED=2026-11-28   # run against a local Ollama; the hosted endpoints come from their docs
LANE_NOTE="python 3 and an API key variable (see docs/lanes/api.md)"
# Keys: mmo-run loads ~/.config/mmo/keys.env (or the file MMO_KEYS_FILE names) for every lane.
# The endpoint's usage object goes to a side file, so stdout stays the pure answer (mmo_usage.py reads it).
lane_env() { export MMO_API_USAGE_FILE="$TMP/api-usage.json"; }
lane_cmd() {
  # mmo_api.py rejects an empty model or one without "endpoint:" with a message naming the format.
  CMD=("$LANE_BIN" "$PROVDIR/../mmo_api.py" "$MODEL")
}
