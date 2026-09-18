# supermatt

A Claude Code plugin that turns a curated skill set into one engineering workflow: a resumable pipeline, a fused skill set and optional per-repo enforcement. It also keeps the tooling that checks the older skill spine.

## Language

**Skill spine**:
The curated set of skills installed from the source clones into the skills directory, each as a link. Retired: the plugin's fused skill set replaced it, and the links were removed.
_Avoid_: skill set, merged set, skill config

**Spine manifest**:
The committed list of every skill the spine should contain, each with its source clone and its path inside that clone.
_Avoid_: config, registry, inventory

**Entry**:
One skill in the spine manifest: a skill command name, a source clone and a path inside that clone.
_Avoid_: row, item, record

**Skill command name**:
The name a skill is invoked by, which is the name of its link in the skills directory, not the `name` in its frontmatter.
_Avoid_: skill name, slug

**Source clone**:
A local git clone that supplies spine skills: `mp` (mattpocock/skills) or `sp` (obra/superpowers).
_Avoid_: upstream, repo, source

**Skills directory**:
The personal Claude Code skills directory the spine is installed into, normally `~/.claude/skills`.
_Avoid_: skills folder, install dir

**Plugin**:
The supermatt Claude Code plugin in `plugin/`, installed as a link named `supermatt` in the skills directory and loaded as `supermatt@skills-dir`.
_Avoid_: package, extension

**Fused skill set**:
The skills the plugin owns, invoked as `/supermatt:<name>`: adapted from the source clones, with overlapping upstream skills merged into one and cross-references rewritten to supermatt names.
_Avoid_: spine (the spine is the older set of links to the source clones)

**Pipeline**:
The fixed sequence of stages `/supermatt:run` drives a feature through, with progress recorded so it can resume.
_Avoid_: workflow, flow

**Stage**:
One step of the pipeline: grill, spec, tickets, implement, verify, finish, then done.
_Avoid_: phase, step

**Feature**:
The unit of work the pipeline carries, named by a kebab-case slug that also names its tracker directory.
_Avoid_: project, task

**Ticket state**:
Where one ticket is in the pipeline: implementing, blocked (waiting on the user), needs-review or done. Separate from the triage status in the tracker.
_Avoid_: ticket status

**Opted-in repo**:
A repo with a committed `.supermatt/config.json`. Enforcement rules and the pipeline act only in opted-in repos.
_Avoid_: enabled repo, configured project

**Enforcement rule**:
One check the plugin's hooks apply in an opted-in repo: tests_before_commit, ticket_before_code, review_after_ticket or green_before_stop. Each is set to off, warn or block.
_Avoid_: guard, gate, policy

**Trusted config**:
A config this machine has approved to run hooks, recorded by repo path and the config's exact bytes. A config that changed since it was trusted is untrusted, and hooks ignore it.
_Avoid_: allowed, approved repo

**Preset**:
A named setting for all four enforcement rules at once: strict, standard, light or off.
_Avoid_: profile, mode

**Pipeline state**:
The local, gitignored `.supermatt/state.json`: the active feature, its stage, ticket states and the last green test fingerprint.
_Avoid_: progress file, session
