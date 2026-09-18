---
name: grill
description: Grill the user relentlessly about a plan, decision, or idea until you share one understanding, recording glossary terms in CONTEXT.md and decisions as ADRs as they settle. Use when the user wants to stress-test their thinking, sharpen a feature before building it, or uses any 'grill' trigger phrase.
argument-hint: "[--no-docs] [--auto] <what to grill>"
---

# Grill

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Modes

- **Docs mode (default in a working directory).** Run the interview and, as you go, keep the domain model current by following [DOMAIN-MODELING.md](DOMAIN-MODELING.md): challenge terms against `CONTEXT.md`, write resolved terms into it the moment they settle ([CONTEXT-FORMAT.md](CONTEXT-FORMAT.md)), and record hard-to-reverse decisions as ADRs ([ADR-FORMAT.md](ADR-FORMAT.md)).
- **`--no-docs`, or no working directory.** The same interview, stateless: write nothing.
- **`--auto`** (set by `/supermatt:run` when `pipeline.interview` is `auto`). Do not wait for answers. Work the tree yourself: settle every decision with your recommended answer, grounded in the code and docs, and mark each one **assumed**. Write the assumed decisions to the conversation as one numbered list so the spec can carry them and the user can overturn any of them later. Docs mode still applies.

## Rounds

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

When a question can only be settled by something runnable (state, business logic, a UI the user has to see), say so and suggest `/supermatt:prototype` rather than guessing.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding (in `--auto` mode, until the assumed-decisions list is written).
