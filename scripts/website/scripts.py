from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import List

import yaml

from .models import FirmwareVersion, ScriptMeta, ScriptStatus, SemVer, VehicleType

SCRIPT_DIRS = ["applets", "drivers", "tools"]
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Allow REPO_ROOT env var override; fall back to relative path.
# __file__ is scripts/website/scripts.py → .parent.parent.parent = repo root.
_env_root = os.environ.get("REPO_ROOT")
_REPO_ROOT = Path(_env_root) if _env_root else Path(__file__).resolve().parent.parent.parent


def _parse_frontmatter(md_path: Path) -> tuple[dict, str]:
    """Return (frontmatter_dict, markdown_body) for a given .md file."""
    content = md_path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    fm = yaml.safe_load(match.group(1)) or {}
    body = content[match.end() :]
    return fm, body


def _build_index(repo_root: Path) -> List[ScriptMeta]:
    scripts: List[ScriptMeta] = []

    for dir_name in SCRIPT_DIRS:
        script_dir = repo_root / "lua" / dir_name
        if not script_dir.is_dir():
            continue

        for lua_path in sorted(script_dir.glob("*.lua")):
            md_path = lua_path.with_suffix(".md")
            if not md_path.exists():
                continue

            fm, body = _parse_frontmatter(md_path)

            vehicle = fm.get("vehicle", ["all"])
            if isinstance(vehicle, str):
                vehicle = [VehicleType(vehicle)]
            else:
                vehicle = [VehicleType(v) for v in vehicle]

            raw_date = fm.get("date")
            if isinstance(raw_date, date):
                parsed_date = raw_date
            elif isinstance(raw_date, str) and raw_date.strip():
                parsed_date = date.fromisoformat(raw_date.strip())
            else:
                parsed_date = date(2000, 1, 1)

            scripts.append(
                ScriptMeta(
                    name=str(fm.get("name", lua_path.stem)),
                    type=dir_name,
                    short_description=str(fm.get("short_description", "")),
                    vehicle=vehicle,
                    min_firmware=FirmwareVersion(str(fm.get("min_firmware") or "4.5")),
                    version=SemVer(str(fm.get("version", "0.0.0"))),
                    date=parsed_date,
                    status=ScriptStatus(str(fm.get("status", "working"))),
                    download_url=f"/{dir_name}/{lua_path.stem}.lua",
                    page_url=f"/scripts/{dir_name}/{lua_path.stem}",
                    description=body.strip(),
                )
            )

    return scripts


def get_index() -> List[ScriptMeta]:
    """Return cached script index."""
    return _build_index(_REPO_ROOT)
