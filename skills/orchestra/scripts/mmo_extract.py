"""Pull the final answer out of a lane's raw output.

    python mmo_extract.py PARSER RAW_FILE

Parsers (one per output shape, named in a provider's LANE_EXTRACT):
    text      plain stdout is the answer (ANSI colors removed)
    kimi      Kimi Code --output-format stream-json
    claude    Claude Code -p --output-format json (one result object; also Cursor and Droid json)
    result-stream  JSON lines that end with a {"type":"result"} line (Amp --stream-json)
    field:K   one JSON document whose key K holds the answer (K may be dotted: a.b, and
              -1.result means the last item's result when the document is an array)
    jsonl:K   JSON lines; the answer is K of the last line that has a non-empty K
    opencode  opencode run --format json: the last event of type "text" (part.text); an "error" event
              with no text is a lane error
    qwen      qwen --output-format json: array of messages, the answer is the last "result" item;
              is_error true is a lane error
    gptme     gptme -n --output-format json: JSON lines, one per message; the answer is the content of
              the last message whose role is "assistant"
    aider     aider plain output: the text between the MMO-ANSWER-BEGIN and MMO-ANSWER-END lines
              (last pair); with no markers the whole output, unless a litellm error is printed

Exit codes: 0 answer printed | 1 no answer in the output | 3 the CLI reported an error inside
its output (the runner then treats the lane as failed even if the CLI exited 0) | 2 usage.
"""
import json
import re
import sys

ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")


class LaneError(Exception):
    """The CLI exited normally but its output says the run failed."""


def text(raw: str) -> str:
    return ANSI.sub("", raw)


def kimi(raw: str) -> str:
    # One JSON object per line; the answer is the last assistant message with text.
    last = ""
    for ev in _json_lines(raw):
        if ev.get("role") != "assistant":
            continue
        content = ev.get("content")
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if isinstance(content, str) and content.strip():
            last = content
    return last


def claude(raw: str) -> str:
    data = json.loads(raw)
    if isinstance(data, list):  # some versions emit the event list
        data = data[-1] if data else {}
    if data.get("is_error") or data.get("permission_denials"):
        raise LaneError("claude lane error: " + str(data.get("result") or data.get("permission_denials")))
    return data.get("result", "") or ""


def result_stream(raw: str) -> str:
    # Amp streams events in the Claude Code schema; the last result line holds the answer.
    res = None
    for ev in _json_lines(raw):
        if ev.get("type") == "result":
            res = ev
    if res is None:
        return ""
    if res.get("is_error"):
        raise LaneError("lane error: " + str(res.get("result") or res.get("error") or "run failed"))
    return res.get("result", "") or ""


def _json_lines(raw: str):
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(ev, dict):
            yield ev


def _dig(obj, dotted: str):
    for key in dotted.split("."):
        if isinstance(obj, list) and key.lstrip("-").isdigit():
            obj = obj[int(key)] if -len(obj) <= int(key) < len(obj) else None
        elif isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj


def _as_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):  # content blocks: [{"type": "text", "text": "..."}]
        return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in value)
    return ""


def _error_in(obj) -> str:
    err = obj.get("error") if isinstance(obj, dict) else None
    if not err:
        return ""
    return err.get("message", "") or json.dumps(err) if isinstance(err, dict) else str(err)


def field(raw: str, key: str) -> str:
    try:  # the whole output is one JSON document (an object, or an array of events)
        whole = json.loads(raw)
    except json.JSONDecodeError:
        whole = None
    if whole is not None:
        answer = _as_text(_dig(whole, key))
        if not answer.strip() and _error_in(whole):
            raise LaneError("lane error: " + _error_in(whole))
        return answer
    # The object may follow log lines: parse from the first "{" that opens a valid document.
    start = raw.find("{")
    while start != -1:
        try:
            data = json.loads(raw[start:])
            break
        except json.JSONDecodeError:
            start = raw.find("{", start + 1)
    else:
        return ""
    answer = _as_text(_dig(data, key))
    if not answer.strip() and _error_in(data):
        raise LaneError("lane error: " + _error_in(data))
    return answer


def jsonl(raw: str, key: str) -> str:
    last, err = "", ""
    for ev in _json_lines(raw):
        got = _as_text(_dig(ev, key))
        if got.strip():
            last = got
        err = _error_in(ev) or err
    if not last.strip() and err:
        raise LaneError("lane error: " + err)
    return last


PARSERS = {"text": text, "kimi": kimi, "claude": claude, "result-stream": result_stream}


def opencode(raw: str) -> str:
    # Reasoning events also carry part.text, so only events whose own type is "text" count.
    last, err = "", ""
    for ev in _json_lines(raw):
        if ev.get("type") == "text":
            got = _as_text(_dig(ev, "part.text"))
            if got.strip():
                last = got
        elif ev.get("type") == "error":
            err = _error_in(ev) or err
    if not last.strip() and err:
        raise LaneError("lane error: " + err)
    return last


def qwen(raw: str) -> str:
    data = json.loads(raw)
    items = data if isinstance(data, list) else [data]
    res = [i for i in items if isinstance(i, dict) and i.get("type") == "result"]
    if not res:
        return ""
    last = res[-1]
    if last.get("is_error"):
        # Real qwen 0.29 puts the reason in error.message and leaves result empty.
        err = last.get("error")
        why = err.get("message") if isinstance(err, dict) else err
        raise LaneError("qwen lane error: " + str(why or last.get("result") or last.get("subtype")))
    return _as_text(last.get("result"))


AIDER_MARKED = re.compile(r"^MMO-ANSWER-BEGIN[ \t]*\r?\n(.*?)\r?\n?^MMO-ANSWER-END[ \t]*$", re.S | re.M)
AIDER_ERR = re.compile(r"litellm\.\w*(AuthenticationError|RateLimitError|NotFoundError|BadRequestError)")


def aider(raw: str) -> str:
    raw = text(raw)
    found = AIDER_MARKED.findall(raw)
    if found:
        return found[-1]
    # aider can exit 0 after printing a provider error; do not pass that text off as an answer.
    if AIDER_ERR.search(raw):
        raise LaneError("aider lane error: " + AIDER_ERR.search(raw).group(0))
    return raw


def gptme(raw: str) -> str:
    # System and tool messages follow the assistant's tool calls, so "last line" is not the answer.
    last = ""
    for ev in _json_lines(raw):
        if ev.get("role") == "assistant":
            got = _as_text(ev.get("content"))
            if got.strip():
                last = got
    return last


PARSERS.update({"opencode": opencode, "qwen": qwen, "aider": aider, "gptme": gptme})


def extract(parser: str, raw: str) -> str:
    if parser in PARSERS:
        return PARSERS[parser](raw)
    kind, _, key = parser.partition(":")
    if kind == "field" and key:
        return field(raw, key)
    if kind == "jsonl" and key:
        return jsonl(raw, key)
    print(__doc__, file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)
    with open(sys.argv[2], encoding="utf-8", errors="replace") as f:
        raw = f.read()
    try:
        answer = extract(sys.argv[1], raw)
    except LaneError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(3)
    except (json.JSONDecodeError, ValueError):
        raise SystemExit("no answer in lane output")
    if not answer.strip():
        raise SystemExit("no answer in lane output")
    # Write UTF-8 bytes: a Windows console code page cannot encode every character a model emits.
    sys.stdout.buffer.write((answer.rstrip() + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
