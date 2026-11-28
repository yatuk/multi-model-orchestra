#!/usr/bin/env bash
# Offline tests for bench/grade.py: no model, no network.
# Proves the new tasks leave headroom and resist test editing:
#   reference solution = 1.00, starting code = low but not zero, an edited or deleted
#   visible test = 0.00 with the reason, special-casing the visible inputs = low.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
B="$ROOT/bench"
PY="$(command -v python3 || command -v python)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fails=0

check() {  # name, grade output, wanted score (exact "1.00" or "<0.50" or ">0.00"), detail substring
  local name="$1" out="$2" want="$3" sub="${4:-}" score ok=1
  score="$(printf '%s' "$out" | cut -f1)"
  case "$want" in
    "<"*) "$PY" -c "import sys; sys.exit(0 if float('$score') < float('${want#<}') else 1)" || ok=0 ;;
    ">"*) "$PY" -c "import sys; sys.exit(0 if float('$score') > float('${want#>}') else 1)" || ok=0 ;;
    *) [ "$score" = "$want" ] || ok=0 ;;
  esac
  if [ -n "$sub" ] && ! printf '%s' "$out" | grep -qF -- "$sub"; then ok=0; fi
  if [ $ok = 1 ]; then echo "ok   $name: $out"; else echo "FAIL $name (want $want ${sub:+with '$sub'}): $out"; fails=$((fails + 1)); fi
}

# A lane worktree as the lane would leave it: the starting files, then the lane's changes.
start_copy() { rm -rf "$T/$2"; mkdir -p "$T/$2"; cp -r "$B/tasks/$1/start/." "$T/$2/"; }
with_reference() { start_copy "$1" "$2"; cp -r "$B/reference/$1/." "$T/$2/"; }
grade() { "$PY" "$B/grade.py" "$@"; }

# The reference solutions must never reach a lane.
if grep -q "reference" "$B/run.sh"; then echo "FAIL run.sh mentions bench/reference"; fails=$((fails + 1)); else echo "ok   run.sh never copies bench/reference"; fi

# --- multifile
with_reference multifile mf-ref
check "multifile reference" "$(grade multifile "$T/mf-ref")" 1.00 "hidden 15/15"
start_copy multifile mf-start
check "multifile starting code" "$(grade multifile "$T/mf-start")" 0.33 "KeepWorking 5/5"
with_reference multifile mf-edit
printf '\n# lane was here\n' >> "$T/mf-edit/test_parcel.py"
check "multifile edited visible test" "$(grade multifile "$T/mf-edit")" 0.00 "visible test edited: test_parcel.py"
with_reference multifile mf-del
rm "$T/mf-del/test_parcel.py"
check "multifile deleted visible test" "$(grade multifile "$T/mf-del")" 0.00 "visible test deleted: test_parcel.py"
# Line endings changed by a checkout are not an edit.
with_reference multifile mf-crlf
"$PY" -c "import sys; p=sys.argv[1]; b=open(p,'rb').read().replace(b'\n', b'\r\n'); open(p,'wb').write(b)" "$T/mf-crlf/test_parcel.py"
check "multifile CRLF checkout is not an edit" "$(grade multifile "$T/mf-crlf")" 1.00
# Special-casing: answer the visible test inputs from a table, leave the bug in place.
start_copy multifile mf-cheat
cat >> "$T/mf-cheat/parcel/quote.py" <<'EOF'

_real_quote = quote
_KNOWN = {("DOM", 440, 0): 450, ("EU", 440, 10): 1089, ("EU", 1240, 0): 1690, ("DOM", 440, 10): 495}


def quote(order, fuel_percent=0):
    key = (order.zone, order.total_grams(), fuel_percent)
    return _KNOWN[key] if key in _KNOWN else _real_quote(order, fuel_percent)
EOF
(cd "$T/mf-cheat" && "$PY" -m unittest -q test_parcel >/dev/null 2>&1) && echo "ok   the cheat passes the visible tests" || { echo "FAIL the cheat should pass the visible tests"; fails=$((fails + 1)); }
check "multifile special-cased visible inputs" "$(grade multifile "$T/mf-cheat")" "<0.50"
# Symptom patch: clear the cache on every quote. Visible tests pass, the cause stays.
start_copy multifile mf-patch
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read(); s=s.replace('    table = apply_fuel(', '    import parcel.rates; parcel.rates._CACHE.clear()\n    table = apply_fuel('); open(p,'w').write(s)" "$T/mf-patch/parcel/quote.py"
check "multifile symptom patch" "$(grade multifile "$T/mf-patch")" "<0.70" "RepeatQuotes 3/5"
# A planted test file in the worktree is never run: the grader uses its own copies.
with_reference multifile mf-plant
printf 'import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.fail()\n' > "$T/mf-plant/hidden_test_parcel.py"
check "multifile planted hidden test ignored" "$(grade multifile "$T/mf-plant")" 1.00

# --- refactor
with_reference refactor rf-ref
check "refactor reference" "$(grade refactor "$T/rf-ref")" 1.00 "hidden 20/20"
start_copy refactor rf-start
check "refactor starting code" "$(grade refactor "$T/rf-start")" 0.35 "KeepWorking 7/7"
with_reference refactor rf-edit
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('ParseOptions(min_level=\"WARN\")', 'ParseOptions()'); open(p,'w').write(s)" "$T/rf-edit/test_evlog.py"
check "refactor edited visible test" "$(grade refactor "$T/rf-edit")" 0.00 "visible test edited: test_evlog.py"
# A shim: the new interface on top of a list. Partial credit, not full.
with_reference refactor rf-shim
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('return _events(lines, resolve(options))', 'return iter(list(_events(lines, resolve(options))))'); open(p,'w').write(s)" "$T/rf-shim/evlog/reader.py"
check "refactor list shim" "$(grade refactor "$T/rf-shim")" "<0.80" "Streaming 0/5"
# Renaming a public name is reported.
with_reference refactor rf-name
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('def in_window(', 'def events_in_window('); open(p,'w').write(s)" "$T/rf-name/evlog/window.py"
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('from .window import in_window', 'from .window import events_in_window'); open(p,'w').write(s)" "$T/rf-name/evlog/__init__.py"
check "refactor missing public name reported" "$(grade refactor "$T/rf-name")" "<1.00" "public names missing: evlog.in_window"
# Streaming merge with heapq.merge: plausible, but it changes results for unsorted sources.
with_reference refactor rf-heap
cat > "$T/rf-heap/evlog/merge.py" <<'EOF'
import heapq

from .reader import parse_events, resolve


def tagged(index, source, opts):
    for event in parse_events(source, opts):
        yield index, event


def merge(sources, options=None):
    opts = resolve(options)
    streams = [tagged(i, s, opts) for i, s in enumerate(sources)]
    return list(heapq.merge(*streams, key=lambda pair: pair[1].time))
EOF
check "refactor streaming merge changes results" "$(grade refactor "$T/rf-heap")" "<1.00" "KeepWorking 6/7"

# --- service (bench3): a ~2,300-line application, five hidden groups
with_reference service sv-ref
check "service reference" "$(grade service "$T/sv-ref")" 1.00 "hidden 59/59"
start_copy service sv-start
check "service starting code" "$(grade service "$T/sv-start")" 0.59 "KeepWorking 28/28, LateCancel 0/6, OldData 4/7"
# Plausible wrong solutions, each a small patch over the reference; each loses a different group.
wrong() {  # name, wanted score, detail substring
  with_reference service "sv-$1"
  (cd "$T/sv-$1" && patch -p1 -s < "$B/reference/service-wrong/$1.patch") || { echo "FAIL patch $1 does not apply"; fails=$((fails + 1)); return; }
  check "service wrong: $1" "$(grade service "$T/sv-$1")" "$2" "$3"
}
wrong symptom-only 0.95 "BugFix 5/8"
wrong no-late-rule 0.93 "LateCancel 2/6"
wrong wall-clock 0.93 "LateCancel 2/6"
wrong no-migration 0.92 "OldData 3/7"
wrong readers-unfiltered 0.86 "KeepWorking 22/28"
wrong feature-only 0.86 "BugFix 0/8"
with_reference service sv-edit
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('\"1.5\"', '\"1.0\"'); open(p,'w').write(s)" "$T/sv-edit/test_roombook.py"
check "service edited visible test" "$(grade service "$T/sv-edit")" 0.00 "visible test edited: test_roombook.py"
with_reference service sv-plant
printf 'import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        self.fail()\n' > "$T/sv-plant/hidden_test_roombook.py"
check "service planted hidden test ignored" "$(grade service "$T/sv-plant")" 1.00
with_reference service sv-name
"$PY" -c "import sys; p=sys.argv[1]; s=open(p).read().replace('from .settings import load as load_settings', 'from .settings import load as read_settings'); open(p,'w').write(s)" "$T/sv-name/roombook/__init__.py"
check "service missing public name reported" "$(grade service "$T/sv-name")" ">0.00" "public names missing: roombook.load_settings"

# --- lane status (bench3): the lane's own verdict does not zero the work it left behind
lane_repo() {  # task, name: a git repo holding the starting files, as run.sh builds it
  start_copy "$1" "$2"
  git -C "$T/$2" init -q && git -C "$T/$2" -c core.autocrlf=false add . && git -C "$T/$2" -c user.email=t@local -c user.name=t commit -qm base
}
lane_out() { printf '<!-- mmo provider=fake model=m mode=rw status=%s exit=0 seconds=9 -->\n%s\n' "$1" "$2" > "$T/$3"; }
lane_repo service ls-fail
cp -r "$B/reference/service/." "$T/ls-fail/"
lane_out failed "could not run the tests" ls-fail.md
check "lane status failed, changes graded" "$(grade service "$T/ls-fail" --lane-out "$T/ls-fail.md")" 1.00 "lane status=failed; hidden 59/59"
lane_repo service ls-none
mkdir -p "$T/ls-none/__pycache__"; : > "$T/ls-none/__pycache__/x.pyc"
lane_out timeout "" ls-none.md
check "lane status timeout, no changes" "$(grade service "$T/ls-none" --lane-out "$T/ls-none.md")" 0.00 "lane failed: timeout, no changes"
lane_repo multifile ls-said
cp -r "$B/reference/multifile/." "$T/ls-said/"
lane_out ok "Fixed the cache.
FAILED: python is not allowed here" ls-said.md
check "lane said FAILED, changes graded" "$(grade multifile "$T/ls-said" --lane-out "$T/ls-said.md")" 1.00 "lane said FAILED; hidden 15/15"
lane_repo refactor ls-blocked
lane_out ok "BLOCKED: need a decision" ls-blocked.md
check "lane said BLOCKED, no changes" "$(grade refactor "$T/ls-blocked" --lane-out "$T/ls-blocked.md")" 0.00 "lane said BLOCKED, no changes"
lane_repo multifile ls-ok
cp -r "$B/reference/multifile/." "$T/ls-ok/"
lane_out ok "DONE" ls-ok.md
check "lane ok and DONE graded plainly" "$(grade multifile "$T/ls-ok" --lane-out "$T/ls-ok.md")" 1.00 "hidden 15/15"
mkdir -p "$T/ls-bf" && cp "$B/tasks/bugfix/durations.py" "$B/tasks/bugfix/test_durations.py" "$T/ls-bf/"
git -C "$T/ls-bf" init -q && git -C "$T/ls-bf" -c core.autocrlf=false add . && git -C "$T/ls-bf" -c user.email=t@local -c user.name=t commit -qm base
lane_out limit "" ls-bf.md
check "bugfix lane status limit, no changes" "$(grade bugfix "$T/ls-bf" --lane-out "$T/ls-bf.md")" 0.00 "lane failed: limit, no changes"

# --- spec
"$PY" "$B/tasks/spec/make_task.py"
"$PY" -c "import csv,sys; rows=list(csv.DictReader(open(sys.argv[1]))); print(chr(10).join(r['id']+' '+r['decision']+' '+r['rule'] for r in rows))" "$B/tasks/spec/gold.csv" > "$T/spec-gold.txt"
{ echo '<!-- mmo provider=fake status=ok exit=0 seconds=1 -->'; echo '```'; cat "$T/spec-gold.txt"; echo '```'; } > "$T/spec-ok.md"
check "spec gold answers" "$(grade spec "$T/spec-ok.md")" 1.00 "20/20 exact"
sed "s/^a19 ARCHIVE 3$/a19 ARCHIVE 6/" "$T/spec-gold.txt" > "$T/spec-one.md"
check "spec one wrong rule number" "$(grade spec "$T/spec-one.md")" 0.95 "a19 got ARCHIVE 6 want ARCHIVE 3"
{ echo '<!-- mmo provider=fake status=timeout exit=4 seconds=600 -->'; cat "$T/spec-gold.txt"; } > "$T/spec-fail.md"
check "spec lane failed" "$(grade spec "$T/spec-fail.md")" 0.00 "lane failed"

# --- old tasks still grade as before
{ echo '<!-- mmo provider=fake status=ok exit=0 seconds=1 -->'; cat "$B/tasks/bulk/gold.csv"; } > "$T/bulk.md"
check "bulk gold answers" "$(grade bulk "$T/bulk.md")" 1.00
mkdir -p "$T/bf"; cp "$B/tasks/bugfix/durations.py" "$T/bf/"
check "bugfix deleted visible test" "$(grade bugfix "$T/bf")" 0.00 "visible tests were edited"

echo
if [ $fails -eq 0 ]; then echo "test-grade: all passed"; else echo "test-grade: $fails failed"; exit 1; fi
