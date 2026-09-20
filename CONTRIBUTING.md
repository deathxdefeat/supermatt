# Contributing to supermatt

To work on supermatt itself, install from a local clone:

```bash
git clone https://github.com/deathxdefeat/supermatt.git
claude plugin marketplace add /path/to/supermatt
claude plugin install supermatt@supermatt
```

Or link the plugin folder into your skills directory. Claude Code then loads it in place as `supermatt@skills-dir`, and your edits apply in the next session (or after `/reload-plugins`):

```bash
ln -s /path/to/supermatt/plugin ~/.claude/skills/supermatt
```

Run the tests and validate the manifests from the repo root:

```bash
python3 -m unittest
claude plugin validate . && claude plugin validate plugin
```

The tests drive `plugin/bin/supermatt` the way the hooks call it, in temporary git repos. They also check that the skills' names, links and cross-references stay consistent, and that this README lists every skill. CI runs them on Ubuntu and macOS with Python 3.9 and 3.13.

| Path | What it is |
|---|---|
| `plugin/.claude-plugin/plugin.json` | The plugin manifest |
| `.claude-plugin/marketplace.json` | The marketplace entry that makes `supermatt@supermatt` installable |
| `plugin/skills/<name>/` | The 21 skills. `run`, `status` and `drift` are original, and so is `advise` apart from its skills map; the rest are adapted from the source skills (see `plugin/NOTICE.md`). |
| `plugin/bin/supermatt` | The command that holds options, pipeline state and the hook logic |
| `plugin/hooks/hooks.json` | The PreToolUse, Stop and SessionStart hooks, all calling `supermatt hook` |
| `tests/` | The unit tests |
| `docs/configuration.md`, `docs/security.md`, `docs/cli.md` | The reference docs the README links to |
| `CONTEXT.md`, `docs/adr/` | Project terms and design decisions |

## Diagrams

The diagram sources are the JSON specs in `docs/diagrams/`. Each has two captures in `docs/images/`: `<name>.png` (light) and `<name>-dark.png`, which the docs pair in a `<picture>` element so GitHub shows the one matching the reader's theme. To change a diagram, edit its spec, render it with Archify's `render <type> <name>.json <name>.html --quality showcase` command (the HTML is gitignored), open the HTML with `?theme=light` and `?theme=dark`, and capture the diagram at 2x, cropped to its content.
