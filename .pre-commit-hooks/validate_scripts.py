#!/usr/bin/env python3
"""
validate_scripts.py - pre-commit hook that checks every script directory.

Rules enforced:
  1. Each .lua file must have a matching .md file (same stem, same directory).
  2. Each .md file must have a matching .lua file.
  3. Every .md must contain valid YAML frontmatter with required fields.
  4. short_description must be <= 127 characters.
  5. version must match semantic versioning (MAJOR.MINOR[.PATCH], optional prerelease/build metadata).
  6. date must be a valid ISO 8601 calendar date (YYYY-MM-DD).
  7. min_firmware must be MAJOR.MINOR or MAJOR.MINOR.PATCH (e.g. "4.5").
  8. vehicle, if present, must be a string or list of valid vehicle types.
  9. status, if present, must be "working" or "broken" (defaults to "working").
  10. Script names (stems) must be unique across all script directories.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

# Allow imports from scripts/ when running this hook directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    import yaml
    from website.models import FirmwareVersion, SemVer, ScriptMeta, ScriptStatus, VehicleType
except ImportError:
    print("ERROR: PyYAML and the website package are required. Install with: pip install '.[dev]'", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIRS = ["applets", "drivers", "tools"]
REQUIRED_FIELDS = ["name", "short_description", "version", "date", "min_firmware"]
SHORT_DESC_MAX = 127
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


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
    """Return True if *value* is a valid ISO 8601 calendar date (YYYY-MM-DD)."""
    if isinstance(value, date) and not isinstance(value, bool):
        return True
    try:
        date.fromisoformat(str(value).strip())
        return True
    except (ValueError, TypeError):
        return False


def main(repo_root: Path | None = None) -> int:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    seen_names: dict[str, Path] = {}

    for dir_name in SCRIPT_DIRS:
        script_dir = repo_root / "lua" / dir_name
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

        # Rules 3–9: validate frontmatter for each paired .md
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

            # Use ScriptMeta as the source of truth for version, firmware, date, and vehicle validation.
            if not any(field not in fm or fm[field] is None or str(fm[field]).strip() == "" for field in REQUIRED_FIELDS):
                try:
                    vehicle = fm.get("vehicle", ["all"])
                    if isinstance(vehicle, str):
                        vehicle = [vehicle]
                    elif vehicle is None:
                        vehicle = ["all"]
                    elif not isinstance(vehicle, list):
                        raise ValueError("vehicle must be a string or list of strings")

                    if not validate_date(fm["date"]):
                        raise ValueError(f"Invalid date: '{fm['date']}'. Expected YYYY-MM-DD")
                    parsed_date = date.fromisoformat(str(fm["date"]).strip())

                    ScriptMeta(
                        name=str(fm.get("name", stem)),
                        type=dir_name,
                        short_description=str(fm.get("short_description", "")),
                        vehicle=[VehicleType(v) for v in vehicle],
                        min_firmware=FirmwareVersion(str(fm.get("min_firmware", "")).strip()),
                        version=SemVer(str(fm.get("version", "")).strip()),
                        date=parsed_date,
                        status=ScriptStatus(str(fm.get("status", "working"))),
                        download_url=f"/{dir_name}/{stem}.lua",
                        page_url=f"/scripts/{dir_name}/{stem}",
                        description="",
                    )
                except ValueError as exc:
                    errors.append(f"{dir_name}/{stem}.md: {exc}")
                except TypeError:
                    errors.append(f"{dir_name}/{stem}.md: vehicle must be a string or list of strings")

            # Rule 9: unique names
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
