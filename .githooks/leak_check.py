#!/usr/bin/env python3
"""Refuse commits and pushes that would put private material into this public repo.

Checks added lines for secrets, home-directory paths and email addresses, checks that session and
work files are not being committed, and checks that commit identities use a GitHub noreply address.
Extra private words (your name, employer, clients) go one regex per line in the file named by
SUPERMATT_PRIVATE_PATTERNS, default ~/.config/supermatt/private-patterns. That file never enters
the repo, so the words themselves stay private.

  leak_check.py staged          the staged diff (pre-commit)
  leak_check.py push            the commits named on stdin (pre-push)
  leak_check.py tree            every tracked file (tests, CI)
"""
import os
import re
import subprocess
import sys

HOME = "/" + "Users/|/" + "home/"  # split so this file does not match itself
PATTERNS = {
    "home directory path": re.compile(r"(?:%s)(?!you/|me/|name/|user/|runner/)[A-Za-z0-9._-]+/" % HOME),
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.com|users\.noreply\.github\.com|anthropic\.com)"
                                r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[a-z]{2,}\b"),
    "private key": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    "credential": re.compile(r"sk-ant-[A-Za-z0-9_-]{8}|\bsk-[A-Za-z0-9]{20}|\bgh[pousr]_[A-Za-z0-9]{20}|github_pat_\w{20}"
                             r"|\bAKIA[0-9A-Z]{16}\b|\bxox[abp]-[A-Za-z0-9-]{10}|\bop://[^\s\"']+/"
                             r"|\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}"),
    "assigned secret": re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*[\"'][^\"'\s]{12,}[\"']"),
}
# Session and work files: never part of this repo, whatever .gitignore says.
FORBIDDEN_PATHS = re.compile(r"(^|/)(\.scratch|\.claude|\.codex|\.supermatt|\.env[^/]*|.*\.pem|.*\.key"
                             r"|id_(rsa|ed25519)[^/]*|.*\.jsonl|\.DS_Store)(/|$)|^(handoffs?|memory)(/|$)")
NOREPLY = re.compile(r"@users\.noreply\.github\.com$|^noreply@(anthropic\.com|github\.com)$")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, errors="replace").stdout


def private_patterns():
    path = os.environ.get("SUPERMATT_PRIVATE_PATTERNS") or os.path.expanduser("~/.config/supermatt/private-patterns")
    try:
        with open(path) as f:
            lines = [line.strip() for line in f]
    except OSError:
        return {}
    return {f"private pattern {n}": re.compile(line, re.I) for n, line in enumerate(lines, 1)
            if line and not line.startswith("#")}


def scan_lines(where, numbered_lines, patterns):
    found = []
    for number, line in numbered_lines:
        for name, pattern in patterns.items():
            if pattern.search(line):
                # Private patterns are reported by number, and the line is not echoed, so logs stay clean.
                found.append(f"{where}:{number}: {name}")
    return found


def scan_diff(diff, patterns):
    found, path, number = [], None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@"):
            number = int(re.search(r"\+(\d+)", line).group(1)) - 1
        elif path and line.startswith("+"):
            number += 1
            found += scan_lines(path, [(number, line[1:])], patterns)
        elif path and not line.startswith("-"):
            number += 1
    return found


def scan_paths(paths):
    return [f"{p}: session or work file, never committed here" for p in paths if p and FORBIDDEN_PATHS.search(p)]


def main(mode):
    patterns = dict(PATTERNS, **private_patterns())
    found = []
    if mode == "staged":
        found += scan_paths(git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines())
        found += scan_diff(git("diff", "--cached", "-U0", "--no-color"), patterns)
        for who in ("author", "committer"):
            email = git("var", f"GIT_{who.upper()}_IDENT").rsplit("<", 1)[-1].split(">")[0]
            if not NOREPLY.search(email):
                found.append(f"{who} email is not a GitHub noreply address; set `git config user.email`")
    elif mode == "push":
        for ref in sys.stdin.read().splitlines():
            _, local, _, remote = (ref.split() + [""] * 4)[:4]
            if not local or set(local) == {"0"}:
                continue
            span = [local, "--not", "--remotes"] if set(remote) == {"0"} else [f"{remote}..{local}"]
            for commit in git("rev-list", *span).split():
                emails = git("show", "-s", "--format=%ae%n%ce", commit).split()
                found += [f"{commit[:8]}: identity {n} is not a noreply address" for n, e in enumerate(emails) if not NOREPLY.search(e)]
                found += [f"{commit[:8]}: {f}" for f in scan_paths(git("show", "--format=", "--name-only", "--diff-filter=ACMR", commit).splitlines())]
                found += [f"{commit[:8]}: {f}" for f in scan_diff(git("show", "--format=%B", "-U0", "--no-color", commit), patterns)]
                found += [f"{commit[:8]}: message: {f}" for f in scan_lines("message", enumerate(git("show", "-s", "--format=%B", commit).splitlines(), 1), patterns)]
    elif mode == "tree":
        paths = git("ls-files", "-z").split("\0")
        found += scan_paths(paths)
        for path in filter(None, paths):
            try:
                with open(path, errors="replace") as f:
                    found += scan_lines(path, enumerate(f, 1), patterns)
            except OSError:
                pass
    else:
        sys.exit(__doc__)
    if found:
        print("leak check: refused. This repo is public.\n  " + "\n  ".join(found), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
