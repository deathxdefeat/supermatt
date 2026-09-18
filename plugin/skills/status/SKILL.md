---
name: status
description: Show where the supermatt pipeline is (feature, stage, tickets) and the repo's supermatt options, and change options such as enforcement rules, presets, the test command or pipeline behaviour. Use when the user asks about supermatt's state or settings, or wants a rule turned on, off, or to warn.
argument-hint: "[<option> <value> | preset <name>]"
---

# Status

`SM` means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`.

1. Run `SM status` and show the output as is. If the repo is not set up, say so and offer `/supermatt:setup`.
2. If the user asked to change something, map it to one command and run it, then run `SM status` again to show the result:
   - A whole preset: `SM config preset strict|standard|light|off`
   - One rule: `SM config enforce.<rule> off|warn|block`, where rule is `tests_before_commit`, `ticket_before_code`, `review_after_ticket` or `green_before_stop`
   - The test command: `SM config test_command "<cmd>"` (run it once first to confirm it works)
   - Pipeline behaviour: `SM config pipeline.interview full|auto`, `SM config pipeline.pause_at <stage,stage>` (stages: grill, spec, tickets, implement, verify, finish; an empty value never pauses), `SM config pipeline.branch|worktree|ticket_agents true|false`, `SM config pipeline.finish ask|merge|pr|keep`
   - Paths the code rules ignore: `SM config exempt "<glob>,<glob>"` (replaces the list)
3. `.supermatt/config.json` is committed, so an option change is a repo change: mention that it shows up in `git status`.

What the rules do:

- **tests_before_commit**: a `git commit` runs the test command first; red blocks (or warns about) the commit.
- **ticket_before_code**: editing a non-exempt file needs a ticket `implementing` or `needs-review`.
- **review_after_ticket**: the next ticket cannot start, and the session cannot stop, while a committed ticket awaits review.
- **green_before_stop**: a turn cannot end while uncommitted code fails the tests; after three blocked stops it lets go and tells the user.
