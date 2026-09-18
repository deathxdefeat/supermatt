# supermatt — repository agreement

Project rules for any coding agent. The global agreement (`~/.codex/AGENTS.md`)
already covers execution, verification and delivery; this file holds only
supermatt-specific truth.

## State

New local git repository on `main`, with no remote configured. Commits stay local
until a remote is added. The only stack is Python 3, standard library only, for
the spine-check command. There is no typechecker. There is no other
architecture or product contract yet. Do not infer or invent them.

As they become real, add Overview, Commands, Architecture, Conventions and
Gotchas sections here. Run every command before documenting it.

## Commands

- Tests: `python3 -m unittest` (run from the repo root)

## Agent skills

### Issue tracker

Issues and specs live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
