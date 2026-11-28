#!/usr/bin/env bash
# Offline test for the api lane and the Claude-Code-on-another-vendor lanes.
# A fake chat server listens on 127.0.0.1 only; a fake claude is on PATH. No real API is contacted.
# Run: bash skills/orchestra/scripts/test-mmo-api.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"
SRV=""
trap '[ -n "$SRV" ] && kill "$SRV" 2>/dev/null; rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; [ -f "$T/out" ] && sed 's/^/    /' "$T/out"; fail=1; }
run() { PATH="$T/bin:$PATH" bash "$HERE/mmo-run" "$@" --out "$T/out" 2> "$T/log"; }
header() { head -1 "$T/out"; }
KEY="sk-test-SECRET-0123456789"
# Never read the real key file; tests that need one point MMO_KEYS_FILE at a temp file.
export MMO_KEYS_FILE="$T/no-such-keys.env"

# The fake server decides what to do from the model name in the request body.
cat > "$T/server.py" <<'PYEOF'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def reply(self, code, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        model = body["model"]
        open(sys.argv[2], "a").write("%s|%s|%s\n" % (self.path, self.headers.get("Authorization"), model))
        if model.startswith("good"):
            text = "héllo ✓ Ünïcode model=" + model
            self.reply(200, {"choices": [{"message": {"role": "assistant", "content": text}}]})
        elif model == "m401":
            self.reply(401, {"error": {"message": "Invalid API key", "type": "invalid_authentication_error"}})
        elif model == "m402":
            self.reply(402, {"error": {"message": "Insufficient credits", "code": 402}})
        elif model == "m429":
            self.reply(429, {"error": {"message": "Rate limit reached", "type": "rate_limit_reached_error"}})
        elif model == "m404":
            self.reply(404, {"error": {"message": "The model `m404` does not exist", "type": "invalid_request_error"}})
        elif model == "m1211":
            self.reply(400, {"error": {"code": "1211", "message": "Unknown Model, please check the model code."}})
        else:
            self.reply(500, {"error": {"message": "boom"}})

srv = HTTPServer(("127.0.0.1", 0), H)
open(sys.argv[1], "w").write(str(srv.server_address[1]))
srv.serve_forever()
PYEOF
: > "$T/seen"
"$PY" "$T/server.py" "$T/port" "$T/seen" &
SRV=$!
for _ in $(seq 1 50); do [ -s "$T/port" ] && break; sleep 0.1; done
[ -s "$T/port" ] || { echo "FAIL fake server did not start"; exit 1; }
export MMO_API_FAKE_URL="http://127.0.0.1:$(cat "$T/port")/v1"
export MMO_API_FAKE_KEY="$KEY"

mkdir -p "$T/bin"
echo "Say hello." > "$T/brief"

# --- api lane ---
run api --brief "$T/brief" -m FAKE:good/x:8b
if [ $? -eq 0 ] && header | grep -q "status=ok" && header | grep -q "mode=ro"; then ok "good answer"; else bad "good answer"; fi
if "$PY" - "$T/out" <<'PYEOF'
import sys
t = open(sys.argv[1], encoding="utf-8").read()
sys.exit(0 if "héllo ✓ Ünïcode model=good/x:8b" in t else 1)
PYEOF
then ok "non-ASCII text and a model id with slash and colon survive"; else bad "non-ASCII text survives"; fi
if grep -q '^/v1/chat/completions|Bearer '"$KEY"'|good/x:8b$' "$T/seen"; then ok "request path, bearer key and model reach the server"; else bad "request reaches the server"; fi
if ! grep -rq "$KEY" "$T/out" "$T/log"; then ok "key is not in the out file or the log"; else bad "key leaked"; fi

for pair in "m401:7:auth" "m402:6:limit" "m429:6:limit" "m404:8:model" "m1211:8:model"; do
  m="${pair%%:*}"; rest="${pair#*:}"; rc="${rest%%:*}"; st="${rest#*:}"
  run api --brief "$T/brief" -m "FAKE:$m"; got=$?
  if [ $got -eq "$rc" ] && header | grep -q "status=$st"; then ok "$m -> $st"; else bad "$m -> $st (rc=$got)"; fi
  if grep -rq "$KEY" "$T/out" "$T/log"; then bad "key leaked on $m"; fi
done
run api --brief "$T/brief" -m FAKE:m500
if [ $? -eq 3 ] && header | grep -q "status=failed" && grep -q "HTTP 500 FAKE: boom" "$T/out"; then ok "HTTP 500 is a plain failure with the message"; else bad "HTTP 500"; fi

( unset MMO_API_FAKE_KEY; run api --brief "$T/brief" -m FAKE:good )
if [ $? -eq 7 ] && header | grep -q "status=auth" && grep -q "no API key: set MMO_API_FAKE_KEY" "$T/out"; then ok "missing key -> auth"; else bad "missing key -> auth"; fi
( unset DEEPSEEK_API_KEY; run api --brief "$T/brief" -m deepseek:deepseek-v4-pro )
if [ $? -eq 7 ] && grep -q "no API key: set DEEPSEEK_API_KEY" "$T/out"; then ok "table endpoint names its key variable"; else bad "table endpoint key variable"; fi

run api --brief "$T/brief"
if [ $? -ne 0 ] && grep -q "endpoint:model" "$T/out"; then ok "no model names the endpoint:model format"; else bad "no model"; fi
run api --brief "$T/brief" -m justamodel
if [ $? -ne 0 ] && grep -q "endpoint:model" "$T/out"; then ok "model without endpoint is refused"; else bad "model without endpoint"; fi
run api --brief "$T/brief" -m NOPE:x
if [ $? -ne 0 ] && grep -q "unknown endpoint" "$T/out"; then ok "unknown endpoint is refused"; else bad "unknown endpoint"; fi

( export MMO_API_FAKE2_URL="http://127.0.0.1:1/v1" MMO_API_FAKE2_KEY=k; run api --brief "$T/brief" -m FAKE2:good -t 30 )
if [ $? -eq 3 ] && grep -q "network error" "$T/out"; then ok "network error"; else bad "network error"; fi

run api --mode rw --brief "$T/brief" -m FAKE:good
if [ $? -eq 2 ]; then ok "rw refused (exit 2)"; else bad "rw refused"; fi

# --- Claude Code on another vendor, with a fake claude that returns the environment it got ---
cat > "$T/bin/claude" <<'SH'
#!/bin/sh
printf '{"result": "BASE=%s TOKEN=%s APIKEY=[%s] MODEL=%s OPUS=%s SONNET=%s HAIKU=%s SUB=%s"}\n' \
  "$ANTHROPIC_BASE_URL" "$ANTHROPIC_AUTH_TOKEN" "$ANTHROPIC_API_KEY" "$ANTHROPIC_MODEL" \
  "$ANTHROPIC_DEFAULT_OPUS_MODEL" "$ANTHROPIC_DEFAULT_SONNET_MODEL" "$ANTHROPIC_DEFAULT_HAIKU_MODEL" "$CLAUDE_CODE_SUBAGENT_MODEL"
SH
chmod +x "$T/bin/claude"

check_vendor() { # lane, key variable, base url, default model
  local lane="$1" var="$2" base="$3" model="$4"
  ( export "$var=vendor-key-1"; ANTHROPIC_API_KEY=should-be-cleared run "$lane" --brief "$T/brief" )
  if [ $? -eq 0 ] && header | grep -q "status=ok" \
     && grep -q "BASE=$base TOKEN=vendor-key-1 APIKEY=\[\] MODEL=$model OPUS=$model SONNET=$model HAIKU=$model" "$T/out"; then
    ok "$lane: base url, token and model variables arrive"
  else bad "$lane: environment"; fi
  ( export "$var=vendor-key-1"; run "$lane" --brief "$T/brief" -m custom-id )
  if grep -q "MODEL=custom-id OPUS=custom-id" "$T/out"; then ok "$lane: -m sets the model variables"; else bad "$lane: -m"; fi
  ( unset "$var"; run "$lane" --brief "$T/brief" )
  if [ $? -eq 7 ] && header | grep -q "status=auth" && grep -q "set $var" "$T/out"; then ok "$lane: missing key -> auth"; else bad "$lane: missing key"; fi
}
check_vendor claude-deepseek DEEPSEEK_API_KEY "https://api.deepseek.com/anthropic" deepseek-v4-pro
check_vendor claude-kimi MOONSHOT_API_KEY "https://api.moonshot.ai/anthropic" kimi-k3
check_vendor claude-minimax MINIMAX_API_KEY "https://api.minimax.io/anthropic" MiniMax-M3.1-Flash

list="$(PATH="$T/bin:$PATH" env -u DEEPSEEK_API_KEY bash "$HERE/mmo-run" --list)"
if echo "$list" | grep "^claude-deepseek " | grep -q setup; then ok "--list shows a vendor lane without its key as setup"; else bad "--list setup state"; fi

# The key file serves every lane: a claude-* lane gets its key from the file, and --list sees it too.
printf 'DEEPSEEK_API_KEY=file-key-77
' > "$T/keys.env"
( unset DEEPSEEK_API_KEY; MMO_KEYS_FILE="$T/keys.env" run claude-deepseek --brief "$T/brief" )
if [ $? -eq 0 ] && grep -q "TOKEN=file-key-77" "$T/out"; then ok "claude-deepseek takes its key from the key file"; else bad "key file reaches claude-deepseek"; fi
list="$(PATH="$T/bin:$PATH" env -u DEEPSEEK_API_KEY MMO_KEYS_FILE="$T/keys.env" bash "$HERE/mmo-run" --list)"
if echo "$list" | grep "^claude-deepseek " | grep -q " ok "; then ok "--list shows a lane as ok when the key is only in the key file"; else bad "--list with key file"; fi
list="$(PATH="$T/bin:$PATH" env -u DEEPSEEK_API_KEY bash "$HERE/mmo-run" --list)"
if echo "$list" | grep "^claude-deepseek " | grep -q " setup "; then ok "--list shows setup when the key is nowhere"; else bad "--list without key"; fi

# --- classifier strings for the api lane ---
cl() { printf '%s\n' "$2" > "$T/e"; got="$("$PY" "$HERE/mmo_classify.py" api "$T/brief" "$T/e")"; [ "$got" = "$1" ] && ok "classify '$2' -> $1" || { echo "FAIL classify '$2': got $got"; fail=1; }; }
cl auth "HTTP 401 openrouter: No auth credentials found"
cl auth "no API key: set OPENROUTER_API_KEY"
cl limit "HTTP 402 openrouter: Insufficient credits"
cl limit "HTTP 429 groq: Rate limit reached"
cl model "HTTP 404 openrouter: The model xyz does not exist"
cl model "HTTP 400 mistral: model foo not found"
cl model "HTTP 400 zai: Request failed (code 1211)"
cl failed "network error: connection refused"
exit $fail
