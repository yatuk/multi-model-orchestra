Outcome: <one sentence: what is true when you are done>

Context:
- Repo: <what it is, language, how tests run>
- Relevant files: <paths>, read these first
- Background: <the two or three facts a stranger would need>

Steps:
1. <exact step>
2. <exact step>
3. Run `<exact check command>` and make it pass.

You may edit: <paths or globs>
Do not: edit or delete existing tests, add dependencies, commit, push, touch files outside the list
above, silence warnings, or change public names and signatures unless a step says so.

If the job cannot be done honestly (the check contradicts the task, something you need is missing,
the steps are wrong), stop and say so. That is a good answer. Changing a test or special-casing an
input so the check turns green is not.

Report in at most ten lines: what changed, which files, the last line of the check. Put anything
longer in <notes file>.
Finish with one line: DONE, FAILED: <reason>, or BLOCKED: <reason>.
