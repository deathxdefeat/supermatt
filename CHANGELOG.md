# Changelog

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
