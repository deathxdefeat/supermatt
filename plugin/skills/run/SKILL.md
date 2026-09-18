---
name: run
description: Drive a feature from idea to shipped through the whole supermatt pipeline (grill, spec, tickets, implement with TDD and review per ticket, verify, finish), resuming wherever it left off. Use when the user runs /supermatt:run, asks to take a feature end to end, or asks to resume the pipeline.
argument-hint: "[<feature description> | resume] [--auto | --guided]"
disable-model-invocation: true
---

# Run

One command for the whole flow. You drive the stages in order, call the stage skills, and record progress with the `supermatt` command so the pipeline survives `/clear`, compaction and new sessions.

`SM` below means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`.

## 0. Load state and options

Run `SM status --json`.

- **Not configured** → call the Skill tool with "supermatt:setup" first, then come back here.
- **Arguments name a new feature** → pick a short kebab-case slug for it and run `SM start <slug>`. If another feature is in flight and not `done`, say which one and ask whether to abandon it or resume it instead; this is the only question this step asks.
- **No arguments, or `resume`** → continue the active feature at its recorded stage. With no active feature, ask what to build.

Options come from `config.pipeline`; flags on this invocation override them for this run only:

- `--auto` → `interview=auto` and `pause_at=[]` (run to the end without stopping, except where a decision is genuinely the user's: the `finish` menu when `finish` is `ask`).
- `--guided` → `interview=full` and pause after every stage.

**Pausing.** When the stage you just finished is in `pause_at`, stop: summarise what the stage produced in a few lines, name the next stage, and wait for the user's go-ahead. Otherwise move straight on. Record each stage transition with `SM stage <stage>` *before* starting that stage's work.

## 1. grill

Call the Skill tool with "supermatt:grill", passing the feature description, plus `--auto` when `interview` is `auto`. Grilling runs in docs mode, so `CONTEXT.md` and ADRs grow as terms and decisions settle. If a question needs a runnable answer, detour through `/supermatt:prototype` and come back.

Keep stages 1 to 3 in one unbroken context: the spec and tickets build on the grilling.

## 2. spec

`SM stage spec`, then call the Skill tool with "supermatt:spec". It publishes the spec to the tracker (locally `.scratch/<slug>/spec.md`), including any assumed decisions.

## 3. tickets

`SM stage tickets`, then call the Skill tool with "supermatt:tickets" with the spec. It publishes tracer-bullet tickets with blocking edges.

## 4. implement

`SM stage implement`.

**Workspace, once per feature.** If `pipeline.worktree` is true, call the Skill tool with "supermatt:worktree". Otherwise, if `pipeline.branch` is true and you are on the default branch, create and switch to a `<slug>` branch. Remember the branch you started from: `finish` merges back into it.

**Ticket loop.** Repeat until every ticket is done:

1. Pick the **frontier**: the lowest-numbered open ticket whose blockers are all done (per the tracker and `SM status`). A ticket already `implementing` or `needs-review` in `SM status` is resumed first.
2. Build it:
   - `pipeline.ticket_agents` false → call the Skill tool with "supermatt:implement" with the ticket. It records `implementing`, builds test-first, commits, records `needs-review`, and hands to "supermatt:review", which fixes findings and records `done`.
   - `pipeline.ticket_agents` true → dispatch one general-purpose subagent per ticket, in sequence, with a prompt that names the ticket (path or URL), the spec path, the repo root, and says: "Call the Skill tool with `supermatt:implement` for this ticket and follow it through `supermatt:review` until the ticket is marked done. Report the commits you made, the review findings you fixed and any you left." Check the result yourself (`SM status`, `git log`) before the next ticket; the agent's report is not evidence.
3. Confirm `SM status` shows the ticket `done` before picking the next one. If review found a spec problem rather than a code problem, stop and raise it with the user.

The enforcement hooks back this loop up when they are on: commits run the tests, code edits need a ticket in progress, and the next ticket waits for the last one's review. If a hook blocks you, fix the cause it names; never switch a rule off to get past it unless the user tells you to.

## 5. verify

`SM stage verify`, then call the Skill tool with "supermatt:verify". A missing or partial requirement goes back to step 3 as a new ticket; do not carry it into `finish`.

## 6. finish

`SM stage finish`, then call the Skill tool with "supermatt:finish". It honours `pipeline.finish` and records `SM stage done` when the work is integrated.

## Reporting

At the end (or at a pause), report in a few lines: the feature, the stage reached, tickets done, the verify result with its evidence, and how the work was integrated. Name anything assumed rather than decided by the user.
