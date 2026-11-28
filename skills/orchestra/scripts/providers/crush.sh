# Charm Crush (charmbracelet/crush), crush run for one prompt.
LANE_BIN=crush
LANE_DEFAULT_MODEL=""      # empty: the model set in crush's own config; -m accepts model or provider/model
LANE_FAMILY=any
LANE_RO=throwaway          # real help lists -y/--yolo (skip permission prompts); how run behaves without it is not proven
LANE_EXTRACT=text
LANE_VERIFIED=help-0.104.0
LANE_NOTE="install crush (npm i -g @charmland/crush) and configure a provider or API key env var"
LANE_PROMPT=stdin          # crush run reads a piped stdin as the prompt
lane_env() {
  # No telemetry from an unattended lane.
  export CRUSH_DISABLE_METRICS=1
}
lane_cmd() {
  # The same command for ro and rw: there is no flag to turn approval off or on.
  CMD=(crush run -q)
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
}
