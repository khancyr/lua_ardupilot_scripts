# ArduPilot Lua Community Scripts

A community repository of Lua scripts for [ArduPilot](https://ardupilot.org) autopilots,
with automated validation and a searchable web interface.

## Repository structure

``` bash
applets/   Ready-to-use scripts — drop onto SD card and fly
drivers/   Hardware drivers for peripherals not in the firmware
tools/     Utility scripts (monitoring, logging, etc.)
```

Each script is a paired `<Name>.lua` + `<Name>.md` file.

## Using a script

1. Enable scripting: set `SCR_ENABLE = 1` and reboot.
2. Upload the `.lua` file to `APM/scripts/` on the autopilot SD card
   (MAVFTP from Mission Planner, QGroundControl, or MAVProxy).
3. Reboot — all scripts in the folder are loaded automatically.

Full ArduPilot Lua documentation: <https://ardupilot.org/copter/docs/common-lua-scripts.html>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Local development

### 1 — System dependencies

**luacheck** (Lua linter, required by the pre-commit hook):

```bash
brew install luacheck          # macOS
sudo apt install lua-check     # Debian/Ubuntu
```

**lua-language-server** (Lua formatter — used by VS Code and any LSP editor):

```bash
brew install lua-language-server   # macOS
bash scripts/install-lua-ls.sh    # Linux — installs latest release to ~/.local/
```

### 2 — Python tooling

```bash
# Create and activate the virtual environment (one-time)
python3 -m venv .venv
source .venv/bin/activate

# Install pre-commit, ruff, pyyaml, pytest
pip install -r requirements.txt

# Install the git hook (runs luacheck, ruff, markdownlint, validate-scripts on every commit)
pre-commit install
```

### 3 — Run all checks manually

```bash
source .venv/bin/activate
pre-commit run --all-files
```

To run luacheck on its own:

```bash
luacheck applets/ drivers/ tools/
```

### 4 — Run the website locally

```bash
source .venv/bin/activate
pip install -r website/requirements.txt
cd website && uvicorn app.main:app --reload
```

Then open <http://localhost:8000>.

### 5 — Run tests

```bash
# Website tests
source .venv/bin/activate
pip install -r website/requirements.txt
cd website && pytest tests/ -v

# Script validator tests
source .venv/bin/activate
pytest .pre-commit-hooks/tests/ -v
```

## License

This repository uses a dual license, matching the convention used by the ArduPilot project:

| Component | License |
| --------- | ------- |
| Lua scripts (`applets/`, `drivers/`, `tools/`) | [MIT](LICENSE-MIT) |
| Everything else (website, tooling, CI, docs) | [GPL-3.0](LICENSE) |
