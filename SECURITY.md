# Security policy

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private vulnerability reporting for this repository:
the **Security** tab, then **Report a vulnerability** (a private security advisory). Include the version or
commit, the steps to reproduce, and what an attacker gains. Remove any real secrets from what you send.

## Scope

In scope:

- The runner (`skills/orchestra/scripts/mmo-run`) and its helpers: escaping a worktree, writing outside the
  allowed directory, a read-only lane that can change the main checkout, command injection through a brief,
  model name or path.
- Bypasses of the otomode hook: a command or tool call that the guard rail is meant to deny but lets through.
- Briefs, templates or scripts that leak data, such as sending local files or environment values to a vendor
  without the user asking.

Out of scope: bugs in the vendor CLIs themselves (report those upstream), and model behavior that needs no
flaw in these scripts.

## otomode is a guard rail, not a sandbox

The otomode hook denies prompts and refuses a list of dangerous commands and tool names. It reduces
accidents during an unattended run. It does not isolate the agent, and a determined or confused agent with
shell access can find ways around a pattern list. Run unattended work in a worktree or a disposable
environment, and keep credentials the agent should not use out of reach.
