---
name: status
description: Show where the supermatt pipeline is (feature, stage, tickets, trust) and the repo's supermatt options, and change options when the user asks - enforcement rules, presets, the test command or pipeline behaviour. Use when the user asks about supermatt's state or settings, or asks for a rule to be turned on, off, or to warn.
argument-hint: "[<option> <value> | preset <name> | trust]"
---

# Status

`SM` means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`.

1. Run `SM status` and show the output as is. If the repo is not set up, say so and offer `/supermatt:setup`. If it says the config is not trusted, show the config's `test_command` and explain that hooks stay off until the user approves it; run `SM trust` only when the user says so.
2. **Change options only when the user asked for that change in this conversation.** Never relax a rule on your own initiative, for example to get past a hook that blocked you. Map the request to one command, run it, then run `SM status` again:
   - A whole preset: `SM config preset strict|standard|light|solo|off`
   - One rule: `SM config enforce.<rule> off|warn|block`, where rule is `tests_before_commit`, `ticket_before_code`, `review_after_ticket` or `green_before_stop`
   - The test command: `SM config test_command "<cmd>"` (run it once first to confirm it works); `SM config test_timeout <seconds>` (at most 570)
   - Pipeline behaviour: `SM config pipeline.interview full|auto`; `SM config pipeline.pause_at <stage,stage>` (stages to pause before: grill, spec, tickets, implement, verify, finish; `none` never pauses); `SM config pipeline.branch|worktree|ticket_agents|review_agents true|false`; `SM config pipeline.branch_prefix <prefix>` (for example `claude/`); `SM config pipeline.finish ask|merge|push|pr|keep`
   - Paths the code rules ignore: `SM config exempt "<glob>,<glob>"` (replaces the list)
3. `.supermatt/config.json` is committed, so an option change is a repo change: mention that it shows up in `git status`, and that teammates approve the new config with `supermatt trust` after they pull it.

What the rules do:

- **tests_before_commit**: a `git commit` runs the test command first, unless these exact files already passed it; red blocks (or warns about) the commit.
- **ticket_before_code**: editing a non-exempt file needs a ticket `implementing` or `needs-review`.
- **review_after_ticket**: the next ticket cannot start, and a turn cannot end, while a committed ticket awaits review.
- **green_before_stop**: a turn cannot end while uncommitted code fails the tests, except mid-ticket (`implementing`), where red is part of test-first work; it never blocks twice on the same unchanged files, and after three blocked stops in a row it lets go and tells the user.

A ticket recorded as `blocked` (waiting on the user) lets the turn end regardless.
