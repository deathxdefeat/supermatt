# Changelog

## 0.5.0

Less repeated checking, for people who need to move fast. Nothing was removed: tests still gate every commit, every ticket is still reviewed, and the spec is still verified.

- The test suite runs once per change. supermatt remembers which files passed, so the commit rule, the end-of-turn check, review, `verify` and `finish` skip the suite when nothing has changed since the last green run. It used to run up to four times per ticket and three more per feature on identical files. New `supermatt test [--force]` is how the skills run the suite.
- Review runs in the main context by default, one axis after the other, instead of two subagents per ticket. `pipeline.review_agents true` brings the parallel subagents back for large diffs.
- The end-of-turn check never blocks twice on the same unchanged files; it warns you instead.
- `verify` opens one round of gap tickets per feature. Gaps left after that come to you instead of looping.
- `run` never waits indefinitely on a background command or subagent.
- New `solo` preset: `tests_before_commit` block, `review_after_ticket` warn, the other two off.
- CI runs two jobs (oldest Python on macOS, newest on Linux) instead of four.

## 0.4.0

- New `/supermatt:drift` checks a prompt, a plan or work in progress against what you actually approved. It lists each departure under "goes against what you approved" or "goes beyond what you approved", recommends trash, keep or change for each, and waits for your ruling before rewriting or undoing anything. Only your own words count as approval; an edited spec does not.
- `run` calls it mid-ticket when it cannot trace what it is building to the ticket, the spec or your words. Kept items go into the spec and a ticket; trashed commits are reverted, never rewritten.

## 0.3.0

`/supermatt:advise` and `/supermatt:setup` catch the mistakes found in two real planning sessions:

- `advise` checks the test command as a guardrail. Does it run the kind of test the plan's outcomes need, such as browser tests for browser-level outcomes? Does it test current code rather than an old build? Is it stable? Is it too slow to run at the end of every turn?
- `advise` compares the tool versions the repo pins with what's installed, and makes a mismatch the first step of the plan.
- `advise` reads the repo's and your own standing rules, for example pushing straight to `main`, rules about review, or a release step, and sets the options to match.
- `advise` checks its plan before giving it to you. Every problem it found must be a step or a named risk. The options must match the steps (for example, a `/clear` between tickets and building needs a pause before `implement`). Every promised outcome must be proven by a named command, and the guardrails must suit the test suite.
- `advise` now starts its plan with a **Settings** block listing every supermatt setting the plan relies on, each with its reason. It shows conflicts between your repo's rules and your global rules for you to decide. It knows how pauses, `--from` entry points and finish modes actually behave, and phrases option changes as setup answers rather than commands you can't run.
- New `pipeline.finish: push` merges, runs the tests, then pushes the base branch, for teams that push straight to `main`. `finish` shows a repo's documented release step (such as a promote command) and runs it only when you say go.
- New `pipeline.branch_prefix` names feature branches the way your repo requires, for example `claude/<feature>`.
- `advise` includes a table showing which `pause_at` stage gives you which review. It picks a toolchain switch command that works on your machine, reads recent test failure records, gives firm settings, and leaves to you only the checks that need your eyes.
- `tickets` labels tickets that wait on a decision only you can make as `needs-info`, and `run` skips them until you answer.
- `setup` checks the pinned tool versions and your standing rules. It runs the test command twice to catch flaky tests, and includes the browser tests in the test command when the repo has them, and raises `test_timeout` when the suite needs more than 300 seconds.

## 0.2.0

- `/supermatt:run --from spec|tickets|implement|verify` starts a feature partway through, for work that was already planned outside the pipeline (an audit, a design doc, an existing spec or tickets). The pipeline still records its progress, so the work can be resumed. The `supermatt start` command takes a matching `--stage` option.
- `run` no longer pauses before the stage you just started or resumed.
- `/supermatt:advise` recognises work that's already planned and recommends `--from`.
- Added a security policy (`SECURITY.md`). The README now explains that trusting a config approves the command, not the code the command runs. `/supermatt:triage` now treats issue and pull request text as data and never runs commands from it without your approval.
- Removed the retired `spine_check.py` tooling; it's still in the git history.
- `/supermatt:setup` checks that the test command tests your current source rather than an old build. It also suggests turning off `green_before_stop` when the test suite is slow, and explains `pipeline.branch false` for teams that commit straight to the main branch.

## 0.1.0

First release.

- `/supermatt:run`: a pipeline you can resume. It takes a feature through grill → spec → tickets → implement → verify → finish, and the `supermatt` command records its progress.
- `/supermatt:advise`: turns a description of your situation, plus the repo's actual state, into a plan that says which skills to run and in what order.
- A merged skill set of 20 skills, adapted from mattpocock/skills and obra/superpowers.
- Guardrails for each repo (`tests_before_commit`, `ticket_before_code`, `review_after_ticket`, `green_before_stop`). Each one can block, warn or be off, and presets set all four at once.
- A repo's config only takes effect after this machine trusts it, so a cloned or pulled config can't run commands until you approve it.
