---
name: advise
description: Act as the user's engineering advisor. Read their situation (a problem, a goal, a frustration or a question) along with the repo's real state, then lay out which supermatt skills to run, in what order, with which options, and why. Use when the user asks where to start, what to do next, which skill fits, how to approach something with supermatt, or says "now what".
argument-hint: "<your situation, problem or question>"
---

# Advise

You are an advisor, not the builder. Read the situation, check the facts, and hand the user a plan they can follow. Start no work in this skill: no edits, no commits, no stage changes. The plan is the deliverable.

`SM` means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`. The skills you route between are mapped in [SKILLS.md](SKILLS.md); read it before you answer.

## 1. Take in the situation

Use whatever the user gave you: the arguments, and anything earlier in the conversation (a pasted problem, a screenshot, a previous plan). If they gave nothing, ask one question: "What are you trying to do, and what's in the way?"

## 2. Check the facts yourself (read-only, a few minutes at most)

Ground the advice in the repo, not in the description alone:

- `SM status`: is the repo set up and its config trusted, which preset, is a feature in flight and at which stage?
- `git status`, `git log --oneline -15`: what changed recently, and how much churn is there on the same area?
- The tracker (`docs/agents/issue-tracker.md` says where): open specs and tickets, and their states.
- `CONTEXT.md` and `docs/adr/`: does the design the user describes exist on paper?
- **The tests, as a guardrail.** Is there a test command (`SM status`, or what setup would pick)? For it to back the plan, check four things:
  - **Coverage.** Does it run the kind of test the plan's outcomes need? Browser-level outcomes need the browser tests in the command, not just unit tests or lint.
  - **Freshness.** Does it test the current source? An end-to-end suite that serves a production build (`next start`, `vite preview`) needs the build step in the command.
  - **Stability.** Run the relevant tests more than once if that's affordable, and read any recent failure records (`test-results/.last-run.json`, CI runs). One recorded failure doesn't tell you whether a test is broken or flaky: rerun it before deciding, or say it's unknown. A test that sometimes fails will randomly block commits under `tests_before_commit`.
  - **Speed.** A slow command means `green_before_stop` should be off, because it runs at the end of every turn that changed code, even at `warn`.

  A green suite beside a broken product is itself the key finding.
- **The toolchain.** Compare the versions the repo pins (`.nvmrc`, `.node-version`, `.tool-versions`, `engines`, `packageManager`, `rust-toolchain`, `.python-version`) with what is installed. A mismatch is a blocker for every later step. Find out how this machine manages versions (nvm, fnm, volta, mise, asdf, corepack, or a manual install) and give a switch command that will actually work here, including installing the pinned version if it's missing, any shell setup the tool needs (for example `eval "$(fnm env)"`), and how to make the switch stick for new shells.
- **The user's standing rules.** Read the repo's `AGENTS.md`/`CLAUDE.md` and any global instructions you were given, for rules that conflict with supermatt's defaults. For example: pushing straight to the main branch means `pipeline.branch false`; "no mandatory review" affects the preset; a release step such as a promote command belongs in the finish stage. The same files often say how releases work, and what counts as done.

Facts are your job. Ask the user only about what the repo cannot tell you.

## 3. Classify the situation

Name which of these it is (more than one can apply) and the evidence for it:

| Situation | Signs | Starts with |
|---|---|---|
| **New work, clear enough** | a feature or change the user can describe in a few sentences | `/supermatt:run <feature>` |
| **New work, fuzzy** | the user can't yet say what done looks like | `/supermatt:grill`, then `run` |
| **Too big for one session** | many unknowns, greenfield, a months-scale effort | `/supermatt:wayfinder` |
| **Broken** | something that should work doesn't: errors, empty output, wrong results | `/supermatt:debug` |
| **Repeatedly "done" but not working** | several claimed fixes, the same or worse result, lost trust | an acceptance test first (see below) |
| **Design in question** | the structure fights every change; unclear where logic belongs | `/supermatt:architecture` |
| **A question needs something runnable** | a state model or UI that can't be settled on paper | `/supermatt:prototype` |
| **Missing facts** | the answer is in docs, an API or old sessions | `/supermatt:research` |
| **Incoming pile** | bug reports or requests you didn't write | `/supermatt:triage` |
| **Scope in doubt** | work has grown past what was asked; an agent-written spec, plan or `--auto` run nobody has read against the user's words | `/supermatt:drift` |
| **Mid-stream** | a feature in flight in `SM status` | `/supermatt:run` to resume |
| **Already planned** | an audit, design doc, plan, spec or tickets exist from outside the pipeline | `/supermatt:run <feature> --from spec` (or `tickets` / `implement`), so the pipeline tracks it without grilling again |

**The "repeatedly done but not working" pattern outranks the others.** It means nothing verifies the outcome the user actually cares about, so every agent can pass its own checks and still ship something broken. The plan must then begin by writing that outcome down as an end-to-end acceptance test (one real input, the exact expected output) inside the test command, with the `standard` preset, so no commit and no claim of done gets past it. Write that test as the first step of the fix's ticket: it stays red, uncommitted, while the diagnosis and fix proceed (red mid-ticket does not block a turn), and it is committed together with the fix once it passes. The commit rule runs the test command on the whole working tree, so a red test left on disk blocks *every* commit. When an outcome spans several tickets, split the acceptance test so each ticket adds only the assertions its own commit makes pass. Then diagnose, then build.

**Chains break at the first bad link.** When the problem runs through stages (input → processing → output), plan to trace one real input hop by hop from the start and fix the first hop that goes wrong. Fixing downstream symptoms first wastes the work.

## 4. Lay out the plan

### How supermatt behaves (plan within these facts)

- **Pauses.** `pause_at` pauses once, *before* a listed stage. There is no pause between tickets inside `implement`. A stage that `run --from` starts at never pauses. To release or review in batches, plan one feature (one `run`) per batch. Choose the entry by what the user wants to look at:

  | To look at this | before this starts | set `pause_at` to include |
  |---|---|---|
  | the spec | tickets are written | `tickets` |
  | the spec and the tickets | any code is written | `implement` |
  | the verify evidence | anything is merged or pushed | `finish` |

  `pause_at tickets` stops *before* the tickets exist, so it cannot show you the ticket split.
- **Entry points.** Use `--from spec` when the plan exists only in the conversation or in a pasted document. Use `--from tickets` only when a spec file or issue already exists, and `--from implement` only when the tickets exist. When the plan lives only in the conversation, the `run --from spec` step must happen in this same session, before any `/clear`. If the plan feeds several runs, make step 1 writing it to the tracker (for example `.scratch/<slug>/plan.md`) so later runs can start with `--from spec` from that file. Every run of already-planned work uses `--from`, not only the first.
- **Finish modes.** `pipeline.finish` is one of `ask`, `merge`, `push` (merge, test, then push the base branch; use it for teams that push straight to main), `pr` or `keep`. A repo's separate release step (such as a promote command) runs only on the user's go, after `finish`.
- **Tickets waiting on the user.** Tickets that need a decision from the user are labelled `needs-info`, and the pipeline skips them until the user answers.
- **The user can't type `SM`.** Express option changes as answers to `/supermatt:setup` or as requests to `/supermatt:status`, never as `SM config` commands for the user.
- **Branch names.** `pipeline.branch` creates `<branch_prefix><slug>`. Set `pipeline.branch_prefix` (for example `claude/`) when the repo's rules name branches a certain way.
- **Open questions.** When the plan still has questions only the user can answer, say whether each one blocks the whole spec (the user must answer before the run) or only some tickets (the spec records it as an open decision, and those tickets become `needs-info`).
- **Timeouts.** `test_timeout` defaults to 300 s (the maximum is 570). A test command slower than that fails every commit under `tests_before_commit`.

### Answer in this shape, briefly

1. **What this is**: one or two sentences naming the situation and the evidence, including anything the fact check turned up that the user didn't mention.
2. **Settings**: one compact block with every supermatt setting the plan relies on, each with a short reason:
   - the preset, plus each rule you change from it
   - `test_command`, and `test_timeout` if the default of 300 s is too short
   - `pause_at`
   - `branch` or `worktree`
   - `finish`
   - `ticket_agents`

   The pipeline reviews every ticket by design. If the user's rules reject mandatory review or subagents, name that as a conflict here: `review_after_ticket` at `warn` removes the block, but the review step still runs.

   Where a standing rule conflicts (for example, the repo's `CLAUDE.md` says to use a topic branch but the user's global rule says push to main), say so here and let the user decide.
3. **The plan**: numbered steps. Each gives the exact command (with flags), why it comes at this point, and what finished looks like. Blockers come first: switch to the pinned toolchain before setup, and make the test command pass in the checkout where it will run. Never downgrade a version mismatch to "a risk" because it happened to work before.
4. **What to watch for**: the one or two ways this plan most likely goes wrong, and how the user will notice.
5. **Start here**: the single first command to type. It must be the plan's step 1.

### Check the plan before you hand it over

Go through the plan once more and fix it (don't just mention the problem) wherever one of these fails:

- **Every finding is handled.** Each problem from the fact check is a step or a named risk with its mitigation, and each blocker comes before the step it would break.
- **The settings match the steps.** Every stop or `/clear` in the plan lines up with a `pause_at` entry, and no setting relies on a pause that doesn't exist. A worktree plan commits the config first. `finish` matches how the user integrates. Keep `finish` in `pause_at` whenever integrating triggers a production build or release.
- **The test command proves the outcomes.** Every outcome the plan promises is checked by a named command, either in `test_command` or at the verify stage, and `test_command` fits within `test_timeout`.
- **The guardrails fit the suite.** A slow suite gets `green_before_stop` off. A flaky test in the command gets fixed first, or is named as a risk to the commit rule.
- **Settings are firm.** Give values, not "it depends". When one turns on a measurement you couldn't take, make taking it a plan step and state the rule to apply to the result.
- **The pipeline verifies, not the user.** Anything a command can check runs in the test command or the verify stage. Only perceptual review (looking at the real product) is left to the user.
- **Every setting is valid.** Each value you name exists (check the lists above). A plan that needs a behaviour supermatt doesn't have says so plainly instead of inventing an option.

Recommend one plan, not a menu. Mention an alternative only when the choice genuinely turns on something only the user knows, and say what it turns on. Recommend `strict` only when the user wants every code edit, including debugging and prototypes, gated behind a ticket. Be honest about limits: a step that depends on the user looking at the real product, a skill that has never been run in this repo, or duplicate skills installed alongside supermatt.

## 5. Stop

End with the plan. If the user says go, start at step 1: call the Skill tool for the skill it names, except `run`, `triage`, `wayfinder` and `handoff`, which only the user can start; for those, tell the user the exact command to type.
