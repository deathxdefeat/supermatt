#!/usr/bin/env python3
"""Check the installed skill spine against the committed spine manifest. Read-only."""
import argparse
import json
import os
import sys

CLONES = ("mp", "sp")
MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spine-manifest.json")


def main(argv=None, manifest_path=MANIFEST):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", default="~/.claude/skills")
    parser.add_argument("--mp-root", default="~/skills-src/mp")
    parser.add_argument("--sp-root", default="~/skills-src/sp")
    args = parser.parse_args(argv)
    roots = {"mp": os.path.expanduser(args.mp_root), "sp": os.path.expanduser(args.sp_root)}
    skills_dir = os.path.expanduser(args.skills_dir)

    try:
        entries = load_manifest(manifest_path)
    except ManifestError as e:
        print(f"spine-check: bad manifest {manifest_path}: {e}", file=sys.stderr)
        return 2

    failed = False
    for entry in entries:
        ok, reason = check_entry(entry, skills_dir, roots)
        failed = failed or not ok
        print(f"{'PASS' if ok else 'FAIL'} {entry['name']}: {reason}")
    return 1 if failed else 0


class ManifestError(Exception):
    pass


def load_manifest(path):
    try:
        with open(path) as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise ManifestError(e)
    entries = data.get("skills") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        raise ManifestError('expected an object with a "skills" list')
    for i, entry in enumerate(entries):
        for field in ("name", "clone", "path"):
            if not isinstance(entry, dict) or not isinstance(entry.get(field), str):
                raise ManifestError(f'entry {i}: missing string field "{field}"')
        if entry["clone"] not in CLONES:
            raise ManifestError(f'entry {i}: clone must be one of {", ".join(CLONES)}')
    return entries


def check_entry(entry, skills_dir, roots):
    """Return (passed, reason) for one manifest entry."""
    link = os.path.join(skills_dir, entry["name"])
    if not os.path.lexists(link):
        return False, "missing"
    if not os.path.islink(link):
        return False, "not a symlink"
    if not os.path.exists(link):
        return False, "dangling symlink -> " + os.readlink(link)
    resolved = os.path.realpath(link)
    expected = os.path.realpath(os.path.join(roots[entry["clone"]], entry["path"]))
    if resolved != expected:
        return False, f"wrong target: {resolved} (expected {expected})"
    if not os.path.isfile(os.path.join(resolved, "SKILL.md")):
        return False, "no SKILL.md in " + resolved
    return True, "-> " + resolved


if __name__ == "__main__":
    sys.exit(main())
