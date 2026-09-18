import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import spine_check


# The 23 spine links installed in Phase 1: (skill command name, source clone, path in clone).
SPINE = [
    (name, "mp", "skills/engineering/" + name)
    for name in (
        "setup-matt-pocock-skills", "wayfinder", "domain-modeling", "research", "prototype",
        "to-spec", "to-tickets", "codebase-design", "implement", "tdd", "diagnosing-bugs",
        "resolving-merge-conflicts", "code-review", "triage", "improve-codebase-architecture",
        "ask-matt", "grill-with-docs",
    )
] + [
    ("grill-me", "mp", "skills/productivity/grill-me"),
    ("mp-handoff", "mp", "skills/productivity/handoff"),
    ("grilling", "mp", "skills/productivity/grilling"),
    ("using-git-worktrees", "sp", "skills/using-git-worktrees"),
    ("verification-before-completion", "sp", "skills/verification-before-completion"),
    ("finishing-a-development-branch", "sp", "skills/finishing-a-development-branch"),
]


class SpineCheckTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = tmp.name
        self.skills = os.path.join(self.root, "skills")
        self.mp = os.path.join(self.root, "mp")
        self.sp = os.path.join(self.root, "sp")
        for d in (self.skills, self.mp, self.sp):
            os.makedirs(d)
        self.manifest = os.path.join(self.root, "manifest.json")

    def make_skill(self, clone_root, path, skill_md=True):
        target = os.path.join(clone_root, path)
        os.makedirs(target, exist_ok=True)
        if skill_md:
            with open(os.path.join(target, "SKILL.md"), "w") as f:
                f.write("---\nname: x\n---\n")
        return target

    def link(self, name, target):
        os.symlink(target, os.path.join(self.skills, name))

    def write_manifest(self, entries):
        with open(self.manifest, "w") as f:
            json.dump({"skills": entries}, f)

    def run_check(self, **kwargs):
        kwargs.setdefault("manifest_path", self.manifest)
        out, err = io.StringIO(), io.StringIO()
        argv = ["--skills-dir", self.skills, "--mp-root", self.mp, "--sp-root", self.sp]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = spine_check.main(argv, **kwargs)
        return code, out.getvalue().splitlines(), err.getvalue()

    def test_correctly_linked_skill_passes_and_exits_zero(self):
        target = self.make_skill(self.mp, "skills/engineering/tdd")
        self.link("tdd", target)
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, err = self.run_check()

        self.assertEqual(code, 0)
        self.assertEqual(lines, ["PASS tdd: -> " + os.path.realpath(target)])
        self.assertEqual(err, "")


    def test_missing_link_fails_and_exits_one(self):
        self.make_skill(self.mp, "skills/engineering/tdd")
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual(lines, ["FAIL tdd: missing"])

    def test_real_directory_in_place_of_link_fails_as_not_a_symlink(self):
        self.make_skill(self.skills, "tdd")
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual(lines, ["FAIL tdd: not a symlink"])

    def test_dangling_link_fails_and_names_its_target(self):
        gone = os.path.join(self.mp, "skills/engineering/tdd")
        self.link("tdd", gone)
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual(lines, ["FAIL tdd: dangling symlink -> " + gone])

    def test_link_into_the_wrong_clone_fails_with_both_paths(self):
        expected = self.make_skill(self.mp, "skills/engineering/tdd")
        wrong = self.make_skill(self.sp, "skills/engineering/tdd")
        self.link("tdd", wrong)
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual(
            lines,
            ["FAIL tdd: wrong target: %s (expected %s)"
             % (os.path.realpath(wrong), os.path.realpath(expected))],
        )

    def test_target_without_skill_md_fails(self):
        target = self.make_skill(self.mp, "skills/engineering/tdd", skill_md=False)
        self.link("tdd", target)
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual(lines, ["FAIL tdd: no SKILL.md in " + os.path.realpath(target)])

    def test_relative_symlink_that_resolves_to_the_expected_path_passes(self):
        target = self.make_skill(self.mp, "skills/engineering/tdd")
        self.link("tdd", os.path.relpath(target, self.skills))
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 0)
        self.assertEqual(lines, ["PASS tdd: -> " + os.path.realpath(target)])

    def test_mixed_results_print_one_line_per_entry_in_manifest_order(self):
        self.link("to-spec", self.make_skill(self.mp, "skills/engineering/to-spec"))
        self.link("using-git-worktrees", self.make_skill(self.sp, "skills/using-git-worktrees"))
        self.write_manifest([
            {"name": "to-spec", "clone": "mp", "path": "skills/engineering/to-spec"},
            {"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"},
            {"name": "using-git-worktrees", "clone": "sp", "path": "skills/using-git-worktrees"},
        ])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 1)
        self.assertEqual([line.split(":")[0] for line in lines],
                         ["PASS to-spec", "FAIL tdd", "PASS using-git-worktrees"])

    def test_skills_not_in_the_manifest_are_ignored(self):
        self.link("tdd", self.make_skill(self.mp, "skills/engineering/tdd"))
        self.make_skill(self.skills, "personal-skill")
        os.symlink(os.path.join(self.root, "nowhere"), os.path.join(self.skills, "handoff"))
        self.write_manifest([{"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"}])

        code, lines, _ = self.run_check()

        self.assertEqual(code, 0)
        self.assertEqual(len(lines), 1)

    def assert_manifest_error(self):
        code, lines, err = self.run_check()
        self.assertEqual(code, 2)
        self.assertEqual(lines, [])
        self.assertNotEqual(err, "")

    def test_invalid_json_manifest_exits_two_without_skill_lines(self):
        with open(self.manifest, "w") as f:
            f.write("{not json")
        self.assert_manifest_error()

    def test_entry_missing_a_field_exits_two_without_skill_lines(self):
        self.link("tdd", self.make_skill(self.mp, "skills/engineering/tdd"))
        self.write_manifest([
            {"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"},
            {"name": "to-spec", "clone": "mp"},
        ])
        self.assert_manifest_error()

    def test_unknown_clone_exits_two_without_skill_lines(self):
        self.link("tdd", self.make_skill(self.mp, "skills/engineering/tdd"))
        self.write_manifest([
            {"name": "tdd", "clone": "mp", "path": "skills/engineering/tdd"},
            {"name": "brainstorming", "clone": "superpowers", "path": "skills/brainstorming"},
        ])
        self.assert_manifest_error()

    def test_committed_manifest_passes_against_a_complete_spine(self):
        roots = {"mp": self.mp, "sp": self.sp}
        for name, clone, path in SPINE:
            self.link(name, self.make_skill(roots[clone], path))

        code, lines, err = self.run_check(manifest_path=spine_check.MANIFEST)

        self.assertEqual((code, err), (0, ""))
        self.assertEqual(sorted(line.split(":")[0] for line in lines),
                         sorted("PASS " + name for name, _, _ in SPINE))

    def test_without_flags_it_checks_the_default_locations_under_home(self):
        home = os.path.join(self.root, "home")
        skills = os.path.join(home, ".claude", "skills")
        os.makedirs(skills)
        target = self.make_skill(os.path.join(home, "skills-src", "sp"), "skills/using-git-worktrees")
        os.symlink(target, os.path.join(skills, "using-git-worktrees"))
        self.write_manifest([{"name": "using-git-worktrees", "clone": "sp", "path": "skills/using-git-worktrees"}])

        out = io.StringIO()
        with mock.patch.dict(os.environ, {"HOME": home}), contextlib.redirect_stdout(out):
            code = spine_check.main([], manifest_path=self.manifest)

        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "PASS using-git-worktrees: -> %s\n" % os.path.realpath(target))

    def test_committed_manifest_has_23_entries_with_valid_clones_and_relative_paths(self):
        with open(spine_check.MANIFEST) as f:
            entries = json.load(f)["skills"]

        self.assertEqual(len(entries), 23)
        for entry in entries:
            self.assertIn(entry["clone"], ("mp", "sp"), entry)
            self.assertFalse(os.path.isabs(entry["path"]), entry)

if __name__ == "__main__":
    unittest.main()
