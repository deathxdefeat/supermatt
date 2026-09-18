---
name: run
description: Drive a feature from idea to shipped through the whole supermatt pipeline (grill, spec, tickets, implement with TDD and review per ticket, verify, finish), resuming wherever it left off. Use when the user runs /supermatt:run, asks to take a feature end to end, or asks to resume the pipeline.
argument-hint: "[<feature description> | resume] [--from spec|tickets|implement|verify] [--auto | --guided]"
disable-model-invocation: true
---

# Run

One command for the whole pipeline. You drive the stages in order, call the stage skills, and record progress with the `supermatt` command so the pipeline survives `/clear`, compaction and new sessions.

`SM` below means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`.

## 0. Load state and options

Run `SM status --json`.

- **`configured` is false** → call the Skill tool with "supermatt:setup" first, then come back here.
- **`trusted` is false** → the repo's config came from elsewhere (a clone or a pull). Show the user its `test_command` and ask them to approve it; on a yes, run `SM trust`. Without trust the enforcement hooks stay off.
- **Arguments name a new feature** → pick a short kebab-case slug for it and run `SM start <slug>` (with `--stage <stage>` when `--from` is given; see below). If another feature is in flight and not `done`, say which one and ask whether to abandon it or resume it instead.
- **No arguments, or `resume`** → continue the active feature at its recorded stage. With no active feature, ask what to build.

**Starting later with `--from`.** When the earlier stages already happened outside the pipeline (an audit, a design doc, a plan made in this conversation, an existing spec or tickets), start the feature at a later stage instead of grilling again: `SM start <slug> --stage <stage>`, then continue from that stage below. What each start point expects:

- `--from spec`: the design is already settled in this conversation or in a document the user names. The spec stage synthesises from that; any open question it can't answer from the material goes to the user before the spec is published.
- `--from tickets`: a spec already exists. Get its path or URL from the user if they didn't give it, and pass it to the tickets stage.
- `--from implement`: tickets already exist on the tracker. Read them first; any ticket without acceptance criteria or seams under test gets them added (with the user's OK on a hosted tracker) before the ticket loop starts.
- `--from verify`: the work is built and needs verifying against its spec before finishing.

**Effective mode.** Start from `config.pipeline`; flags on this invocation override it for this run only:

- `--auto` → `interview=auto` and `pause_at=[]`. Runs to the end without stopping, except where a decision is genuinely the user's (the `finish` menu when `finish` is `ask`).
- `--guided` → `interview=full` and pause before every stage.

**Pausing.** `pause_at` lists stages to pause *before*. Before starting a listed stage, stop: summarise what the previous stage produced in a few lines, name the next stage, and wait for the user's go-ahead. The default, `implement,finish`, lets the user check the spec and tickets before any code is written, and check the verify evidence before anything is merged.

Never pause before the stage this invocation starts or resumes at: the user just asked for it. Record each stage with `SM stage <stage>` as you start it.

**Ticket ids.** A ticket's id is its local file number (`01`, `02`, ...) or its issue number on a hosted tracker (`123`, no `#`). Use the same id with every `SM ticket` call.

## 1. grill

Call the Skill tool with "supermatt:grill", passing the feature description, plus `--auto` when the effective `interview` is `auto`. Grilling keeps `CONTEXT.md` and ADRs current as terms and decisions settle. If a question can only be settled by running something, detour through `/supermatt:prototype` for that one question and bring the answer back as a decision; the prototype does not change product code.

Keep the grill, spec and tickets stages in one unbroken context: the spec and tickets build on the grilling.

## 2. spec

`SM stage spec`, then call the Skill tool with "supermatt:spec", plus `--auto` when the effective `interview` is `auto`. It publishes the spec (locally `.scratch/<slug>/spec.md`), including the seams under test and any assumed decisions.

## 3. tickets

`SM stage tickets`, then call the Skill tool with "supermatt:tickets" with the spec, plus `--auto` when the effective `interview` is `auto`. It publishes tracer-bullet tickets with blocking edges and seams.

## 4. implement

`SM stage implement`.

**Workspace, once per feature.** Record where the work will merge back: `SM base <current branch>`. Then, if `pipeline.worktree` is true, call the Skill tool with "supermatt:worktree" (the option is the user's consent to create one). Otherwise, if `pipeline.branch` is true and you are on the base branch, create and switch to a `<slug>` branch.

**Ticket loop.** Repeat until every ticket is done:

1. Pick the next ticket: the lowest-numbered open ticket whose blockers are all done (per the tracker and `SM status`). A ticket already `implementing`, `blocked` or `needs-review` in `SM status` is resumed first.
2. Build it:
   - `pipeline.ticket_agents` false → call the Skill tool with "supermatt:implement" with the ticket. It records `implementing`, builds test-first, commits, records `needs-review`, and hands the ticket to "supermatt:review", which fixes findings and records `done`.
   - `pipeline.ticket_agents` true → dispatch one general-purpose subagent per ticket, in sequence, with a prompt that names the ticket id and path or URL, the spec path, and the repo root, and says: "Call the Skill tool with `supermatt:implement` for this ticket and follow it through `supermatt:review` until the ticket is recorded done. You are a subagent: run both review axes yourself, one after the other, instead of spawning reviewers. Report the commits you made, the review findings you fixed and any you left." Check the result yourself (`SM status`, `git log`) before the next ticket; the agent's report is not evidence.
3. Confirm `SM status` shows the ticket `done` before picking the next one. If review found a spec problem rather than a code problem, record `SM ticket <id> blocked`, raise it with the user, and wait.

**Asking the user mid-ticket.** Before any question that ends your turn while a ticket is open, record `SM ticket <id> blocked`, so the stop checks let the turn end. When the answer arrives, set the ticket back to `implementing` or `needs-review` and carry on.

The enforcement hooks back this loop up when they are on: commits run the tests, code edits need a ticket in progress, and the next ticket waits for the last one's review. If a hook blocks you, fix the cause it names. Never change an enforcement option to get past a block; only the user decides that.

## 5. verify

`SM stage verify`, then call the Skill tool with "supermatt:verify". For each missing or partial requirement, add one ticket (the next free number) that covers exactly that gap, run `SM stage implement`, and go back into the ticket loop. Do not carry a gap into `finish`.

## 6. finish

`SM stage finish`, then call the Skill tool with "supermatt:finish". It merges back into the base branch from `SM status`, honours `pipeline.finish`, and records `SM stage done` when the work is integrated.

## Reporting

At the end (or at a pause), report in a few lines: the feature, the stage reached, tickets done, the verify result with its evidence, and how the work was integrated. Name anything assumed rather than decided by the user.
