# AWS Kiro CLI in headless chat (kiro-cli chat --no-interactive).
LANE_BIN=kiro-cli
LANE_DEFAULT_MODEL=""      # empty: Kiro default; `kiro-cli chat --list-models` shows the ids
LANE_FAMILY=any
LANE_RO=sandbox            # only the trusted tools run; every other tool call is denied headless
LANE_EXTRACT=text          # the success record of stream-json is not documented, so use plain output
LANE_VERIFIED=docs-3.6.2
LANE_NOTE="curl -fsSL https://cli.kiro.dev/install | bash; kiro-cli login, or set KIRO_API_KEY (a stored login wins over the key)"
LANE_PROMPT=stdin          # documented: the whole stdin is the instruction
lane_cmd() {
  # --v3 pins the harness; the default differs between releases.
  CMD=(kiro-cli chat --v3 --no-interactive)
  [ -n "$MODEL" ] && CMD+=(--model "$MODEL")
  if [ "$MODE" = rw ]; then CMD+=(--trust-all-tools); else CMD+=(--trust-tools=read_file,grep_search); fi
}
