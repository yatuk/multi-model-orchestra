#!/usr/bin/env bash
# Offline test for mmo-cloud: a fake HTTP server on 127.0.0.1 stands in for every vendor.
# No real network call is made. Run: bash skills/orchestra/scripts/test-mmo-cloud.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"
SRV=""
trap '[ -n "$SRV" ] && kill "$SRV" 2>/dev/null; rm -rf "$T"' EXIT
fail=0; passed=0
ok() { echo "PASS $1"; passed=$((passed + 1)); }
bad() { echo "FAIL $1"; sed 's/^/    /' "$T/out" "$T/err" 2>/dev/null; fail=1; }

# The fake vendor: routes.json maps "METHOD /path" to a list of responses. Each request takes the
# first one; the last one repeats. Every request is logged so a case can check what was sent.
cat > "$T/server.py" <<'EOF'
import json, sys, http.server
routes, log, portfile = sys.argv[1:4]
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle_one(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n).decode() if n else ""
        with open(routes) as f: r = json.load(f)
        key = self.command + " " + self.path
        seq = r.get(key) or [{"code": 404, "body": {"error": {"code": "not_found", "message": key}}}]
        resp = seq[0]
        if len(seq) > 1:
            r[key] = seq[1:]
            with open(routes, "w") as f: json.dump(r, f)
        with open(log, "a") as f:
            f.write(json.dumps({"key": key, "body": body,
                                "auth": self.headers.get("Authorization", "")}) + "\n")
        data = json.dumps(resp.get("body", {})).encode()
        self.send_response(resp.get("code", 200))
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)
    do_GET = do_POST = do_DELETE = handle_one
s = http.server.HTTPServer(("127.0.0.1", 0), H)
open(portfile, "w").write(str(s.server_port))
s.serve_forever()
EOF
echo '{}' > "$T/routes.json"
"$PY" "$T/server.py" "$T/routes.json" "$T/reqs.log" "$T/port" &
SRV=$!
for _ in $(seq 100); do [ -s "$T/port" ] && break; sleep 0.1; done
[ -s "$T/port" ] || { echo "FAIL fake server did not start"; exit 1; }
URL="http://127.0.0.1:$(cat "$T/port")"

KEY="cog_SECRETKEY0123456789"
export MMO_DEVIN_BASE="$URL" MMO_CURSOR_BASE="$URL" MMO_COPILOT_BASE="$URL"
export DEVIN_API_KEY="$KEY" DEVIN_ORG_ID="org-test" CURSOR_API_KEY="$KEY" COPILOT_AGENT_TOKEN="$KEY"
echo "Fix the flaky test in a.py." > "$T/brief"
: > "$T/all"
DEV="/v3/organizations/org-test/sessions"

routes() { printf '%s' "$1" > "$T/routes.json"; : > "$T/reqs.log"; }
mc() { bash "$HERE/mmo-cloud" "$@" > "$T/out" 2> "$T/err"; rc=$?; cat "$T/out" "$T/err" >> "$T/all"; return $rc; }
head1() { head -1 "$T/out"; }
newstate() { rm -f "$T/state.json"; }
# A state file written by hand, so status cases do not depend on start.
state() { # agent id [extra json]
  printf '{"agent":"%s","id":"%s","repo":"acme/app","base":"main","started":"x","cap":"none"%s}' \
    "$1" "$2" "${3:-}" > "$T/state.json"
}

# ---- start
newstate
routes "{\"POST $DEV\": [{\"code\": 200, \"body\": {\"session_id\": \"devin-1\", \"url\": \"https://app.example/devin-1\"}}]}"
mc start devin --brief "$T/brief" --repo acme/app --base main --cap 5 --state "$T/state.json"
if [ $? -eq 0 ] && head1 | grep -q "status=started id=devin-1 cap=5acu" && grep -q '"id": "devin-1"' "$T/state.json" \
   && grep -q '\\"max_acu_limit\\": 5' "$T/reqs.log" && grep -q "Bearer $KEY" "$T/reqs.log"; then
  ok "devin start writes state and sends the ACU cap"; else bad "devin start writes state and sends the ACU cap"; fi

newstate; routes '{}'
mc start devin --brief "$T/brief" --repo acme/app --state "$T/state.json"
if [ $? -eq 2 ] && grep -q "pass --cap" "$T/err" && [ ! -s "$T/reqs.log" ] && [ ! -e "$T/state.json" ]; then
  ok "devin start refused without --cap"; else bad "devin start refused without --cap"; fi

mc start cursor --brief "$T/brief" --repo acme/app --cap 5 --state "$T/state.json"
if [ $? -eq 2 ] && grep -q "no cap" "$T/err"; then ok "--cap refused for an agent with no cap"; else bad "--cap refused for an agent with no cap"; fi

newstate
routes '{"POST /v1/agents": [{"code": 200, "body": {"agent": {"id": "bc-1", "latestRunId": "run-1"}, "run": {"id": "run-1", "status": "CREATING"}}}]}'
mc start cursor --brief "$T/brief" --repo acme/app --base main --state "$T/state.json"
if [ $? -eq 0 ] && head1 | grep -q "cap=none" && grep -q "note: Cursor documents no cost or time cap" "$T/out" \
   && grep -q '"run_id": "run-1"' "$T/state.json" && grep -q 'autoCreatePR' "$T/reqs.log" && grep -q 'startingRef' "$T/reqs.log"; then
  ok "cursor start says there is no cap"; else bad "cursor start says there is no cap"; fi

newstate
routes '{"POST /agents/repos/acme/app/tasks": [{"code": 201, "body": {"id": "task-9", "state": "queued"}}]}'
mc start copilot --brief "$T/brief" --repo acme/app --base main --state "$T/state.json"
if [ $? -eq 0 ] && head1 | grep -q "id=task-9" && grep -q "59 minutes" "$T/out" && grep -q 'create_pull_request' "$T/reqs.log" && grep -q 'base_ref' "$T/reqs.log"; then
  ok "copilot start asks for a PR on the base branch"; else bad "copilot start asks for a PR on the base branch"; fi

newstate
( unset DEVIN_API_KEY; mc start devin --brief "$T/brief" --repo acme/app --cap 5 --state "$T/state.json" ); rc=$?
cat "$T/out" "$T/err" >> "$T/all"
if [ $rc -eq 7 ] && grep -q "DEVIN_API_KEY is not set" "$T/err"; then ok "missing key is auth"; else bad "missing key is auth"; fi

newstate
routes "{\"POST $DEV\": [{\"code\": 401, \"body\": {\"detail\": \"invalid token $KEY\"}}]}"
mc start devin --brief "$T/brief" --repo acme/app --cap 5 --state "$T/state.json"
if [ $? -eq 7 ] && head1 | grep -q "status=auth" && [ ! -e "$T/state.json" ]; then ok "401 is auth"; else bad "401 is auth"; fi

routes "{\"POST $DEV\": [{\"code\": 429, \"body\": {\"detail\": \"rate limited\"}}]}"
mc start devin --brief "$T/brief" --repo acme/app --cap 5 --state "$T/state.json"
if [ $? -eq 6 ] && head1 | grep -q "status=limit"; then ok "429 is limit"; else bad "429 is limit"; fi

routes '{"POST /v1/agents": [{"code": 403, "body": {"error": {"code": "plan_required", "message": "upgrade"}}}]}'
mc start cursor --brief "$T/brief" --repo acme/app --state "$T/state.json"
if [ $? -eq 6 ]; then ok "cursor plan_required is limit"; else bad "cursor plan_required is limit"; fi

mc start devin --brief "$T/brief" --repo "not a repo" --cap 5 --state "$T/state.json"
if [ $? -eq 2 ]; then ok "bad --repo is usage"; else bad "bad --repo is usage"; fi

# ---- status mapping, one case per documented vendor state
check_map() { # agent label route-json expected
  state "$1" "$2" "${5:-}"; routes "$3"; mc status --state "$T/state.json"
  if head1 | grep -q "status=$4 "; then ok "$1 $6 -> $4"; else bad "$1 $6 -> $4"; fi
}
for pair in new:queued claimed:queued running:running resuming:running exit:done error:failed suspended:waiting; do
  s="${pair%%:*}"; want="${pair#*:}"
  check_map devin devin-1 "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"$s\"}}]}" "$want" "" "status $s"
done
for pair in working:running waiting_for_user:waiting waiting_for_approval:waiting finished:done inactivity:expired \
            user_request:cancelled usage_limit_exceeded:limit out_of_credits:limit out_of_quota:limit \
            no_quota_allocation:limit payment_declined:limit org_usage_limit_exceeded:limit \
            user_usage_limit_exceeded:limit total_session_limit_exceeded:limit contract_expired:limit error:failed; do
  d="${pair%%:*}"; want="${pair#*:}"
  check_map devin devin-1 "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"suspended\", \"status_detail\": \"$d\"}}]}" "$want" "" "detail $d"
done
for pair in CREATING:queued RUNNING:running WAITING_FOR_BACKGROUND_WORK:running FINISHED:done ERROR:failed CANCELLED:cancelled EXPIRED:expired; do
  s="${pair%%:*}"; want="${pair#*:}"
  check_map cursor bc-1 "{\"GET /v1/agents/bc-1/runs/run-1\": [{\"body\": {\"id\": \"run-1\", \"status\": \"$s\", \"git\": {\"branches\": []}}}]}" "$want" ',"run_id":"run-1"' "run $s"
done
for pair in queued:queued in_progress:running completed:done failed:failed waiting_for_user:waiting timed_out:expired cancelled:cancelled idle:waiting; do
  s="${pair%%:*}"; want="${pair#*:}"
  check_map copilot task-9 "{\"GET /agents/repos/acme/app/tasks/task-9\": [{\"body\": {\"id\": \"task-9\", \"state\": \"$s\"}}]}" "$want" "" "state $s"
done
check_map copilot task-9 '{"GET /agents/repos/acme/app/tasks/task-9": [{"body": {"state": "idle", "artifacts": [{"type": "branch", "data": {"head_ref": "copilot/fix"}}]}}]}' done "" "idle with a branch"
check_map devin devin-1 "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"teleported\"}}]}" failed "" "unknown status"

state devin devin-1; routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"suspended\", \"status_detail\": \"out_of_credits\"}}]}"
mc status --state "$T/state.json"
if [ $? -eq 6 ] && grep -q '"last_status": "limit"' "$T/state.json"; then ok "out of credits exits 6 and is saved"; else bad "out of credits exits 6 and is saved"; fi

state devin devin-1; routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"running\", \"status_detail\": \"waiting_for_user\"}}]}"
mc status --state "$T/state.json"
if [ $? -eq 10 ]; then ok "waiting exits 10"; else bad "waiting exits 10"; fi

state devin devin-1; routes "{\"GET $DEV/devin-1\": [{\"code\": 401, \"body\": {}}]}"
mc status --state "$T/state.json"
if [ $? -eq 7 ] && head1 | grep -q "status=auth"; then ok "status 401 is auth"; else bad "status 401 is auth"; fi

# ---- wait
state devin devin-1; routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"running\", \"status_detail\": \"working\"}}]}"
t0=$(date +%s); mc wait --state "$T/state.json" -t 2 --every 0.5; rc=$?; t1=$(date +%s)
if [ $rc -eq 4 ] && head1 | grep -q "status=timeout" && [ $((t1 - t0)) -lt 10 ] && [ "$(wc -l < "$T/reqs.log")" -ge 2 ]; then
  ok "wait times out with exit 4"; else bad "wait times out with exit 4"; fi

state devin devin-1
routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"new\"}}, {\"body\": {\"status\": \"running\", \"status_detail\": \"working\"}}, {\"body\": {\"status\": \"exit\", \"status_detail\": \"finished\"}}]}"
mc wait --state "$T/state.json" -t 20 --every 0.2
if [ $? -eq 0 ] && head1 | grep -q "status=done" && [ "$(wc -l < "$T/reqs.log")" -eq 3 ]; then ok "wait polls until done"; else bad "wait polls until done"; fi

mc wait --state "$T/state.json"
if [ $? -eq 2 ]; then ok "wait without -t is usage (never waits forever)"; else bad "wait without -t is usage (never waits forever)"; fi

# ---- result
state devin devin-1
routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"exit\", \"status_detail\": \"finished\", \"pull_requests\": [{\"pr_url\": \"https://github.com/acme/app/pull/7\", \"pr_state\": \"open\"}]}}]}"
mc result --state "$T/state.json"
if [ $? -eq 0 ] && grep -qx "pr=https://github.com/acme/app/pull/7" "$T/out"; then ok "devin result prints the PR URL"; else bad "devin result prints the PR URL"; fi

state cursor bc-1 ',"run_id":"run-1"'
routes '{"GET /v1/agents/bc-1/runs/run-1": [{"body": {"status": "FINISHED"}}], "GET /v1/agents/bc-1": [{"body": {"id": "bc-1", "git": {"branches": [{"repoUrl": "https://github.com/acme/app", "branch": "cursor/fix-1", "prUrl": "https://github.com/acme/app/pull/8"}]}}}]}'
mc result --state "$T/state.json"
if [ $? -eq 0 ] && grep -qx "branch=cursor/fix-1" "$T/out" && grep -qx "pr=https://github.com/acme/app/pull/8" "$T/out"; then
  ok "cursor result prints branch and PR"; else bad "cursor result prints branch and PR"; fi

state copilot task-9
routes '{"GET /agents/repos/acme/app/tasks/task-9": [{"body": {"state": "completed", "artifacts": [{"type": "pull", "data": {"id": 42}}, {"type": "branch", "data": {"head_ref": "copilot/fix", "base_ref": "main"}}]}}]}'
mc result --state "$T/state.json"
if [ $? -eq 0 ] && grep -qx "branch=copilot/fix" "$T/out" && grep -q "pull id 42" "$T/out"; then ok "copilot result prints branch and pull id"; else bad "copilot result prints branch and pull id"; fi

state devin devin-1; routes "{\"GET $DEV/devin-1\": [{\"body\": {\"status\": \"running\"}}]}"
mc result --state "$T/state.json"
if [ $? -eq 5 ]; then ok "result with no PR exits 5"; else bad "result with no PR exits 5"; fi

# ---- cancel
state devin devin-1; routes "{\"DELETE $DEV/devin-1\": [{\"body\": {}}]}"
mc cancel --state "$T/state.json"
if [ $? -eq 0 ] && grep -q "DELETE $DEV/devin-1" "$T/reqs.log" && head1 | grep -q "status=cancelled"; then ok "devin cancel sends DELETE"; else bad "devin cancel sends DELETE"; fi

state cursor bc-1 ',"run_id":"run-1"'; routes '{"POST /v1/agents/bc-1/runs/run-1/cancel": [{"body": {}}]}'
mc cancel --state "$T/state.json"
if [ $? -eq 0 ] && grep -q "runs/run-1/cancel" "$T/reqs.log"; then ok "cursor cancel posts to the run"; else bad "cursor cancel posts to the run"; fi

state copilot task-9; routes '{}'
mc cancel --state "$T/state.json"
if [ $? -eq 2 ] && grep -q "no documented cancel for copilot" "$T/err" && [ ! -s "$T/reqs.log" ]; then ok "copilot has no cancel"; else bad "copilot has no cancel"; fi

# ---- list and secrets
mc list
if [ $? -eq 0 ] && grep -q "^devin .*ok" "$T/out" && grep -q "not supported: jules" "$T/out"; then ok "list"; else bad "list"; fi
( unset CURSOR_API_KEY; bash "$HERE/mmo-cloud" list > "$T/out" 2>&1 )
if grep -q "^cursor .*absent" "$T/out"; then ok "list shows a missing key"; else bad "list shows a missing key"; fi

if ! grep -q "$KEY" "$T/all" && ! grep -rq "$KEY" "$T"/state.json; then ok "the key never appears in output or state"; else bad "the key never appears in output or state"; fi

echo "$passed passed"
exit $fail
