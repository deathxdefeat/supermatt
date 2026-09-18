# supermatt is a plugin that owns its skills

supermatt started as 23 links from the skills directory into two source clones, plus a command that checked the links. That gave nothing the upstream skills did not already give. We made supermatt a Claude Code plugin that owns a fused copy of the skills (overlapping upstream skills merged, cross-references rewritten to `supermatt:` names), adds a `/supermatt:run` pipeline that records its progress with a small stdlib Python command, and adds hooks that enforce the workflow in repos that opt in with `.supermatt/config.json`. Every enforcement rule and pipeline behaviour is an option, set per repo.

## Considered options

- **Keep linking to the source clones.** Rejected: the skills stay separate, reference each other by upstream names, and nothing ties them into one flow.
- **Orchestrator skill only, still linking upstream.** Rejected: an orchestrator cannot keep state or enforce anything, and upstream edits could silently break the flow.
- **A marketplace install.** Deferred: a link in the skills directory loads the plugin in place (`supermatt@skills-dir`), so edits in this repo take effect on the next session without a reinstall.

## Consequences

- The fused skills drift from upstream. `plugin/NOTICE.md` records the upstream commits they were imported from; pulling upstream changes is a manual merge.
- Hooks are no-ops outside opted-in repos, so the plugin can stay enabled everywhere.
- The upstream links can coexist with the plugin, but then the same skill appears twice (for example `/tdd` and `/supermatt:implement`).
