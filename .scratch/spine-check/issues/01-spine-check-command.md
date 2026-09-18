# 01: spine-check command with the committed spine manifest

**What to build:** A read-only, standard-library Python 3 command that reads the committed spine manifest and checks each entry against the skills directory and the `mp` and `sp` source clones, printing one PASS or FAIL line per entry with the reason and exiting non-zero if any entry fails. The committed spine manifest lists the 23 spine links from Phase 1. The skills directory and both clone roots can be overridden with flags so the whole behaviour is tested against temporary directories. See the spec at `.scratch/spine-check/spec.md`.

**Blocked by:** None (can start immediately)

**Status:** resolved

- [x] The spine manifest is committed as JSON with a top-level `skills` list; each entry has `name`, `clone` (`mp` or `sp`) and `path` relative to that clone's root.
- [x] The committed manifest lists exactly the 23 spine links, keyed by link directory name (Matt's handoff as `mp-handoff`), and no personal skills.
- [x] An entry passes only when its link in the skills directory is a symlink, its resolved target equals the resolved manifest path inside the named source clone, and that directory contains `SKILL.md`; a relative symlink that resolves correctly passes.
- [x] Failures report, first failing rule winning: `missing`, `not a symlink`, `dangling symlink -> <target>`, `wrong target: <resolved> (expected <expected>)`, `no SKILL.md in <resolved>`.
- [x] Output is one `PASS <name>: <reason>` or `FAIL <name>: <reason>` line per entry, in manifest order; PASS reasons name the resolved target.
- [x] Exit code is 0 when every entry passes and 1 when any entry fails.
- [x] An unreadable or malformed manifest (invalid JSON, missing field, clone other than `mp`/`sp`) prints an error to stderr and exits 2 with no per-skill lines.
- [x] `--skills-dir`, `--mp-root` and `--sp-root` override the defaults `~/.claude/skills`, `~/skills-src/mp` and `~/skills-src/sp`.
- [x] Entries in the skills directory that the manifest does not list are ignored.
- [x] The command never writes anything, and uses only the Python 3 standard library.
- [x] Tests run with `python3 -m unittest` from the repo root, build every skills directory and clone root in temporary directories, and never touch the real `~/.claude`.

## Comments

- Resolved. Merged to `main` in 7f02a10 (Merge branch 'spine-check'; implementation 95c8cc0, review fix c8c3fce).
- Tests: `python3 -m unittest` on merged `main`: Ran 15 tests, OK.
- All 11 criteria verified: by the 15 tests; an unreadable (nonexistent) manifest probe returned exit 2 with a stderr error; read-only and standard-library-only by inspection (imports are argparse, json, os, sys; the only `open` is the manifest read).
- Review follow-ups not in scope for this ticket: absolute manifest paths are accepted, argparse usage errors also exit 2, permission errors read as `missing`, an empty `name` passes validation.
