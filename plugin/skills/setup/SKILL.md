---
name: setup
description: "Set this repo up for supermatt: issue tracker, triage labels, domain doc layout, test command, enforcement preset and pipeline options. Run once per repo; /supermatt:run runs it for you when it is missing."
---

# Setup

Scaffold the per-repo configuration that the supermatt skills assume:

- **Issue tracker**: where issues live (GitHub by default; local markdown is also supported out of the box)
- **Triage labels**: the strings used for the five canonical triage roles
- **Domain docs**: where `CONTEXT.md` and ADRs live, and the consumer rules for reading them
- **supermatt options** in `.supermatt/config.json`: the test command, which enforcement rules are on, and how `/supermatt:run` behaves

This is a prompt-driven skill, not a deterministic script. Explore, present what you found, confirm with the user, then write.

## Process

### 1. Explore

Look at the current repo to understand its starting state. Read whatever exists; don't assume:

- `git remote -v` and `.git/config`: is this a GitHub repo? Which one?
- `AGENTS.md` and `CLAUDE.md` at the repo root: does either exist? Is there already an `## Agent skills` section in either?
- `CONTEXT.md` and `CONTEXT-MAP.md` at the repo root
- `docs/adr/` and any `src/*/docs/adr/` directories
- `docs/agents/`: does this skill's prior output already exist?
- `.scratch/`: a sign that a local-markdown issue tracker convention is already in use
- `.supermatt/config.json`: is the repo already set up, and does this machine trust its config? (`"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" status`). A config that exists but is not trusted came from a clone or pull: show the user its `test_command`, and on their OK run `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" trust` instead of re-running setup.
- The test command: `package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, `go.mod`, the repo's `AGENTS.md`/`CLAUDE.md` commands section, CI config. Run the candidate once to confirm it works before proposing it.
- Monorepo signals: a `pnpm-workspace.yaml`, a `workspaces` field in `package.json`, or a populated `packages/*` with its own `src/`. These are present only in a genuinely large multi-package repo; their absence means single-context, which is almost every repo.

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order. One section, one answer, then the next.

Lead each section with the recommended answer so the user can accept it in a word. Give a one-line explainer only when the choice genuinely branches; skip the section entirely when exploration already settled it (Section C when there's no monorepo).

**Section A: Issue tracker.**

> Explainer: The "issue tracker" is where issues live for this repo. Skills like `supermatt:tickets`, `supermatt:triage`, and `supermatt:spec` read from and write to it. They need to know whether to call `gh issue create`, write a markdown file under `.scratch/`, or follow some other workflow you describe. Pick the place you actually track work for this repo.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that. If a `git remote` points at GitLab (`gitlab.com` or a self-hosted host), propose GitLab. Otherwise (or if the user prefers), offer:

- **GitHub**: issues live in the repo's GitHub Issues (uses the `gh` CLI)
- **GitLab**: issues live in the repo's GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Local markdown**: issues live as files under `.scratch/<feature>/` in this repo (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.): ask the user to describe the workflow in one paragraph; the skill will record it as freeform prose

Record the choice in `docs/agents/issue-tracker.md`. The GitHub and GitLab templates carry a "PRs as a request surface" flag, defaulted **off**. Leave it off and don't raise it: a user who wants external PRs in the triage queue can flip the flag in the file later.

**Section B: Triage label vocabulary.** Ask exactly one question:

> Do you want to keep the default triage labels? (recommended: **yes**)

The defaults are the five canonical roles, each label string equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only if the user says no, usually because their tracker already uses other names (e.g. `bug:triage` for `needs-triage`), collect the overrides so `supermatt:triage` applies existing labels instead of creating duplicates.

**Section C: Domain docs.** Default to **single-context** (one `CONTEXT.md` + `docs/adr/` at the repo root). This fits almost every repo; write it without asking.

Offer **multi-context** (a root `CONTEXT-MAP.md` pointing to per-context `CONTEXT.md` files) only when exploration found monorepo signals. Then confirm which layout they want.

**Section D: Test command.** Propose the command you confirmed in exploration. Check that it tests the current source, not a stale artifact: an end-to-end suite that serves a production build (for example Playwright starting `next start`) needs the build step in the command (`npm run build && npm run test:e2e`). Time the confirming run: the command must finish within `test_timeout` (at most 570 seconds). It is what the enforcement rules and the `verify` stage run. If the repo has no tests yet, record none: the test rules then stay quiet until one is set with `supermatt config test_command "<cmd>"`.

**Section E: Enforcement preset.** Ask one question, recommending **standard**:

| Preset | tests_before_commit | ticket_before_code | review_after_ticket | green_before_stop |
|---|---|---|---|---|
| strict | block | block | block | block |
| standard | block | warn | block | block |
| light | warn | warn | warn | warn |
| off | off | off | off | off |

- **tests_before_commit**: a `git commit` runs the test command first; red blocks (or warns about) the commit.
- **ticket_before_code**: editing code (anything not matched by `exempt`, which defaults to `.scratch/*`, `docs/*`, `.supermatt/*`, `*.md`) needs a ticket in progress.
- **review_after_ticket**: a committed ticket must be reviewed before the next ticket starts or the session stops.
- **green_before_stop**: Claude cannot end a turn while uncommitted code fails the tests (it gives up after three tries and tells the user).

Any single rule can be changed later: `supermatt config enforce.<rule> off|warn|block`.

When the confirming run was slow (a build plus an end-to-end suite, say over a minute), recommend `green_before_stop` off: it runs the command at the end of every turn that changed code, even at `warn`. `tests_before_commit` at `block` is then the gate that matters.

**Section F: Pipeline options.** Show the defaults and ask whether to keep them (recommended: **yes**):

- `pipeline.interview`: `full` (the grilling waits for the user's answers) or `auto` (it settles every question with its recommended answer and records them as assumed decisions in the spec)
- `pipeline.pause_at`: stages `/supermatt:run` pauses *before*, waiting for the user's go-ahead. Default `implement,finish`: check the spec and tickets before code is written, and the verify evidence before anything is merged. Stages: `grill`, `spec`, `tickets`, `implement`, `verify`, `finish`; `none` never pauses.
- `pipeline.branch`: create a `<feature-slug>` branch before implementing (default `true`; set `false` for teams that commit straight to the main branch)
- `pipeline.worktree`: implement in an isolated worktree via `/supermatt:worktree` (default `false`)
- `pipeline.ticket_agents`: build each ticket in a fresh subagent instead of this context (default `false`)
- `pipeline.finish`: `ask` (show the merge / PR / keep menu), or always `merge`, `pr` or `keep`

### 3. Confirm and edit

Show the user a draft of:

- The `## Agent skills` block to add to whichever of `CLAUDE.md` / `AGENTS.md` is being edited (see step 4 for selection rules)
- The contents of `docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and `docs/agents/triage-labels.md`
- The supermatt options from Sections D to F

Let them edit before writing.

### 4. Write

**Pick the file to edit:**

- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask the user which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there.

If an `## Agent skills` block already exists in the chosen file, update its contents in-place rather than appending a duplicate. Don't overwrite user edits to the surrounding sections.

The block:

```markdown
## Agent skills

### Issue tracker

[one-line summary of where issues are tracked]. See `docs/agents/issue-tracker.md`.

### Triage labels

[one-line summary of the label vocabulary]. See `docs/agents/triage-labels.md`.

### Domain docs

[one-line summary of layout: "single-context" or "multi-context"]. See `docs/agents/domain.md`.
```


Then write the docs files using the seed templates in this skill folder as a starting point:

- [issue-tracker-github.md](./issue-tracker-github.md): GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md): GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md): local-markdown issue tracker
- [triage-labels.md](./triage-labels.md): label mapping
- [domain.md](./domain.md): domain doc consumer rules + layout

For "other" issue trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

Then write the supermatt options:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" init --preset <preset> --test-command "<test command>"   # omit --test-command when there is none
"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" config pipeline.<option> <value>                       # once per changed pipeline option
```

`init` writes `.supermatt/config.json` (commit it, before any worktree is created, so worktrees see it), gitignores `.supermatt/state.json` (the pipeline's local progress), and trusts the config on this machine. Teammates who pull the config approve it once with `supermatt trust`. On a repo that is already set up, change options with `config` instead of re-running `init`.

### 5. Done

Tell the user the setup is complete, which preset is active, and that `/supermatt:run <feature>` starts the pipeline. `/supermatt:status` shows and changes options later; `docs/agents/*.md` can be edited directly.
