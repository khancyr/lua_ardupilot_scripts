#!/usr/bin/env python3
"""
validate_scripts.py — pre-commit hook that checks every script directory.

Rules enforced:
  1. Each .lua file must have a matching .md file (same stem, same directory).
  2. Each .md file must have a matching .lua file.
  3. Every .md must contain valid YAML frontmatter with required fields.
  4. short_description must be <= 127 characters.
  5. version must match semantic versioning (MAJOR.MINOR.PATCH).
  6. date must be a valid ISO 8601 calendar date (YYYY-MM-DD).
  7. min_firmware must be MAJOR.MINOR or MAJOR.MINOR.PATCH (e.g. "4.5").
  8. Script names (stems) must be unique across all script directories.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIRS = ["applets", "drivers", "tools"]
REQUIRED_FIELDS = ["name", "short_description", "version", "date", "min_firmware"]
SHORT_DESC_MAX = 127
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FIRMWARE_RE = re.compile(r"^\d+\.\d+(\.\d+)?$")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# Update when a new stable ArduPilot release is published.
# Contributors who do not know the minimum required version should use this value.
LATEST_RELEASE = "4.5"


def parse_frontmatter(md_path: Path) -> dict | None:
    """Return the parsed YAML frontmatter dict, or None if absent/invalid."""
    content = md_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1)) or {}
    except (yaml.YAMLError, ValueError):
        return None


def validate_date(value: object) -> bool:
    """Return True if value is a valid YYYY-MM-DD date."""
    s = str(value)
    if not DATE_RE.match(s):
        return False
    try:
        date.fromisoformat(s)
        return True
    except ValueError:
        return False


def main(repo_root: Path | None = None) -> int:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    seen_names: dict[str, Path] = {}

    for dir_name in SCRIPT_DIRS:
        script_dir = repo_root / dir_name
        if not script_dir.is_dir():
            continue

        lua_stems = {p.stem for p in script_dir.glob("*.lua")}
        md_stems = {p.stem for p in script_dir.glob("*.md")}

        # Rule 1: every .lua needs a .md
        for stem in sorted(lua_stems - md_stems):
            errors.append(f"{dir_name}/{stem}.lua: missing matching {stem}.md")

        # Rule 2: every .md needs a .lua
        for stem in sorted(md_stems - lua_stems):
            errors.append(f"{dir_name}/{stem}.md: missing matching {stem}.lua")

        # Rules 3–7: validate frontmatter for each paired .md
        for stem in sorted(md_stems & lua_stems):
            md_path = script_dir / f"{stem}.md"
            fm = parse_frontmatter(md_path)

            if fm is None:
                errors.append(f"{dir_name}/{stem}.md: missing or invalid YAML frontmatter")
                continue

            # Rule 3: required fields
            for field in REQUIRED_FIELDS:
                if field not in fm or fm[field] is None or str(fm[field]).strip() == "":
                    errors.append(f"{dir_name}/{stem}.md: missing required frontmatter field '{field}'")

            # Rule 4: short_description length
            desc = str(fm.get("short_description", ""))
            if len(desc) > SHORT_DESC_MAX:
                errors.append(f"{dir_name}/{stem}.md: short_description is {len(desc)} chars (max {SHORT_DESC_MAX}): {desc!r}")

            # Rule 5: semver version
            version = str(fm.get("version", ""))
            if version and not SEMVER_RE.match(version):
                errors.append(f"{dir_name}/{stem}.md: version '{version}' is not valid semver (expected MAJOR.MINOR.PATCH)")

            # Rule 6: ISO date
            dt = fm.get("date")
            if dt is not None and not validate_date(dt):
                errors.append(f"{dir_name}/{stem}.md: date '{dt}' is not a valid YYYY-MM-DD date")

            # Rule 7: firmware version format
            fw = fm.get("min_firmware")
            if fw is not None and str(fw).strip() and not FIRMWARE_RE.match(str(fw)):
                errors.append(
                    f"{dir_name}/{stem}.md: min_firmware '{fw}' must be MAJOR.MINOR "
                    f"or MAJOR.MINOR.PATCH (e.g. '{LATEST_RELEASE}')"
                )

            # Rule 8: unique names
            name = str(fm.get("name", stem))
            if name in seen_names:
                errors.append(f"{dir_name}/{stem}.md: script name '{name}' already used by {seen_names[name]}")
            else:
                seen_names[name] = md_path.relative_to(repo_root)

    if errors:
        print("Script validation failed:\n", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        print(file=sys.stderr)
        return 1

    print(f"Script validation passed ({len(seen_names)} script(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
