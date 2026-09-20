# Configuration: options and guardrails

Every option supermatt reads, the four guardrail rules and how they are checked. For the overview, see the [README](../README.md).

Guardrails are four rules, enforced by Claude Code hooks and the `supermatt` command, that can stop Claude committing with failing tests (`tests_before_commit`), editing code with no ticket open (`ticket_before_code`), moving on before a finished ticket is reviewed (`review_after_ticket`), or ending its turn with failing changes (`green_before_stop`). Each rule is `off`, `warn` (the action goes ahead with a warning) or `block` (the action is stopped and Claude is told why). A preset sets all four at once.

Each repo keeps its options in `.supermatt/config.json`, which you commit so the whole team shares them. To change one, ask `/supermatt:status` in plain words ("turn ticket_before_code off", "use the strict preset", "pause before every stage"), or have Claude run [`supermatt config`](cli.md).

## Ticket states

The guardrails work from each ticket's state, which the skills record as they go.

![Ticket states: implementing, needs-review, done, and blocked while Claude waits on your answer](images/ticket-states.svg)

*The state supermatt records for each ticket. `blocked` means Claude is waiting on you; once you answer, the ticket returns to whichever state it came from.*

A ticket's id is its local file number (`01`) or its issue number on a hosted tracker (`123`).

## The four rules

| Rule | Checked when | What it enforces |
|---|---|---|
| `tests_before_commit` | Claude runs `git commit` through its Bash tool | The test command runs first, unless these exact files already passed it. If it fails, the commit is stopped (at `warn`, it goes ahead with a warning), and Claude sees the last 30 lines of output. A pass shows nothing. Does nothing without a `test_command`. |
| `ticket_before_code` | Claude edits a file with Edit, Write, MultiEdit or NotebookEdit | The current ticket must be `implementing` or `needs-review`. Files outside the repo, and paths matching `exempt`, are ignored. |
| `review_after_ticket` | A ticket is started or marked done, and when Claude tries to end its turn | While a committed ticket waits in `needs-review`, no other ticket can start and the turn cannot end. A ticket still `implementing` or `blocked` cannot be marked `done`: it goes through review first. A `blocked` current ticket lets the turn end. |
| `green_before_stop` | Claude tries to end its turn | Uncommitted changes to non-exempt files must pass the tests. Skipped while the current ticket is `implementing` (failing tests are a normal step in test-first work) or `blocked`, and when those changes already passed. It never blocks twice on the same unchanged files. Does nothing without a `test_command`. |

## Presets

| Preset | tests_before_commit | ticket_before_code | review_after_ticket | green_before_stop |
|---|---|---|---|---|
| `strict` | block | block | block | block |
| `standard` (default) | block | warn | block | block |
| `light` | warn | warn | warn | warn |
| `solo` | block | off | warn | off |
| `off` | off | off | off | off |

`standard` suits most repos. Choose `solo` when you work alone and want speed: tests still gate every commit, but nothing runs per edit or at the end of a turn. Choose `strict` when every code edit, including debugging and prototypes, should need a ticket first. If your test command is slow (a build plus an end-to-end suite, say), consider turning `green_before_stop` off: it runs the tests at the end of every turn that changed code, even at `warn`, and `tests_before_commit` at `block` remains the gate that matters.

## The end-of-turn check

This is the check that stops Claude from ending a turn with work unfinished.

![The end-of-turn check: the questions supermatt asks before letting Claude end its turn](images/end-of-turn.svg)

*Shown with `review_after_ticket` and `green_before_stop` at `block`. At `warn`, the turn ends with a warning to you instead of being blocked. Not shown: when the tests fail on exactly the files that failed at the last end of turn, the turn ends with a warning instead of a second block.*

Once a set of files passes, nothing reruns the tests until the code changes again: not this check, not the commit rule, not `verify` or `finish`. The pipeline runs the suite through `supermatt test`, which shares that memory; `supermatt test --force` reruns regardless. If the same unchanged files fail twice in a row, the second end of turn warns you instead of blocking again.

## Pipeline and other options

| Option | Default | Meaning |
|---|---|---|
| `test_command` | none | The command the guardrails and the verify stage run. Without one, the two test rules do nothing. |
| `test_timeout` | `300` | Seconds before a test run counts as failed. At most 570, because Claude Code stops the commit and end-of-turn hooks after 600. |
| `exempt` | `.scratch/*`, `docs/*`, `.supermatt/*`, `*.md` | Paths the code rules ignore |
| `pipeline.interview` | `full` | `full` waits for your answers during grilling. `auto` answers each question with the recommended answer and lists these as assumptions in the spec. |
| `pipeline.pause_at` | `implement,finish` | The stages `run` pauses *before*, waiting for your go-ahead: any of `grill`, `spec`, `tickets`, `implement`, `verify`, `finish`. `none` never pauses. |
| `pipeline.branch` | `true` | Create a branch named after the feature before implementing |
| `pipeline.branch_prefix` | empty | Prefix for that branch's name, for example `claude/` when your repo names branches that way |
| `pipeline.worktree` | `false` | Implement in an isolated worktree instead, through `/supermatt:worktree` |
| `pipeline.ticket_agents` | `false` | Build each ticket in a fresh subagent. The pipeline then checks `supermatt status` and `git log` itself before the next ticket, because a subagent's report is not evidence. That subagent runs both reviews itself, one after the other. |
| `pipeline.review_agents` | `false` | Run each review's two axes as parallel subagents instead of in the main context. Costs about three reads of the diff instead of one; worth it on large diffs. |
| `pipeline.finish` | `ask` | `ask` shows a menu. `merge`, `push` (merge, test, then push the base branch), `pr` or `keep` always does that one. |

The equivalent commands:

```bash
supermatt config                                   # show every option
supermatt config preset strict                     # set all four rules
supermatt config enforce.ticket_before_code off    # set one rule
supermatt config pipeline.pause_at spec,implement,finish
supermatt config pipeline.pause_at none            # never pause
supermatt config test_command "npm test"
```

## When the tests pass but the product is broken

The rules are only as good as the test command ([Limits](security.md#limits)). [`/supermatt:advise`](../README.md#the-advisor) has a row for "work that keeps being called done but still doesn't work":

If that row applies together with another one, the advisor deals with it first. It means nothing checks the outcome you actually care about, so every step can pass its own checks and still ship something broken. The plan starts by writing that outcome as one end-to-end acceptance test (a real input and the exact expected output) and adding it to your test command. Under the `standard` preset, Claude then can't commit while that test fails.
