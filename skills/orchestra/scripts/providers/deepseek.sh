# DeepSeek models through the Kimi Code CLI (a deepseek/* model alias in its config.toml).
. "$PROVDIR/kimi.sh"
LANE_DEFAULT_MODEL=deepseek/deepseek-v4-pro
LANE_FAMILY=deepseek
LANE_NOTE="add a deepseek/* model to Kimi Code's config.toml"
lane_model() { case "$MODEL" in deepseek/*) ;; *) MODEL="deepseek/$MODEL" ;; esac; }
lane_ready() {
  local cfg="${KIMI_CONFIG:-$HOME/.kimi-code/config.toml}"
  [ -f "$cfg" ] && grep -q 'models\."deepseek/' "$cfg"
}
