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
    r"invalid model|model .{0,80}(does not exist|not found)|no such model", re.I)
LIMIT = re.compile(
    r"insufficient balance|\b402\b|quota|usage limit|rate.?limit|\b429\b|exceeded your|"
    r"does not have access|upgrade to", re.I)
AUTH = re.compile(
    r"authenticat|not logged in|log in|sign in|unauthorized|\b401\b|session expired", re.I)
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
    if MODEL.search(body):
        return "model"
    if LIMIT.search(body):
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
