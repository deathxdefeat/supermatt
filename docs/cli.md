# The `supermatt` command

The command-line reference. For the options it sets, see [Configuration](configuration.md); for the overview, see the [README](../README.md).

The skills and hooks work through `plugin/bin/supermatt`, a single standard-library Python script that reads your options, records progress and runs your tests.

![How the pieces fit: skills and hooks call the supermatt command, which reads the config, writes the state file and runs your test command](images/command.svg)

When the plugin is enabled, it is on the `PATH` of Claude's Bash tool, so Claude can run any of these commands when you ask. It is not on your own terminal's `PATH`. To run it there, call `python3 <plugin dir>/bin/supermatt <command>` from inside a repo, where `<plugin dir>` is `~/.claude/plugins/cache/supermatt/supermatt/<version>` for a marketplace install, or `<clone>/plugin` for a local clone or link. If unsure, ask Claude to run `command -v supermatt` for the full path. It acts on the git repo that contains the current directory.

| Command | What it does |
|---|---|
| `init [--preset P] [--test-command CMD] [--force]` | Sets the repo up: writes and trusts `.supermatt/config.json`, and gitignores the state file. The preset defaults to `standard`. Won't replace an existing config without `--force`. |
| `status [--json]` | Shows the pipeline's progress, the options, and whether the config is trusted |
| `config` | Prints every option |
| `config KEY [VALUE]` | Shows or sets one option by dotted key, for example `enforce.green_before_stop block`. `pipeline.pause_at` and `exempt` take comma-separated lists, and `pipeline.pause_at none` clears the pauses. |
| `config preset P` | Sets all four rules from a preset |
| `trust` | Approves this repo's current config on this machine |
| `start SLUG [--stage STAGE]` | Starts a feature at `grill`, or at a later stage when the earlier work already exists |
| `stage STAGE` | Records the stage: `grill`, `spec`, `tickets`, `implement`, `verify`, `finish` or `done` |
| `base BRANCH` | Records the branch the feature started from, which finish merges back into |
| `test [--force]` | Runs the test command, unless these exact files already passed it |
| `ticket ID implementing\|blocked\|needs-review\|done` | Records a ticket's state, applying `review_after_ticket` |
| `hook pre-tool\|stop\|session-start` | The entry point `plugin/hooks/hooks.json` calls, with the hook event as JSON on stdin |
