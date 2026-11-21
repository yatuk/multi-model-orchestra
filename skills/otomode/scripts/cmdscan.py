"""Find the commands a Bash command line would actually run, and judge them.

otomode's hook used to grep the whole command text, so a heredoc or an echo
that only *wrote* "docker rm" into a file was denied. This module splits the
line the way a shell does (quotes, escapes, ; && || | & newlines, comments,
redirections, heredocs) and checks the first word of each simple command,
after env assignments and wrappers (sudo, env, xargs, timeout, nohup, ...).
It looks inside everything that runs code: $(...), backticks, <(...),
`bash -c "..."`, `eval`, `find -exec`, `powershell -Command`, and heredoc or
here-string bodies fed to a shell.

Conservative: anything it cannot parse raises Unsure, and the caller falls
back to the old whole-text regex (deny when in doubt).
"""
import os
import re


class Unsure(Exception):
    """The command could not be parsed with confidence."""


STDIN_SHELL = object()  # marker: a shell that reads its script from stdin

SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "ash", "fish", "busybox"}
KEYWORDS = {"!", "{", "}", "if", "then", "else", "elif", "fi", "do", "done",
            "while", "until", "for", "in", "case", "esac", "select", "function", "coproc"}
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?\+?=")
REDIR = re.compile(r"\d*(<<<|<<-|<<|<>|<&|>&|>>|>\||&>>|&>|<|>)")
DYN = "\x00"  # stands for an expansion whose value is unknown

DELETE = {"rm", "rmdir", "del", "erase", "shred", "unlink", "rd"}
DEPLOY = {"kubectl", "helm", "terraform", "ansible-playbook", "pulumi", "vercel",
          "netlify", "flyctl", "fly", "az", "aws", "gcloud"}
REMOTE = {"scp", "rsync", "ssh", "sftp"}
MAIL = {"sendmail", "mail", "mailx", "mutt"}
MACHINE = {"shutdown", "reboot", "poweroff", "halt"}


# ---------------------------------------------------------------- tokenizer

def _read_paren(text, i):
    """text[i:] follows '$(' or '<(' : return (body, index after the matching ')')."""
    depth, j, n = 1, i, len(text)
    while j < n:
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "'":
            k = text.find("'", j + 1)
            if k < 0:
                raise Unsure("unterminated quote")
            j = k + 1
            continue
        if c == '"':
            j += 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            j += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[i:j], j + 1
        j += 1
    raise Unsure("unterminated $(")


def _read_backtick(text, i):
    """text[i:] follows a backtick: return (body, index after the closing one)."""
    j = i
    while j < len(text):
        if text[j] == "\\":
            j += 2
            continue
        if text[j] == "`":
            return text[i:j], j + 1
        j += 1
    raise Unsure("unterminated backtick")


def _read_word(text, i):
    """Read one shell word from text[i]. Return (literal, next index, code bodies, quoted)."""
    out, subs, quoted, n = [], [], False, len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n;&|()":
            break
        if c in "<>":
            if i + 1 < n and text[i + 1] == "(":  # process substitution
                body, i = _read_paren(text, i + 2)
                subs.append(body)
                out.append(DYN)
                continue
            break
        if c == "\\":
            if i + 1 < n and text[i + 1] != "\n":
                out.append(text[i + 1])
            i += 2
            continue
        if c == "'":
            k = text.find("'", i + 1)
            if k < 0:
                raise Unsure("unterminated quote")
            out.append(text[i + 1:k])
            quoted, i = True, k + 1
            continue
        if c == '"':
            quoted, i = True, i + 1
            while True:
                if i >= n:
                    raise Unsure("unterminated quote")
                d = text[i]
                if d == '"':
                    i += 1
                    break
                if d == "\\" and i + 1 < n and text[i + 1] in '"\\$`\n':
                    out.append(text[i + 1])
                    i += 2
                elif d == "$" and text.startswith("$(", i):
                    body, i = _read_paren(text, i + 2)
                    subs.append(body)
                    out.append(DYN)
                elif d == "`":
                    body, i = _read_backtick(text, i + 1)
                    subs.append(body)
                    out.append(DYN)
                elif d == "$" and i + 1 < n and (text[i + 1].isalnum() or text[i + 1] in "_{@*#?$!-"):
                    out.append(DYN)
                    i += 1
                else:
                    out.append(d)
                    i += 1
            continue
        if c == "$":
            nxt = text[i + 1] if i + 1 < n else ""
            if nxt == "(":
                body, i = _read_paren(text, i + 2)
                subs.append(body)
                out.append(DYN)
                continue
            if nxt in "'\"":
                raise Unsure("$'...' or $\"...\" quoting")
            if nxt.isalnum() or nxt in "_{@*#?$!-":
                out.append(DYN)
                i += 1
                continue
        if c == "`":
            body, i = _read_backtick(text, i + 1)
            subs.append(body)
            out.append(DYN)
            continue
        out.append(c)
        i += 1
    return "".join(out), i, subs, quoted


def _code_in(body):
    """$(...) and backtick bodies inside unquoted-heredoc text."""
    subs, i = [], 0
    while i < len(body):
        if body[i] == "\\":
            i += 2
        elif body.startswith("$(", i):
            s, i = _read_paren(body, i + 2)
            subs.append(s)
        elif body[i] == "`":
            s, i = _read_backtick(body, i + 1)
            subs.append(s)
        else:
            i += 1
    return subs


def parse(text, depth=0):
    """Split a script into simple commands.

    Returns (commands, stdin_texts): commands is a list of argv lists (quotes
    removed, DYN for unknown expansions), including commands inside $(...),
    backticks and process substitution; stdin_texts are heredoc and
    here-string bodies (they only run if a shell reads stdin).
    """
    if depth > 8:
        raise Unsure("nested too deep")
    cmds, stdin_texts, pending = [], [], []
    words = []
    i, n = 0, len(text)

    def end():
        nonlocal words
        if words:
            cmds.append(words)
        words = []

    def run_subs(subs):
        for s in subs:
            sub_cmds, sub_stdin = parse(s, depth + 1)
            cmds.extend(sub_cmds)
            stdin_texts.extend(sub_stdin)

    while i < n:
        c = text[i]
        if c == "\n":
            end()
            i += 1
            for delim, strip, quoted in pending:  # heredoc bodies start here
                lines = []
                while i < n:
                    j = text.find("\n", i)
                    line = text[i:] if j < 0 else text[i:j]
                    i = n if j < 0 else j + 1
                    check = (line.lstrip("\t") if strip else line).rstrip("\r")
                    if check == delim:
                        break
                    lines.append(line)
                body = "\n".join(lines)
                stdin_texts.append(body)
                if not quoted:
                    run_subs(_code_in(body))
            pending = []
            continue
        if c in " \t\r":
            i += 1
            continue
        if c == "\\" and text.startswith("\\\n", i):
            i += 2
            continue
        if c == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if text.startswith(("&&", "||", "|&", ";;"), i):
            end()
            i += 2
            continue
        m = REDIR.match(text, i)
        if m and not (m.group(1) in "<>" and text.startswith("(", m.end())):
            op, i = m.group(1), m.end()
            while i < n and text[i] in " \t":
                i += 1
            start = i
            word, i, subs, quoted = _read_word(text, i)
            run_subs(subs)
            if op in ("<<", "<<-"):
                if not word:
                    raise Unsure("heredoc without delimiter")
                pending.append((word, op == "<<-", quoted or "\\" in text[start:i]))
            elif op == "<<<":
                stdin_texts.append(word)
            continue
        if c in ";&|()":
            end()
            i += 1
            continue
        word, i, subs, quoted = _read_word(text, i)
        run_subs(subs)
        if word or quoted:
            words.append(word)
    end()
    return cmds, stdin_texts


# ---------------------------------------------------------------- judging

def _name(word):
    name = os.path.basename(word.replace("\\", "/")).lower()
    return name[:-4] if name.endswith(".exe") else name


def _skip_opts(args, with_value=()):
    """Drop leading options; options in with_value also drop their value."""
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--":
            return args[i + 1:]
        if not a.startswith("-") or a == "-":
            return args[i:]
        i += 2 if a in with_value else 1
    return []


def check_script(text, depth=0):
    """Return a block label for a Bash script, or None."""
    cmds, stdin_texts = parse(text, depth)
    reads_stdin = False
    for argv in cmds:
        label = check_argv(argv, depth)
        if label is STDIN_SHELL:
            reads_stdin = True
        elif label:
            return label
    if reads_stdin:
        if not stdin_texts:  # script comes from a pipe or a file: cannot inspect
            return "run a script piped into a shell (cannot inspect)"
        for body in stdin_texts:
            label = check_script(body, depth + 1)
            if label:
                return label
    return None


def check_argv(argv, depth=0):
    """Return a block label (or STDIN_SHELL) for one simple command, else None."""
    if depth > 8:
        raise Unsure("nested too deep")
    argv = list(argv)
    while argv and (argv[0] in KEYWORDS or ASSIGN.match(argv[0])):
        argv.pop(0)
    if not argv:
        return None
    if DYN in argv[0]:
        raise Unsure("command name comes from an expansion")
    name, args = _name(argv[0]), argv[1:]
    low = [a.lower() for a in args]

    # wrappers: judge the command they run
    if name in ("sudo", "doas"):
        return check_argv(_skip_opts(args, ("-u", "-g", "-p", "-U", "-C", "-D", "-r", "-t", "-T", "-h")), depth + 1)
    if name == "env":
        for k, a in enumerate(args):
            if a in ("-S", "--split-string") and k + 1 < len(args):
                return check_script(args[k + 1], depth + 1)
        return check_argv(_skip_opts(args, ("-u", "--unset", "-C", "--chdir")), depth + 1)
    if name in ("nohup", "time", "exec", "builtin", "stdbuf", "unbuffer", "caffeinate"):
        return check_argv(_skip_opts(args), depth + 1)
    if name == "command":
        if any(a in ("-v", "-V") for a in args):
            return None
        return check_argv(_skip_opts(args), depth + 1)
    if name in ("nice", "ionice", "chrt", "taskset"):
        return check_argv(_skip_opts(args, ("-n", "-c", "-p", "--adjustment")), depth + 1)
    if name == "timeout":
        rest = _skip_opts(args, ("-s", "--signal", "-k", "--kill-after"))
        return check_argv(rest[1:], depth + 1)
    if name == "xargs":
        rest = _skip_opts(args, ("-I", "-n", "-P", "-L", "-l", "-d", "-E", "-e", "-s", "-a",
                                 "--max-args", "--max-procs", "--delimiter", "--arg-file", "--replace"))
        return check_argv(rest + [DYN], depth + 1) if rest else None  # stdin supplies the arguments
    if name == "watch":
        rest = _skip_opts(args, ("-n", "--interval", "-d"))
        return check_script(" ".join(rest), depth + 1) if rest else None
    if name == "eval":
        return check_script(" ".join(args), depth + 1)
    if name in SHELLS:
        has_c, k = False, 0
        while k < len(args):
            a = args[k]
            if a in ("-o", "-O", "+o", "+O", "--rcfile", "--init-file"):
                k += 2
                continue
            if a.startswith(("-", "+")) and len(a) > 1:
                if not a.startswith("--") and "c" in a[1:]:
                    has_c = True
                k += 1
                continue
            if has_c:  # expansions become a plain word; a command name from one stays unknown
                return check_script(a.replace(DYN, "_v_"), depth + 1)
            return None  # runs a script file we cannot see
        return None if has_c else STDIN_SHELL
    if name in ("powershell", "pwsh"):
        for k, a in enumerate(low):
            if a in ("-encodedcommand", "-enc", "-ec", "-e"):
                return "run an encoded command (cannot inspect)"
            if a in ("-command", "-c", "-com", "-comm"):
                return powershell_reason(" ".join(args[k + 1:]))
        return None
    if name == "cmd":
        for k, a in enumerate(low):
            if a in ("/c", "/k"):
                return regex_reason(" ".join(args[k + 1:]))
        return None
    if name == "find":
        if "-delete" in args:
            return "delete (find -delete)"
        for k, a in enumerate(args):
            if a in ("-exec", "-execdir", "-ok", "-okdir"):
                sub = []
                for b in args[k + 1:]:
                    if b in (";", "+"):
                        break
                    sub.append(b)
                label = check_argv(sub, depth + 1)
                if label and label is not STDIN_SHELL:
                    return label
        return None

    # the commands themselves
    if name in DELETE:
        return "delete" if args else None
    if name in DEPLOY:
        return "deploy" if args else None
    if name in REMOTE:
        return "remote host" if args else None
    if name in MAIL:
        return "send mail"
    if name in MACHINE:
        return "machine control"
    if name == "git":
        return _git(args)
    if name == "gh":
        return _gh(low)
    if name in ("docker", "podman", "nerdctl", "docker-compose"):
        return _docker(name, low)
    if name in ("npm", "pnpm", "yarn") and any(a in ("publish", "unpublish") for a in low):
        return "publish"
    if name in ("cargo", "poetry") and "publish" in low or name == "twine" and "upload" in low \
            or name == "gem" and "push" in low:
        return "publish"
    if name == "curl":
        return _curl(args)
    if name == "wget":
        if any(a.startswith(("--post-data", "--post-file", "--body-data", "--body-file")) for a in low):
            return "outbound write request"
        for k, a in enumerate(low):
            m = a.split("=", 1)[1] if a.startswith("--method=") else (low[k + 1] if a == "--method" and k + 1 < len(low) else "")
            if m and m.upper() not in ("GET", "HEAD", "OPTIONS"):
                return "outbound write request"
        return None
    return None


def _git(args):
    rest = _skip_opts(args, ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"))
    if not rest:
        return None
    sub, a = rest[0].lower(), rest[1:]
    flags = set(a)
    if sub in ("push", "send-email"):
        return "git push"
    if sub == "rm":
        return "delete (git rm)"
    if sub == "branch" and (flags & {"-d", "-D", "--delete"} or any(re.match(r"^-[a-zA-Z]*[dD]", x) for x in a)):
        return "delete branch"
    if sub == "clean":
        return "delete (git)"
    if sub == "worktree" and a and a[0] in ("remove", "prune"):
        return "delete (git)"
    if sub == "stash" and a and a[0] in ("drop", "clear"):
        return "delete (git)"
    if sub == "reset" and "--hard" in flags:
        return "git reset --hard"
    if sub == "checkout" and flags & {"--", ".", "-f", "--force"}:
        return "discard changes"
    if sub == "restore" and (not flags & {"--staged", "-S"} or flags & {"--worktree", "-W"}):
        return "discard changes"
    if sub == "tag" and flags & {"-d", "--delete"}:
        return "delete tag"
    if sub == "update-ref" and "-d" in flags:
        return "delete (git)"
    return None


def _gh(low):
    sub, a = (low[0], low[1:]) if low else ("", [])
    nxt = a[0] if a else ""
    if sub == "pr" and nxt in ("create", "merge", "comment", "close", "review", "edit", "ready", "reopen"):
        return "GitHub write"
    if sub == "issue" and nxt in ("create", "comment", "close", "edit", "delete", "reopen", "transfer"):
        return "GitHub write"
    if sub in ("release", "api", "secret", "variable", "gist") or (sub == "repo" and nxt in ("create", "delete", "edit", "fork", "rename", "archive")):
        return "GitHub write"
    if sub == "workflow" and nxt in ("run", "enable", "disable") or sub == "run" and nxt in ("rerun", "cancel", "delete"):
        return "GitHub write"
    return None


def _docker(name, low):
    rest = low if name == "docker-compose" else _skip_opts(low, ("--context", "-c", "-h", "--host", "--config", "-l", "--log-level"))
    if name == "docker-compose":
        rest = ["compose"] + rest
    if not rest:
        return None
    sub, a = rest[0], rest[1:]
    if sub == "compose":
        a = _skip_opts(a, ("-f", "--file", "-p", "--project-name", "--profile", "--env-file", "--project-directory"))
        return "docker deploy/delete" if a and a[0] in ("up", "down", "rm", "run", "push") else None
    if sub in ("push", "run", "rm", "rmi", "kill"):
        return "docker deploy/delete"
    if sub in ("system", "builder") and a and a[0] == "prune":
        return "docker deploy/delete"
    if sub in ("container", "image", "volume", "network") and a and a[0] in ("rm", "remove", "prune", "run", "push", "kill"):
        return "docker deploy/delete"
    return None


def _curl(args):
    for k, a in enumerate(args):
        if a in ("-X", "--request") and k + 1 < len(args):
            method = args[k + 1].upper()
        elif a.startswith("-X") and len(a) > 2:
            method = a[2:].upper()
        elif a.startswith("--request="):
            method = a.split("=", 1)[1].upper()
        else:
            method = ""
        if method and method not in ("GET", "HEAD", "OPTIONS"):
            return "outbound write request"
        if a in ("-d", "-F", "-T", "--json", "--form", "--upload-file") or a.startswith(("--data", "--form")):
            return "outbound write request"
    return None


# ---------------------------------------------------------------- regex rules
# Used for PowerShell, for `cmd /c`, and as the fallback when a Bash line
# cannot be parsed. C = the word is in command position.
C = r"(^|[;&|(]\s*|\bsudo\s+|\bxargs\s+)"
REGEX_RULES = [
    (C + r"rm\s", "delete (rm)"),
    (r"\bgit\s+rm\s", "delete (git rm)"),
    (C + r"(rmdir|del|erase|shred|unlink|rd)\s", "delete"),
    (r"\b(Remove-Item|Clear-Content)\b", "delete (Remove-Item)"),
    (r"git\s+(push|send-email)\b", "git push"),
    (r"git\s+branch\s+.*-[dD]\b", "delete branch"),
    (r"git\s+(clean|worktree\s+remove|worktree\s+prune|stash\s+(drop|clear))\b", "delete (git)"),
    (r"git\s+reset\s+--hard", "git reset --hard"),
    (r"git\s+checkout\s+--\s", "discard changes"),
    (r"git\s+restore\b(?!.*--staged)", "discard changes"),
    (r"git\s+tag\s+.*-d\b", "delete tag"),
    (r"\bgh\s+(pr\s+(create|merge|comment|close|review)|issue\s+(create|comment|close)|release|repo\s+delete|api\b)", "GitHub write"),
    (C + r"(kubectl|helm|terraform|ansible-playbook|pulumi|vercel|netlify|flyctl|fly|az|aws|gcloud)\s", "deploy"),
    (r"docker\s+(push|compose\s+up|run|rm|rmi|system\s+prune|volume\s+rm)", "docker deploy/delete"),
    (r"\b(npm|pnpm|yarn)\s+publish\b|\bcargo\s+publish\b|\btwine\s+upload\b", "publish"),
    (C + r"(scp|rsync|ssh|sftp)\s", "remote host"),
    (r"\b(curl|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b.*(-X\s*(POST|PUT|DELETE|PATCH)|--data|-d\s|-F\s|-Method\s+(Post|Put|Delete|Patch))", "outbound write request"),
    (C + r"(sendmail|mail|mutt)\s|\bSend-MailMessage\b", "send mail"),
    (C + r"shutdown\s|\b(Restart-Computer|Stop-Computer)\b", "machine control"),
]


def regex_reason(text):
    for pattern, label in REGEX_RULES:
        if re.search(pattern, text, re.I):
            return label
    return None


def powershell_reason(text):
    return regex_reason(text)


def bash_reason(text):
    """Block label for a Bash command line, or None. Unparseable means regex fallback."""
    try:
        label = check_script(text)
        return None if label is STDIN_SHELL else label
    except Unsure:
        return regex_reason(text)
