# supermatt

A Claude Code plugin that turns Matt Pocock's engineering skills and three Superpowers skills into one workflow.

## Install

The plugin loads from a link in your skills directory:

```bash
ln -s ~/developer/supermatt/plugin ~/.claude/skills/supermatt
```

`claude plugin list` should show `supermatt@skills-dir` as loaded. New sessions pick up edits to `plugin/`, and `/reload-plugins` picks them up mid-session.

## Use

In any repo:

```text
/supermatt:run add CSV export to the reports page
```

On first use in a repo it runs `/supermatt:setup`, which asks where issues live, which test command to run, how strict to be and how the pipeline should behave. Then it drives the feature through **grill → spec → tickets → implement (TDD, commit, two-axis review per ticket) → verify → finish**, recording progress in `.supermatt/state.json`. Run `/supermatt:run` with no arguments to resume, even in a new session.

Flags for one run: `--auto` settles the grilling questions itself and runs without pausing; `--guided` pauses after every stage.

You can still run each stage on its own: `/supermatt:grill`, `/supermatt:spec`, `/supermatt:tickets`, `/supermatt:implement`, `/supermatt:review`, `/supermatt:verify`, `/supermatt:finish`. Side skills: `debug`, `merge`, `triage`, `prototype`, `research`, `architecture`, `wayfinder`, `worktree`, `handoff`. Not sure where to start? Describe the situation to `/supermatt:advise` (for example, paste the problem). It checks the repo, works out what kind of situation it is, and gives you a numbered plan: which skills to run, in what order, with which options, and the first command to type.

## Options

Each repo has its own options in `.supermatt/config.json`. Use `/supermatt:status` to see them and change them, for example "turn ticket_before_code off" or "use the strict preset".

| Rule | What it does |
|---|---|
| `tests_before_commit` | `git commit` runs the test command first, and a failing suite stops the commit |
| `ticket_before_code` | code edits need a ticket in progress |
| `review_after_ticket` | the next ticket can't start, and the session can't stop, until the committed ticket is reviewed |
| `green_before_stop` | Claude can't finish a turn while uncommitted code fails the tests |

Each rule is `off`, `warn` or `block`. The presets set all four rules at once:

| Preset | `tests_before_commit` | `ticket_before_code` | `review_after_ticket` | `green_before_stop` |
|---|---|---|---|---|
| `strict` | block | block | block | block |
| `standard` | block | warn | block | block |
| `light` | warn | warn | warn | warn |
| `off` | off | off | off | off |

The pipeline options are `interview` (`full` or `auto`), `pause_at` (a list of stages), `branch`, `worktree`, `ticket_agents` (build each ticket in a fresh subagent) and `finish` (`ask`, `merge`, `pr` or `keep`).

In repos without `.supermatt/config.json` the hooks do nothing.

## Develop

```bash
python3 -m unittest
```

```bash
claude plugin validate plugin
```

Upstream licences and the commits the skills were imported from are in `plugin/NOTICE.md`.
