#!/usr/bin/env bash
# Offline test for mmo-lessons: temp dir, fake providers dir, no model calls.
# Run: bash skills/orchestra/scripts/test-mmo-lessons.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
ok() { echo "PASS $1"; }
bad() { echo "FAIL $1"; fail=1; }
L() { bash "$HERE/mmo-lessons" "$@"; }
# expect NAME WANT_EXIT -- args : runs the tool and checks the exit code only
expect() { local n="$1" w="$2"; shift 3; L "$@" >/dev/null 2>&1; local rc=$?; [ $rc -eq "$w" ] && ok "$n" || bad "$n: exit $rc, wanted $w"; }
# eq NAME WANTED ACTUAL
eq() { [ "$2" = "$3" ] && ok "$1" || { bad "$1"; printf '    wanted: %s\n    got:    %s\n' "$2" "$3"; }; }

mkdir -p "$T/prov"
echo 'run opencode v1' > "$T/prov/opencode.sh"
echo 'run grok v1' > "$T/prov/grok.sh"
export MMO_PROVIDERS_DIR="$T/prov"
export MMO_LESSONS="$T/lessons.jsonl"
echo '<!-- mmo-check status=pass exit=0 seconds=1 -->' > "$T/pass"
echo '<!-- mmo-check status=fail exit=1 seconds=1 -->' > "$T/fail"
echo 'just some notes' > "$T/notes"

expect "add refuses a fail report" 3 -- add --lane opencode --text "x" --check "$T/fail"
expect "add refuses a non-report file" 3 -- add --lane opencode --text "x" --check "$T/notes"
expect "add refuses a missing report" 3 -- add --lane opencode --text "x" --check "$T/nope"
[ ! -s "$MMO_LESSONS" ] && ok "refused adds write nothing" || bad "refused adds wrote a line"

eq "first add prints L1" "L1" "$(L add --lane opencode/x --text "use absolute paths" --check "$T/pass")"
eq "second add prints L2" "L2" "$(L add --lane '*' --text "run the test before saying done" --check "$T/pass")"

eq "opencode/x lesson does not show for grok" "- run the test before saying done  [L2]" "$(L show --lane grok)"
eq "star lesson shows for every lane" "- run the test before saying done  [L2]" "$(L show --lane kimi)"
eq "opencode/x lesson shows for opencode/x" "- run the test before saying done  [L2]
- use absolute paths  [L1]" "$(L show --lane opencode/x)"
eq "opencode/x lesson does not show for opencode/other" "- run the test before saying done  [L2]" "$(L show --lane opencode/other)"

L add --lane opencode --text "keep diffs small" --check "$T/pass" >/dev/null
eq "provider-only lesson shows for opencode/any-model" "- keep diffs small  [L3]" "$(L show --lane opencode/any-model | grep L3)"

for i in 1 2 3 4 5 6 7; do L add --lane '*' --text "star lesson $i" --check "$T/pass" >/dev/null; done
eq "show returns at most 5" "5" "$(L show --lane grok -n 99 | wc -l | tr -d ' ')"
eq "show -n 2 returns 2" "2" "$(L show --lane grok -n 2 | wc -l | tr -d ' ')"
eq "show returns the newest first" "- star lesson 7  [L10]" "$(L show --lane grok | head -1)"

rm -f "$MMO_LESSONS"
L add --lane grok --text "old way" --check "$T/pass" >/dev/null
eq "supersedes prints the new id" "L2" "$(L add --lane grok --text "new way" --check "$T/pass" --supersedes L1)"
eq "supersedes hides the old one" "- new way  [L2]" "$(L show --lane grok)"
expect "supersedes an unknown id is refused" 2 -- add --lane grok --text "z" --check "$T/pass" --supersedes L99

L drop L2 >/dev/null
eq "drop hides the lesson" "" "$(L show --lane grok)"
eq "drop appends, history stays" "3" "$(wc -l < "$MMO_LESSONS" | tr -d ' ')"
expect "drop of an unknown id is refused" 2 -- drop L99

rm -f "$MMO_LESSONS"
L add --lane opencode --text "stale soon" --check "$T/pass" >/dev/null
L add --lane '*' --text "never stale" --check "$T/pass" >/dev/null
eq "unchanged adapter keeps the lesson" "2" "$(L show --lane opencode | wc -l | tr -d ' ')"
echo 'run opencode v2' > "$T/prov/opencode.sh"
eq "changed adapter makes the lesson stale" "- never stale  [L2]" "$(L show --lane opencode)"

rm -f "$MMO_LESSONS"
L add --lane nosuchprovider --text "no adapter" --check "$T/pass" >/dev/null
eq "missing adapter file never goes stale" "- no adapter  [L1]" "$(L show --lane nosuchprovider)"

long="$(printf 'a%.0s' $(seq 1 241))"
expect "text over 240 characters refused" 2 -- add --lane '*' --text "$long" --check "$T/pass"
expect "text with a newline refused" 2 -- add --lane '*' --text "line one
line two" --check "$T/pass"
expect "api-key-like text refused (sk-)" 2 -- add --lane '*' --text "use key sk-abc123def456" --check "$T/pass"
expect "api-key-like text refused (ghp_)" 2 -- add --lane '*' --text "token ghp_abc123def456" --check "$T/pass"
expect "long hex run refused" 2 -- add --lane '*' --text "id 0123456789abcdef0123456789abcdef0123" --check "$T/pass"
expect "email refused" 2 -- add --lane '*' --text "mail me at someone@example.com" --check "$T/pass"
expect "windows home path refused" 2 -- add --lane '*' --text 'see C:\Users\bob\x' --check "$T/pass"
expect "unix home path refused" 2 -- add --lane '*' --text "see /home/bob/x" --check "$T/pass"
expect "mac home path refused" 2 -- add --lane '*' --text "see /Users/bob/x" --check "$T/pass"

rm -f "$MMO_LESSONS"
L add --lane opencode --text "one" --check "$T/pass" >/dev/null
L add --lane grok --text "two" --check "$T/pass" --supersedes L1 >/dev/null
L add --lane grok --text "three" --check "$T/pass" >/dev/null
L drop L3 >/dev/null
echo 'run grok v2' > "$T/prov/grok.sh"
all="$(L list --all)"
if echo "$all" | grep -q "^L1.*superseded" && echo "$all" | grep -q "^L2.*stale" && echo "$all" | grep -q "^L3.*dropped"; then
  ok "list --all shows the flags"
else
  bad "list --all shows the flags"; echo "$all"
fi
eq "list without --all hides non-ok" "0" "$(L list | wc -l | tr -d ' ')"

[ $fail -eq 0 ] || exit 1
