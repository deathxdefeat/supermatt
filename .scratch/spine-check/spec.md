# Spec: spine-check

**Status:** ready-for-agent

## Problem Statement

The skill spine on this machine is a set of links in the skills directory, each pointing into one of two source clones (`mp` and `sp`). Nothing records which links should exist or where they should point, so a missing link, a link replaced by a real directory, a link pointing at the wrong clone or path, or a target without a `SKILL.md` goes unnoticed until a skill fails to load mid-session. Checking by hand means reading two dozen symlinks and comparing paths by eye.

## Solution

A read-only command in this repo, written in Python 3 with the standard library only, checks the installed skill spine against a spine manifest committed to the repo. The manifest lists every entry: its skill command name, its source clone (`mp` or `sp`) and its path inside that clone. For each entry the command prints one PASS or FAIL line with the reason, in manifest order, and exits non-zero if any entry fails. The skills directory and both clone roots can be overridden with flags, so tests run entirely against temporary directories and never touch the real `~/.claude`.

## User Stories

1. As the machine owner, I want one command that checks every spine skill, so that I can confirm the spine is intact after changing links or clones.
2. As the machine owner, I want the expected spine committed to the repo as a spine manifest, so that the intended state is versioned and reviewable rather than implied by whatever links exist.
3. As the machine owner, I want each entry to name the skill command name, source clone and path inside that clone, so that the manifest alone says exactly where each skill must come from.
4. As the machine owner, I want an entry to pass only when its link in the skills directory is a symlink, so that a real directory copied in place of a link is caught.
5. As the machine owner, I want an entry to pass only when the link's resolved target is the manifest path inside the named source clone, so that a link into the wrong clone or wrong skill is caught.
6. As the machine owner, I want an entry to pass only when the resolved target contains `SKILL.md`, so that a link to an empty or wrong directory is caught.
7. As the machine owner, I want a link that resolves correctly through a relative symlink to pass, so that only the resolved location matters, not how the link is spelled.
8. As the machine owner, I want a missing link reported as `missing`, so that I know to create it.
9. As the machine owner, I want a non-symlink at the link path reported as `not a symlink`, so that I know something replaced the link.
10. As the machine owner, I want a link whose target does not exist reported as a dangling symlink with its target, so that I can see where it was meant to point.
11. As the machine owner, I want a link that resolves elsewhere reported with both the resolved path and the expected path, so that I can see the mismatch in one line.
12. As the machine owner, I want a target without `SKILL.md` reported with the resolved path, so that I know which directory is incomplete.
13. As the machine owner, I want exactly one line per entry, starting with PASS or FAIL and the skill command name, so that the output is easy to scan and to grep.
14. As the machine owner, I want PASS lines to name the resolved target, so that a passing run still shows where each skill comes from.
15. As the machine owner, I want lines in manifest order, so that the output lines up with the manifest.
16. As the machine owner, I want exit status 0 when every entry passes and 1 when any entry fails, so that scripts and other agents can gate on the result.
17. As the machine owner, I want an unreadable or malformed spine manifest (invalid JSON, a missing field, or a source clone other than `mp` or `sp`) to print an error to stderr and exit 2 without per-skill lines, so that a broken manifest is not mistaken for a broken spine.
18. As the machine owner, I want to override the skills directory with a flag, so that I can check a different skills directory.
19. As the machine owner, I want to override each source clone root with its own flag, so that I can check against clones in other locations.
20. As the machine owner, I want defaults of `~/.claude/skills` for the skills directory and `~/skills-src/mp` and `~/skills-src/sp` for the clone roots, so that a bare run checks this machine's real spine.
21. As the machine owner, I want the command never to create, change or delete anything, so that running it is always safe.
22. As the machine owner, I want entries in the skills directory that the manifest does not list to be ignored, so that personal skills (such as the personal `handoff`) never cause failures.
23. As a maintainer, I want the manifest to list the 23 spine links by their link directory name (so Matt's handoff is listed as `mp-handoff`), so that the check matches the skill command names Claude Code actually uses.
24. As a maintainer, I want the tests to run with `python3 -m unittest` from the repo root, so that no test runner needs installing.
25. As a maintainer, I want every test to build its own skills directory and clone roots in temporary directories, so that the tests never read or write the real `~/.claude`.
26. As a maintainer, I want the command to use only the Python 3 standard library, so that it runs on any machine with Python 3 and nothing to install.

## Implementation Decisions

- One new standard-library Python module at the repo root implements the command; it is run directly with `python3`.
- The spine manifest is a JSON document committed at the repo root with a single top-level `skills` list. Each entry is an object with `name` (skill command name), `clone` (`mp` or `sp`) and `path` (relative to that clone's root). Shape: `{"skills": [{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}]}`.
- The manifest lists the 23 Phase 1 spine links: 20 from `mp` (17 under `skills/engineering/`; `grill-me`, `grilling` and `mp-handoff` -> `skills/productivity/handoff` under `skills/productivity/`) and 3 from `sp` under `skills/` (`using-git-worktrees`, `verification-before-completion`, `finishing-a-development-branch`).
- Flags: `--skills-dir` (default `~/.claude/skills`), `--mp-root` (default `~/skills-src/mp`), `--sp-root` (default `~/skills-src/sp`). `~` is expanded. There is no flag for the manifest location.
- The command's entry point is a `main(argv, manifest_path)` function returning the exit code, with `manifest_path` defaulting to the committed manifest. The script calls it and exits with its return value.
- Per-entry check, first failing rule wins:
  1. nothing at `<skills-dir>/<name>` (not even a broken link) -> `missing`
  2. the path exists but is not a symlink -> `not a symlink`
  3. the symlink's target does not exist -> `dangling symlink -> <link target>`
  4. `realpath` of the link differs from `realpath` of `<clone-root>/<path>` -> `wrong target: <resolved> (expected <expected>)`
  5. no `SKILL.md` file in the resolved directory -> `no SKILL.md in <resolved>`
  6. otherwise PASS with reason `-> <resolved>`
- Output line format: `PASS <name>: <reason>` or `FAIL <name>: <reason>`, one per entry, in manifest order, on stdout.
- Exit codes: 0 when all entries pass, 1 when any entry fails, 2 when the manifest cannot be read or is malformed (error on stderr, no per-skill lines).
- The command is read-only: no writes, no git calls, no network.
- There is no typechecker in this repo, and none is being added.

## Testing Decisions

- One seam: the command's `main(argv, manifest_path)` entry point, driven in-process with stdout and stderr captured. Tests assert only on the exit code and the printed lines, never on internal helpers.
- Each test builds a temporary skills directory and temporary `mp` and `sp` clone roots with `tempfile`, writes a small manifest into the temp area, and passes all three roots through the flags. No test touches the real `~/.claude` or `~/skills-src`.
- Cases: all-pass run (exit 0); each failure reason (missing, not a symlink, dangling symlink, wrong target including the wrong clone, no SKILL.md); a relative symlink that resolves correctly passes; unlisted entries in the skills directory are ignored; mixed pass and fail exits 1 with one line per entry in manifest order; malformed manifest (bad JSON, missing field, unknown clone) exits 2 with no per-skill lines.
- One test loads the committed spine manifest and checks it has 23 entries, each with a valid clone and a relative path, so the real manifest cannot silently rot.
- Tests run with `python3 -m unittest` from the repo root; the test package needs an `__init__.py` for discovery.
- Prior art: none. This is the first code in the repo.

## Out of Scope

- Checking git pins, branches or commits of the source clones.
- Checking the plugin registry (installed plugins, marketplaces, enabled state).
- Fixing, creating, changing or removing links, clones or anything else.
- Reporting skills in the skills directory that the manifest does not list.
- Validating duplicate names in the manifest.
- Adding a typechecker, linter or third-party dependency.

## Further Notes

- Skill command names come from the link's directory name, not the frontmatter `name`. Phase 1 found that Claude Code's command list shows Matt's handoff with the display name `handoff` while the invocable key is `mp-handoff`; the manifest keys on the directory name.
- The glossary terms used here (skill spine, spine manifest, entry, skill command name, source clone, skills directory) are defined in `CONTEXT.md`.
