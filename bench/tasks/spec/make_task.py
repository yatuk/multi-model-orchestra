"""Build the spec task: a written retention policy, 20 artifacts, and the gold answers.

The records are fixed (no randomness) so every run grades the same input. `decide` below
is the reference implementation of the policy text in RULES; the gold file comes from it.
Each record is there to hit one boundary, one precedence or one exception. Rule 8 makes
some answers depend on another record's answer, and some records point forward.
"""
from pathlib import Path

# id, branch, kind, age_days, size_mb, downloads_30d, pinned, tag, of
RECORDS = [
    ("a01", "main", "log", 50, 1, 0, "no", "-", "a07"),
    ("a02", "feature/ui", "log", 91, 2, 0, "yes", "-", "a14"),
    ("a03", "release/2.1", "log", 400, 5, 0, "no", "ga", "-"),
    ("a04", "main", "report", 200, 2, 0, "no", "-", "a09"),
    ("a05", "release/5.2", "binary", 100, 300, 0, "no", "rc", "-"),
    ("a06", "releases/old", "report", 300, 2, 0, "no", "-", "-"),
    ("a07", "main", "binary", 120, 80, 0, "no", "-", "-"),
    ("a08", "main", "log", 200, 3000, 0, "no", "-", "a09"),
    ("a09", "main", "binary", 400, 60, 0, "yes", "-", "-"),
    ("a10", "release/5.2", "log", 31, 1, 9, "no", "rc", "a05"),
    ("a11", "feature/pay", "report", 10, 3, 0, "no", "-", "a16"),
    ("a12", "main", "log", 30, 2049, 0, "no", "-", "-"),
    ("a13", "release/5.2", "report", 200, 4, 0, "no", "ga", "a05"),
    ("a14", "feature/ui", "binary", 91, 4000, 20, "yes", "ga", "-"),
    ("a15", "main", "report", 300, 2, 0, "no", "-", "a18"),
    ("a16", "feature/pay", "binary", 20, 30, 0, "no", "-", "-"),
    ("a17", "feature/pay", "log", 10, 1, 0, "yes", "-", "a16"),
    ("a18", "main", "binary", 95, 50, 3, "no", "-", "-"),
    ("a19", "release/1.0", "binary", 400, 2100, 10, "no", "rc", "-"),
    ("a20", "hotfix/disk", "log", 40, 4096, 0, "no", "-", "-"),
]

RULES = """You apply a retention policy to build artifacts. For every artifact decide KEEP, ARCHIVE or
DELETE, and say which rule decided it.

Fields: branch, kind (binary, log or report), age in days, size in MB, downloads in the last 30
days, pinned (yes or no), tag (ga, rc, or - for none), and of: for a log or report that belongs
to a binary, the id of that binary (always a binary in the list); otherwise -.

Definitions:
- "older than N days" means age > N. An artifact exactly N days old is not older than N days.
- "larger than N MB" means size > N.
- A feature branch is a branch whose name starts with "feature/". A release branch starts with
  "release/". The main branch is exactly "main". Any other name is none of these.

Rules 1-7 decide each artifact on its own. Go from rule 1 down; the first rule that decides is
the result. A rule that "does not decide" passes the artifact on to the next rule.
1. Pinned. A pinned artifact is KEEP. Exception: a pinned artifact on a feature branch that is
   older than 90 days is not protected; rule 1 does not decide it.
2. GA tag. An artifact tagged ga is KEEP. Exception: a log tagged ga that is older than 365 days
   is ARCHIVE.
3. Oversize. An artifact larger than 2048 MB and older than 30 days is DELETE. Exception: if it
   had 10 or more downloads, it is ARCHIVE instead. Exception to that exception: on a feature
   branch downloads never save an artifact, so it stays DELETE. Rule 3 does not decide any
   other artifact.
4. Feature branch. An artifact on a feature branch is DELETE when older than 14 days,
   otherwise KEEP.
5. Release branch. For an artifact on a release branch, in this order:
   a. a log older than 30 days is DELETE, whatever its tag;
   b. tagged rc: ARCHIVE when older than 180 days, otherwise KEEP;
   c. otherwise: DELETE when older than 60 days, otherwise KEEP.
6. Main branch. An artifact on main older than 90 days is ARCHIVE when it had at least 1
   download, otherwise DELETE. An artifact on main 90 days old or younger is KEEP.
7. Anything that reaches rule 7 is KEEP.

Rule 8 runs after rules 1-7 have given every artifact a result. It applies only to a log or
report whose of field names a binary, and it looks at that binary's result from rules 1-7.
8. Companions.
   - If the binary is KEEP, the companion becomes KEEP, unless its own result was DELETE by
     rule 3.
   - If the binary is DELETE, the companion becomes DELETE, unless its own result was KEEP by
     rule 1 or rule 2.
   - If the binary is ARCHIVE, nothing changes.
   When rule 8 changes the decision, the rule number becomes 8. When the decision stays the
   same, the rule number stays the one from rules 1-7."""

FORMAT = """Reply with one line per artifact, in the order given, and nothing else:
ID DECISION RULE
where DECISION is KEEP, ARCHIVE or DELETE and RULE is the number 1-8 of the rule that decided.
Example line: a99 ARCHIVE 3
Work it out by reading the rules carefully; do not write or run code."""


def older(age, n):
    return age > n


def decide_alone(rec):
    """Rules 1-7."""
    _, branch, kind, age, size, downloads, pinned, tag, _of = rec
    feature = branch.startswith("feature/")
    release = branch.startswith("release/")
    if pinned == "yes" and not (feature and older(age, 90)):
        return "KEEP", 1
    if tag == "ga":
        if kind == "log" and older(age, 365):
            return "ARCHIVE", 2
        return "KEEP", 2
    if size > 2048 and older(age, 30):
        if downloads >= 10 and not feature:
            return "ARCHIVE", 3
        return "DELETE", 3
    if feature:
        return ("DELETE" if older(age, 14) else "KEEP"), 4
    if release:
        if kind == "log" and older(age, 30):
            return "DELETE", 5
        if tag == "rc":
            return ("ARCHIVE" if older(age, 180) else "KEEP"), 5
        return ("DELETE" if older(age, 60) else "KEEP"), 5
    if branch == "main":
        if older(age, 90):
            return ("ARCHIVE" if downloads >= 1 else "DELETE"), 6
        return "KEEP", 6
    return "KEEP", 7


def decide_all(records):
    """Rules 1-7 for every record, then rule 8 against the binaries' rule 1-7 results."""
    alone = {r[0]: decide_alone(r) for r in records}
    final = {}
    for r in records:
        rid, kind, of = r[0], r[2], r[8]
        result = alone[rid]
        if kind in ("log", "report") and of != "-":
            parent = alone[of][0]
            if parent == "KEEP" and result != ("DELETE", 3):
                new = "KEEP"
            elif parent == "DELETE" and result not in (("KEEP", 1), ("KEEP", 2)):
                new = "DELETE"
            else:
                new = result[0]
            if new != result[0]:
                result = (new, 8)
        final[rid] = result
    return final


def main():
    here = Path(__file__).parent
    header = "id | branch | kind | age_days | size_mb | downloads_30d | pinned | tag | of"
    table = "\n".join(" | ".join(str(v) for v in r) for r in RECORDS)
    # newline="\n": the same bytes on every OS, so a rebuild never shows as a change.
    (here / "brief.md").write_text(
        RULES + "\n\nArtifacts:\n\n" + header + "\n" + table + "\n\n" + FORMAT + "\n", encoding="utf-8", newline="\n"
    )
    final = decide_all(RECORDS)
    gold = "".join(f"{r[0]},{final[r[0]][0]},{final[r[0]][1]}\n" for r in RECORDS)
    (here / "gold.csv").write_text("id,decision,rule\n" + gold, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
