"""Structural checks that keep the plugin's skills and docs from rotting."""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin")
SKILLS = os.path.join(PLUGIN, "skills")
SKILL_NAMES = sorted(d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d)))
# Names the skills were imported under; none should survive as an invocable reference.
UPSTREAM = ("setup-matt-pocock-skills", "grill-with-docs", "grill-me", "domain-modeling",
            "to-spec", "to-tickets", "tdd", "code-review", "verification-before-completion",
            "finishing-a-development-branch", "using-git-worktrees", "diagnosing-bugs",
            "resolving-merge-conflicts", "improve-codebase-architecture", "codebase-design",
            "ask-matt", "mp-handoff")


def skill_files():
    for dirpath, _, files in os.walk(SKILLS):
        for name in files:
            if name.endswith(".md"):
                yield os.path.join(dirpath, name)


def frontmatter(path):
    text = open(path).read()
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    fields = {}
    for line in (match.group(1).splitlines() if match else []):
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


class PluginLayoutTest(unittest.TestCase):
    def test_every_skill_has_a_named_and_described_entry_point(self):
        self.assertGreater(len(SKILL_NAMES), 0)
        for name in SKILL_NAMES:
            fields = frontmatter(os.path.join(SKILLS, name, "SKILL.md"))
            self.assertEqual(fields.get("name"), name)
            self.assertTrue(20 < len(fields.get("description", "")) <= 1024, name)

    def test_relative_links_resolve(self):
        for path in skill_files():
            prose = re.sub(r"^(```|~~~).*?^\1", "", open(path).read(), flags=re.S | re.M)  # templates are examples
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", prose):
                if "://" in target:
                    continue
                with self.subTest(file=os.path.relpath(path, ROOT), link=target):
                    self.assertTrue(os.path.exists(os.path.join(os.path.dirname(path), target)))

    def test_skill_references_name_real_skills(self):
        docs = list(skill_files()) + [os.path.join(ROOT, "README.md")]
        for path in docs:
            for ref in set(re.findall(r"supermatt:([a-z-]+)", open(path).read())):
                with self.subTest(file=os.path.relpath(path, ROOT), ref=ref):
                    self.assertIn(ref, SKILL_NAMES)

    def test_no_upstream_skill_names_are_invoked(self):
        pattern = re.compile(r"(/|Skill tool with \"|`)(" + "|".join(map(re.escape, UPSTREAM)) + r")\b")
        for path in skill_files():
            for line_no, line in enumerate(open(path), 1):
                with self.subTest(file=os.path.relpath(path, ROOT), line=line_no):
                    self.assertIsNone(pattern.search(line), line.strip())

    def test_hooks_point_at_the_bundled_command(self):
        cli = os.path.join(PLUGIN, "bin", "supermatt")
        self.assertTrue(os.access(cli, os.X_OK))
        hooks = json.load(open(os.path.join(PLUGIN, "hooks", "hooks.json")))["hooks"]
        commands = [h["command"] for groups in hooks.values() for g in groups for h in g["hooks"]]
        self.assertTrue(commands)
        for command in commands:
            self.assertIn('"${CLAUDE_PLUGIN_ROOT}/bin/supermatt" hook ', command)

    def test_marketplace_lists_the_plugin(self):
        market = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))
        manifest = json.load(open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))
        entry = next(p for p in market["plugins"] if p["name"] == manifest["name"])
        self.assertEqual(os.path.realpath(os.path.join(ROOT, entry["source"])), PLUGIN)

    def test_readme_lists_every_skill(self):
        readme = open(os.path.join(ROOT, "README.md")).read()
        for name in SKILL_NAMES:
            with self.subTest(skill=name):
                self.assertIn(f"/supermatt:{name}", readme)


if __name__ == "__main__":
    unittest.main()
