#!/usr/bin/env bash
# Offline test for mmo_classify.py: no model calls. Run: bash skills/orchestra/scripts/test-mmo-classify.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
check() { # name expected provider prompt-file err-file
  got="$("$PY" "$HERE/mmo_classify.py" "$3" "$4" "$5" /dev/null)"
  if [ "$got" = "$2" ]; then echo "PASS $1 -> $got"; else echo "FAIL $1: expected $2, got $got"; fail=1; fi
}
printf 'Review this design.\nNote: the API returns 429 rate limit and quota errors.\nPlease answer briefly.\n' > "$T/brief"
MNF='ERROR: {"error":{"message":"The '"'"'gpt-x'"'"' model is not supported when using Codex with a ChatGPT account.","code":"model_not_found"}} 400 Bad Request'

{ echo "user"; cat "$T/brief"; echo "$MNF"; } > "$T/e1"
check "echoed 429 brief + model_not_found" model codex "$T/brief" "$T/e1"

printf 'ERROR: exceeded retry limit, last status: 429 Too Many Requests (rate limit)\n' > "$T/e2"
check "real rate limit" limit codex "$T/brief" "$T/e2"

{ cat "$T/brief"; echo "ERROR: 401 Unauthorized, please sign in again"; } > "$T/e3"
check "auth error" auth codex "$T/brief" "$T/e3"

{ echo "user"; cat "$T/brief"; echo "ERROR: connection reset"; } > "$T/e4"
check "echoed brief only, plain failure" failed codex "$T/brief" "$T/e4"

printf 'LLM provider error: 402 insufficient balance\n' > "$T/e5"
check "kimi/deepseek empty balance" limit deepseek "$T/brief" "$T/e5"

printf 'unknown model: deepseek/nope\n' > "$T/e6"
check "unknown model (kimi)" model kimi "$T/brief" "$T/e6"

# End to end with a fake codex on PATH: brief mentions 429, CLI fails with model_not_found / succeeds.
mkdir -p "$T/bin"
cat > "$T/bin/codex" <<'FAKE'
#!/bin/sh
for a; do last="$a"; done
if [ -n "${FAKE_FAIL:-}" ]; then echo "user"; echo "$last"; echo 'ERROR: {"error":{"code":"model_not_found"}} 400'; exit 1; fi
while [ $# -gt 0 ]; do [ "$1" = -o ] && echo hello > "$2"; shift; done; exit 0
FAKE
chmod +x "$T/bin/codex"
PATH="$T/bin:$PATH" FAKE_FAIL=1 "$HERE/mmo-run" codex --brief "$T/brief" --out "$T/o1" 2>/dev/null; rc=$?
if [ $rc -eq 8 ] && grep -q 'status=model' "$T/o1"; then echo "PASS run: model_not_found -> exit 8"; else echo "FAIL run: rc=$rc"; fail=1; fi
PATH="$T/bin:$PATH" "$HERE/mmo-run" codex --brief "$T/brief" --out "$T/o2" 2>/dev/null; rc=$?
if [ $rc -eq 0 ] && grep -q 'status=ok' "$T/o2"; then echo "PASS run: clean run -> ok"; else echo "FAIL run clean: rc=$rc"; fail=1; fi
exit $fail
