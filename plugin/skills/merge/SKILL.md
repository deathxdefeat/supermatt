---
name: merge
description: "Resolve an in-progress git merge or rebase conflict by intent, hunk by hunk, then finish the operation. Use when a merge, rebase or cherry-pick has stopped on conflicts."
---

# Merge

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve rather than `--abort`, unless the user asks to abort.

4. Discover the project's **automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage the files you resolved (and any the checks required you to fix), never a blanket `git add -A`, then commit. If rebasing, continue the rebase process until all commits are rebased.
