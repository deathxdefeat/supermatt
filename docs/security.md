# Security: trust, what the hooks run, and limits

What supermatt runs on your machine, when, and what it cannot protect you from. To report a vulnerability, see [SECURITY.md](../SECURITY.md). For the overview, see the [README](../README.md).

The config names a command that the hooks run on their own, so supermatt acts on a repo's config only after this machine has approved it. Without that check, cloning a repo could make Claude Code run any command the repo's author chose, the next time Claude commits or ends a turn.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/trust-dark.png">
  <img alt="Config trust: configs written by supermatt init are trusted, configs arriving by clone or pull stay off until you run supermatt trust" src="images/trust.png">
</picture>

*Trust records the repo's path and a SHA-256 hash of the config's exact contents, so any change made outside `supermatt config` has to be approved again.*

- **Trust is exact.** `supermatt init` trusts the config it writes, and `supermatt config` keeps a trusted config trusted after its own edit. Any other change (a pull, a teammate's edit, your own hand edit) needs approving again. `/supermatt:run`, `/supermatt:setup` and `/supermatt:status` show you the `test_command` and ask before trusting.
- **You are told when supermatt is off.** An untrusted or invalid config turns the hooks off for that repo, and each session start (including after `/clear` or compaction) tells you which it is. Only the hooks go quiet: with a valid but untrusted config, the `supermatt ticket` command still applies `review_after_ticket`, because the skills call it directly.
- **Trust covers the command, not the code it runs.** Approval pins the exact `test_command` text. If that command runs code from the repo (`npm test` runs your test files), pulling or checking out code you haven't reviewed, such as an outside pull request, means the hooks will run that code the next time Claude commits or ends a turn. Review untrusted branches before working on them with the guardrails on, or set `enforce` to `off` for that checkout.
- **Where trust lives.** Trusted configs are listed in `~/.config/supermatt/trusted.json`, or at `$SUPERMATT_TRUST_FILE` if set. Linked worktrees share the main checkout's trust and pipeline state.

## What the hooks run

| Hook | Fires on | Runs | Claude Code timeout |
|---|---|---|---|
| PreToolUse | Bash tool calls | Your `test_command`, only when the command contains `git commit` and these files have not already passed it. Every other Bash call returns before touching git or the disk. | 600 s |
| PreToolUse | Edit, Write, MultiEdit, NotebookEdit | Only `git` lookups and a read of the config and pipeline state | 10 s |
| Stop | Every end of turn | `git status`, and your `test_command` when uncommitted code changed since the last passing test run. Files that failed last time and have not changed since are not run again. | 600 s |
| SessionStart | Session start, resume, `/clear` and compaction | Only `git` lookups; tells Claude which feature is in flight, or tells you why supermatt is off | 10 s |

Apart from your `test_command`, which runs through the shell in the repo root and is stopped after `test_timeout` seconds, the hooks run only read-only `git` commands, and the only file they write is `.supermatt/state.json`.

## Limits

- **Guardrails, not a sandbox.** `ticket_before_code` watches Claude's file-editing tools, not every shell command that could write a file.
- **Commits are recognised by pattern.** `tests_before_commit` looks for `git commit` in a Bash command, including forms like `git -C path commit`. A commit made through a git alias or a script is not seen, and commits you make in your own terminal are never touched.
- **Tests run on the working tree**, not only the staged changes.
- **The end-of-turn check gives up.** After three blocks in a row it lets the turn end with a warning, and it never blocks twice on the same unchanged files, so a session cannot get stuck. A stubborn failure gets through with that warning.
- **A remembered pass is about files, not the world.** supermatt skips the suite when the same non-exempt files already passed. It cannot see a database, a service or an environment variable changing underneath them. `supermatt test --force` reruns the suite when you suspect that, or a flaky test.
- **The rules are only as good as the test command.** A suite that doesn't cover the outcome you care about stays green while the product is broken. That is why `/supermatt:advise` starts such cases with an acceptance test.
- **Relaxing a rule is policy, not a lock.** The skills tell Claude never to change an option to get past a block. Claude could still run `supermatt config` itself; because the config is committed, such a change shows up in `git status`.
- **The hooks never break a session.** Bad hook input, a broken config or a bug inside supermatt never fail a tool call: a bug is reported as a message, a broken or untrusted config is reported when a session starts, and otherwise the hook quietly does nothing.
