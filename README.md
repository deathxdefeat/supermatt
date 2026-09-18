# supermatt

A Claude Code plugin that takes a feature from rough idea to shipped code as one workflow. It includes:

- **A pipeline you can resume.** `/supermatt:run <feature>` goes through grill → spec → tickets → implement → verify → finish. Each ticket is built test-first, committed, then reviewed. The pipeline records where it is, so you can `/clear`, compact, or come back tomorrow and carry on.
- **A merged skill set.** 20 skills under `/supermatt:*`, adapted from [mattpocock/skills](https://github.com/mattpocock/skills) and [obra/superpowers](https://github.com/obra/superpowers). Upstream skills that overlapped are merged into one, and the skills call each other by their supermatt names.
- **Optional guardrails.** Hooks can stop a commit that fails the tests, a code edit with no ticket in progress, a new ticket started before the last one is reviewed, and a turn that ends with failing code. You choose, for each repo, whether each rule blocks, warns, or is off.
- **An advisor.** Describe your situation to `/supermatt:advise` and get back a step-by-step plan.

## Requirements

- Claude Code with plugin support
- `python3` 3.9 or newer on `PATH`, standard library only
- `git`
- macOS or Linux

## Install

From a clone of this repo:

```bash
claude plugin marketplace add /path/to/supermatt
```

```bash
claude plugin install supermatt@supermatt
```

If the repo is hosted somewhere, `claude plugin marketplace add <git-url>` works the same way. Restart Claude Code, or run `/reload-plugins`, and check that `claude plugin list` shows `supermatt@supermatt` as enabled.

**While developing supermatt itself**, link the plugin folder into your skills directory instead. Claude Code then loads it in place as `supermatt@skills-dir`, and your edits apply to the next session:

```bash
ln -s /path/to/supermatt/plugin ~/.claude/skills/supermatt
```

Uninstall with `claude plugin uninstall supermatt@supermatt` (or delete the link). Repos you set up keep their `.supermatt/` folder. The hooks ignore it once the plugin is gone.

## Quick start

```text
/supermatt:run add CSV export to the reports page
```

The first run in a repo starts `/supermatt:setup`. It asks five things:

- where issues live (GitHub, GitLab, local markdown, or something else)
- which test command to run
- how strict the guardrails should be
- how the pipeline should behave
- whether to keep the default triage labels

The pipeline starts once setup is done. Run `/supermatt:run` with no arguments to resume. Flags apply to one run only: `--auto` answers the grilling questions itself and doesn't pause; `--guided` pauses before every stage.

Not sure where to start? Paste the problem and run `/supermatt:advise`. It checks the repo, works out what kind of situation you're in, and gives you a numbered plan that ends with the first command to type.

## Skills

| Skill | What it does |
|---|---|
| `/supermatt:run` | Runs a feature through every stage and resumes where it stopped |
| `/supermatt:advise` | Reads your situation and the repo, then lays out which skills to run, in what order, and why |
| `/supermatt:setup` | Sets a repo up once: issue tracker, labels, domain docs, test command, options |
| `/supermatt:status` | Shows the pipeline's progress and changes any option |
| `/supermatt:grill` | Questions you in rounds until the design is clear, writing `CONTEXT.md` terms and ADRs as they're decided |
| `/supermatt:spec` | Turns the conversation into a spec in your issue tracker |
| `/supermatt:tickets` | Splits a spec into small end-to-end tickets that each list what blocks them |
| `/supermatt:implement` | Builds a ticket test-first, commits it, and hands it to review |
| `/supermatt:review` | Reviews against your coding standards and against the spec, in parallel, then fixes the findings and closes the ticket |
| `/supermatt:verify` | Requires fresh evidence before anything is called done |
| `/supermatt:finish` | Merges, opens a pull request, or keeps the branch |
| `/supermatt:debug` | Diagnoses hard bugs: first a command that reproduces the failure, then a fix with a regression test |
| `/supermatt:merge` | Resolves an in-progress merge or rebase by what each side meant to do |
| `/supermatt:triage` | Sorts incoming issues and writes briefs an agent can work from |
| `/supermatt:prototype` | Builds throwaway code to settle a design question |
| `/supermatt:research` | Sends a background agent to primary sources and saves a cited Markdown file |
| `/supermatt:architecture` | Helps design modules and finds places where a module should do more behind a smaller interface |
| `/supermatt:wayfinder` | Breaks a large, unclear effort into decision tickets and resolves them one at a time |
| `/supermatt:worktree` | Sets up an isolated workspace for feature work |
| `/supermatt:handoff` | Writes a handoff document for a fresh session |

`run`, `setup`, `triage`, `wayfinder` and `handoff` run only when you call them. Claude can pick the others on its own when your request matches.

## Options

Each repo keeps its own options in `.supermatt/config.json`, which you commit. You can change them by asking `/supermatt:status` (for example "turn ticket_before_code off" or "use the strict preset"), or run the `supermatt config` command bundled in `plugin/bin`.

### Guardrails

| Rule | What it does |
|---|---|
| `tests_before_commit` | `git commit` runs the test command first. Failing tests stop the commit. |
| `ticket_before_code` | Editing code (anything not matched by `exempt`) needs a ticket that is in progress or in review. |
| `review_after_ticket` | A committed ticket must be reviewed before the next one starts or the turn ends. |
| `green_before_stop` | A turn can't end while uncommitted code fails the tests. The exception is mid-ticket, where failing tests are a normal part of test-first work. After three blocked attempts in a row it lets the turn end and warns you. |

Each rule is `off`, `warn` or `block`. A preset sets all four at once:

| Preset | tests_before_commit | ticket_before_code | review_after_ticket | green_before_stop |
|---|---|---|---|---|
| `strict` | block | block | block | block |
| `standard` (default) | block | warn | block | block |
| `light` | warn | warn | warn | warn |
| `off` | off | off | off | off |

### Pipeline and other options

| Option | Default | Meaning |
|---|---|---|
| `test_command` | none | The command the guardrails and the verify stage run. Without one, the two test rules do nothing. |
| `test_timeout` | `300` | Seconds before a test run counts as failed (at most 570, because Claude Code stops a hook after 600) |
| `exempt` | `.scratch/*`, `docs/*`, `.supermatt/*`, `*.md` | Paths the code rules ignore |
| `pipeline.interview` | `full` | `full` waits for your answers during grilling. `auto` answers each question with the recommended answer and lists these as assumptions in the spec. |
| `pipeline.pause_at` | `implement,finish` | The stages `run` pauses before, waiting for your go-ahead. The default lets you check the spec and tickets before any code is written, and the verify results before anything is merged. `none` never pauses. |
| `pipeline.branch` | `true` | Create a branch for the feature before implementing |
| `pipeline.worktree` | `false` | Implement in an isolated worktree instead |
| `pipeline.ticket_agents` | `false` | Build each ticket in a fresh subagent |
| `pipeline.finish` | `ask` | `ask` shows a menu. `merge`, `pr` or `keep` always does that one. |

## How the guardrails work, and their limits

- **Setup is per repo.** Without `.supermatt/config.json`, every hook exits straight away and does nothing.
- **Configs need your approval.** The config names a command that the hooks run on their own, so supermatt acts on it only once this machine trusts it. `supermatt init` trusts the config it writes, and `supermatt config` keeps a trusted config trusted after an edit. A config that arrives any other way (a clone, a pull, a teammate's edit) stays inactive until you review it and run `supermatt trust`. Trust records the repo's path and the config's exact contents, so any change to the config needs approving again. Trusted configs are listed in `~/.config/supermatt/trusted.json`, or at `$SUPERMATT_TRUST_FILE` if set. Each new session tells you when a repo's config is waiting for approval.
- **Test runs are remembered.** Once a set of changes passes, the end-of-turn check doesn't rerun the tests until the code changes again.
- **They are guardrails, not a sandbox.** `ticket_before_code` watches Claude's file-editing tools, not every shell command that could write a file. Tests run on the working tree, not just the staged changes.
- **Questions still get through.** Before Claude asks you something mid-ticket, it marks the ticket `blocked`, so the end-of-turn checks let the question through.
- **The hooks never break a session.** Bad hook input, a broken config or a bug inside supermatt all result in a message, never a failed tool call. A broken config turns supermatt off for that repo, and the next session tells you why.

The pipeline's progress lives in `.supermatt/state.json`, which is kept out of git because it's local to your machine.

## The `supermatt` command

The skills and hooks work through `plugin/bin/supermatt`, a single Python script. When the plugin is enabled, it's on the `PATH` of Claude's Bash tool. You can also run it yourself with `python3 plugin/bin/supermatt`.

| Command | What it does |
|---|---|
| `init [--preset P] [--test-command CMD]` | Sets the repo up: writes and trusts `.supermatt/config.json`, and gitignores the state file |
| `status [--json]` | Shows the pipeline's progress, the options, and whether the config is trusted |
| `config [KEY [VALUE]]` / `config preset P` | Shows or changes an option |
| `trust` | Approves this repo's current config on this machine |
| `start SLUG`, `stage STAGE`, `base BRANCH` | Record the feature, the stage and the branch it started from |
| `ticket ID implementing\|blocked\|needs-review\|done` | Records a ticket's state (review comes before `done`) |
| `hook pre-tool\|stop\|session-start` | The entry point `hooks/hooks.json` calls |

## Troubleshooting

- **Nothing happens in a repo.** Run `/supermatt:status`. The repo may not be set up, or its config may not be trusted on this machine.
- **The same skill appears twice.** You have the upstream skills installed as well, for example `/tdd` next to `/supermatt:implement`. Remove one set so Claude doesn't pick between duplicates.
- **A commit or a stop is blocked.** The message says which rule blocked it and shows the end of the test output. Fix the cause, or change the rule with `/supermatt:status`.

## Develop

```bash
python3 -m unittest
```

```bash
claude plugin validate . && claude plugin validate plugin
```

The tests drive `plugin/bin/supermatt` the way the hooks call it, in temporary git repos. They also check that the skills' names, links and cross-references stay consistent, and that this README lists every skill. See `CONTEXT.md` for terms and `docs/adr/` for design decisions. `spine_check.py` is maintainer tooling that checks the older symlinks to the upstream skill folders on the author's machine. The plugin doesn't need it.

## Credits and licence

MIT. See `LICENSE`. Most skills are adapted from Matt Pocock's [skills](https://github.com/mattpocock/skills) and Jesse Vincent's [superpowers](https://github.com/obra/superpowers), both MIT. `plugin/NOTICE.md` has their licences and the upstream commits the skills were imported from.
