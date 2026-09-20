# Troubleshooting

For the overview, see the [README](../README.md).

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
