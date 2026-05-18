from __future__ import annotations

import os
import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import yaml

from .models import ScriptMeta

SCRIPT_DIRS = ["applets", "drivers", "tools"]
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Allow REPO_ROOT env var override (used in Docker); fall back to relative path.
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
        script_dir = repo_root / dir_name
        if not script_dir.is_dir():
            continue

        for lua_path in sorted(script_dir.glob("*.lua")):
            md_path = lua_path.with_suffix(".md")
            if not md_path.exists():
                continue

            fm, body = _parse_frontmatter(md_path)

            vehicle = fm.get("vehicle", ["all"])
            if isinstance(vehicle, str):
                vehicle = [vehicle]

            scripts.append(
                ScriptMeta(
                    name=str(fm.get("name", lua_path.stem)),
                    type=dir_name,
                    short_description=str(fm.get("short_description", "")),
                    vehicle=vehicle,
                    min_firmware=str(fm.get("min_firmware") or "4.5"),
                    version=str(fm.get("version", "0.0.0")),
                    date=fm.get("date")
                    if isinstance(fm.get("date"), date)
                    else date.fromisoformat(str(fm.get("date", "2000-01-01"))),
                    download_url=f"/api/v1/scripts/{dir_name}/{lua_path.stem}/raw",
                    doc_url=f"/scripts/{dir_name}/{lua_path.stem}",
                    description=body.strip(),
                )
            )

    return scripts


@lru_cache(maxsize=1)
def get_index() -> List[ScriptMeta]:
    """Return cached script index. Call invalidate_index() to refresh."""
    return _build_index(_REPO_ROOT)


def invalidate_index() -> None:
    get_index.cache_clear()


def get_script(script_type: str, name: str) -> Optional[ScriptMeta]:
    return next(
        (s for s in get_index() if s.type == script_type and s.name == name),
        None,
    )


def get_lua_path(script_type: str, name: str) -> Optional[Path]:
    return _REPO_ROOT / script_type / f"{name}.lua"
