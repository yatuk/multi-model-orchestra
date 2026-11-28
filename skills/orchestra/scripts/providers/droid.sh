# Factory Droid in exec mode (droid exec).
LANE_BIN=droid
LANE_DEFAULT_MODEL=""      # empty: the account default; `droid exec --help` lists the ids
LANE_FAMILY=any
LANE_RO=throwaway          # droid exec is read-only unless --auto is given (real help), not proven with a signed-in run
LANE_EXTRACT=claude        # json output is one result object with is_error and result
LANE_VERIFIED=help-1.23.0
LANE_NOTE="npm install -g droid (or the installer at app.factory.ai/cli); set FACTORY_API_KEY (starts fk-)"
lane_cmd() {
  CMD=(droid exec -f "$PROMPT_FILE" -o json --cwd "$RUNDIR")
  [ -n "$MODEL" ] && CMD+=(-m "$MODEL")
  # medium lets the lane run builds, tests and git commit; low would only allow file edits.
  [ "$MODE" = rw ] && CMD+=(--auto medium)
}
