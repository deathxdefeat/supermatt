import json
import os
import subprocess
import sys
import tempfile
import unittest

CLI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugin", "bin", "supermatt")


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


class CliTest(unittest.TestCase):
    """Drives the supermatt command the way skills and hooks do: as a process in a git repo."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = os.path.realpath(tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        self.write("app.py", "x = 1\n")
        # The fake test suite passes while docs/PASS exists. docs/ is exempt, so toggling it
        # flips the suite without changing which code the hooks see as changed.
        self.write("docs/PASS", "")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")

    def write(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def fail_tests(self):
        os.remove(os.path.join(self.repo, "docs", "PASS"))

    def pass_tests(self):
        self.write("docs/PASS", "")

    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, CLI, *args], cwd=self.repo, input=stdin,
                              capture_output=True, text=True)

    def init(self, preset="standard"):
        out = self.run_cli("init", "--preset", preset, "--test-command", "test -f docs/PASS && echo ok || (echo FAILED; exit 1)")
        self.assertEqual(out.returncode, 0, out.stderr)

    def hook(self, event, **fields):
        fields.setdefault("cwd", self.repo)
        return self.run_cli("hook", event, stdin=json.dumps(fields))

    def state(self):
        with open(os.path.join(self.repo, ".supermatt", "state.json")) as f:
            return json.load(f)

    # ---- opting in ----

    def test_hooks_do_nothing_in_a_repo_without_config(self):
        self.fail_tests()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m x"})
        self.assertEqual((out.returncode, out.stdout, out.stderr), (0, "", ""))
        out = self.hook("stop")
        self.assertEqual((out.returncode, out.stdout), (0, ""))

    def test_init_writes_config_and_ignores_state(self):
        self.init("strict")
        status = json.loads(self.run_cli("status", "--json").stdout)
        self.assertTrue(status["configured"])
        self.assertEqual(set(status["config"]["enforce"].values()), {"block"})
        with open(os.path.join(self.repo, ".gitignore")) as f:
            self.assertIn(".supermatt/state.json", f.read().splitlines())
        self.assertEqual(self.run_cli("init").returncode, 1)

    def test_config_changes_options_and_rejects_bad_values(self):
        self.init()
        self.assertEqual(self.run_cli("config", "enforce.ticket_before_code", "block").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.pause_at", "grill,finish").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.ticket_agents", "true").returncode, 0)
        config = json.loads(self.run_cli("config").stdout)
        self.assertEqual(config["enforce"]["ticket_before_code"], "block")
        self.assertEqual(config["pipeline"]["pause_at"], ["grill", "finish"])
        self.assertIs(config["pipeline"]["ticket_agents"], True)
        self.assertEqual(config["pipeline"]["interview"], "full")
        for bad in (("enforce.ticket_before_code", "loud"), ("pipeline.pause_at", "lunch"),
                    ("pipeline.branch", "yes"), ("nope", "1")):
            self.assertEqual(self.run_cli("config", *bad).returncode, 1, bad)
        self.assertEqual(self.run_cli("config", "preset", "light").returncode, 0)
        self.assertEqual(set(json.loads(self.run_cli("config").stdout)["enforce"].values()), {"warn"})

    # ---- tests before commit ----

    def test_commit_is_blocked_when_tests_fail(self):
        self.init()
        self.fail_tests()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git add -A && git commit -m wip"})
        self.assertEqual(out.returncode, 2)
        self.assertIn("FAILED", out.stderr)

    def test_commit_passes_when_tests_pass_and_other_commands_are_ignored(self):
        self.init()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git -C . commit -m ok"})
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        self.fail_tests()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git log --oneline"})
        self.assertEqual((out.returncode, out.stdout), (0, ""))

    def test_warn_level_lets_a_red_commit_through_with_a_message(self):
        self.init("light")
        self.fail_tests()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m wip"})
        self.assertEqual(out.returncode, 0)
        self.assertIn("FAILED", json.loads(out.stdout)["systemMessage"])

    # ---- ticket before code ----

    def test_code_edits_need_a_ticket_in_progress(self):
        self.init("strict")
        edit = dict(tool_name="Edit", tool_input={"file_path": os.path.join(self.repo, "app.py")})
        self.assertEqual(self.hook("pre-tool", **edit).returncode, 2)
        for exempt in ("notes.md", ".scratch/f/spec.md", "docs/adr/0001.txt"):
            out = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": os.path.join(self.repo, exempt)})
            self.assertEqual(out.returncode, 0, exempt)
        out = self.hook("pre-tool", tool_name="Write", tool_input={"file_path": "/elsewhere/app.py"})
        self.assertEqual(out.returncode, 0)
        self.run_cli("start", "feat")
        self.run_cli("ticket", "01", "implementing")
        self.assertEqual(self.hook("pre-tool", **edit).returncode, 0)
        self.run_cli("ticket", "01", "needs-review")
        self.assertEqual(self.hook("pre-tool", **edit).returncode, 0)
        self.run_cli("ticket", "01", "done")
        self.assertEqual(self.hook("pre-tool", **edit).returncode, 2)

    # ---- review after ticket ----

    def test_next_ticket_waits_for_review_of_the_last(self):
        self.init("standard")
        self.run_cli("start", "feat")
        self.run_cli("ticket", "01", "implementing")
        self.assertEqual(self.run_cli("ticket", "01", "done").returncode, 1)
        self.run_cli("ticket", "01", "needs-review")
        out = self.run_cli("ticket", "02", "implementing")
        self.assertEqual(out.returncode, 1)
        self.assertIn("not reviewed", out.stderr)
        self.assertEqual(self.run_cli("ticket", "01", "done").returncode, 0)
        self.assertEqual(self.run_cli("ticket", "02", "implementing").returncode, 0)
        self.assertEqual(self.state()["ticket"], "02")

    def test_stop_is_blocked_while_a_ticket_awaits_review(self):
        self.init("standard")
        self.run_cli("start", "feat")
        self.run_cli("ticket", "01", "implementing")
        self.run_cli("ticket", "01", "needs-review")
        out = self.hook("stop")
        self.assertEqual(out.returncode, 2)
        self.assertIn("/supermatt:review", out.stderr)

    # ---- green before stop ----

    def test_stop_runs_tests_on_uncommitted_code_and_remembers_green(self):
        self.init("standard")
        self.assertEqual(self.hook("stop").returncode, 0)  # clean tree: nothing to verify
        self.write("app.py", "x = 2\n")
        self.fail_tests()
        out = self.hook("stop")
        self.assertEqual(out.returncode, 2)
        self.assertIn("FAILED", out.stderr)
        self.pass_tests()
        self.assertEqual(self.hook("stop").returncode, 0)
        green = self.state()["green"]
        self.assertTrue(green)
        # Same code again: the remembered green run is reused, so a now-red suite is not rerun.
        self.fail_tests()
        self.assertEqual(self.hook("stop").returncode, 0)
        # Changed code is checked afresh.
        self.write("app.py", "x = 3\n")
        self.assertEqual(self.hook("stop").returncode, 2)
        self.pass_tests()
        self.assertEqual(self.hook("stop").returncode, 0)
        green = self.state()["green"]
        self.write("notes.md", "exempt\n")
        self.assertEqual(self.state()["green"], green)

    def test_stop_gives_up_blocking_after_three_attempts(self):
        self.init("standard")
        self.write("app.py", "x = 2\n")
        self.fail_tests()
        for _ in range(3):
            self.assertEqual(self.hook("stop", stop_hook_active=True).returncode, 2)
        out = self.hook("stop", stop_hook_active=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn("stopped blocking", json.loads(out.stdout)["systemMessage"])

    # ---- session start ----

    def test_session_start_reports_a_feature_in_flight(self):
        self.init()
        self.assertEqual(self.hook("session-start").stdout, "")
        self.run_cli("start", "dark-mode")
        self.run_cli("stage", "implement")
        self.run_cli("ticket", "02", "implementing")
        context = json.loads(self.hook("session-start").stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("dark-mode", context)
        self.assertIn("implement", context)
        self.assertIn("02", context)


if __name__ == "__main__":
    unittest.main()
