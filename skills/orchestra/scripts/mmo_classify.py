#!/usr/bin/env python3
"""Classify a failed lane from the CLI's own error output.

usage: mmo_classify.py PROVIDER PROMPT_FILE FILE [FILE ...]
Prints one word: model | limit | auth | failed

Codex (and others) echo the brief into stderr, so a brief that mentions "429" or "rate limit"
must not make a real failure look like a limit. Two guards:
  1. every line that also appears in the prompt is dropped before matching;
  2. for codex, only lines that look like the CLI's own error lines are matched
     (ERROR:, error:, JSON objects, stream/turn failure prefixes).
"""
import re
import sys

MODEL = re.compile(
    r"model_not_found|model is not supported|model .{0,80}not supported|unknown model|"
    r"invalid model|model (?:is )?unavailable|model .{0,80}is not available|model .{0,80}(does not exist|not found)|no such model|cannot use this model|code 1211\b|requires specifying a model", re.I)
LIMIT = re.compile(
    r"insufficient balance|\b402\b|quota|usage limit|rate.?limit|\b429\b|exceeded your|"
    r"does not have access|upgrade to", re.I)
AUTH = re.compile(
    r"authenticat|not logged in|log in|sign in|unauthorized|\b401\b|session expired|no api key|"
    r"api key (?:is )?(?:invalid|expired|missing)", re.I)
# A CLI that starts a sign-in flow is not signed in, whatever else it prints afterwards.
SIGN_IN = re.compile(
    r"waiting for authorization|you are not authenticated|to sign in, open|open this url in your browser|"
    r"please run .{0,40}login|run `?\S+ (auth )?login`?", re.I)
# Strings quoted from the docs or source of gemini, crush, aider and opencode (no sign-in word in them).
# Checked before MODEL and LIMIT, so only messages that can mean nothing else belong here; a looser
# phrase such as "api key is missing" goes in AUTH, which is checked last.
EXTRA_AUTH = re.compile(
    r"please set an auth method|no providers configured|unable to proceed without an? .{0,30}api key|"
    r"is required to resolve the provider endpoint|no auth type is selected|"
    r"invalid[_ ]api[_ ]key|invalid x-api-key", re.I)
EXTRA_LIMIT = re.compile(
    r"exhausted your capacity|capacity exceeded|model_capacity_exhausted|"
    r"not included in your (weekly )?usage|credit balance is too low|resource_exhausted", re.I)
CODEX_ERR = re.compile(
    r"^\s*(error|warning: stream|stream error|unexpected status|exceeded retry|turn\.failed|"
    r"\{|\[?error)", re.I)


def own_lines(provider, prompt, texts):
    echoed = {ln.strip() for ln in prompt.splitlines() if len(ln.strip()) > 3}
    out = []
    for text in texts:
        for ln in text.splitlines():
            s = ln.strip()
            if not s or s in echoed:
                continue
            if provider == "codex" and not CODEX_ERR.match(ln):
                continue
            out.append(s)
    return "\n".join(out)


def classify(provider, prompt, texts):
    body = own_lines(provider, prompt, texts)
    if SIGN_IN.search(body) or EXTRA_AUTH.search(body):
        return "auth"
    if MODEL.search(body):
        return "model"
    if LIMIT.search(body) or EXTRA_LIMIT.search(body):
        return "limit"
    if AUTH.search(body):
        return "auth"
    return "failed"


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: mmo_classify.py PROVIDER PROMPT_FILE FILE...", file=sys.stderr)
        sys.exit(2)
    print(classify(sys.argv[1], read(sys.argv[2]), [read(p) for p in sys.argv[3:]]))
