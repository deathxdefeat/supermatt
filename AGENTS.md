# supermatt — repository agreement

Project rules for any coding agent working on supermatt.

## State

Hosted at github.com/deathxdefeat/supermatt; `main` is the only branch and CI
runs the tests on every push. The only stack is Python 3, standard library
only. There is no typechecker. Run every command before documenting it.

## This repo is public

Nothing from a working session is ever committed here: no specs or tickets
(`.scratch/`), no `.claude/`, `.codex/` or `.supermatt/` files, no handoffs,
memory, transcripts or env files, no home-directory paths, no real names,
emails, employers or clients, and no credentials. Examples in docs and tests
use placeholders (`~`, `you@example.com`).

- `.githooks/leak_check.py` enforces this on every commit and push. After
  cloning, turn it on: `git config core.hooksPath .githooks`. Never bypass it
  with `--no-verify`; fix the finding, or ask the user.
- Words only the owner knows to be private go in
  `~/.config/supermatt/private-patterns` (one regex per line), which stays on
  their machine. Never copy its contents into the repo, a commit message or a
  test.
- Commit identities use a GitHub noreply address.

## Overview

supermatt is a Claude Code plugin (`plugin/`): a fused skill set invoked as
`/supermatt:<name>`, a resumable pipeline (`/supermatt:run`), and enforcement
hooks that act only in repos with `.supermatt/config.json`. See `CONTEXT.md`
for terms and `docs/adr/0001-supermatt-is-a-plugin-that-owns-its-skills.md`
for why.

## Architecture

- `plugin/.claude-plugin/plugin.json`: the manifest.
- `plugin/skills/<name>/`: the fused skills. `run`, `status` and `drift` are original, and so is
  `advise` apart from its skills map; the rest are adapted from the source skills (see `plugin/NOTICE.md`).
- `plugin/bin/supermatt`: the stdlib Python command the skills and hooks call
  for options (`.supermatt/config.json`, committed) and pipeline state
  (`.supermatt/state.json`, gitignored).
- `plugin/hooks/hooks.json`: PreToolUse, Stop and SessionStart hooks, all
  running `supermatt hook <event>`.
- `.claude-plugin/marketplace.json`: makes the repo installable with
  `claude plugin marketplace add`.
- `docs/diagrams/*.json`: the README diagram sources; `docs/images/*.png` are
  their light-theme captures.

## Commands

- Tests: `python3 -m unittest` (run from the repo root)
- Leak check over every tracked file: `python3 .githooks/leak_check.py tree`
- Validate the marketplace and plugin: `claude plugin validate . && claude plugin validate plugin`
- Develop against a live install: link `plugin/` to
  `~/.claude/skills/supermatt`; `claude plugin list` then shows
  `supermatt@skills-dir`, and edits load in the next session (or
  `/reload-plugins`).

## Gotchas

- Skills call the command as `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`; keep it
  standard-library Python so it runs anywhere `python3` does.
- A broken `.supermatt/config.json` makes every hook a no-op rather than
  wedging sessions; `supermatt status` reports the error.
- The Stop hook blocks at most three times in a row, then lets the turn end
  with a warning. It never blocks twice on the same unchanged files.
- `supermatt test` and the commit and Stop hooks share one memory of which
  files passed (`green` in the state file). Skills run the suite through
  `supermatt test`, never the raw command, so nothing is tested twice.
- Hooks act only on a trusted config (`supermatt trust`; stored outside the
  repo). Tests set `SUPERMATT_TRUST_FILE` to a temp path; never let a test
  write the real trust file.
- `python3 -m unittest` runs under the macOS system Python (3.9) too; keep the
  command 3.9-compatible.

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`, which is gitignored: they stay on this machine. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
