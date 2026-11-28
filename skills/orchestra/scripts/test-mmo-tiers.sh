#!/usr/bin/env bash
# Offline test for mmo_tiers.py (the one tier table). Run: bash skills/orchestra/scripts/test-mmo-tiers.sh
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
fail=0
cd "$HERE" || exit 1
"$PY" - <<'PYEOF' || fail=1
import sys
from mmo_tiers import tier_of, note_of
cases = [
 ("grok", "grok-4.7", "middle"), ("grok", "grok-4.6", "middle"), ("grok", "grok-4.5", "middle"),
 ("grok", "grok-4.7-build-fast", "cheap"), ("deepseek", "deepseek-v4-pro", "cheap"),
 ("deepseek", "deepseek-flash", "bulk"), ("opencode", "opencode/deepseek-v4.1-flash-free", "bulk"),
 ("opencode", "opencode/beam-free", "bulk"), ("opencode", "opencode/big-pickle", "bulk"),
 ("cursor", "composer-2.5", "middle"), ("agy", "gemini-4-neon-high", "strong"),
 ("agy", "gemini-4-carbon", "strong"), ("agy", "gemini-4-argon-high", "middle"),
 ("agy", "gemini-4-hydrogen-high", "bulk"), ("gemini", "gemini-3.8-flash", "bulk"),
 ("claude", "opus", "strong"), ("claude-agent", "fable", "strong"), ("claude", "sonnet", "middle"),
 ("claude", "haiku", "bulk"), ("codex", "gpt-6.1-sol", "middle"), ("codex", "gpt-6-astra", "strong"),
 ("codex", "gpt-6-luna", "bulk"), ("api", "ablit:abliterated-model-large-v2", "middle"),
 ("api", "ablit:abliterated-model-large-flash", "bulk"),
 ("api", "openrouter:baidu/ernie-5.5-flash-preview:free", "bulk"),
 ("api", "openrouter:particle-ai/particle-1:free", "bulk"),
 ("copilot", "gemini-4-neon", "strong"),          # "mini" must not match inside "gemini"
 ("claude-kimi", "whatever", "cheap"),            # a cheap vendor's lane
 ("codex", "gpt-9-new", "middle"),                # unknown id: the lane default
 ("mystery-cli", "x", "unknown"),                 # unknown lane and id
]
bad = 0
for p, m, want in cases:
    got = tier_of(p, m)
    if got != want:
        bad += 1
        print("FAIL tier_of(%r, %r) = %s, want %s" % (p, m, got, want))
if tier_of("codex", "gpt-9-new", default=False) != "unknown":
    bad += 1; print("FAIL default=False must not guess")
if tier_of("deepseek", "x", default=False) != "cheap":
    bad += 1; print("FAIL cheap vendor lanes stay cheap in strict mode")
if "no tools" not in note_of("api") or note_of("codex"):
    bad += 1; print("FAIL api lane note")
print("PASS %d tier cases" % (len(cases) + 3) if not bad else "%d FAILED" % bad)
sys.exit(1 if bad else 0)
PYEOF
[ $fail -eq 0 ] && echo "all mmo-tiers tests passed" || { echo "some mmo-tiers tests FAILED"; exit 1; }
