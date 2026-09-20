# The pipeline

What `/supermatt:run` does, stage by stage, and what it leaves behind. For the overview, see the [README](../README.md).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/pipeline-dark.png">
  <img alt="The supermatt pipeline: grill, spec and tickets, a pause, then test, commit and review for each ticket, verify, a second pause, and finish" src="images/pipeline.png">
</picture>

## Stages

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

## First-time setup

The first run in a repo starts `/supermatt:setup`. It looks around the repo, then asks five things, one at a time, each with a recommended answer you can accept in a word:
- where issues live: GitHub, GitLab, local markdown files, or something else you describe
- whether to keep the default triage labels (the labels used to sort incoming issues)
- which test command to run (it runs the candidate once to check it works)
- how strict the guardrails should be (a [preset](configuration.md#presets))
- how the pipeline should behave: when to pause, whether to branch, how to finish

It shows you drafts of everything it will write before writing it.

## Flags for a single run

With no flag, a run uses this repo's options: by default, Claude waits for your answers during grilling and pauses before `implement` and `finish`. Flags change a single run:

| Flag | Effect |
|---|---|
| `--auto` | Claude answers its own grilling questions with the recommended answers, lists them as assumptions in the spec, and does not pause. It still stops for the finish menu, unless the repo is set to always merge, always open a PR or always keep the branch (`pipeline.finish`). |
| `--guided` | Claude waits for your answers during grilling and pauses before every stage. |
| `--from spec\|tickets\|implement\|verify` | Starts a new feature at a later stage when the earlier work already exists (a settled design, a spec, tickets or built code), so the pipeline still tracks it without grilling you again. |

## What a finished run leaves you

- The feature's commits, each made after your test command passed (with a test command set and the default preset)
- The spec and a set of closed tickets in your tracker. With the local tracker these are `.scratch/<feature>/spec.md` and `.scratch/<feature>/issues/01-<slug>.md` onwards.
- Any new glossary terms in `CONTEXT.md` and decisions in `docs/adr/`
- A verify report, shown at the second pause, that lists each spec requirement with the evidence that it is met
- The commits merged into the branch you started from, in a pull request, or kept on their own branch, whichever you choose

## What supermatt adds to your repo

| Path | Commit it? | What it holds |
|---|---|---|
| `.supermatt/config.json` | Yes, before any worktree is created, so worktrees see it | This repo's options: test command, guardrail levels, pipeline behaviour. Each teammate approves it on their own machine, and again after any change they pull, before its hooks run (see [Trust](security.md)). |
| `.supermatt/state.json` | No, setup gitignores it | The pipeline's progress on this machine |
| `docs/agents/issue-tracker.md`, `triage-labels.md`, `domain.md` | Yes | Where issues live, the label names, and where the domain docs live. Edit them freely. |
| An `## Agent skills` section in `CLAUDE.md` or `AGENTS.md` | Yes | Points agents at the three files above. Setup edits whichever file exists, and asks if neither does. |
| `CONTEXT.md`, `docs/adr/` | Yes | Glossary terms and design decisions, kept up to date during grilling |
| `.scratch/<feature>/` | Your choice | Only with the local markdown tracker: `spec.md` and one `issues/NN-<slug>.md` per ticket |
