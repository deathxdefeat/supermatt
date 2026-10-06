# Third-party notices

Most supermatt skills are adapted from two MIT-licensed skill collections. Files were imported, renamed to supermatt's skill names, merged where upstream skills overlapped, and edited to fit the pipeline.

| Source | Commit imported | supermatt skills |
|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | `74ca5fe`, with local edits (see below); synced to `6fd9479` (v1.3.1+) | setup, grill, spec, tickets, implement, review, debug, merge, triage, prototype, research, wayfinder, architecture, handoff, retro, finish's PR body (`pr`), advise (the skills map) |
| [obra/superpowers](https://github.com/obra/superpowers) | `b36e082` | verify, finish, worktree |

The mattpocock/skills import was taken from a local branch on top of upstream `74ca5fe` that had five small edits: chain skills allowed to be model-invoked; implement commits before review and invokes tdd and code-review through the Skill tool; review sub-agents told not to spawn more sub-agents; tdd's trigger description narrowed; and the handoff skill renamed. supermatt's own adaptations go further than these.

The sync to `6fd9479` took upstream's `GLOSSARY.md`/`GLOSSARY-MAP.md` rename (supermatt still reads a legacy `CONTEXT.md`), the GitHub sub-issue and external-PR operations, the tickets sub-issue rule, the handoff temp-dir order, and the new `retro` and `pr` skills (`pr` became `finish/PR-BODY.md`). It did not take `implement-spec` (the `run` pipeline covers it) or the experimental `chief-of-staff`. Upstream removed `resolving-merge-conflicts`; supermatt keeps it as `merge`, because `finish` can stop on a conflict.

The pull request body's menu of Summary visuals comes from Dex Horthy's `show-me` skill (Humanlayer), by way of mattpocock/skills' `pr`.

`run`, `status`, `drift`, the `advise` process, `bin/supermatt` and `hooks/` are original to supermatt.

## mattpocock/skills

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## obra/superpowers

```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
