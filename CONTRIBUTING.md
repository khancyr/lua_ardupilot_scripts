# Contributing

Thank you for contributing a Lua script! Please follow these guidelines so
automated checks pass and scripts are easy to discover.

## Quick checklist

- [ ] Script name is unique across the whole repo
- [ ] Files are named `<Name>.lua` and `<Name>.md` (same stem, same directory)
- [ ] `.md` has valid YAML frontmatter with all required fields
- [ ] `short_description` ≤ 127 characters
- [ ] `version` follows semver (`MAJOR.MINOR.PATCH`)
- [ ] `date` is `YYYY-MM-DD`
- [ ] `min_firmware` is set (use `4.5` if the minimum version is unknown)
- [ ] Script passes `luacheck` with no errors
- [ ] Script is formatted with the LuaLS built-in formatter

## Choosing a directory

| Directory | Use when… |
| --------- | --------- |
| `lua/applets/` | Script needs no user editing before use |
| `lua/drivers/` | Script implements a hardware driver for a new peripheral |
| `lua/tools/` | Script is a utility (logging, monitoring, helper) |

## File pair

Every script needs two files in the same directory:

``` bash
lua/applets/
  MyScript.lua   ← the Lua script
  MyScript.md    ← documentation with YAML frontmatter
```

## Documentation format

```markdown
---
name: MyScript
short_description: One-line summary shown in GCS and website listings (max 127 chars).
vehicle: [copter, plane, rover]   # optional; omit for all vehicles
min_firmware: "4.5"               # required; use 4.5 if the minimum version is unknown
version: "1.0.0"
date: 2026-05-18
---

## Description

Explain what the script does and why someone would use it.

## Setup

Step-by-step instructions for installation and configuration.

## Parameters

| Constant | Default | Description |
|----------|---------|-------------|
| `MY_PARAM` | 100 | What this constant controls. |
```

## Setup and running checks locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install          # installs git hook
pre-commit run --all-files  # run all checks now
```

Pre-commit runs automatically on every `git commit`. All checks must pass
before a PR can be merged.

## Bumping the version

When updating an existing script:

1. Increment `version` in the `.md` frontmatter (follow semver - patch for
   bug fixes, minor for new features, major for breaking changes).
2. Update `date` to today's date.

## ArduPilot API autocomplete in VSCode

Install the recommended extensions (VSCode will prompt you on first open).
The `.vscode/settings.json` points the Lua language server at `.checks/docs.lua`,
which provides autocomplete for all ArduPilot globals (`ahrs`, `gps`, `battery`, etc.).

## Lua tooling without VS Code

### Checking with luacheck

`luacheck` is run automatically by pre-commit on every commit. To run it manually:

```bash
# Install (pick one)
brew install luacheck          # macOS
sudo apt install lua-check     # Debian/Ubuntu
luarocks install luacheck      # via LuaRocks (any platform)

# Run against all script directories
luacheck lua/applets/ lua/drivers/ lua/tools/
```

### Formatting with lua-language-server

The repo uses the [LuaLS built-in formatter](https://github.com/LuaLS/lua-language-server),
configured via `.editorconfig` (4-space indent, 120-column limit, double quotes).
Any editor with LSP support can invoke it.

**Install lua-language-server:**

```bash
brew install lua-language-server   # macOS
bash scripts/install-lua-ls.sh    # Linux - installs latest release to ~/.local/
# Or download a binary manually from https://github.com/LuaLS/lua-language-server/releases
```

**Other LSP editors** (Emacs, Helix, Sublime Text, …): configure `lua-language-server`
as the Lua language server and use your editor’s format-buffer command.
