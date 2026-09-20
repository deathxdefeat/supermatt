import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(ROOT, ".githooks", "leak_check.py")


class LeakCheckTest(unittest.TestCase):
    """The repo is public: the guard must pass on what is tracked and refuse private material."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = tmp.name
        self.patterns = os.path.join(tmp.name, "..private")
        self.env = dict(os.environ, SUPERMATT_PRIVATE_PATTERNS=self.patterns)
        for args in (["init", "-q"], ["config", "user.email", "1+t@users.noreply.github.com"], ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def staged(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        subprocess.run(["git", "add", "-f", rel], cwd=self.repo, check=True)
        out = subprocess.run([sys.executable, CHECK, "staged"], cwd=self.repo, capture_output=True, text=True, env=self.env)
        subprocess.run(["git", "rm", "-qf", "--cached", rel], cwd=self.repo, check=True)
        return out

    def test_tracked_files_are_clean(self):
        out = subprocess.run([sys.executable, CHECK, "tree"], cwd=ROOT, capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_private_material_is_refused(self):
        self.assertEqual(self.staged("src/ok.py", "x = 1  # see ~/.claude/skills\n").returncode, 0)
        cases = {
            "src/a.py": "ROOT = '/" + "Users/someone/work'\n",
            "src/b.py": "contact = 'someone@" + "corp.io'\n",
            "src/c.py": "key = 'sk-" + "ant-abcdefgh12345678'\n",
            "src/d.py": "api_key = '" + "a1b2c3d4e5f6g7h8i9'\n",
            ".scratch/feat/spec.md": "harmless\n",
            ".claude/settings.local.json": "{}\n",
            "notes/.env.local": "A=1\n",
        }
        for rel, text in cases.items():
            self.assertEqual(self.staged(rel, text).returncode, 1, rel)

    def test_private_words_come_from_outside_the_repo_and_are_not_echoed(self):
        with open(self.patterns, "w") as f:
            f.write("# comment\nacme\\s+corp\n")
        out = self.staged("src/e.py", "client = 'Acme Corp'\n")
        self.assertEqual(out.returncode, 1)
        self.assertNotIn("Acme", out.stderr)

    def test_a_personal_commit_email_is_refused(self):
        subprocess.run(["git", "config", "user.email", "me@" + "personal.dev"], cwd=self.repo, check=True)
        self.assertEqual(self.staged("src/ok.py", "x = 1\n").returncode, 1)
