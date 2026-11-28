#!/usr/bin/env bash
# Offline test for mmo-check: a tiny git repo, no model calls.
# Run: bash skills/orchestra/scripts/test-mmo-check.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0
expect() { # name, wanted exit code, wanted text in the report, then the mmo-check arguments
  local name="$1" want="$2" text="$3"; shift 3
  bash "$HERE/mmo-check" "$@" --out "$T/report" 2>/dev/null; local rc=$?
  if [ $rc -eq "$want" ] && grep -q -- "$text" "$T/report"; then echo "PASS $name"
  else echo "FAIL $name: exit $rc (wanted $want), report:"; sed 's/^/    /' "$T/report"; fail=1; fi
}

git init -q "$T/main"
cd "$T/main" || exit 1
git config user.email t@example.com; git config user.name t; git config core.autocrlf false
printf 'echo $(( $1 - $2 ))\n' > calc.sh                       # the bug: subtracts
printf '[ "$(sh calc.sh 0 0)" = 0 ]\n' > calc_test.sh
git add . && git commit -qm init
fresh() { git worktree remove --force "$T/wt" 2>/dev/null; git branch -qD lane/x 2>/dev/null; git worktree add -q "$T/wt" -b lane/x; }

fresh   # a real fix with a test that fails without it
printf 'echo $(( $1 + $2 ))\n' > "$T/wt/calc.sh"
printf '[ "$(sh calc.sh 0 0)" = 0 ] && [ "$(sh calc.sh 2 3)" = 5 ]\n' > "$T/wt/calc_test.sh"
expect "fix with a failing-before test passes" 0 "status=pass" -C "$T/wt" --cmd "sh calc_test.sh" --red
expect "changed existing test is listed" 0 "M calc_test.sh" -C "$T/wt" --cmd "sh calc_test.sh"
expect "protected test file touched" 3 "PROTECTED" -C "$T/wt" --cmd "sh calc_test.sh" --protect "*_test.sh"
echo x > "$T/wt/stray.txt"
expect "file outside the allowed list" 3 "stray.txt" -C "$T/wt" --cmd "sh calc_test.sh" --allow "calc*.sh"

fresh   # the check passes without the change: it proves nothing
printf '# tidy\necho $(( $1 - $2 ))\n' > "$T/wt/calc.sh"
expect "check that passes on the base is not red" 5 "NOT RED" -C "$T/wt" --cmd "sh calc_test.sh" --red

fresh   # a broken change
printf 'echo broken\n' > "$T/wt/calc.sh"
expect "failing check" 1 "status=fail" -C "$T/wt" --cmd "sh calc_test.sh"
expect "timeout" 4 "status=timeout" -C "$T/wt" --cmd "sleep 20" -t 1

printf '{}\n' > "$T/wt/package.json"; printf 'echo $(( $1 - $2 ))\n' > "$T/wt/calc.sh"
expect "dependency manifest reported" 0 "deps_changed=1" -C "$T/wt" --cmd "sh calc_test.sh"

[ "$(git worktree list | wc -l)" -eq 2 ] || { echo "FAIL leftover worktree"; git worktree list; fail=1; }
exit $fail
