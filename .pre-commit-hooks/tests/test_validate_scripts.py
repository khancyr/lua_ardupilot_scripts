"""Tests for validate_scripts.py"""

from __future__ import annotations

import sys
import textwrap
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate_scripts import main, parse_frontmatter, validate_date  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_FM = textwrap.dedent("""\
    ---
    name: MyScript
    short_description: A short description
    version: 1.0.0
    date: 2024-01-15
    min_firmware: "4.5"
    ---
""")


def _make_pair(
    root: Path,
    dir_name: str,
    stem: str,
    frontmatter: str = _VALID_FM,
    lua: str = "-- lua\n",
) -> None:
    d = root / "lua" / dir_name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{stem}.lua").write_text(lua, encoding="utf-8")
    (d / f"{stem}.md").write_text(frontmatter, encoding="utf-8")


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid(self, tmp_path: Path) -> None:
        md = tmp_path / "test.md"
        md.write_text(_VALID_FM, encoding="utf-8")
        fm = parse_frontmatter(md)
        assert fm is not None
        assert fm["name"] == "MyScript"
        assert fm["version"] == "1.0.0"

    def test_no_frontmatter(self, tmp_path: Path) -> None:
        md = tmp_path / "test.md"
        md.write_text("No frontmatter here.\n", encoding="utf-8")
        assert parse_frontmatter(md) is None

    def test_empty_frontmatter_block(self, tmp_path: Path) -> None:
        md = tmp_path / "test.md"
        # Regex requires a newline before the closing ---
        md.write_text("---\n\n---\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}


# ---------------------------------------------------------------------------
# validate_date
# ---------------------------------------------------------------------------


class TestValidateDate:
    @pytest.mark.parametrize("value", ["2024-01-15", "2000-12-31", date(2024, 6, 1)])
    def test_valid(self, value: object) -> None:
        assert validate_date(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "15-01-2024",  # wrong order
            "2024/01/15",  # wrong separator
            "not-a-date",  # garbage
            "2024-13-01",  # month 13
            "2024-02-30",  # Feb 30
        ],
    )
    def test_invalid(self, value: str) -> None:
        assert validate_date(value) is False


# ---------------------------------------------------------------------------
# main() - integration via tmp_path
# ---------------------------------------------------------------------------


class TestMain:
    # --- happy paths ---

    def test_no_script_dirs(self, tmp_path: Path) -> None:
        """Repo with no applets/drivers/tools at all is valid."""
        assert main(tmp_path) == 0

    def test_single_valid_script(self, tmp_path: Path) -> None:
        _make_pair(tmp_path, "applets", "Hello")
        assert main(tmp_path) == 0

    def test_multiple_valid_scripts_across_dirs(self, tmp_path: Path) -> None:
        for dir_name, stem, name in [
            ("applets", "Hello", "Hello"),
            ("drivers", "MyDriver", "MyDriver"),
            ("tools", "MyTool", "MyTool"),
        ]:
            _make_pair(
                tmp_path,
                dir_name,
                stem,
                frontmatter=textwrap.dedent(f"""\
                    ---
                    name: {name}
                    short_description: desc
                    version: 1.0.0
                    date: 2024-01-15
                    min_firmware: "4.5"
                    ---
                """),
            )
        assert main(tmp_path) == 0

    # --- Rule 1: .lua without .md ---

    def test_lua_missing_md(self, tmp_path: Path) -> None:
        d = tmp_path / "lua" / "applets"
        d.mkdir(parents=True)
        (d / "Orphan.lua").write_text("-- lua\n", encoding="utf-8")
        assert main(tmp_path) == 1

    # --- Rule 2: .md without .lua ---

    def test_md_missing_lua(self, tmp_path: Path) -> None:
        d = tmp_path / "lua" / "applets"
        d.mkdir(parents=True)
        (d / "Orphan.md").write_text(_VALID_FM, encoding="utf-8")
        assert main(tmp_path) == 1

    # --- Rule 3: missing frontmatter ---

    def test_missing_frontmatter_block(self, tmp_path: Path) -> None:
        _make_pair(tmp_path, "applets", "Test", frontmatter="No YAML here.\n")
        assert main(tmp_path) == 1

    @pytest.mark.parametrize("missing_field", ["name", "short_description", "version", "date", "min_firmware"])
    def test_missing_required_field(self, tmp_path: Path, missing_field: str) -> None:
        fields = {
            "name": "Test",
            "short_description": "A desc",
            "version": "1.0.0",
            "date": "2024-01-15",
            "min_firmware": "4.5",
        }
        del fields[missing_field]
        fm = "---\n" + "\n".join(f"{k}: {v}" for k, v in fields.items()) + "\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 4: short_description length ---

    def test_short_description_exactly_127_chars(self, tmp_path: Path) -> None:
        desc = "x" * 127
        fm = f"---\nname: Test\nshort_description: {desc}\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 0

    def test_short_description_too_long(self, tmp_path: Path) -> None:
        desc = "x" * 128
        fm = f"---\nname: Test\nshort_description: {desc}\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 5: semver version ---

    @pytest.mark.parametrize("version", ["1.0.0", "0.1.0", "12.34.56", "1.0", "1.0.0-beta", "2.3.1+build.1"])
    def test_valid_semver(self, tmp_path: Path, version: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: {version}\ndate: 2024-01-15\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 0

    @pytest.mark.parametrize("version", ["v1.0.0", "latest"])
    def test_invalid_semver(self, tmp_path: Path, version: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: {version}\ndate: 2024-01-15\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 6: ISO date ---

    def test_invalid_date_format(self, tmp_path: Path) -> None:
        fm = "---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 15-01-2024\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    def test_invalid_calendar_date(self, tmp_path: Path) -> None:
        fm = "---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-02-30\nmin_firmware: 4.5\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 7: min_firmware format ---

    @pytest.mark.parametrize("fw", ["4.5", "4.3", "4.5.0", "4.10.2", "5.0"])
    def test_valid_min_firmware(self, tmp_path: Path, fw: str) -> None:
        fm = f'---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: "{fw}"\n---\n'
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 0

    @pytest.mark.parametrize("fw", ["4", "latest", "v4.5", "4.5.0.1"])
    def test_invalid_min_firmware(self, tmp_path: Path, fw: str) -> None:
        fm = f'---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: "{fw}"\n---\n'
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 8: vehicle values ---

    @pytest.mark.parametrize("vehicle", ["all", "copter", "plane", "rover", "[copter, plane]"])
    def test_valid_vehicle(self, tmp_path: Path, vehicle: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\nvehicle: {vehicle}\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 0

    @pytest.mark.parametrize("vehicle", ["helicopter", "submarine", "[copter, helicopter]"])
    def test_invalid_vehicle(self, tmp_path: Path, vehicle: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\nvehicle: {vehicle}\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 9: status values ---

    @pytest.mark.parametrize("status", ["working", "broken"])
    def test_valid_status(self, tmp_path: Path, status: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\nstatus: {status}\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 0

    def test_status_absent_defaults_to_working(self, tmp_path: Path) -> None:
        _make_pair(tmp_path, "applets", "Test")
        assert main(tmp_path) == 0

    @pytest.mark.parametrize("status", ["ok", "unknown", "yes"])
    def test_invalid_status(self, tmp_path: Path, status: str) -> None:
        fm = f"---\nname: Test\nshort_description: desc\nversion: 1.0.0\ndate: 2024-01-15\nmin_firmware: 4.5\nstatus: {status}\n---\n"
        _make_pair(tmp_path, "applets", "Test", frontmatter=fm)
        assert main(tmp_path) == 1

    # --- Rule 10: unique names ---

    def test_duplicate_name_across_dirs(self, tmp_path: Path) -> None:
        _make_pair(tmp_path, "applets", "Hello")
        # same `name:` field as _VALID_FM ("MyScript")
        _make_pair(tmp_path, "drivers", "World")
        assert main(tmp_path) == 1

    def test_same_stem_different_name_ok(self, tmp_path: Path) -> None:
        _make_pair(tmp_path, "applets", "Hello")
        fm2 = textwrap.dedent("""\
            ---
            name: OtherScript
            short_description: Something else
            version: 2.0.0
            date: 2025-03-10
            min_firmware: "4.5"
            ---
        """)
        _make_pair(tmp_path, "drivers", "Hello", frontmatter=fm2)
        assert main(tmp_path) == 0
