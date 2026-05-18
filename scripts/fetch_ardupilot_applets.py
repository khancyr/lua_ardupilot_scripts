#!/usr/bin/env python3
"""Download ArduPilot applets and wrap them with the required YAML frontmatter."""

import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APPLETS_DIR = REPO_ROOT / "lua" / "applets"

TODAY = date.today().isoformat()
MIN_FW = "4.5"

BASE_RAW = "https://raw.githubusercontent.com/ArduPilot/ardupilot/master/libraries/AP_Scripting/applets"
BASE_API = "https://api.github.com/repos/ArduPilot/ardupilot/contents/libraries/AP_Scripting/applets"

# Scripts to skip (already have custom versions or not suitable for community repo)
SKIP = {"HelloWorld"}

# Known vehicle tags per script name keyword
_VEHICLE_KW = {
    "copter": "copter",
    "heli": "copter",
    "quadcopter": "copter",
    "plane": "plane",
    "fw_": "plane",
    "vtol": "plane",
    "quadplane": "plane",
    "rover": "rover",
    "boat": "rover",
}


def _infer_vehicles(name: str, desc: str) -> list[str]:
    combined = (name + " " + desc).lower()
    found = []
    for kw, vehicle in _VEHICLE_KW.items():
        if kw in combined and vehicle not in found:
            found.append(vehicle)
    return found


def _extract_short_desc(md: str, fallback: str) -> str:
    """Pull the first meaningful prose sentence from a markdown document."""
    for line in md.splitlines():
        s = line.strip()
        # Skip headings, blank lines, table rows, images, HTML
        if not s or s.startswith(("#", "|", "!", "<", "---", "```")):
            continue
        # Strip inline markdown formatting
        s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
        s = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", s)
        s = re.sub(r"`(.+?)`", r"\1", s)
        s = re.sub(r"\*(.+?)\*", r"\1", s)
        s = s.strip()
        if len(s) > 12:
            return s[:127]
    return f"ArduPilot {fallback} applet"[:127]


def _fetch(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.read()
    except Exception as e:
        print(f"    fetch error {url}: {e}")
        return None


def _build_frontmatter(name: str, short_desc: str, vehicles: list[str]) -> str:
    vehicle_line = ""
    if vehicles:
        vehicle_line = f"vehicle: [{', '.join(vehicles)}]\n"
    return (
        "---\n"
        f"name: {name}\n"
        f"short_description: {short_desc}\n"
        "version: 1.0.0\n"
        f"date: {TODAY}\n"
        f"min_firmware: {MIN_FW}\n"
        f"{vehicle_line}"
        "---\n"
    )


def main() -> None:
    # Fetch directory listing from GitHub API
    print("Fetching applets directory listing…")
    data = _fetch(BASE_API)
    if data is None:
        sys.exit("Failed to fetch directory listing")

    items = json.loads(data)
    lua_names = {
        item["name"][:-4]  # stem
        for item in items
        if item["type"] == "file" and item["name"].endswith(".lua") and " " not in item["name"]  # skip filenames with spaces
    }
    md_names_lower = {
        item["name"][:-3].lower(): item["name"][:-3]  # lowercase → original stem
        for item in items
        if item["type"] == "file" and item["name"].endswith(".md") and item["name"] != "README.md"
    }

    # Find pairs with both .lua and .md
    pairs: list[tuple[str, str]] = []
    for stem in sorted(lua_names):
        md_stem = md_names_lower.get(stem.lower())
        if md_stem:
            pairs.append((stem, md_stem))

    print(f"Found {len(pairs)} applets with both .lua and .md files")

    created = 0
    skipped = 0
    for lua_stem, md_stem in pairs:
        if lua_stem in SKIP:
            print(f"  skip {lua_stem} (reserved)")
            skipped += 1
            continue

        lua_out = APPLETS_DIR / f"{lua_stem}.lua"
        md_out = APPLETS_DIR / f"{lua_stem}.md"

        if lua_out.exists() and md_out.exists():
            print(f"  skip {lua_stem} (already exists)")
            skipped += 1
            continue

        print(f"  {lua_stem} …", end=" ", flush=True)

        lua_bytes = _fetch(f"{BASE_RAW}/{lua_stem}.lua")
        md_bytes = _fetch(f"{BASE_RAW}/{md_stem}.md")

        if lua_bytes is None or md_bytes is None:
            print("FAILED")
            skipped += 1
            continue

        orig_md = md_bytes.decode("utf-8", errors="replace")
        short_desc = _extract_short_desc(orig_md, lua_stem)
        vehicles = _infer_vehicles(lua_stem, short_desc)

        frontmatter = _build_frontmatter(lua_stem, short_desc, vehicles)
        new_md = frontmatter + "\n" + orig_md

        lua_out.write_bytes(lua_bytes)
        md_out.write_text(new_md, encoding="utf-8")

        print(f"✓  ({short_desc[:60]}…)" if len(short_desc) > 60 else f"✓  ({short_desc})")
        created += 1
        time.sleep(0.05)  # be polite to GitHub

    print(f"\nDone: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
