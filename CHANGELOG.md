# Changelog

## 0.1.0

First release.

- `/supermatt:run`: a pipeline you can resume. It takes a feature through grill → spec → tickets → implement → verify → finish, and the `supermatt` command records its progress.
- `/supermatt:advise`: turns a description of your situation, plus the repo's actual state, into a plan that says which skills to run and in what order.
- A merged skill set of 20 skills, adapted from mattpocock/skills and obra/superpowers.
- Guardrails for each repo (`tests_before_commit`, `ticket_before_code`, `review_after_ticket`, `green_before_stop`). Each one can block, warn or be off, and presets set all four at once.
- A repo's config only takes effect after this machine trusts it, so a cloned or pulled config can't run commands until you approve it.
