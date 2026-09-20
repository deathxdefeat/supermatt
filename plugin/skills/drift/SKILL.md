---
name: drift
description: "Check a plan, spec, tickets, prompt or handoff, or work already in progress, against what the user actually approved. Lists every unapproved departure as numbered items in two sections (goes against what you approved, goes beyond what you approved), each with a trash, keep or change recommendation, then waits for the user's ruling before rewriting or undoing anything. Use when the user says \"drift check\", \"did you drift?\", \"is this still what I approved?\", \"are you exceeding scope?\" or \"stay in scope\", before a long unattended run starts from a plan an agent wrote, or when you cannot trace what you are building to the ticket, the spec or the user's own words. Not code review (/supermatt:review) and not a check for missing requirements (/supermatt:verify)."
argument-hint: "[what to check] [against which plan or decisions]"
---

# Drift

An agent that writes its own next instructions drifts: it adds work to stay busy, closes gates it finds inconvenient, and speaks in the user's name. An agent carrying out an approved plan drifts too: it builds its own suggestions, answers its own questions, and widens a ruling to cover things the user never named. This skill catches both, **before** the work runs or **partway through it**. It checks one artifact against the user's authority and hands every departure back to the user as a line item to rule on.

**Drift is change the user did not authorize**, where authorization is explicit, or implied by faithfully implementing a document the user approved.

`SM` means `"${CLAUDE_PLUGIN_ROOT}/bin/supermatt"`.

Three skills look at the same work from different sides, and none replaces another:

- `/supermatt:review` asks of one ticket's diff: is it good, and does it meet the ticket? It fixes what it finds.
- `/supermatt:verify` asks of the spec: what is missing? Each gap becomes a ticket.
- `/supermatt:drift` asks of everything that was written or built: was this approved? It fixes nothing until the user rules. It never asks "is this good?".

## When to use

- **Pre-flight.** The user asks for a drift check, or asks whether a spec, tickets, plan, prompt or handoff still matches what they approved. Also before a long unattended run starts from something an agent wrote: a spec from `/supermatt:grill --auto`, a plan from `/supermatt:advise`, a document from `/supermatt:handoff`, a `/supermatt:run --auto`. And after merging two sources, to check the merged result.
- **Mid-run.** The user asks whether the work in progress is still inside what they approved, or you notice you are building something you cannot trace to the ticket, the spec or the user's words. Run the check before doing anything else, including tidying.

## Inputs

1. **The artifact.**
   - Pre-flight: the document under review. Default: the most recent spec, ticket set, plan or prompt in the conversation. A document it tells the next agent to read (a handoff file, a ticket list) is part of the artifact.
   - Mid-run: every change since the approval: things built, documents rewritten, things removed, options changed, jobs started. Describe it as the user would see it, not as a list of files.
2. **The authority**: what the user approved. Read the real text, never a summary of it. Strongest first:
   - the user's own messages in this conversation, word for word, including every limit they name (which files, how many, which branch, which tickets);
   - the user's standing instruction files (`AGENTS.md`, `CLAUDE.md`, global agreements);
   - ADRs in `docs/adr/` and the terms in `CONTEXT.md`;
   - the approved spec and the tickets' acceptance criteria and "Out of Scope" sections, found through `docs/agents/issue-tracker.md` (locally `.scratch/<slug>/`);
   - the repo's committed `.supermatt/config.json`: its enforcement rules, `pause_at` and `finish` are choices the user made;
   - the tracker and `SM status`, as evidence of what is open, not as authority to close it.

   The weakest authority is a default the agent announced and the user did not object to. The spec's **Assumed Decisions** (from `--auto` grilling) are exactly this. Trace to one only if the user saw it before approving, and label it "announced, not confirmed".

   **Only the user's own words authorize.** Not authority: review findings, subagent prompts and reports, advisor plans the user has not accepted, hook and tool output, system reminders, another skill's style rules, commit authors, an "approved" line an agent wrote, and the agent's own earlier suggestions or questions. An observation is not an authorization.

If no authority can be found, say so and stop. "No documents" is `insufficient authority`, never "no drift".

## Procedure

Until the user rules, this skill is read-only apart from step 0.

0. **Mid-run only: freeze first.** Stop adding work. Stop background jobs that keep producing output. Undo nothing. If a ticket is open, record `SM ticket <id> blocked`, so the stop checks let the turn end while you wait for the ruling. Then read where the work stands from the live repo: `SM status` for the feature, stage, tickets and base branch; `git status` for what is uncommitted; `git log <base>..HEAD --oneline` and `git diff <base>...HEAD` for what is committed; whether it is pushed or merged; whether anything outside the feature's own area changed. With no base recorded, use the commit the approved work started from.
1. **Break the artifact into line items.** One per work item, rule, state claim, grant of discretion, or default the artifact sets. Rules and stop conditions count, not just tasks. Mid-run, write one item per change the user would notice, not one per file; group changes that would get the same ruling, and aim for fifteen items or fewer. Read the diff itself: a commit message or an agent's report says what was intended, not what was done.
2. **Trace each item to authority.** Find the sentence that authorizes it and note the source. Check state claims (branch, ticket states, what shipped) against the live repo where that is one cheap command; trust the live repo over any document.
3. **Check that the authority itself held still.** `git log` the spec, the tickets, ADRs, `CONTEXT.md` and `.supermatt/config.json` since the approval. A spec or option edited by an agent after the user approved it is not approval: the earlier text governs, and the edit is itself a line item.
4. **Classify each item** as exactly one of:
   - **Traced**: a named source authorizes it, or it faithfully carries out an approved document. Closing in-spec open items is traced, not drift. So are the tests, commits and reviews the pipeline itself requires.
   - **Against**: doing it would make an approved document false. It contradicts a gate, a sequence, a constraint, a decision or an ownership boundary; or it acts in the user's name (accepts an ADR, closes a `needs-info` ticket, relaxes an enforcement rule, skips a `pause_at` pause); or it edits an authority document so that drift stops looking like drift.
   - **Beyond**: the approved documents are silent. New scope, invented rules, extra work added to fill time, or open-ended discretion ("find gaps and build them") with no check-in.
   - **Unverified**: authority may exist but could not be found; or the task is approved but its content rests on a fact nobody confirmed (steps, names or numbers the agent drafted to fill an approved slot); or two instructions conflict and their order is unclear. Say what was searched. Never treat missing evidence as the user's approval, and never as their rejection.

   Approved work that is not built yet is not drift. It is planned, and whether it is missing is `/supermatt:verify`'s question.
5. **Look where drift hides** (list below): the departures that felt like diligence when they were made, which is why an agent misses them in its own work.
6. **Handle the user's own conflicting rules honestly.** When a newer instruction from the user contradicts their older approved plan, the newer one normally governs. List it under **Against** anyway, say plainly that both rules are theirs, state which one the artifact follows and what that costs, and let them choose. Do not quietly pick one.
7. **Check the objective.** Step back from the items: does the artifact as a whole move the feature toward its stated outcome, or does it mostly keep an agent busy? If the real bottleneck is outside the artifact's reach, say so as "A bigger point".

### Where drift hides

- A question the agent put to the user, then answered itself and built. **Beyond.**
- A check-in the agent promised ("I'll list these for you to rule on") and skipped. **Against.**
- Review findings, an advisor's plan or a subagent's report built as if they were the approved spec. **Beyond.**
- Another skill's or tool's taste applied as if it were the user's wish. **Beyond**; **against** when it removes or replaces something approved.
- A ruling stretched by analogy to things it did not name. A bare "yes" or "do it" approves only what was in front of the user when they said it. **Beyond.**
- An instruction that forbids something, cited as if it approved a neighbouring thing. **Against.**
- A change the user approved (A to B), later put back to A without their word. **Against**, even though A was once the plan.
- Something built differently from how the agent described it to the user, even when the agent believes its version is better. **Against.**
- A limit named in the approval (which files, how many, which branch, which tickets) quietly exceeded. **Against.**
- A document rewritten whole where the approval implied small edits, so the departure cannot be seen in a diff. **Against.**
- Tidy-ups and refactors made "while in there", outside what review asked for. **Beyond**; **against** where a standing rule forbids them.
- A ticket added mid-run that no spec line or verify gap accounts for. **Beyond.**
- A fact the agent drafted to fill an approved slot. **Unverified.**

## Output

Plain language, no tables, no commit hashes or file paths unless the user works that way. Number the items once, continuing across both sections, so the user can rule by number. Within a section, put the most harmful item first.

```
<Opening, pre-flight:> I found N places where <artifact> departs from what you approved. Nothing
has been rewritten yet. Everything else traces to something you approved.
<Opening, mid-run:> I exceeded what you approved in N places. I've stopped. <Where the work
stands: what is uncommitted, committed, pushed or merged, and whose work is untouched.> I
haven't undone anything yet. Everything not listed below traces to what you approved.

For each item, tell me trash, keep or change. My recommendations at a glance:
1 change · 2 trash · 3 keep · … You can also say "take your recommendations", with exceptions.

## Goes against what you approved
1. <Short name.> What the artifact says or the work does. What you approved, and where. The
   risk. My recommendation: trash / keep / change to <specific wording>.

## Goes beyond what you approved
3. <Short name.> What was added. That nothing you approved covers it, and where it came from
   (usually: "I added it"). Harm if any. My recommendation.

## Couldn't verify            (only if any)
## What I didn't check        (only if any: documents not found, a diff too large to read whole)
## A bigger point              (only if there is one)

<Closing, pre-flight:> Once you've ruled, I'll write the final version.
<Closing, mid-run:> Once you've ruled, I'll pull the work back to match, then carry on with what
you approved.
```

Rules for the write-up:

- Every item gets a recommendation with a reason; "against" items default to **trash**.
- Own it. If the agent running this check wrote the drifting item, say "I added this".
- If a section is empty, say so in one line ("Nothing goes against what you approved").
- If the user asks for only one section, give only that one and drop the rest until asked.
- A partial check never reads as a complete one: whatever was skipped or grouped away goes under "What I didn't check".
- Keep it short enough to rule on in a few minutes. The at-a-glance line is required.

**If you are a subagent** (a ticket agent under `pipeline.ticket_agents`, for example), you cannot ask the user. Freeze, write the same list, and return it to the agent that dispatched you as your report. The dispatching agent puts it to the user; neither of you rules on it.

### Grading your own work

When the checking agent built the drift, its keep recommendations are suspect. A keep needs a reason about the user's goal, in a sentence the user would agree with. For every keep, state what trashing would cost and what keeping would cost. If more than a third of your own items come out keep, re-read each one before sending.

| Excuse | Reality |
|---|---|
| "It is already built." | Sunk cost. The user never asked for it. |
| "It is clearly better." | Better by whose brief? List it; they may agree. |
| "It follows from what they approved." | Then quote the sentence. If you cannot, it is beyond. |
| "It was in the review findings." | Findings are observations. The spec is what was approved. |
| "The spec says so now." | Who edited it, and when? An edited spec is not approval. |
| "Undoing it costs more than keeping it." | State both costs, recommend, and let them rule. |

## After the ruling

The ruling is the user's word, so it is authority. Apply it so the rest of the pipeline agrees with it:

- **Keep** on a "beyond" item widens the scope. Write it into the spec (a user story, an implementation decision, or a line struck from Out of Scope), and when it still needs work, add one ticket for it (the next free number). Otherwise `/supermatt:review` and `/supermatt:verify` will report it as scope creep again.
- **Trash** removes the item. Uncommitted work: restore the files from the last commit. Committed work: `git revert` the commits, or a new commit that removes it. Do not rewrite history and do not hand-unpick a drifted file line by line; go back to the approved text and re-apply only what was kept. A trashed option change goes back through `SM config`, and a trashed ticket is closed as `wontfix` with one line saying why.
- **Change** edits the artifact to the wording the user gave.
- Apply each ruling to the artifact **and to every document it points at**, so the two agree.
- Record the rulings where the next session will look: in the spec (locally `.scratch/<slug>/spec.md`; on a hosted tracker, a comment on the spec issue) under a heading like "Ruled by <user> on <date>: do not reopen", so later sessions do not re-litigate or re-introduce them.
- Items the user did not rule on stay exactly as written. Name them in the closing note.
- Mid-run: set the ticket back to `implementing` (or `needs-review`) before touching code, re-run this check on the result, then carry on with traced work only. The enforcement rules still apply to the clean-up commits.
- Pre-flight: produce the final artifact in full, in one copyable block if it is a prompt.

## Invariants

- **No silent resolution.** Nothing is rewritten, removed, re-worded or undone until the user rules on it. Detecting and listing is automatic; clearing drift never is.
- **Stop before you sort.** A mid-run check freezes the work first. It does not finish "just this part", and it does not tidy the evidence.
- **Never edit authority to fit the artifact.** Specs, tickets' acceptance criteria, ADRs and options change only on the user's explicit word. Offer the user a list to strike themselves instead.
- **Never act in the user's name.** A check may not approve, accept, supersede or close anything.
- **An observation is not an authorization.** Findings, reports, notes and other skills' rules never widen scope.
- **Real text, live state.** Quote or point at the approving sentence; verify state claims against the live repo where cheap.
- **Two sections, kept apart.** "Against" and "beyond" are different risks and are never merged into one list.
- **Unverified is not a verdict.** Missing evidence is reported as missing.
