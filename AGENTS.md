# supermatt — repository agreement

Project rules for any coding agent. The global agreement (`~/.codex/AGENTS.md`)
already covers execution, verification and delivery; this file holds only
supermatt-specific truth.

## State

Local git repository on `main`, with no remote configured. Commits stay local
until a remote is added. The only stack is Python 3, standard library only.
There is no typechecker. Run every command before documenting it.

## Overview

supermatt is a Claude Code plugin (`plugin/`): a fused skill set invoked as
`/supermatt:<name>`, a resumable pipeline (`/supermatt:run`), and enforcement
hooks that act only in repos with `.supermatt/config.json`. See `CONTEXT.md`
for terms and `docs/adr/0001-supermatt-is-a-plugin-that-owns-its-skills.md`
for why.

## Architecture

- `plugin/.claude-plugin/plugin.json`: the manifest.
- `plugin/skills/<name>/`: the fused skills. `run` and `status` are original;
  the rest are adapted from the source clones (see `plugin/NOTICE.md`).
- `plugin/bin/supermatt`: the stdlib Python command the skills and hooks call
  for options (`.supermatt/config.json`, committed) and pipeline state
  (`.supermatt/state.json`, gitignored).
- `plugin/hooks/hooks.json`: PreToolUse, Stop and SessionStart hooks, all
  running `supermatt hook <event>`.
- `spine_check.py` + `spine-manifest.json`: the older check of the 23 links
  into the source clones.

## Commands

- Tests: `python3 -m unittest` (run from the repo root)
- Validate the plugin: `claude plugin validate plugin`
- Installed state: `claude plugin list` shows `supermatt@skills-dir` loaded
  from the `~/.claude/skills/supermatt` link to `plugin/`. Edits here load in
  the next session (or `/reload-plugins`).

## Gotchas

- Skills call the command as `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`; keep it
  standard-library Python so it runs anywhere `python3` does.
- A broken `.supermatt/config.json` makes every hook a no-op rather than
  wedging sessions; `supermatt status` reports the error.
- The Stop hook blocks at most three times in a row, then lets the turn end
  with a warning.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
