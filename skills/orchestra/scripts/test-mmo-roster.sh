#!/usr/bin/env bash
# Offline test for mmo-roster: a copy of mmo-run with fake providers, fake CLIs on PATH, no model calls.
# Run: bash skills/orchestra/scripts/test-mmo-roster.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; [ -f "$T/stdout" ] && sed 's/^/    /' "$T/stdout"; fail=1; }

# The runner copy: real mmo-run, real extractor and classifier, only fake providers next to it.
mkdir -p "$T/runner/providers" "$T/bin" "$T/home"
cp "$HERE/mmo-run" "$HERE/mmo_extract.py" "$HERE/mmo_classify.py" "$T/runner/"
export MMO_RUN="$T/runner/mmo-run"
prov() { # lane, default model, read-only kind
  cat > "$T/runner/providers/$1.sh" <<P
LANE_BIN=$1
LANE_DEFAULT_MODEL="$2"
LANE_FAMILY=any
LANE_RO=$3
LANE_EXTRACT=text
LANE_VERIFIED=docs-test
lane_cmd() { CMD=("\$LANE_BIN"); [ -n "\$MODEL" ] && CMD+=(--model "\$MODEL"); CMD+=("\$PROMPT"); }
P
}
fake() { printf '#!/bin/sh\n%s\n' "$2" > "$T/bin/$1"; chmod +x "$T/bin/$1"; }
prov fakeok m1 sandbox
prov fakelimit m2 sandbox
prov fakeauth m3 sandbox
prov fakenomodel "" sandbox
prov fakeslow m5 sandbox
prov fakeabsent m6 sandbox
fake fakeok 'case "$2" in bad-id) echo "error: unknown model bad-id" >&2; exit 1 ;; esac; echo PONG'
fake fakelimit 'echo "Error: You have hit your usage limit (api_key=sk-test1234567890abcdef). Try again at Dec 3rd, 2026 9:00 AM." >&2; exit 1'
fake fakeauth 'echo "$3" >&2; echo "Error: not logged in. Run fakeauth login" >&2; exit 1'
fake fakenomodel 'echo PONG'
fake fakeslow 'sleep 30; echo PONG'

R="$T/roster.json"
roster() { PATH="$T/bin:$PATH" HOME="$T/home" bash "$HERE/mmo-roster" "$@" > "$T/stdout" 2> "$T/stderr"; }
field() { python - "$R" "$1" "$2" "$3" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
for x in r["lanes"]:
    if x["lane"] == sys.argv[2] and (sys.argv[3] == "*" or x["model"] == sys.argv[3]):
        print(x.get(sys.argv[4], "")); break
PY
}

start=$(date +%s)
roster probe --out "$R" -t 3; rc=$?
secs=$(( $(date +%s) - start ))
[ $rc -eq 0 ] && [ -s "$R" ] && ok "probe writes the roster" || bad "probe writes the roster"
[ "$(field fakeok m1 status)" = ok ] && [ "$(field fakeok m1 ready)" = True ] && ok "ready lane" || bad "ready lane"
[ "$(field fakelimit '*' status)" = limit ] && grep -q "top up" "$R" && ok "limit lane, with the fix" || bad "limit lane, with the fix"
[ "$(field fakeauth '*' status)" = auth ] && [ "$(field fakeauth '*' error)" != "" ] && ok "auth lane, with its error line" || bad "auth lane, with its error line"
[ "$(field fakenomodel '*' status)" = needs-model ] && ok "lane without a default model is needs-model" || bad "needs-model"
[ "$(field fakeslow '*' status)" = timeout ] && ok "timeout lane" || bad "timeout lane"
[ "$(field fakeabsent '*' status)" = "" ] && ok "absent CLI is not probed" || bad "absent CLI is not probed"
[ $secs -lt 30 ] && ok "probe is bounded ($secs s)" || bad "probe is bounded ($secs s)"
if ! grep -q "Reply with exactly" "$R" && ! grep -q "sk-test1234567890abcdef" "$R" && ! grep -q "$T/home" "$R"; then
  ok "no brief, key or home path in the roster"; else bad "no brief, key or home path in the roster"; fi
grep -q "fakelimit" "$T/stdout" && grep -q "READY" "$T/stdout" && ok "probe prints the table" || bad "probe prints the table"

roster lineup --file "$R"; rc=$?
n=$(wc -l < "$T/stdout" | tr -d ' ')
if [ $rc -eq 0 ] && [ "$n" -le 8 ] && grep -q "cheap: fakeok m1" "$T/stdout" \
   && grep -q "strong: Claude opus (sub-agent)" "$T/stdout" && grep -q "second opinion: fakeok m1" "$T/stdout" \
   && grep -q "fakelimit (limit until Dec 3rd, 2026 9:00 AM)" "$T/stdout" && grep -q "fakeauth (not signed in)" "$T/stdout" \
   && grep -q "fakenomodel (needs a model id)" "$T/stdout" && grep -q "fakeslow (no answer in" "$T/stdout" \
   && ! grep -q '[|]' "$T/stdout" && ! grep -q "fakeabsent" "$T/stdout"; then
  ok "lineup: one line per tier, not-usable reasons, at most 8 lines"; else bad "lineup"; fi

# A models file: a model for the lane without a default, two for another, one rejected id.
printf 'fakenomodel some-flash\nfakeok fake-ultra\nfakeok bad-id\n' > "$T/models"
roster probe --out "$R" --lanes fakeok,fakenomodel --models "$T/models" -t 5
[ "$(field fakenomodel some-flash status)" = ok ] && [ "$(field fakenomodel some-flash tier)" = bulk ] && ok "models file gives a model; its id sets the tier" || bad "models file"
[ "$(field fakeok bad-id status)" = model ] && ok "rejected model id" || bad "rejected model id"
[ "$(field fakelimit '*' status)" = limit ] && ok "partial probe keeps the other lanes" || bad "partial probe keeps the other lanes"

roster ready --tier strong --file "$R"
[ "$(sed -n 1p "$T/stdout")" = "subagent opus" ] && [ "$(sed -n 2p "$T/stdout")" = "fakeok fake-ultra" ] \
  && ok "ready --tier strong: Claude Opus first, then external" || bad "ready --tier strong"
printf 'strong fakeok   # the user wants this lane first\nbulk subagent haiku\n' > "$T/prefer"
MMO_PREFER="$T/prefer" roster ready --tier strong --file "$R"
[ "$(sed -n 1p "$T/stdout")" = "fakeok fake-ultra" ] && ok "preference file reorders a tier" || bad "preference file reorders a tier"
MMO_PREFER="$T/prefer" roster ready --tier bulk --file "$R"
[ "$(sed -n 1p "$T/stdout")" = "subagent haiku" ] && ok "preference file can put a sub-agent first" || bad "preference file can put a sub-agent first"
roster ready --tier bulk --file "$R"
[ "$(sed -n 1p "$T/stdout")" = "fakenomodel some-flash" ] && ! grep -q fakelimit "$T/stdout" && ok "ready --tier lists only ready lanes" || bad "ready --tier bulk"
roster ready --tier nonsense --file "$R"; [ $? -eq 2 ] && ok "unknown tier is a usage error" || bad "unknown tier"

# Default models file: $MMO_MODELS, else ~/.config/mmo/models (a temp HOME here, never the real one).
mkdir -p "$T/home/.config/mmo"
printf '# comment line\n\nfakenomodel home-flash   # trailing comment\nfakenomodel home-two\n' > "$T/home/.config/mmo/models"
roster probe --out "$R" --lanes fakenomodel -t 5
[ "$(field fakenomodel home-flash status)" = ok ] && [ "$(field fakenomodel home-two status)" = ok ] \
  && ok "default models file in HOME is read; two models for one lane give two rows" || bad "default models file"
[ "$(field fakenomodel '*' model)" != "" ] && ! grep -q '"comment"' "$R" && ok "comments and blank lines are ignored" || bad "comments ignored"
printf 'fakenomodel flag-only\n' > "$T/flagmodels"
roster probe --out "$R" --lanes fakenomodel --models "$T/flagmodels" -t 5
[ "$(field fakenomodel flag-only status)" = ok ] && [ "$(field fakenomodel home-flash status)" = "" ] && ok "--models overrides the default file" || bad "--models overrides"
printf 'fakenomodel env-pick\n' > "$T/envmodels"
MMO_MODELS="$T/envmodels" roster probe --out "$R" --lanes fakenomodel -t 5
[ "$(field fakenomodel env-pick status)" = ok ] && [ "$(field fakenomodel home-flash status)" = "" ] && ok "MMO_MODELS overrides the home path" || bad "MMO_MODELS overrides"
rm -f "$T/home/.config/mmo/models"
roster probe --out "$R" --lanes fakenomodel -t 5
[ "$(field fakenomodel '*' status)" = needs-model ] && ok "no models file: needs-model as before" || bad "no models file"

# Write stage: three fake CLIs that stand in for a lane that works, one that cannot run, one that cannot write.
PYV="$(python --version 2>&1)"
prov fakewrok m1 sandbox; prov fakewnorun m1 sandbox; prov fakewnone m1 sandbox
fake fakewrok 'echo mmo-probe-7391 > probe.txt; python --version > ver.txt 2>&1; echo DONE'
fake fakewnorun 'echo mmo-probe-7391 > probe.txt; echo "Python 0.0.0" > ver.txt; echo DONE'
fake fakewnone 'echo DONE'
roster probe --out "$R" --lanes fakewrok,fakewnorun,fakewnone,fakeok --write -t 20 --write-timeout 30
[ "$(field fakewrok '*' can_write)" = true ] && [ "$(field fakewrok '*' can_run)" = true ] && ok "write stage: writes and runs" || bad "write stage: writes and runs"
[ "$(field fakewnorun '*' can_write)" = true ] && [ "$(field fakewnorun '*' can_run)" = false ] && ok "write stage: typed text without the real command output is can_run false" || bad "write stage: can_run false"
[ "$(field fakewnone '*' can_write)" = false ] && [ "$(field fakewnone '*' can_run)" = false ] && ok "write stage: nothing written is can_write false" || bad "write stage: can_write false"
grep -q "WRITE" "$T/stdout" && grep -E "^fakewnorun +" "$T/stdout" | grep -q "no-run" && grep -E "^fakewnone +" "$T/stdout" | grep -q "no-write" && ok "show has a compact WRITE column" || bad "WRITE column"
roster ready --tier cheap --file "$R"
grep -q "fakewnorun" "$T/stdout" && ok "ready without --for lists the lane as before" || bad "ready default unchanged"
roster ready --tier cheap --for write --file "$R"
if grep -q "fakewrok" "$T/stdout" && ! grep -q "fakewnorun" "$T/stdout" && ! grep -q "fakewnone" "$T/stdout"; then ok "ready --for write skips can_run false"; else bad "ready --for write"; fi
roster ready --tier nonsense --for write --file "$R" >/dev/null; [ $? -eq 2 ] && ok "ready --for write needs a real tier" || bad "ready --for"
# (a leftover would be a mmo-write-* folder in the temp dir)
left="$(python -c 'import glob,os,tempfile; print(len(glob.glob(os.path.join(tempfile.gettempdir(),"mmo-write-*"))))')"
[ "$left" = 0 ] && ok "write stage cleans its temp repos" || bad "write stage cleans its temp repos"
roster probe --out "$R" --lanes fakeok -t 5
[ "$(field fakeok '*' can_run)" = not-tested ] && ok "without --write nothing is tested" || bad "without --write"
# lineup names a lane that cannot run commands
python - "$R" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
for x in r["lanes"]:
    if x["kind"] == "external":
        x["can_run"] = "false"
json.dump(r, open(sys.argv[1], "w"))
PY
roster lineup --file "$R"
grep -q "cheap: .* (cannot run commands: give it answer-only work)" "$T/stdout" && ok "lineup marks a lane that cannot run commands" || bad "lineup marks"

# A lane whose model id starts with the lane's own name: every view prints "<lane> <model>", with a
# space and no slash, so a conductor copying it never writes lane/lane-model.
prov fakepre fakepre-v4-pro sandbox
fake fakepre 'echo PONG'
roster probe --out "$T/pre.json" --lanes fakepre -t 5
roster lineup --file "$T/pre.json"; grep -q "cheap: fakepre fakepre-v4-pro" "$T/stdout" && ! grep -q "fakepre/" "$T/stdout" && ok "lineup: lane and model joined by a space" || bad "lineup lane+model with a prefix"
roster ready --tier cheap --file "$T/pre.json"; [ "$(cat "$T/stdout")" = "fakepre fakepre-v4-pro" ] && ok "ready: lane and model joined by a space" || bad "ready lane+model with a prefix"
roster show --file "$T/pre.json"; ! grep -q "fakepre/" "$T/stdout" && grep -Eq "^fakepre +fakepre-v4-pro " "$T/stdout" && ok "show: lane and model in separate columns" || bad "show lane+model with a prefix"

# Pass rate only from 5 or more checked tasks.
L="$T/lanes.jsonl"; : > "$L"
for i in 1 2 3 4 5; do
  printf '{"kind":"run","provider":"fakeok","model":"m1","status":"ok","task":"T%s"}\n' "$i" >> "$L"
  st=pass; [ $i -eq 5 ] && st=fail
  printf '{"kind":"check","status":"%s","task":"T%s"}\n' "$st" "$i" >> "$L"
done
printf '{"kind":"lane","lane":"sonnet","task":"T9"}\n{"kind":"check","status":"pass","task":"T9"}\n' >> "$L"
MMO_LOG="$L" roster probe --out "$R" --lanes fakeok -t 5
[ "$(field fakeok m1 pass)" = "4/5" ] && [ "$(field subagent sonnet pass)" = "" ] && ok "pass rate from 5 checked tasks, none from 1" || bad "pass rate"
grep -q '"task"' "$L" && [ "$(grep -c . "$L")" -eq 12 ] && ok "probes do not write into MMO_LOG" || bad "probes do not write into MMO_LOG"

# Age: show exits 3 on a stale or missing roster; probe --max-age reuses a fresh one.
python - "$R" <<'PY'
import json, sys, time
r = json.load(open(sys.argv[1]))
for x in r["lanes"]:
    x["checked"] = time.time() - 13 * 3600
json.dump(r, open(sys.argv[1], "w"))
PY
roster show --file "$R"; rc=$?
[ $rc -eq 3 ] && grep -q "13.0 h ago" "$T/stdout" && ok "stale roster: show exits 3 and says how old" || bad "stale roster exit 3"
roster show --file "$R" --max-age 24; [ $? -eq 0 ] && ok "--max-age 24 accepts it" || bad "--max-age 24"
roster show --file "$T/none.json"; [ $? -eq 3 ] && ok "missing roster exits 3" || bad "missing roster exits 3"
start=$(date +%s); roster probe --out "$R" --max-age 24 -t 5
[ $(( $(date +%s) - start )) -lt 3 ] && grep -q "13.0 h ago" "$T/stdout" && ok "probe --max-age reuses a fresh roster" || bad "probe --max-age"

[ $fail -eq 0 ] && echo "all mmo-roster tests passed" || { echo "some mmo-roster tests FAILED"; exit 1; }
