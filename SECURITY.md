# Security policy

supermatt installs Claude Code hooks that can run a repo's configured test command on your machine, so security reports are taken seriously.

## Reporting a vulnerability

Please report it privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Don't open a public issue for a security problem.

Include what an attacker controls (for example a cloned repo's `.supermatt/config.json`), what runs as a result, and the steps to reproduce it.

## Scope

In scope: `plugin/bin/supermatt`, `plugin/hooks/hooks.json`, the config trust model, and skill instructions that could lead an agent to act unsafely.

The trust model is described in [docs/security.md](docs/security.md). By design, a trusted `test_command` runs your repo's own code. Running code from a branch you haven't reviewed is covered there, and is not treated as a vulnerability.
