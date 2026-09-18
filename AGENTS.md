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
- `plugin/skills/<name>/`: the fused skills. `run`, `status` and `advise` are original;
  the rest are adapted from the source clones (see `plugin/NOTICE.md`).
- `plugin/bin/supermatt`: the stdlib Python command the skills and hooks call
  for options (`.supermatt/config.json`, committed) and pipeline state
  (`.supermatt/state.json`, gitignored).
- `plugin/hooks/hooks.json`: PreToolUse, Stop and SessionStart hooks, all
  running `supermatt hook <event>`.
- `.claude-plugin/marketplace.json`: makes the repo installable with
  `claude plugin marketplace add`.
- `spine_check.py` + `spine-manifest.json`: the retired skill spine. The 23
  links were removed from `~/.claude/skills` on 2026-09-18 because the plugin
  replaces them, so `spine_check.py` now reports every entry `missing`. The
  manifest still records how to recreate them:
  `python3 -c "import json,os;[os.symlink(os.path.expanduser('~/skills-src/'+e['clone']+'/'+e['path']),os.path.expanduser('~/.claude/skills/'+e['name'])) for e in json.load(open('spine-manifest.json'))['skills']]"`

## Commands

- Tests: `python3 -m unittest` (run from the repo root)
- Validate the marketplace and plugin: `claude plugin validate . && claude plugin validate plugin`
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
- Hooks act only on a trusted config (`supermatt trust`; stored outside the
  repo). Tests set `SUPERMATT_TRUST_FILE` to a temp path; never let a test
  write the real trust file.
- `python3 -m unittest` runs under the macOS system Python (3.9) too; keep the
  command 3.9-compatible.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
