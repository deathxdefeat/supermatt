# The supermatt skills

The map `/supermatt:advise` routes over.

## The main flow: idea → ship

**`/supermatt:run <feature>`** does the whole thing and remembers where it is. The stages it drives can also be run by hand:

1. **`/supermatt:grill`** sharpens the idea by interview, writing `CONTEXT.md` terms and ADRs as they settle (`--no-docs` for a stateless interview, `--auto` to settle questions itself).
2. **`/supermatt:spec`** turns the conversation into a spec on the tracker.
3. **`/supermatt:tickets`** splits it into tracer-bullet tickets with blocking edges.
4. **`/supermatt:implement`** builds one ticket test-first, commits, and hands to **`/supermatt:review`** (Standards + Spec, two parallel reviewers), which fixes findings and closes the ticket.
5. **`/supermatt:verify`**: fresh evidence before any claim of done.
6. **`/supermatt:finish`**: merge, pull request, or keep the branch.

Not a multi-session build? Skip 2 and 3: `/supermatt:implement` straight from the conversation.

Keep stages 1 to 3 in one context window. Each ticket can start fresh (`pipeline.ticket_agents`, or `/clear` between tickets); the ticket carries what it needs. For deciding between continue, `/clear`, `/compact`, a subagent or `/supermatt:handoff` at a boundary, read [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md).

## On-ramps

- **Issues piling up** that you didn't write → **`/supermatt:triage`**, which produces agent-ready issues for `/supermatt:implement`. Never triage tickets `/supermatt:tickets` made.
- **Something broken, flaky or slow** → **`/supermatt:debug`**: builds a tight red feedback loop before theorising, then fixes with a regression test.
- **A huge, foggy effort** too big for one session → **`/supermatt:wayfinder`**: a map of decision tickets resolved one at a time; when it clears, merge onto the main flow at `/supermatt:spec`.

## Standalone

- **`/supermatt:prototype`**: throwaway code to answer one design question (a state model, a UI).
- **`/supermatt:research`**: a background agent reads primary sources and leaves a cited Markdown file.
- **`/supermatt:architecture`**: module design vocabulary for a narrow question, or a full scan for deepening opportunities.
- **`/supermatt:merge`**: resolve an in-progress merge or rebase by intent.
- **`/supermatt:worktree`**: an isolated workspace for feature work.
- **`/supermatt:handoff`**: a portable handoff document for a new harness, directory or colleague.

## Setup and options

- **`/supermatt:advise`**: describe your situation and get a sequenced plan for which of these to run.
- **`/supermatt:setup`**: once per repo (the pipeline runs it for you).
- **`/supermatt:status`**: where the pipeline is, and every option: enforcement presets (`strict`, `standard`, `light`, `off`) or single rules, the test command, and pipeline behaviour (interview mode, pause points, branch or worktree, per-ticket subagents, how to finish).
