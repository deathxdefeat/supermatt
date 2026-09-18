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

- `SM status`: is the repo set up, which preset, is a feature in flight and at which stage?
- `git status`, `git log --oneline -15`: what changed recently, and how much churn is there on the same area?
- The tracker (`docs/agents/issue-tracker.md` says where): open specs and tickets, and their states.
- `CONTEXT.md` and `docs/adr/`: does the design the user describes exist on paper?
- The tests: is there a test command, and does any test cover the outcome the user cares about? Run the suite once if it is cheap; a green suite beside a broken product is itself the key finding.

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
| **Mid-stream** | a feature in flight in `SM status` | `/supermatt:run` to resume |

**The "repeatedly done but not working" pattern outranks the others.** It means nothing verifies the outcome the user actually cares about, so every agent can pass its own checks and still ship something broken. The plan must then begin by writing that outcome down as a failing end-to-end acceptance test (one real input, the exact expected output), putting it in the test command, and using the `strict` preset, so no commit and no claim of done gets past it. Then diagnose, then build.

**Chains break at the first bad link.** When the problem runs through stages (input → processing → output), plan to trace one real input hop by hop from the start and fix the first hop that goes wrong. Fixing downstream symptoms first wastes the work.

## 4. Lay out the plan

Answer in this shape, briefly:

1. **What this is**: one or two sentences naming the situation and the evidence, including anything the fact check turned up that the user didn't mention.
2. **The plan**: numbered steps. Each gives the exact command (with flags), why it comes at this point, and what finished looks like for that step. Put setup and option changes where they belong (for example `/supermatt:setup` with the `strict` preset, `SM config pipeline.pause_at grill,spec,tickets,implement,verify,finish`, or `--guided` / `--auto` on `run`).
3. **What to watch for**: the one or two ways this plan most likely goes wrong, and how the user will notice.
4. **Start here**: the single first command to type.

Recommend one plan, not a menu. Mention an alternative only when the choice genuinely turns on something only the user knows, and say what it turns on. Be honest about limits: a step that depends on the user looking at the real product, a skill that has never been run in this repo, or duplicate skills installed alongside supermatt.

## 5. Stop

End with the plan. If the user says go, start at step 1 by calling the Skill tool for the skill it names.
