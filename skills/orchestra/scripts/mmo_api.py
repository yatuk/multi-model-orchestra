"""Ask one OpenAI-compatible chat endpoint a single question. Stdlib only.

    python mmo_api.py ENDPOINT:MODEL      (the prompt comes on stdin)

ENDPOINT is a name from the table below or any name you define with the environment
variables MMO_API_<NAME>_URL (base URL) and MMO_API_<NAME>_KEY (the key itself).
MODEL is sent as is, so it may hold slashes and colons: only the first colon splits.
Those variables also override the table. Other settings: MMO_API_MAX_TOKENS, MMO_API_TIMEOUT
(seconds, default 600).
MMO_API_USAGE_FILE (set by mmo-run): where to write what the endpoint reported about the call, as
{"usage": {prompt_tokens, completion_tokens, total_tokens, cost}, "model": "..."}. Only fields the
response holds; never the key or the prompt. stdout stays the pure answer.

Exit 0 and the answer on stdout (UTF-8 bytes), or exit 1 and one line on stderr:
    HTTP <status> <endpoint>: <message from the body> [(Retry-After: <value>)]
    network error: <reason>
    no API key: set <ENV_VAR>
The key is read from the environment, sent as a Bearer header and never printed.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

# name -> (base URL, key variable or "" when the endpoint is local and needs none)
ENDPOINTS = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "deepseek": ("https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    "moonshot": ("https://api.moonshot.ai/v1", "MOONSHOT_API_KEY"),
    "zai": ("https://api.z.ai/api/paas/v4", "ZAI_API_KEY"),
    "minimax": ("https://api.minimax.io/v1", "MINIMAX_API_KEY"),
    "xai": ("https://api.x.ai/v1", "XAI_API_KEY"),
    "mistral": ("https://api.mistral.ai/v1", "MISTRAL_API_KEY"),
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "cerebras": ("https://api.cerebras.ai/v1", "CEREBRAS_API_KEY"),
    "together": ("https://api.together.ai/v1", "TOGETHER_API_KEY"),
    "fireworks": ("https://api.fireworks.ai/inference/v1", "FIREWORKS_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
    "ollama": ("http://localhost:11434/v1", ""),
    "lmstudio": ("http://localhost:1234/v1", ""),
}


def fail(msg):
    sys.stderr.write(msg.replace("\n", " ") + "\n")
    raise SystemExit(1)


def resolve(name):
    """Return (base_url, key). Environment overrides win over the table."""
    var = re.sub(r"[^A-Z0-9]", "_", name.upper())
    base, keyvar = ENDPOINTS.get(name.lower(), ("", None))
    base = os.environ.get("MMO_API_%s_URL" % var, base)
    if not base:
        fail("unknown endpoint %r: use one of %s or set MMO_API_%s_URL and MMO_API_%s_KEY"
             % (name, ", ".join(sorted(ENDPOINTS)), var, var))
    override = "MMO_API_%s_KEY" % var
    if override in os.environ:  # set, even empty: the caller decided
        return base, os.environ[override]
    if keyvar == "":
        return base, ""
    keyvar = keyvar or override
    key = os.environ.get(keyvar, "")
    if not key:
        fail("no API key: set %s" % keyvar)
    return base, key


def error_text(body, key):
    msg = ""
    try:
        data = json.loads(body)
        err = data.get("error", data) if isinstance(data, dict) else data
        if isinstance(err, dict):
            msg = str(err.get("message") or err.get("msg") or "")
            if err.get("code") not in (None, ""):
                msg = "%s (code %s)" % (msg, err["code"])
        elif err:
            msg = str(err)
    except (ValueError, AttributeError):
        pass
    if not msg.strip():
        msg = body
    if key:
        msg = msg.replace(key, "***")
    return " ".join(msg.split())[:300]


def write_usage(path, data):
    """Side file for mmo-run: the usage numbers and model the endpoint reported, nothing else."""
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    keep = {k: usage[k] for k in ("prompt_tokens", "completion_tokens", "total_tokens", "cost")
            if isinstance(usage.get(k), (int, float)) and not isinstance(usage.get(k), bool)}
    side = {"usage": keep}
    if isinstance(data.get("model"), str):
        side["model"] = data["model"]
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(side, f)
    except OSError:
        pass  # the answer matters more than its bookkeeping


def content_of(data):
    choice = (data.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content")
    if isinstance(content, list):  # content parts
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def main():
    spec = sys.argv[1] if len(sys.argv) == 2 else ""
    if ":" not in spec or spec.startswith(":") or spec.endswith(":"):
        fail("model must be written endpoint:model, for example openrouter:deepseek/deepseek-v4-pro")
    name, model = spec.split(":", 1)
    base, key = resolve(name)
    prompt = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False}
    if os.environ.get("MMO_API_MAX_TOKENS", "").isdigit():
        payload["max_tokens"] = int(os.environ["MMO_API_MAX_TOKENS"])
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions",
                                 data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        timeout = float(os.environ.get("MMO_API_TIMEOUT", "600"))
    except ValueError:
        timeout = 600.0
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        wait = (exc.headers.get("Retry-After") or "").strip() if exc.headers else ""
        hint = " (Retry-After: %s)" % wait[:40].replace(key, "***") if wait and key != wait else ""
        fail("HTTP %d %s: %s%s" % (exc.code, name, error_text(exc.read().decode("utf-8", errors="replace"), key), hint))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        reason = str(getattr(exc, "reason", exc))
        fail("network error: " + (reason.replace(key, "***") if key else reason))
    try:
        data = json.loads(raw)
    except ValueError:
        fail("HTTP 200 %s: reply is not JSON" % name)
    if isinstance(data, dict) and data.get("error") and not data.get("choices"):
        # OpenRouter can report an error inside a 200 body.
        fail("HTTP 200 %s: %s" % (name, error_text(raw, key)))
    if os.environ.get("MMO_API_USAGE_FILE") and isinstance(data, dict):
        write_usage(os.environ["MMO_API_USAGE_FILE"], data)
    sys.stdout.buffer.write(content_of(data).encode("utf-8"))


if __name__ == "__main__":
    main()
