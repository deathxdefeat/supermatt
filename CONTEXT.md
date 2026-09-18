# supermatt

Tooling that checks the local Claude Code skill setup against what this repo says it should be.

## Language

**Skill spine**:
The curated set of skills installed from the source clones into the skills directory, each as a link.
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
