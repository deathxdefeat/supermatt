# supermatt

[![tests](https://github.com/deathxdefeat/supermatt/actions/workflows/test.yml/badge.svg)](https://github.com/deathxdefeat/supermatt/actions/workflows/test.yml)
[![version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdeathxdefeat%2Fsupermatt%2Fmain%2Fplugin%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=blue)](CHANGELOG.md)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

supermatt is a Claude Code plugin that keeps a feature moving from idea to merged code, and keeps you on track while it does. It takes the engineering skills from [Matt Pocock's skills](https://github.com/mattpocock/skills), adds a few from [obra/superpowers](https://github.com/obra/superpowers) and a few of its own, and runs them as one guided process. Claude knows which step comes next, starts it for you, and remembers where you stopped.

I built it because I needed it: brain injuries from military service left me with a memory that fails in odd ways and a habit of wandering off the real work. supermatt is the bumpers in my bowling lane, and [the full story is below](#why-it-exists).

<p align="center">
  <b><a href="#install">Install</a></b> ·
  <b><a href="#quick-start">Quick start</a></b> ·
  <b><a href="#what-it-does">What it does</a></b> ·
  <b><a href="#how-it-works">How it works</a></b> ·
  <b><a href="#the-advisor">Advisor</a></b> ·
  <b><a href="#skills">Skills</a></b> ·
  <b><a href="#guardrails">Guardrails</a></b> ·
  <b><a href="#security">Security</a></b> ·
  <b><a href="#troubleshooting">Troubleshooting</a></b> ·
  <b><a href="#why-it-exists">Why it exists</a></b> ·
  <b><a href="#docs-and-contributing">Docs</a></b>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/pipeline-dark.png">
  <img alt="The supermatt pipeline: grill, spec and tickets, a pause, then test, commit and review for each ticket, verify, a second pause, and finish" src="docs/images/pipeline.png">
</picture>

*The pipeline `/supermatt:run` drives. The red boxes marked Pause are the two default pauses, where Claude summarises the last stage and waits for your go-ahead. Both pauses are [options](docs/configuration.md#pipeline-and-other-options).*

## Install

You need:

- Claude Code with the `claude plugin` command (check with `claude plugin --help`)
- `python3` 3.9 or newer on `PATH` (standard library only)
- `git`
- macOS or Linux. Windows is untested.
- The `gh` or `glab` CLI, signed in, if your issues live on GitHub or GitLab
- A test command for your repo. Without one, the two test guardrails do nothing and verify has less evidence to work from.

```bash
claude plugin marketplace add deathxdefeat/supermatt
claude plugin install supermatt@supermatt
```

Restart Claude Code, or run `/reload-plugins`, and check that `claude plugin list` shows `supermatt@supermatt` as enabled. Its hooks do nothing in a repo until you set that repo up, so it is safe to leave enabled everywhere.

To uninstall, run `claude plugin uninstall supermatt@supermatt`. Repos you set up keep their `.supermatt/` folder; with the plugin gone, nothing reads it. To work on supermatt itself, see [Develop](CONTRIBUTING.md).


<p align="right"><a href="#supermatt">↑ top</a></p>

## Quick start

Open Claude Code in a git repo and start a feature:

```text
/supermatt:run add CSV export to the reports page
```

1. **Setup, first time only.** The first run in a repo starts `/supermatt:setup`. It looks around the repo, then asks five things, one at a time, each with a recommended answer you can accept in a word:
   - where issues live: GitHub, GitLab, local markdown files, or something else you describe
   - whether to keep the default triage labels (the labels used to sort incoming issues)
   - which test command to run (it runs the candidate once to check it works)
   - how strict the guardrails should be (a [preset](#guardrails))
   - how the pipeline should behave: when to pause, whether to branch, how to finish

   It shows you drafts of everything it will write before writing it.
2. **The pipeline runs** through the stages in [How it works](#how-it-works). At the first pause, read the spec and tickets. At the second, check the verify evidence, then choose merge, pull request or keep the branch.

> **Repo already set up by a teammate?** Setup is skipped. `/supermatt:run` shows you the committed config's `test_command` and asks you to approve it on this machine, because the hooks will run that command. Until you approve it, each session starts with "supermatt is off in this repo". See [Security](#security).

Come back any time: `/supermatt:run` with no arguments resumes the feature at its recorded stage, and each new session (and each `/clear` or compaction) tells Claude which feature is in flight.

With no flag, a run uses this repo's options: by default, Claude waits for your answers during grilling and pauses before `implement` and `finish`. Flags change a single run:

| Flag | Effect |
|---|---|
| `--auto` | Claude answers its own grilling questions with the recommended answers, lists them as assumptions in the spec, and does not pause. It still stops for the finish menu, unless the repo is set to always merge, always open a PR or always keep the branch (`pipeline.finish`). |
| `--guided` | Claude waits for your answers during grilling and pauses before every stage. |
| `--from spec\|tickets\|implement\|verify` | Starts a new feature at a later stage when the earlier work already exists (a settled design, a spec, tickets or built code), so the pipeline still tracks it without grilling you again. |

For a small fix you don't need the whole pipeline: call one skill such as `/supermatt:debug` or `/supermatt:implement`, or ask [the advisor](#the-advisor) where to start.

### What a finished run leaves you

- The feature's commits, each made after your test command passed (with a test command set and the default preset)
- The spec and a set of closed tickets in your tracker. With the local tracker these are `.scratch/<feature>/spec.md` and `.scratch/<feature>/issues/01-<slug>.md` onwards.
- Any new glossary terms in `CONTEXT.md` and decisions in `docs/adr/`
- A verify report, shown at the second pause, that lists each spec requirement with the evidence that it is met
- The commits merged into the branch you started from, in a pull request, or kept on their own branch, whichever you choose

### What supermatt adds to your repo

| Path | Commit it? | What it holds |
|---|---|---|
| `.supermatt/config.json` | Yes, before any worktree is created, so worktrees see it | This repo's options: test command, guardrail levels, pipeline behaviour. Each teammate approves it on their own machine, and again after any change they pull, before its hooks run (see [Trust](#security)). |
| `.supermatt/state.json` | No, setup gitignores it | The pipeline's progress on this machine |
| `docs/agents/issue-tracker.md`, `triage-labels.md`, `domain.md` | Yes | Where issues live, the label names, and where the domain docs live. Edit them freely. |
| An `## Agent skills` section in `CLAUDE.md` or `AGENTS.md` | Yes | Points agents at the three files above. Setup edits whichever file exists, and asks if neither does. |
| `CONTEXT.md`, `docs/adr/` | Yes | Glossary terms and design decisions, kept up to date during grilling |
| `.scratch/<feature>/` | Your choice | Only with the local markdown tracker: `spec.md` and one `issues/NN-<slug>.md` per ticket |


<p align="right"><a href="#supermatt">↑ top</a></p>

## What it does

You describe a feature, or a problem, and get working, tested, reviewed code through a process you can repeat without holding it in your head.

| | Claude Code on its own | With supermatt |
|---|---|---|
| Design | Depends on how you prompt | Claude asks you questions until the design is settled, then writes it down |
| Tests | Depends on how you prompt | Claude writes a failing test before each piece of code |
| "Done" | Claude says so | Your test command passes, each ticket is reviewed, every spec requirement is checked |
| After `/clear` or in a new session | No record of where the feature stands | Resumes at the recorded stage |
| Your say | Whenever you interrupt | Two pauses by default: before any code is written, and before anything is merged |

- **It gives the skills an order.** `/supermatt:run` takes a feature through six stages, so you never have to know which skill is next.
- **It starts the right skill for you.** Most skills start by themselves when your request fits. Four that should only run on purpose (`run`, `triage`, `wayfinder` and `handoff`) stay yours to type.
- **It remembers where you are.** Progress is recorded in your repo, so `/supermatt:run` picks a feature up where it stopped.
- **It tells you where to start.** Describe your situation to [`/supermatt:advise`](#the-advisor) and it lays out which skills to run, in what order, and why.
- **It is one skill set, not two fighting each other.** Of the 21 skills, most are Matt Pocock's and three come from Superpowers (`verify`, `finish` and `worktree`). Overlapping skills were merged and they all call each other by name.
- **It stays light.** supermatt does nothing in a repo until you set that repo up. Its checks run as hooks, a passing test run adds nothing to the conversation, and every rule can be set to `off`, `warn` or `block`.

The evidence is only as strong as your test command (see [Limits](docs/security.md#limits)).


<p align="right"><a href="#supermatt">↑ top</a></p>

## How it works

`/supermatt:run` takes a feature through six stages, each run by the skill of the same name, and the implement stage also calls `/supermatt:review` after each ticket.

| Stage | What happens |
|---|---|
| **grill** | Claude questions you in rounds ("grilling"). Each round is a numbered set of questions, each with a recommended answer, and rounds continue until the design is settled. New terms go into `CONTEXT.md` (the project glossary) and hard-to-reverse decisions into `docs/adr/` as ADRs (short architecture decision records). |
| **spec** | The conversation becomes a written spec in your issue tracker. It names the seams under test (the public interfaces the tests will drive, never internals) and any decisions that were assumed rather than asked. |
| **tickets** | The spec is split into tracer-bullet tickets: thin slices that each work end to end through every layer, so each one can be checked on its own. Each ticket lists the tickets that must finish before it. |
| **implement** | One ticket at a time, Claude writes a failing test, writes just enough code to pass it, repeats until the ticket is covered, and commits. It then reviews the change twice, once against your coding standards and once against the ticket's requirements, and fixes what it finds. |
| **verify** | Every requirement in the spec is checked against current evidence: a command run on the files as they stand, its output read. Each gap becomes a new ticket and goes back through implement, once: gaps left after that round come to you. |
| **finish** | The full test suite runs (unless these exact files already passed it), then the work is merged into the branch it started from, opened as a pull request, or kept on its branch. |

During implement, the standards pass reads files such as `CONTRIBUTING.md` or `CODING_STANDARDS.md`, plus a built-in list of common code smells that applies even if you have none. With `pipeline.review_agents` on, the two passes run as parallel sub-agents, each with a fresh context.

The reviewers are still Claude, so treat the review as a second reading, not an independent audit. The hard evidence is your test command passing and the requirement-by-requirement check against the spec, which you see at the second pause.

`run` records each stage as it starts it. After `/clear`, automatic context compaction or a new session, `/supermatt:run` resumes at that stage. Anything already written down (the spec, the tickets, commits, `CONTEXT.md`, ADRs) carries over. A conversation still in progress inside a stage, such as unfinished grilling, does not, so finish the planning stages in one sitting when you can.


<p align="right"><a href="#supermatt">↑ top</a></p>

## The advisor

Describe your situation in your own words:

```text
/supermatt:advise the export has been "fixed" three times and still writes an empty file
```

`/supermatt:advise` reads what you wrote, then checks the repo itself: the pipeline status, recent commits, open specs and tickets, `CONTEXT.md` and ADRs, and the tests (it runs them once if that is cheap). It makes no edits, commits or stage changes. Its answer has four parts:

1. **What this is**: the kind of situation, with the evidence, including anything the repo showed that you did not mention.
2. **The plan**: numbered steps, each with the exact command, why it comes at that point, and what finished looks like.
3. **What to watch for**: the one or two ways the plan is most likely to go wrong.
4. **Start here**: the first command to type.

Tell it to go and it starts step 1 itself. The exceptions are the four skills only you can start (`run`, `triage`, `wayfinder` and `handoff`): for those, it tells you what to type.

| Situation | Starts with |
|---|---|
| A feature you can describe in a few sentences | `/supermatt:run <feature>` |
| An idea where you can't yet say what done looks like | `/supermatt:grill`, then `/supermatt:run` |
| A plan, spec or tickets that already exist from outside the pipeline | `/supermatt:run <feature> --from <stage>` |
| Work too big for one session | `/supermatt:wayfinder` |
| Something that should work but doesn't | `/supermatt:debug` |
| Work that keeps being called done but still doesn't work | An end-to-end acceptance test first, then diagnosis |
| A design that fights every change | `/supermatt:architecture` |
| A question only running code can settle | `/supermatt:prototype` |
| Facts you need from docs or APIs | `/supermatt:research` |
| A pile of incoming issues | `/supermatt:triage` |
| Work that may have grown past what you approved | `/supermatt:drift` |
| A feature already in flight | `/supermatt:run` to resume |


<p align="right"><a href="#supermatt">↑ top</a></p>

## Skills

All 21 skills are invoked as `/supermatt:<name>`. Where skills from the two source collections (Matt Pocock's and obra/superpowers) overlapped, they were merged into one, and the skills call each other by these names. Claude also starts a skill by itself when your request fits, except the four marked *(you type it)*.

**Driving the workflow**

| Skill | What it does |
|---|---|
| `/supermatt:run` *(you type it)* | Takes a feature through every stage and resumes where it stopped |
| `/supermatt:advise` | Reads your situation and the repo, then lays out which skills to run, in what order, and why |
| `/supermatt:setup` | Sets a repo up once: issue tracker, labels, domain docs, test command, options. `run` starts it for you when a repo isn't set up. |
| `/supermatt:status` | Shows the pipeline's progress, the options, and whether this machine has approved the config ([trust](#security)). Changes options when you ask. |

**Pipeline stages** (`run` calls these; each also works on its own)

| Skill | What it does |
|---|---|
| `/supermatt:grill` | Questions you in rounds until the design is clear, writing `CONTEXT.md` terms and ADRs as they are decided |
| `/supermatt:spec` | Turns the conversation into a spec in your issue tracker, without a new interview |
| `/supermatt:tickets` | Splits a spec into tracer-bullet tickets, each listing what blocks it |
| `/supermatt:implement` | Builds a ticket, a spec or a described behaviour test-first, commits it, and hands it to review |
| `/supermatt:review` | Reviews against your coding standards and against the spec, in parallel, then fixes the findings and closes the ticket |
| `/supermatt:verify` | Requires evidence from the current files before anything is called done |
| `/supermatt:finish` | Runs the full test suite, then merges, opens a pull request, or keeps the branch |

**On demand**

| Skill | What it does |
|---|---|
| `/supermatt:debug` | Diagnoses hard bugs and slowdowns: first a command that reproduces the failure, then a fix with a regression test |
| `/supermatt:merge` | Resolves a stopped merge, rebase or cherry-pick by what each side meant to do |
| `/supermatt:triage` *(you type it)* | Sorts incoming issues and writes briefs an agent can work from |
| `/supermatt:prototype` | Builds throwaway code to settle one design question |
| `/supermatt:research` | Sends a background agent to primary sources and saves a cited Markdown file |
| `/supermatt:architecture` | Helps design modules, and finds places where a module should do more behind a smaller interface |
| `/supermatt:wayfinder` *(you type it)* | Breaks a large, unclear effort into decision tickets and resolves them one at a time |
| `/supermatt:drift` | Checks a spec, tickets, plan or work in progress against what you actually approved, lists each departure as *against* or *beyond* what you approved, and changes nothing until you rule |
| `/supermatt:worktree` | Sets up an isolated workspace, such as a separate git worktree, for feature work |
| `/supermatt:handoff` *(you type it)* | Writes a handoff document so a fresh session can pick up the work |


<p align="right"><a href="#supermatt">↑ top</a></p>

## Guardrails

Guardrails are four rules, enforced by Claude Code hooks and the `supermatt` command, that can stop Claude committing with failing tests (`tests_before_commit`), editing code with no ticket open (`ticket_before_code`), moving on before a finished ticket is reviewed (`review_after_ticket`), or ending its turn with failing changes (`green_before_stop`). Each rule is `off`, `warn` (the action goes ahead with a warning) or `block` (the action is stopped and Claude is told why). A preset sets all four at once.

| Preset | tests_before_commit | ticket_before_code | review_after_ticket | green_before_stop |
|---|---|---|---|---|
| `strict` | block | block | block | block |
| `standard` (default) | block | warn | block | block |
| `light` | warn | warn | warn | warn |
| `solo` | block | off | warn | off |
| `off` | off | off | off | off |

`standard` suits most repos. Choose `solo` when you work alone and want speed: tests still gate every commit, but nothing runs per edit or at the end of a turn. Choose `strict` when every code edit, including debugging and prototypes, should need a ticket first. If your test command is slow (a build plus an end-to-end suite, say), consider turning `green_before_stop` off: it runs the tests at the end of every turn that changed code, even at `warn`, and `tests_before_commit` at `block` remains the gate that matters.

Each repo keeps its options in `.supermatt/config.json`, which you commit so the whole team shares them. To change one, ask `/supermatt:status` in plain words ("turn ticket_before_code off", "use the strict preset", "pause before every stage").

[Configuration](docs/configuration.md) has the four rules in detail, ticket states, the end-of-turn check and every pipeline option. [The `supermatt` command](docs/cli.md) is the command-line reference.


<p align="right"><a href="#supermatt">↑ top</a></p>

## Security

The config names a command that the hooks run on their own, so supermatt acts on a repo's config only after this machine has approved it. Without that check, cloning a repo could make Claude Code run any command the repo's author chose, the next time Claude commits or ends a turn.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/trust-dark.png">
  <img alt="Config trust: configs written by supermatt init are trusted, configs arriving by clone or pull stay off until you run supermatt trust" src="docs/images/trust.png">
</picture>

Trust is exact: it pins a hash of the config, so any change made outside `supermatt config` has to be approved again. It covers the `test_command` text, not the code that command runs, so review an untrusted branch before working on it with the guardrails on. The guardrails are not a sandbox.

[Security](docs/security.md) explains trust in full, lists exactly what each hook runs, and sets out the limits. To report a vulnerability, see [SECURITY.md](SECURITY.md).


<p align="right"><a href="#supermatt">↑ top</a></p>

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Nothing happens in a repo | Run `/supermatt:status`. The repo may not be set up, or its config may not be trusted on this machine. |
| A session starts with "supermatt is off in this repo" | The config is untrusted or invalid, and the message says which. If untrusted, review the file, especially `test_command`, then ask Claude to run `supermatt trust`, or say yes when `/supermatt:status` offers to trust it. If invalid, `supermatt config` won't load it: fix the named option in `.supermatt/config.json` by hand, then have Claude run `supermatt trust`, because a hand edit needs approving again. |
| "no ticket is in progress" | `ticket_before_code` caught an edit made outside a ticket. Start the work through `/supermatt:run` or `/supermatt:implement`, or add the path to `exempt` if it isn't code. |
| A commit or the end of a turn is blocked | The message says what failed and, for test failures, shows the last 30 lines of output. Fix the cause, or change the rule with `/supermatt:status`. |
| "stopped blocking after 3 attempts" | The end-of-turn checks still fail and have let the turn end. The warning lists what still needs fixing. |
| "uncommitted changes still fail the tests (no file has changed since the last failing run)" | The end-of-turn check already blocked once on these exact files and will not loop on them. The tests still fail; the commit rule still stops a commit. |
| The tests did not run on a commit, or `supermatt test` says "not rerun" | These exact files already passed. `supermatt test --force` reruns them. |
| Every turn ends with a slow test run | `green_before_stop` runs the tests at the end of each turn that changed code. Turn it off and rely on `tests_before_commit`. |
| Test runs time out | A run longer than `test_timeout` counts as a failure. Raise it (at most 570 seconds) or point `test_command` at a faster set of tests that still covers what matters. |
| The same skill appears twice | You also have the original source skills installed, for example `/tdd` next to `/supermatt:implement`. Remove one set so Claude doesn't choose between duplicates. |


<p align="right"><a href="#supermatt">↑ top</a></p>

## Why it exists

I built supermatt because I needed it. I have several traumatic brain injuries from active-duty military service during the Global War on Terror, and adult ADHD as a direct result of them. My memory fails in odd ways and I distract myself easily. I start a feature, wander into something interesting, and forget to push the real work forward.

I was using two excellent skill collections, and each solved half of my problem.

- **Superpowers guides you.** Its skills start by themselves and lead you through a process from idea to finished work, so you always know what comes next. That guidance is what keeps me on track. But in my projects it spread its own files and conventions through the repo, and when I called one of Matt Pocock's skills partway through, the session, branch or worktree often ended up in a mess.
- **Matt Pocock's skills are the ones I prefer to build with**, almost every time. But you start each one yourself and nothing connects them. I would forget to use the one I needed and regret it later. I didn't know what order they belonged in as a process. Once I had started, I couldn't tell when a step was finished or which skill came next.

I wanted the guidance of Superpowers with the skills of Matt Pocock, and nothing offered that, so I fused them. For me the result works like the bumpers in a bowling lane. When something off-course catches my attention, I note it for later and keep going, because the process is still there pointing at the next step.

You don't need a brain injury to get something from this. If you have lost an afternoon to a tangent, skipped a step you knew mattered, or come back to a project with no idea where you left off, you have the same problem in a milder form.


<p align="right"><a href="#supermatt">↑ top</a></p>

## Docs and contributing

| Document | What it covers |
|---|---|
| [Configuration](docs/configuration.md) | The four rules, presets, ticket states, the end-of-turn check, every option |
| [Security](docs/security.md) | Config trust, what the hooks run, limits |
| [The `supermatt` command](docs/cli.md) | The command-line reference |
| [Contributing](CONTRIBUTING.md) | Installing from a clone, running the tests, the repo layout, the diagrams |
| [Changelog](CHANGELOG.md) | What changed in each version |
| [CONTEXT.md](CONTEXT.md), [`docs/adr/`](docs/adr/) | The project's glossary and design decisions |

## Credits and licence

MIT; see `LICENSE`. Most skills are adapted from Matt Pocock's [skills](https://github.com/mattpocock/skills) and Jesse Vincent's [superpowers](https://github.com/obra/superpowers), both MIT. `run`, `status`, `drift`, `bin/supermatt` and the hooks are original to supermatt, and so is `advise` apart from its skills map. `plugin/NOTICE.md` has their licences and the commits the skills were imported from. supermatt is an independent project, not affiliated with or endorsed by Matt Pocock or Jesse Vincent. The adapted skills don't follow the source repositories automatically: pulling in their changes is a manual merge.
