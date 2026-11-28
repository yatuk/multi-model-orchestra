#!/usr/bin/env bash
# Offline test for usage capture, --cost, --max-cost and the quota memory: fake CLIs on PATH, a fake chat
# server on 127.0.0.1, a temp HOME, no real key or price file. No model is called.
# Run: bash skills/orchestra/scripts/test-mmo-usage.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"
SRV=""
trap '[ -n "$SRV" ] && kill "$SRV" 2>/dev/null; rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; [ -f "$T/out" ] && sed 's/^/    /' "$T/out"; fail=1; }
chk() { # name, command: passes when the command succeeds
  if eval "$2"; then ok "$1"; else bad "$1"; fi
}
export MMO_KEYS_FILE="$T/no-such-keys.env"
export HOME="$T/home"; mkdir -p "$HOME"
unset MMO_PRICES MMO_LOG MMO_TASK
LOG="$T/log.jsonl"
run() { PATH="$T/bin:$PATH" MMO_LOG="$LOG" bash "$HERE/mmo-run" "$@" --out "$T/out" 2> "$T/err"; }
header() { head -1 "$T/out"; }
lastlog() { tail -n 1 "$LOG"; }
jget() { "$PY" -c 'import json,sys; d=json.loads(sys.argv[1]); v=d.get(sys.argv[2]); print("<absent>" if v is None else v)' "$(lastlog)" "$1"; }

mkdir -p "$T/bin"
fake() { printf '#!/bin/sh\n%s\n' "$2" > "$T/bin/$1"; chmod +x "$T/bin/$1"; }
echo "Say PONG." > "$T/brief"

# ---------------------------------------------------------------- 1. usage from claude JSON
CJ='{"type":"result","subtype":"success","is_error":false,"result":"PONG","total_cost_usd":0.0123,"usage":{"input_tokens":1200,"output_tokens":80,"cache_read_input_tokens":900,"cache_creation_input_tokens":50},"modelUsage":{"claude-sonnet-4-6":{"inputTokens":1200,"outputTokens":80,"costUSD":0.0123}}}'
fake claude 'case "${FAKE_MODE:-ok}" in
  ok) echo '"'$CJ'"' ;;
  nousage) echo "{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,\"result\":\"PONG\"}" ;;
  other) echo "{\"type\":\"result\",\"result\":\"PONG\",\"total_cost_usd\":0.5,\"usage\":{\"input_tokens\":10,\"output_tokens\":5},\"modelUsage\":{\"claude-haiku-4-5\":{\"outputTokens\":5}}}" ;;
  budget) echo "{\"type\":\"result\",\"subtype\":\"error_max_budget_usd\",\"is_error\":true,\"total_cost_usd\":0.51,\"usage\":{\"input_tokens\":300,\"output_tokens\":40},\"result\":\"stopped\"}"; exit 1 ;;
  args) printf "%s\n" "$@" > "$FAKE_ARGS"; echo '"'$CJ'"' ;;
esac'

run claude --brief "$T/brief"
chk "claude: header carries in, out, cached and cost after seconds" 'header | grep -q "seconds=[0-9]* in=1200 out=80 cached=900 cost=0.0123 -->"'
chk "claude: the header is still one line, status first" '[ "$(header | grep -c "^<!-- mmo provider=claude model=sonnet mode=ro status=ok exit=0 ")" = 1 ] && [ "$(sed -n 2p "$T/out")" = PONG ]'
chk "claude: sonnet alias served by claude-sonnet-4-6 is not shown as a different model" '! header | grep -q "served="'
chk "claude: log line holds the numbers" '[ "$(jget tokens_in)" = 1200 ] && [ "$(jget tokens_out)" = 80 ] && [ "$(jget cost_usd)" = 0.0123 ] && [ "$(jget served_model)" = claude-sonnet-4-6 ]'

FAKE_MODE=other run claude --brief "$T/brief" -m opus
chk "claude: a different served model is named in the header" 'header | grep -q " served=claude-haiku-4-5 "'

FAKE_MODE=nousage run claude --brief "$T/brief"
chk "claude: no usage in the output, no usage fields" '! header | grep -qE " (in|out|cached|cost|served)="'
chk "claude: no usage in the output, none in the log" '[ "$(jget tokens_in)" = "<absent>" ] && [ "$(jget cost_usd)" = "<absent>" ] && [ "$(jget served_model)" = "<absent>" ]'

# A lane whose output has no known usage shape writes none, even if the text looks like it.
fake grok 'echo "{\"text\": \"PONG\", \"usage\": {\"input_tokens\": 5, \"output_tokens\": 6}, \"total_cost_usd\": 1}"; case "$*" in *--max-cost*) echo bad >&2 ;; esac'
run grok --brief "$T/brief"
chk "grok: unconfirmed usage shape is left out" '! header | grep -qE " (in|out|cost)=" && [ "$(jget tokens_out)" = "<absent>" ]'

# ---------------------------------------------------------------- 2. api lane through a fake server
cat > "$T/server.py" <<'PYEOF'
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def reply(self, code, obj, extra=None):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        model = body["model"]
        msg = {"role": "assistant", "content": "answer from " + model}
        if model == "priced":
            self.reply(200, {"model": "vendor/renamed-2026", "choices": [{"message": msg}],
                             "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "cost": 0.0042}})
        elif model == "plain":
            self.reply(200, {"model": "plain", "choices": [{"message": msg}],
                             "usage": {"prompt_tokens": 7, "completion_tokens": 3, "total_tokens": 10}})
        elif model == "bare":
            self.reply(200, {"choices": [{"message": msg}]})
        elif model == "slow":
            self.reply(429, {"error": {"message": "Rate limit reached"}}, {"Retry-After": "3600"})
        else:
            self.reply(500, {"error": {"message": "boom"}})

srv = HTTPServer(("127.0.0.1", 0), H)
open(sys.argv[1], "w").write(str(srv.server_address[1]))
srv.serve_forever()
PYEOF
"$PY" "$T/server.py" "$T/port" &
SRV=$!
for _ in $(seq 1 50); do [ -s "$T/port" ] && break; sleep 0.1; done
[ -s "$T/port" ] || { echo "FAIL fake server did not start"; exit 1; }
KEY="sk-test-SECRET-0123456789"
export MMO_API_FAKE_URL="http://127.0.0.1:$(cat "$T/port")/v1" MMO_API_FAKE_KEY="$KEY"

run api --brief "$T/brief" -m FAKE:priced
chk "api: answer on stdout stays the pure answer" '[ "$(sed -n 2p "$T/out")" = "answer from priced" ] && [ "$(wc -l < "$T/out" | tr -d " ")" = 2 ]'
chk "api: tokens and cost reported by the endpoint reach the header" 'header | grep -q " in=100 out=20 cost=0.0042 "'
chk "api: a served model that differs from the requested one is named" 'header | grep -q " served=vendor/renamed-2026 "'
chk "api: log line holds the numbers" '[ "$(jget tokens_in)" = 100 ] && [ "$(jget tokens_out)" = 20 ] && [ "$(jget cost_usd)" = 0.0042 ] && [ "$(jget served_model)" = vendor/renamed-2026 ]'
chk "api: no key in the out file, the log or the error output" '! grep -q "$KEY" "$T/out" "$T/err" "$LOG"'

run api --brief "$T/brief" -m FAKE:plain
chk "api: no cost in the response, no cost field" 'header | grep -q " in=7 out=3 " && ! header | grep -q "cost=" && [ "$(jget cost_usd)" = "<absent>" ] && ! header | grep -q "served="'
run api --brief "$T/brief" -m FAKE:bare
chk "api: a response with no usage object writes no usage" '! header | grep -qE " (in|out|cost|served)=" && [ "$(jget tokens_in)" = "<absent>" ]'

# The side file itself: only usage numbers and the model, never the key or the prompt.
SIDE="$T/side.json"
echo "a secret prompt word: PROMPTMARK" | MMO_API_USAGE_FILE="$SIDE" "$PY" "$HERE/mmo_api.py" FAKE:priced > "$T/stdout"
chk "api side file holds the usage object and the model only" '"$PY" - "$SIDE" <<PYX
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if d == {"usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "cost": 0.0042}, "model": "vendor/renamed-2026"} else 1)
PYX'
chk "api side file has neither the key nor the prompt" '! grep -q -e "$KEY" -e PROMPTMARK "$SIDE" && [ "$(cat "$T/stdout")" = "answer from priced" ]'
rm -f "$SIDE"; echo x | "$PY" "$HERE/mmo_api.py" FAKE:priced > /dev/null
chk "api writes no side file when the variable is not set" '[ ! -e "$SIDE" ]'

# ---------------------------------------------------------------- 3. 429 with Retry-After, quota memory in the header
run api --brief "$T/brief" -m FAKE:slow; rc=$?
chk "api 429: status limit, exit 6" '[ $rc -eq 6 ] && header | grep -q "status=limit"'
chk "api 429: the error line carries Retry-After" 'grep -q "HTTP 429 FAKE: Rate limit reached (Retry-After: 3600)" "$T/out"'
chk "api 429: header and log carry retry_after about an hour ahead" '"$PY" - "$(header)" "$(lastlog)" <<PYX
import datetime, json, re, sys
h = re.search(r" retry_after=(\S+)", sys.argv[1]).group(1)
l = json.loads(sys.argv[2])["retry_after"]
t = datetime.datetime.strptime(h, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
d = (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
sys.exit(0 if h == l and 3500 < d < 3700 else 1)
PYX'

# A limit message with no time remembers nothing.
fake grok 'echo "Error: usage limit reached, upgrade your plan" >&2; exit 1'
run grok --brief "$T/brief"; rc=$?
chk "limit without a time: status limit, no retry_after anywhere" '[ $rc -eq 6 ] && ! header | grep -q retry_after && [ "$(jget retry_after)" = "<absent>" ]'
# The brief echoed into stderr must not set a time.
echo "Reply by Dec 24 2099 9:00 AM if you can. Retry-After: 99" > "$T/brief2"
fake grok 'cat >&2 <<<"$*"; echo "Error: usage limit reached" >&2; exit 1'
run grok --brief "$T/brief2"
chk "a date quoted from the brief is not a return time" '! header | grep -q retry_after'

# ---------------------------------------------------------------- 4. --max-cost
fake vibe 'printf "%s\n" "$@" > "$FAKE_ARGS"; echo PONG'
FAKE_ARGS="$T/args.claude" FAKE_MODE=args run claude --brief "$T/brief" --max-cost 0.50
chk "--max-cost reaches the claude lane as --max-budget-usd" 'grep -qx -e "--max-budget-usd" "$T/args.claude" && grep -qx "0.50" "$T/args.claude" && ! grep -q "no cost ceiling" "$T/err"'
FAKE_ARGS="$T/args.vibe" run vibe --brief "$T/brief" --max-cost 0.25
chk "--max-cost reaches the vibe lane as --max-price" 'grep -qx -e "--max-price" "$T/args.vibe" && grep -qx "0.25" "$T/args.vibe"'
fake grok 'printf "%s\n" "$@" > "$FAKE_ARGS"; echo "{\"text\": \"PONG\"}"'
FAKE_ARGS="$T/args.grok" run grok --brief "$T/brief" --max-cost 1
chk "--max-cost on another lane is noted once and not passed" '[ "$(grep -c "no cost ceiling" "$T/err")" = 1 ] && ! grep -q -e "--max" "$T/args.grok"'
chk "the note names the lane and the value" 'grep -q "mmo-run: note: grok has no cost ceiling; --max-cost 1 is not enforced" "$T/err"'
run claude --brief "$T/brief" --max-cost abc; rc=$?
chk "--max-cost needs a number" '[ $rc -eq 2 ]'
run claude --brief "$T/brief" --max-cost 0; rc=$?
chk "--max-cost 0 is refused" '[ $rc -eq 2 ]'

FAKE_MODE=budget run claude --brief "$T/brief" --max-cost 0.5; rc=$?
chk "stopped at the ceiling: status limit, ceiling=cost, exit 6" '[ $rc -eq 6 ] && header | grep -q "status=limit" && header | grep -q " ceiling=cost "'
chk "stopped at the ceiling: the cost of the failed run is still recorded" 'header | grep -q " cost=0.51 " && [ "$(jget cost_usd)" = 0.51 ] && [ "$(jget status)" = limit ]'
FAKE_MODE=budget run claude --brief "$T/brief"; rc=$?
chk "the same output without --max-cost stays a plain failure" '[ $rc -eq 3 ] && header | grep -q "status=failed" && ! header | grep -q ceiling'

# ---------------------------------------------------------------- 5. mmo-score --cost
S() { bash "$HERE/mmo-score" "$@"; }
has() { case "$3" in *"$2"*) ok "$1";; *) bad "$1"; printf '    wanted to contain: %s\n    got:\n%s\n' "$2" "$3";; esac; }
hasnt() { case "$3" in *"$2"*) bad "$1"; printf '    must not contain: %s\n' "$2";; *) ok "$1";; esac; }
C="$T/cost.jsonl"
r() { printf '{"ts":"t","kind":"run","provider":"%s","model":"%s","status":"%s","seconds":5,"task":"%s"%s}\n' "$@"; }
c() { printf '{"ts":"t","kind":"check","status":"%s","seconds":1,"task":"%s"}\n' "$@"; }
{
  # cheap lane: three runs on t1 (two failures, then a pass) and one on t2 that fails its check
  r kimi k3 ok t1 ',"tokens_in":1000,"tokens_out":100,"cost_usd":0.01'; c fail t1
  r kimi k3 ok t1 ',"tokens_in":1000,"tokens_out":100,"cost_usd":0.01'; c fail t1
  r kimi k3 ok t1 ',"tokens_in":1000,"tokens_out":100,"cost_usd":0.01'; c pass t1
  r kimi k3 ok t2 ',"tokens_in":500,"tokens_out":50,"cost_usd":0.005'; c fail t2
  # dearer lane: passes first time
  r claude sonnet ok t3 ',"tokens_in":2000,"tokens_out":200,"cost_usd":0.06'; c pass t3
  # api lane: tokens, no reported cost, passes
  r api fake:m ok t4 ',"tokens_in":1000000,"tokens_out":500000'; c pass t4
  # a lane that reports nothing
  r codex gpt-6.1-sol ok t5 ''; c pass t5
  r codex gpt-6.1-sol ok t6 ''
} > "$C"
out="$(S "$C" --cost)"
has "--cost has the header columns" "REPORTED" "$out"
kimi_row="$(printf '%s\n' "$out" | grep '^kimi/k3')"
chk "--cost: kimi sums runs, reported cost and tokens" 'echo "$kimi_row" | grep -qE "^kimi/k3 +4 +4 +\\\$0.0350 +- +3500 +350 +1 "'
chk "--cost: cost per passed task counts the retries (0.035 over one passed task)" 'echo "$kimi_row" | grep -qE "\\\$0.0350 +-$"'
claude_row="$(printf '%s\n' "$out" | grep '^claude/sonnet')"
chk "--cost: the lane that passes first time shows its own cost per passed task" 'echo "$claude_row" | grep -qE "\\\$0.0600 +- +2000 +200 +1 +\\\$0.0600"'
codex_row="$(printf '%s\n' "$out" | grep '^codex/gpt-6.1-sol')"
chk "--cost: runs with no reported cost are not free" 'echo "$codex_row" | grep -qE "^codex/gpt-6.1-sol +2 +0 +- +- +- +- +1 +- +-$"'
has "--cost says how many runs had a reported cost" "codex/gpt-6.1-sol: 2 runs, 0 with reported cost" "$out"
chk "--cost shows no estimate without a price file" '! printf "%s\n" "$out" | grep -qE "~\\$[0-9]"'
chk "--cost: the lane that reports no tokens shows dashes, never zero" '! echo "$codex_row" | grep -q "\\\$0.0000"'

printf '# my prices, fake numbers\n\n# comment only\napi/fake:*   2.00  4.00  # per million\nkimi/*  1  1\nbroken line here\n' > "$T/prices"
out="$(S "$C" --cost --prices "$T/prices")"
api_row="$(printf '%s\n' "$out" | grep '^api/fake:m')"
chk "--cost with prices: a run with tokens and no cost gets an estimate marked ~" 'echo "$api_row" | grep -qE "^api/fake:m +1 +0 +- +~\\\$4.00 "'
chk "--cost with prices: per-pass estimate is marked and the reported column stays empty" 'echo "$api_row" | grep -qE " - +~\\\$4.00$"'
has "--cost with prices: explains the ~" "never added to REPORTED" "$out"
has "--cost with prices: bad price lines are counted" "price file: 1 line(s) ignored" "$out"
chk "--cost: a reported cost is never replaced by an estimate" 'printf "%s\n" "$out" | grep "^kimi/k3" | grep -qE "\\\$0.0350 +- "'
out="$(MMO_PRICES="$T/prices" S "$C" --cost)"
has "MMO_PRICES selects the price file" "~\$4.00" "$out"
mkdir -p "$HOME/.config/mmo"; cp "$T/prices" "$HOME/.config/mmo/prices"
has "~/.config/mmo/prices is read when nothing else is set" "~\$4.00" "$(S "$C" --cost)"
rm -f "$HOME/.config/mmo/prices"
printf 'api/*  1  1\napi/fake:*  100 100\n' > "$T/prices2"
has "the first matching price line wins" "~\$1.50" "$(S "$C" --cost --prices "$T/prices2")"
printf 'api/fake:* 2 4 0.5\n' > "$T/prices3"
{ r api fake:m ok t7 ',"tokens_in":1000000,"tokens_out":1000000,"tokens_cached":2000000'; c pass t7; } > "$T/cached.jsonl"
has "a cached price line prices cached tokens" "~\$7.00" "$(S "$T/cached.jsonl" --cost --prices "$T/prices3")"
: > "$T/empty.jsonl"
has "an empty log says so" "no runs in the log" "$(S "$T/empty.jsonl" --cost)"
hasnt "the default table is unchanged by the new fields" "COSTED" "$(S "$C")"

# ---------------------------------------------------------------- 6. quota memory in mmo-roster
mkdir -p "$T/runner/providers" "$T/rbin"
cp "$HERE/mmo-run" "$HERE/mmo_extract.py" "$HERE/mmo_classify.py" "$HERE/mmo_usage.py" "$HERE/mmo_limit.py" "$T/runner/"
export MMO_RUN="$T/runner/mmo-run"
prov() {
  cat > "$T/runner/providers/$1.sh" <<P
LANE_BIN=$1
LANE_DEFAULT_MODEL="m1"
LANE_FAMILY=any
LANE_RO=sandbox
LANE_EXTRACT=text
LANE_VERIFIED=docs-test
lane_cmd() { CMD=("\$LANE_BIN" "\$PROMPT"); }
P
}
rfake() { printf '#!/bin/sh\n%s\n' "$2" > "$T/rbin/$1"; chmod +x "$T/rbin/$1"; }
prov waitlane; prov notime; prov goodlane
COUNT="$T/count"; : > "$COUNT"
rfake waitlane 'echo waitlane >> "'"$COUNT"'"; echo "Error: you have hit your usage limit. Retry-After: 7200" >&2; exit 1'
rfake notime 'echo notime >> "'"$COUNT"'"; echo "Error: you have hit your usage limit." >&2; exit 1'
rfake goodlane 'echo goodlane >> "'"$COUNT"'"; echo PONG'
R="$T/roster.json"
roster() { PATH="$T/rbin:$PATH" bash "$HERE/mmo-roster" "$@" > "$T/stdout" 2> "$T/stderr"; }
calls() { grep -c "^$1\$" "$COUNT"; }
roster probe --out "$R" --lanes waitlane,notime,goodlane -t 20
chk "roster: first probe calls every lane once" '[ "$(calls waitlane)" = 1 ] && [ "$(calls notime)" = 1 ] && [ "$(calls goodlane)" = 1 ]'
rfield() { "$PY" - "$R" "$1" "$2" <<'PYX'
import json, sys
for x in json.load(open(sys.argv[1]))["lanes"]:
    if x["lane"] == sys.argv[2]:
        print(x.get(sys.argv[3], "<absent>"))
PYX
}
chk "roster: a limit with a return time stores retry_after" '[ "$(rfield waitlane status)" = limit ] && [ "$(rfield waitlane retry_after)" != "<absent>" ]'
chk "roster: a limit with no time stores nothing" '[ "$(rfield notime status)" = limit ] && [ "$(rfield notime retry_after)" = "<absent>" ]'
roster probe --out "$R" --lanes waitlane,notime,goodlane -t 20
chk "roster: the lane with a future return time is not called again" '[ "$(calls waitlane)" = 1 ]'
chk "roster: the lane with no known time is probed again" '[ "$(calls notime)" = 2 ] && [ "$(calls goodlane)" = 2 ]'
roster show --file "$R"
chk "roster show says limit until <date time> for the held lane" 'grep "^waitlane" "$T/stdout" | grep -qE "limit until 20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9][0-9]:[0-9][0-9]"'
chk "roster show keeps the plain wording for the lane with no time" 'grep "^notime" "$T/stdout" | grep -q "hit your usage limit" && ! grep "^notime" "$T/stdout" | grep -q "limit until"'
roster lineup --file "$R"
chk "roster lineup says limit until for the held lane" 'grep -qE "waitlane \(limit until 20[0-9][0-9]-" "$T/stdout"'
chk "roster: held lane is not ready" '[ "$(roster ready --tier cheap --file "$R"; cat "$T/stdout")" != "" ] && ! grep -q waitlane "$T/stdout"'
# Once the time has passed the lane is probed again.
"$PY" - "$R" <<'PYX'
import json, sys
r = json.load(open(sys.argv[1]))
for x in r["lanes"]:
    if x["lane"] == "waitlane":
        x["retry_after"] = "2020-01-01T00:00:00Z"
json.dump(r, open(sys.argv[1], "w"))
PYX
roster probe --out "$R" --lanes waitlane,notime,goodlane -t 20
chk "roster: a passed return time means the lane is probed again" '[ "$(calls waitlane)" = 2 ]'
chk "roster: a stored junk time is ignored, not trusted" '"$PY" - "$R" <<PYX
import json, sys
r = json.load(open(sys.argv[1]))
for x in r["lanes"]:
    if x["lane"] == "waitlane":
        x["retry_after"] = "next tuesday"
json.dump(r, open(sys.argv[1], "w"))
PYX
roster probe --out "$R" --lanes waitlane -t 20; [ "$(calls waitlane)" = 3 ]'

[ $fail -eq 0 ] && echo "all usage tests passed" || { echo "some usage tests FAILED"; exit 1; }
