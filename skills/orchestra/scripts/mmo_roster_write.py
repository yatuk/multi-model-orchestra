"""Write stage of `mmo-roster probe --write`: can a lane that answered also write files AND run a command?

A lane whose write mode allows edits but not shell commands cannot run a task's check and reports
FAILED on work that is correct. This stage catches it before real work is sent: one rw brief per lane in
a throwaway git worktree, judged only from the files left behind, never from the lane's words.

can_write: probe.txt or ver.txt appeared. can_run: probe.txt holds the marker AND ver.txt holds what the
real `python --version` (else `git --version`) prints on this machine, so a lane that only typed text
cannot pass. Values are the strings "true", "false" or "not-tested" (the lane never got to work: limit,
sign-in, rejected model, timeout).
"""
import os
import shutil
import stat
import subprocess
import tempfile
import time

MARK = "mmo-probe-7391"
NOT_RUN = ("limit", "auth", "model", "timeout")  # exit statuses that mean the lane never worked
EXIT_STATUS = {0: "ok", 3: "failed", 4: "timeout", 5: "failed", 6: "limit", 7: "auth", 8: "model"}


def version_command():
    """The command whose real output a lane must reproduce: python --version, else git --version."""
    for exe in ("python", "python3"):
        if shutil.which(exe):
            r = subprocess.run([exe, "--version"], capture_output=True, text=True)
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0 and out:
                return exe + " --version", out
    r = subprocess.run(["git", "--version"], capture_output=True, text=True)
    return "git --version", (r.stdout + r.stderr).strip()


def rmtree_force(path):
    def onerr(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=onerr)


def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def make_worktree(tmp):
    """A repo with one commit and a linked worktree (mmo-run refuses rw anywhere else)."""
    repo, wt = os.path.join(tmp, "repo"), os.path.join(tmp, "wt")
    os.makedirs(repo)
    with open(os.path.join(repo, "README"), "w") as f:
        f.write("probe\n")
    base = ["git", "-C", repo, "-c", "user.email=probe@example.invalid", "-c", "user.name=mmo-probe",
            "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false"]
    for args in (["init", "-q"], ["add", "."], ["commit", "-qm", "init"], ["worktree", "add", "-q", wt, "-b", "probe"]):
        if subprocess.run(base + args, capture_output=True).returncode:
            return None
    return wt


def judge(wt, code, cmd_out):
    probe_txt = read_file(os.path.join(wt, "probe.txt"))
    ver_txt = read_file(os.path.join(wt, "ver.txt"))
    wrote = probe_txt is not None or ver_txt is not None
    if not wrote and (code is None or EXIT_STATUS.get(code) in NOT_RUN):
        return "not-tested", "not-tested"
    ran = probe_txt is not None and MARK in probe_txt and ver_txt is not None and cmd_out in ver_txt
    return ("true" if wrote else "false"), ("true" if ran else "false")


def write_probe(jobs, runner, bash, env, timeout):
    """Set can_write and can_run on each job (a roster row) in place. Four lanes at a time, one call each."""
    cmd_text, cmd_out = version_command()
    brief_text = ("Run the shell command `echo %s` and write exactly its output into a file named probe.txt. "
                  "Also run `%s` and write exactly its output into a file named ver.txt. "
                  "Do not commit. Finish with DONE.\n" % (MARK, cmd_text))
    fwd = lambda p: p.replace("\\", "/")
    for start in range(0, len(jobs), 4):
        batch = []
        for i, job in enumerate(jobs[start:start + 4]):
            if i:
                time.sleep(1)  # two lanes on one CLI started in the same second collide on its storage
            tmp = tempfile.mkdtemp(prefix="mmo-write-")
            wt = make_worktree(tmp)
            job["can_write"] = job["can_run"] = "not-tested"
            if wt is None:
                rmtree_force(tmp)
                continue
            brief = os.path.join(tmp, "brief.md")
            with open(brief, "w", encoding="utf-8") as f:
                f.write(brief_text)
            cmd = [bash, runner, job["lane"], "--mode", "rw", "-C", fwd(wt), "-t", str(timeout),
                   "--brief", fwd(brief), "--out", fwd(os.path.join(tmp, "out.md"))]
            if job["model"]:
                cmd[3:3] = ["-m", job["model"]]
            p = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            batch.append((job, tmp, wt, p))
        for job, tmp, wt, p in batch:
            code = None
            try:
                code = p.wait(timeout=timeout + 30)
            except subprocess.TimeoutExpired:
                p.kill()
            job["can_write"], job["can_run"] = judge(wt, code, cmd_out)
            rmtree_force(tmp)
