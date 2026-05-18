# ArduPilot Lua Community Scripts

A community repository of Lua scripts for [ArduPilot](https://ardupilot.org) autopilots,
with automated validation and a searchable web interface.

## Repository structure

``` bash
lua/applets/   Ready-to-use scripts - drop onto SD card and fly
lua/drivers/   Hardware drivers for peripherals not in the firmware
lua/tools/     Utility scripts (monitoring, logging, etc.)
```

Each script is a paired `<Name>.lua` + `<Name>.md` file.

## Using a script

1. Enable scripting: set `SCR_ENABLE = 1` and reboot.
2. Upload the `.lua` file to `APM/scripts/` on the autopilot SD card
   (MAVFTP from Mission Planner, QGroundControl, or MAVProxy).
3. Reboot - all scripts in the folder are loaded automatically.

Full ArduPilot Lua documentation: <https://ardupilot.org/copter/docs/common-lua-scripts.html>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Local development

### 1 - System dependencies

**luacheck** (Lua linter, required by the pre-commit hook):

```bash
brew install luacheck          # macOS
sudo apt install lua-check     # Debian/Ubuntu
```

**lua-language-server** (Lua formatter - used by VS Code and any LSP editor):

```bash
brew install lua-language-server   # macOS
bash scripts/install-lua-ls.sh    # Linux - installs latest release to ~/.local/
```

### 2 - Python tooling

```bash
# Create and activate the virtual environment (one-time)
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies (build tools + dev tools)
pip install -e ".[dev]"

# Install the git hook (runs luacheck, ruff, markdownlint, validate-scripts on every commit)
pre-commit install
```

### 3 - Run all checks manually

```bash
source .venv/bin/activate
pre-commit run --all-files
```

To run luacheck on its own:

```bash
luacheck lua/applets/ lua/drivers/ lua/tools/
```

### 4 - Preview the website locally

```bash
source .venv/bin/activate
python scripts/build_static.py        # writes to dist/
python -m http.server 8080 -d dist
```

Then open <http://localhost:8080>.

Re-run `build_static.py` after any template or script change.

### 5 - Run tests

```bash
source .venv/bin/activate
pytest .pre-commit-hooks/tests/ -v
```

## License

This repository uses a dual license, matching the convention used by the ArduPilot project:

| Component | License |
| --------- | ------- |
| Lua scripts (`lua/applets/`, `lua/drivers/`, `lua/tools/`) | [MIT](LICENSE-MIT) |
| Everything else (website, tooling, CI, docs) | [GPL-3.0](LICENSE) |
