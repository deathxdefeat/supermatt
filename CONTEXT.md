# supermatt

A Claude Code plugin that turns a curated skill set into one engineering workflow: a resumable pipeline, a fused skill set and optional per-repo enforcement.

## Language

**Skill command name**:
The name a skill is invoked by, which is the name of its link in the skills directory, not the `name` in its frontmatter.
_Avoid_: skill name, slug

**Source skills**:
The upstream skill collections the fused skill set is adapted from: mattpocock/skills and obra/superpowers.
_Avoid_: upstream, vendor

**Skills directory**:
The personal Claude Code skills directory, normally `~/.claude/skills`. Linking `plugin/` into it loads supermatt in place for development.
_Avoid_: skills folder, install dir

**Plugin**:
The supermatt Claude Code plugin in `plugin/`, installed from this repo's marketplace as `supermatt@supermatt`, or linked into the skills directory for development as `supermatt@skills-dir`.
_Avoid_: package, extension

**Fused skill set**:
The skills the plugin owns, invoked as `/supermatt:<name>`: adapted from the source skills, with overlapping upstream skills merged into one and cross-references rewritten to supermatt names.
_Avoid_: skill pack, bundle

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
