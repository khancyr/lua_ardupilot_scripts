#!/usr/bin/env python3
"""
Build a fully-static version of the ArduPilot Lua Community Scripts website.

Output layout (dist/):
  index.html
  scripts/index.html                     ← browse page (client-side filtering)
  scripts/{type}/{name}/index.html       ← script detail
  contribute/index.html
  api-reference/index.html
  api/v1/types.json
  api/v1/scripts.json
  api/v1/scripts/{type}/{name}/index.json
  {type}/{name}.lua                      ← raw download
  static/…                               ← CSS / images

Usage:
  python scripts/build_static.py
  BASE_URL=/lua_community_scripts python scripts/build_static.py
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
from pathlib import Path

import markdown as md_lib
from jinja2 import Environment, FileSystemLoader

from website.scripts import get_index

REPO_ROOT = Path(__file__).resolve().parent.parent

# -- configuration -------------------------------------------------------------
# Set BASE_URL env var when deploying to a sub-path (e.g. /lua_community_scripts).
# Leave empty for a root-domain deployment.
BASE_URL: str = os.environ.get("BASE_URL", "").rstrip("/")

DIST = REPO_ROOT / "dist"
TEMPLATES_DIR = REPO_ROOT / "scripts" / "website" / "templates"
STATIC_SRC = REPO_ROOT / "scripts" / "website" / "static"

SCRIPT_TYPES = ("applets", "drivers", "tools")


# -- Jinja2 environment --------------------------------------------------------


def _make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        keep_trailing_newline=True,
    )
    env.globals["base_url"] = BASE_URL
    return env


# -- helpers -------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")


# -- build ---------------------------------------------------------------------


def build() -> None:
    # Start fresh
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    # Disable Jekyll processing so GitHub Pages serves all files as-is
    # (without this, .lua files and any path starting with _ are silently dropped).
    # (DIST / ".nojekyll").touch()

    env = _make_env()
    scripts = get_index()

    # -- static assets ---------------------------------------------------------
    shutil.copytree(STATIC_SRC, DIST / "static")

    # -- raw .lua files --------------------------------------------------------
    for script_type in SCRIPT_TYPES:
        src_dir = REPO_ROOT / "lua" / script_type
        if not src_dir.is_dir():
            continue
        dst_dir = DIST / script_type
        dst_dir.mkdir()
        for lua in src_dir.glob("*.lua"):
            shutil.copy(lua, dst_dir / lua.name)

    # -- home page -------------------------------------------------------------
    tmpl = env.get_template("index.html")
    _write(DIST / "index.html", tmpl.render())

    # -- browse page -----------------------------------------------------------
    tmpl = env.get_template("browse.html")
    types = sorted({s.type for s in scripts})
    _write(DIST / "scripts" / "index.html", tmpl.render(scripts=scripts, types=types))

    # -- script detail pages ---------------------------------------------------
    tmpl = env.get_template("script.html")
    for s in scripts:
        desc_html = md_lib.markdown(s.description or "", extensions=["tables", "fenced_code"])
        # Static download URL already set correctly in scripts.py
        static_script = dataclasses.replace(s, download_url=f"{BASE_URL}/{s.type}/{s.name}.lua")
        content = tmpl.render(script=static_script, description_html=desc_html)
        _write(DIST / "scripts" / s.type / s.name / "index.html", content)

    # -- static pages ----------------------------------------------------------
    tmpl = env.get_template("contribute.html")
    _write(DIST / "contribute" / "index.html", tmpl.render())

    tmpl = env.get_template("api_docs.html")
    _write(DIST / "api-reference" / "index.html", tmpl.render())

    # -- API JSON --------------------------------------------------------------
    api_dir = DIST / "api" / "v1"

    # types
    counts: dict[str, int] = {}
    for s in scripts:
        counts[s.type] = counts.get(s.type, 0) + 1
    _write_json(api_dir / "types.json", [{"type": t, "count": c} for t, c in sorted(counts.items())])

    # scripts list (no description body)
    scripts_list = [dataclasses.asdict(dataclasses.replace(s, description=None)) for s in scripts]
    _write_json(api_dir / "scripts.json", {"total": len(scripts), "results": scripts_list})

    # per-script detail
    for s in scripts:
        data = dataclasses.asdict(s)
        data["download_url"] = f"{BASE_URL}/{s.type}/{s.name}.lua"
        _write_json(api_dir / "scripts" / s.type / s.name / "index.json", data)

    total_html = 2 + len(scripts) + 2  # home + browse + details + contribute + api-reference
    print(f"Built {len(scripts)} scripts → {DIST}  ({total_html} HTML pages)")


if __name__ == "__main__":
    build()
