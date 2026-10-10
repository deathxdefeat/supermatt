import json
import os
import shlex
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
        self.repo = os.path.realpath(os.path.join(tmp.name, "repo"))
        os.makedirs(self.repo)
        # Trust is per machine; keep it in the temp dir so tests never touch the real one.
        self.env = dict(os.environ, SUPERMATT_TRUST_FILE=os.path.join(tmp.name, "trusted.json"))
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "t@example.com")
        git(self.repo, "config", "user.name", "t")
        self.write("app.py", "x = 1\n")
        # The fake test suite passes while a flag outside the repo exists, so tests can flip it without
        # changing any file the hooks fingerprint. It also needs docs/PASS in the tree it runs in.
        self.flag = os.path.join(tmp.name, "PASS")
        open(self.flag, "w").close()
        self.suite = f"test -f docs/PASS && test -f {shlex.quote(self.flag)}"
        self.write("docs/PASS", "")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "init")

    def write(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def fail_tests(self):
        os.remove(self.flag)

    def pass_tests(self):
        open(self.flag, "w").close()

    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, CLI, *args], cwd=self.repo, input=stdin,
                              capture_output=True, text=True, env=self.env)

    def init(self, preset="standard"):
        out = self.run_cli("init", "--preset", preset, "--test-command", f"{self.suite} && echo ok || (echo FAILED; exit 1)")
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

    # ---- trust ----

    def test_a_config_this_machine_did_not_write_is_inert_until_trusted(self):
        self.init("strict")
        self.fail_tests()
        commit = dict(tool_name="Bash", tool_input={"command": "git commit -m x"})
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)
        # A pull that changes the config (here: a new test command) revokes trust.
        path = os.path.join(self.repo, ".supermatt", "config.json")
        with open(path) as f:
            config = json.load(f)
        config["test_command"] = "echo pwned > docs/PWNED; exit 1"
        with open(path, "w") as f:
            json.dump(config, f)
        out = self.hook("pre-tool", **commit)
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        self.write("app.py", "x = 2\n")
        self.assertEqual(self.hook("stop").returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "docs", "PWNED")))
        notice = json.loads(self.hook("session-start").stdout)
        self.assertIn("supermatt trust", notice["systemMessage"])
        self.assertIn("echo pwned", notice["systemMessage"])
        self.assertIn("NOT TRUSTED", self.run_cli("status").stdout)
        # Changing one option must not quietly approve the rest of an untrusted config.
        self.run_cli("config", "pipeline.branch", "false")
        self.assertEqual(self.hook("pre-tool", **commit).stdout, "")
        self.assertFalse(os.path.exists(os.path.join(self.repo, "docs", "PWNED")))
        self.assertEqual(self.run_cli("trust").returncode, 0)
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "docs", "PWNED")))

    def test_a_broken_config_turns_hooks_off_and_says_why(self):
        self.init()
        path = os.path.join(self.repo, ".supermatt", "config.json")
        with open(path, "w") as f:
            json.dump({"enforce": {"tests_before_commit": "blok"}, "test_timeout": "soon"}, f)
        self.run_cli("trust")  # refused: trust needs a valid config
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m x"})
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        message = json.loads(self.hook("session-start").stdout)["systemMessage"]
        self.assertIn("tests_before_commit", message)
        self.assertIn("test_timeout", message)
        self.assertEqual(self.run_cli("status").returncode, 1)

    def test_hooks_survive_garbage_input(self):
        self.init()
        for stdin in ("not json", "[]", json.dumps({"tool_name": "Bash", "tool_input": "x", "cwd": self.repo})):
            out = self.run_cli("hook", "pre-tool", stdin=stdin)
            self.assertEqual(out.returncode, 0, stdin)

    def test_config_changes_options_and_rejects_bad_values(self):
        self.init()
        self.assertEqual(self.run_cli("config", "enforce.ticket_before_code", "block").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.pause_at", "grill,finish").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.ticket_agents", "true").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.finish", "push").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.branch_prefix", "claude/").returncode, 0)
        self.assertEqual(self.run_cli("config", "pipeline.branch_prefix", "bad prefix").returncode, 1)
        config = json.loads(self.run_cli("config").stdout)
        self.assertEqual(config["enforce"]["ticket_before_code"], "block")
        self.assertEqual(config["pipeline"]["pause_at"], ["grill", "finish"])
        self.assertIs(config["pipeline"]["ticket_agents"], True)
        self.assertEqual(config["pipeline"]["interview"], "full")
        for bad in (("enforce.ticket_before_code", "loud"), ("pipeline.pause_at", "lunch"),
                    ("pipeline.branch", "yes"), ("nope", "1"), ("test_timeout", "900"), ("test_timeout", "0")):
            self.assertEqual(self.run_cli("config", *bad).returncode, 1, bad)
        self.assertEqual(self.run_cli("config", "test_timeout", "570").returncode, 0)
        self.assertEqual(self.run_cli("status").returncode, 0)
        self.assertEqual(self.run_cli("config", "preset", "light").returncode, 0)
        self.assertEqual(set(json.loads(self.run_cli("config").stdout)["enforce"].values()), {"warn"})

    def test_solo_preset_and_review_agents_option(self):
        self.init("solo")
        config = json.loads(self.run_cli("config").stdout)
        self.assertEqual(config["enforce"], {"tests_before_commit": "block", "ticket_before_code": "off",
                                             "review_after_ticket": "warn", "green_before_stop": "off"})
        self.assertFalse(config["pipeline"]["review_agents"])
        self.assertEqual(self.run_cli("config", "pipeline.review_agents", "true").returncode, 0)
        self.assertIn("review_agents=true", self.run_cli("status").stdout)

    # ---- tests before commit ----

    def test_commit_is_blocked_when_tests_fail(self):
        self.init()
        self.fail_tests()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git add -A && git commit -m wip"})
        self.assertEqual(out.returncode, 2)
        self.assertIn("FAILED", out.stderr)

    def test_a_failing_turbo_run_reports_only_the_failing_task_and_its_first_error(self):
        noise = "".join(f"@acme/db:test: noisy line {i}\\n" for i in range(60))
        report = (
            noise
            + "@acme/api:typecheck: src/a.ts(3,1): error TS2339: no property n\\n"
            + "@acme/api:typecheck: [ELIFECYCLE] Command failed with exit code 2.\\n"
            + "\\n Tasks:    1 successful, 2 total\\nFailed:    @acme/api#typecheck\\n"
        )
        self.write("suite.sh", f"printf '{report}'\nexit 1\n")
        out = self.run_cli("init", "--test-command", "sh suite.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m wip"})
        self.assertEqual(out.returncode, 2)
        self.assertIn("failing: @acme/api#typecheck", out.stderr)
        self.assertIn("error TS2339: no property n", out.stderr)
        self.assertNotIn("noisy line", out.stderr)
        self.assertNotIn("ELIFECYCLE", out.stderr)

    def test_a_turbo_run_without_log_prefixes_falls_back_to_the_tail(self):
        report = "src/a.ts(3,1): error TS2339: no property n\\n\\nFailed:    @acme/api#typecheck\\n"
        self.write("suite.sh", f"printf '{report}'\nexit 1\n")
        out = self.run_cli("init", "--test-command", "sh suite.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m wip"})
        self.assertEqual(out.returncode, 2)
        self.assertIn("error TS2339: no property n", out.stderr)

    def test_comma_separated_turbo_failures_are_each_reported(self):
        report = (
            "@acme/api:test: AssertionError: expected 1 to be 2\\n"
            "@acme/web:lint: error no-unused-vars\\n"
            + "".join(f"@acme/db:test: noisy line {i}\\n" for i in range(40))
            + "\\nFailed:    @acme/api#test, @acme/web#lint\\n"
        )
        self.write("suite.sh", f"printf '{report}'\nexit 1\n")
        out = self.run_cli("init", "--test-command", "sh suite.sh")
        self.assertEqual(out.returncode, 0, out.stderr)
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -m wip"})
        self.assertIn("failing: @acme/api#test, @acme/web#lint", out.stderr)
        self.assertIn("expected 1 to be 2", out.stderr)
        self.assertIn("error no-unused-vars", out.stderr)
        self.assertNotIn("noisy line", out.stderr)

    def test_commit_passes_when_tests_pass_and_other_commands_are_ignored(self):
        self.init()
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git -C . commit -m ok"})
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        self.fail_tests()
        for command in ("git log --oneline", "git commit-tree HEAD^{tree}", "echo commit"):
            out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": command})
            self.assertEqual((out.returncode, out.stdout), (0, ""), command)
        self.write("app.py", "x = 2\n")
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "cd sub && git -c a=b commit --amend"})
        self.assertEqual(out.returncode, 2)

    def test_a_tree_that_already_passed_is_not_tested_again(self):
        self.init()
        self.write("app.py", "x = 2\n")
        out = self.run_cli("test")
        self.assertEqual(out.returncode, 0)
        self.assertIn("ok", out.stdout)
        self.fail_tests()  # would fail if rerun
        commit = dict(tool_name="Bash", tool_input={"command": "git commit -am x"})
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 0)
        git(self.repo, "commit", "-qam", "x")
        # The same files, now committed: still green for the commit hook, the stop hook and `test`.
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 0)
        self.assertEqual(self.hook("stop").returncode, 0)
        self.assertIn("not rerun", self.run_cli("test").stdout)
        self.assertEqual(self.run_cli("test", "--force").returncode, 1)
        self.write("app.py", "x = 3\n")
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)

    def test_a_pass_covers_exempt_files_and_the_test_command_too(self):
        # Exempt files are not code, but a test can still read them.
        self.init()
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "opt in")
        self.assertEqual(self.run_cli("test").returncode, 0)
        self.fail_tests()  # would fail if rerun
        commit = dict(tool_name="Bash", tool_input={"command": "git commit -am docs"})
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 0)
        self.write("README.md", "changed\n")
        self.assertEqual(self.hook("stop").returncode, 0)  # no uncommitted code: the end-of-turn rule waits
        out = self.hook("pre-tool", **commit)
        self.assertEqual(out.returncode, 2)
        self.assertIn("FAILED", out.stderr)
        # A new test command is a new suite: an old pass does not vouch for it.
        self.write("README.md", "")
        self.pass_tests()
        self.assertEqual(self.run_cli("test").returncode, 0)
        self.run_cli("config", "test_command", "echo FAILED; exit 1")
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)

    def test_a_new_test_command_runs_even_when_git_cannot_see_the_config(self):
        self.init()
        self.write(".gitignore", ".supermatt/\n")
        self.assertEqual(self.run_cli("test").returncode, 0)
        self.run_cli("config", "test_command", "echo FAILED; exit 1")
        out = self.hook("pre-tool", tool_name="Bash", tool_input={"command": "git commit -am x"})
        self.assertEqual(out.returncode, 2)

    def test_a_pass_covers_executable_bits_and_nested_repositories(self):
        self.init()
        self.write("run.sh", "#!/bin/sh\ngrep -q ok vendor/STATUS\n")
        os.chmod(os.path.join(self.repo, "run.sh"), 0o755)
        os.makedirs(os.path.join(self.repo, "vendor"))
        git(os.path.join(self.repo, "vendor"), "init", "-q")
        self.write("vendor/STATUS", "ok\n")
        self.run_cli("config", "test_command", "./run.sh")
        self.assertEqual(self.run_cli("test").returncode, 0)
        commit = dict(tool_name="Bash", tool_input={"command": "git commit -am x"})
        self.write("vendor/STATUS", "bad\n")  # git reports only `vendor/`
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)
        self.write("vendor/STATUS", "ok\n")
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 0)  # the files that passed, not rerun
        os.chmod(os.path.join(self.repo, "run.sh"), 0o644)
        self.assertEqual(self.hook("pre-tool", **commit).returncode, 2)

    def test_a_pass_covers_what_a_submodule_points_at(self):
        self.init()
        sub = os.path.join(os.path.dirname(self.repo), "sub")
        os.makedirs(sub)
        git(sub, "init", "-q")
        with open(os.path.join(sub, "STATUS"), "w") as f:
            f.write("ok\n")
        git(sub, "add", "-A")
        git(sub, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "ok")
        git(self.repo, "-c", "protocol.file.allow=always", "submodule", "add", "-q", sub, "lib")
        git(self.repo, "commit", "-qm", "lib")
        self.run_cli("config", "test_command", "grep -q ok lib/STATUS")
        lib = os.path.join(self.repo, "lib")
        commit = dict(tool_name="Bash", tool_input={"command": "git commit -am x"})
        for text, verdict in (("ok, moved\n", 0), ("bad\n", 2)):  # the pointer moves, then moves again
            self.write("lib/STATUS", text)
            git(lib, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qam", text)
            self.assertEqual(self.hook("pre-tool", **commit).returncode, verdict, text)

    def test_the_test_command_needs_a_trusted_config(self):
        self.init()
        self.write(".supermatt/config.json", json.dumps({"test_command": "touch pwned"}))
        self.assertEqual(self.run_cli("test").returncode, 1)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "pwned")))

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

    def test_files_left_by_the_test_run_do_not_force_a_rerun(self):
        self.init()
        self.run_cli("config", "test_command", f"touch .coverage && {self.suite}")
        self.write("app.py", "x = 2\n")
        self.assertEqual(self.hook("stop").returncode, 0)
        self.fail_tests()  # would fail if rerun
        self.assertEqual(self.hook("stop").returncode, 0)

    def test_ticket_ids_are_checked(self):
        self.init()
        self.run_cli("start", "feat")
        self.assertEqual(self.run_cli("ticket", "GH-12", "implementing").returncode, 0)
        self.assertEqual(self.run_cli("ticket", "../x", "implementing").returncode, 1)

    def test_red_work_mid_ticket_and_questions_to_the_user_can_end_a_turn(self):
        self.init("strict")
        self.run_cli("ticket", "01", "implementing")  # no feature needed for ad-hoc work
        self.write("app.py", "x = 2\n")
        self.fail_tests()
        self.assertEqual(self.hook("stop").returncode, 0)  # red is expected mid-ticket
        self.run_cli("ticket", "01", "needs-review")
        self.assertEqual(self.hook("stop").returncode, 2)
        self.run_cli("ticket", "01", "blocked")  # asking the user something
        self.assertEqual(self.hook("stop").returncode, 0)
        self.assertEqual(self.run_cli("ticket", "01", "done").returncode, 1)  # still needs its review

    def test_a_feature_can_start_at_a_later_stage(self):
        self.init()
        self.assertEqual(self.run_cli("start", "polish", "--stage", "spec").returncode, 0)
        self.assertEqual((self.state()["feature"], self.state()["stage"]), ("polish", "spec"))
        self.assertEqual(self.run_cli("start", "polish", "--stage", "done").returncode, 2)  # argparse refuses
        self.run_cli("start", "other")
        self.assertEqual(self.state()["stage"], "grill")

    def test_pause_at_none_and_base_branch(self):
        self.init()
        self.assertEqual(self.run_cli("config", "pipeline.pause_at", "none").returncode, 0)
        self.assertEqual(json.loads(self.run_cli("config", "pipeline.pause_at").stdout), [])
        self.assertEqual(self.run_cli("base", "main").returncode, 1)  # needs a feature
        self.run_cli("start", "feat")
        self.run_cli("base", "main")
        self.assertEqual(self.state()["base"], "main")

    def test_stop_gives_up_blocking_after_three_attempts(self):
        self.init("standard")
        self.write("app.py", "x = 2\n")
        self.fail_tests()
        for attempt in range(3):
            self.write("app.py", f"x = {attempt + 2}\n")
            self.assertEqual(self.hook("stop", stop_hook_active=True).returncode, 2)
        self.write("app.py", "x = 9\n")
        out = self.hook("stop", stop_hook_active=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn("stopped blocking", json.loads(out.stdout)["systemMessage"])

    def test_stop_does_not_block_twice_on_the_same_red_files(self):
        self.init("standard")
        self.write(".gitignore", "")  # supermatt's own state file, rewritten by every hook, is not a change
        self.write("app.py", "x = 2\n")
        self.fail_tests()
        self.assertEqual(self.hook("stop").returncode, 2)
        out = self.hook("stop", stop_hook_active=True)  # nothing changed: blocking again would only loop
        self.assertEqual(out.returncode, 0)
        self.assertIn("still fail", json.loads(out.stdout)["systemMessage"])
        self.assertEqual(self.state()["stop_blocks"], 0)

    # ---- worktrees ----

    def test_a_linked_worktree_shares_state_and_trust_with_the_main_tree(self):
        self.init("strict")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "opt in")
        self.run_cli("start", "feat")
        tree = os.path.join(os.path.dirname(self.repo), "tree")
        git(self.repo, "worktree", "add", "-q", "-b", "feat", tree)
        in_tree = lambda *args, stdin=None: subprocess.run(  # noqa: E731
            [sys.executable, CLI, *args], cwd=tree, input=stdin, capture_output=True, text=True, env=self.env)
        self.assertEqual(in_tree("ticket", "01", "implementing").returncode, 0)
        self.assertEqual(self.state()["ticket"], "01")
        edit = {"tool_name": "Edit", "tool_input": {"file_path": os.path.join(tree, "app.py")}, "cwd": tree}
        self.assertEqual(in_tree("hook", "pre-tool", stdin=json.dumps(edit)).returncode, 0)
        os.remove(os.path.join(tree, "docs", "PASS"))
        commit = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}, "cwd": tree}
        out = in_tree("hook", "pre-tool", stdin=json.dumps(commit))
        self.assertEqual(out.returncode, 2)  # trusted via the main tree, tests run in the worktree

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
