## Description

<!-- What does this PR do and why? Reference any related issue with "Fixes #NNN". -->

## Type of change

- [ ] New script (`applets/`, `drivers/`, or `tools/`)
- [ ] Script update / bug fix
- [ ] Website / tooling change
- [ ] Documentation only

---

### Script checklist *(skip if no script changes)*

- [ ] Correct directory chosen (`applets/` / `drivers/` / `tools/`)
- [ ] `<Name>.lua` and `<Name>.md` exist with the same stem
- [ ] All frontmatter fields present: `name`, `short_description`, `version`, `date`, `min_firmware`
- [ ] `short_description` ≤ 127 characters
- [ ] `version` follows semver (`MAJOR.MINOR.PATCH`)
- [ ] `date` is `YYYY-MM-DD`
- [ ] `min_firmware` is set (use `4.5` if the minimum version is unknown)
- [ ] Script passes `luacheck` with no errors
- [ ] Script is formatted with the LuaLS formatter

### Website / tooling checklist *(skip if no code changes)*

- [ ] All tests pass (`cd website && pytest tests/ -v`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)

---

## Testing

<!-- How did you test this?
     For scripts: firmware version, vehicle type, and test conditions.
     For website changes: which routes / API endpoints were verified. -->
