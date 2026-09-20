# Skills and the advisor

Every skill, and how `/supermatt:advise` chooses between them. For the overview, see the [README](../README.md).

## The advisor

Describe your situation in your own words:

```text
/supermatt:advise the export has been "fixed" three times and still writes an empty file
```

`/supermatt:advise` reads what you wrote, then checks the repo itself: the pipeline status, recent commits, open specs and tickets, `CONTEXT.md` and ADRs, and the tests (it runs them once if that is cheap). It makes no edits, commits or stage changes. Its answer has four parts:

1. **What this is**: the kind of situation, with the evidence, including anything the repo showed that you did not mention.
2. **The plan**: numbered steps, each with the exact command, why it comes at that point, and what finished looks like.
3. **What to watch for**: the one or two ways the plan is most likely to go wrong.
4. **Start here**: the first command to type.

Tell it to go and it starts step 1 itself. The exceptions are the four skills only you can start (`run`, `triage`, `wayfinder` and `handoff`): for those, it tells you what to type.

| Situation | Starts with |
|---|---|
| A feature you can describe in a few sentences | `/supermatt:run <feature>` |
| An idea where you can't yet say what done looks like | `/supermatt:grill`, then `/supermatt:run` |
| A plan, spec or tickets that already exist from outside the pipeline | `/supermatt:run <feature> --from <stage>` |
| Work too big for one session | `/supermatt:wayfinder` |
| Something that should work but doesn't | `/supermatt:debug` |
| Work that keeps being called done but still doesn't work | An end-to-end acceptance test first, then diagnosis |
| A design that fights every change | `/supermatt:architecture` |
| A question only running code can settle | `/supermatt:prototype` |
| Facts you need from docs or APIs | `/supermatt:research` |
| A pile of incoming issues | `/supermatt:triage` |
| Work that may have grown past what you approved | `/supermatt:drift` |
| A feature already in flight | `/supermatt:run` to resume |

## All 21 skills

All 21 skills are invoked as `/supermatt:<name>`. Where skills from the two source collections (Matt Pocock's and obra/superpowers) overlapped, they were merged into one, and the skills call each other by these names. Claude also starts a skill by itself when your request fits, except the four marked *(you type it)*.

**Driving the workflow**

| Skill | What it does |
|---|---|
| `/supermatt:run` *(you type it)* | Takes a feature through every stage and resumes where it stopped |
| `/supermatt:advise` | Reads your situation and the repo, then lays out which skills to run, in what order, and why |
| `/supermatt:setup` | Sets a repo up once: issue tracker, labels, domain docs, test command, options. `run` starts it for you when a repo isn't set up. |
| `/supermatt:status` | Shows the pipeline's progress, the options, and whether this machine has approved the config ([trust](security.md)). Changes options when you ask. |

**Pipeline stages** (`run` calls these; each also works on its own)

| Skill | What it does |
|---|---|
| `/supermatt:grill` | Questions you in rounds until the design is clear, writing `CONTEXT.md` terms and ADRs as they are decided |
| `/supermatt:spec` | Turns the conversation into a spec in your issue tracker, without a new interview |
| `/supermatt:tickets` | Splits a spec into tracer-bullet tickets, each listing what blocks it |
| `/supermatt:implement` | Builds a ticket, a spec or a described behaviour test-first, commits it, and hands it to review |
| `/supermatt:review` | Reviews against your coding standards and against the spec, in parallel, then fixes the findings and closes the ticket |
| `/supermatt:verify` | Requires evidence from the current files before anything is called done |
| `/supermatt:finish` | Runs the full test suite, then merges, opens a pull request, or keeps the branch |

**On demand**

| Skill | What it does |
|---|---|
| `/supermatt:debug` | Diagnoses hard bugs and slowdowns: first a command that reproduces the failure, then a fix with a regression test |
| `/supermatt:merge` | Resolves a stopped merge, rebase or cherry-pick by what each side meant to do |
| `/supermatt:triage` *(you type it)* | Sorts incoming issues and writes briefs an agent can work from |
| `/supermatt:prototype` | Builds throwaway code to settle one design question |
| `/supermatt:research` | Sends a background agent to primary sources and saves a cited Markdown file |
| `/supermatt:architecture` | Helps design modules, and finds places where a module should do more behind a smaller interface |
| `/supermatt:wayfinder` *(you type it)* | Breaks a large, unclear effort into decision tickets and resolves them one at a time |
| `/supermatt:drift` | Checks a spec, tickets, plan or work in progress against what you actually approved, lists each departure as *against* or *beyond* what you approved, and changes nothing until you rule |
| `/supermatt:worktree` | Sets up an isolated workspace, such as a separate git worktree, for feature work |
| `/supermatt:handoff` *(you type it)* | Writes a handoff document so a fresh session can pick up the work |
