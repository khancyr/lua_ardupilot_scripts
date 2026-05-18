from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


SEMVER_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?$")
FIRMWARE_VERSION_RE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")
VEHICLE_TYPES = {"all", "copter", "plane", "rover"}
SCRIPT_STATUSES = {"working", "broken"}


class SemVer(str):
    __slots__ = ()

    def __new__(cls, value: str) -> "SemVer":
        value_str = str(value).strip()
        if not SEMVER_RE.fullmatch(value_str):
            raise ValueError(f"Invalid semantic version: '{value_str}'. Expected MAJOR.MINOR[.PATCH]")
        return str.__new__(cls, value_str)


class FirmwareVersion(str):
    __slots__ = ()

    def __new__(cls, value: str) -> "FirmwareVersion":
        value_str = str(value).strip()
        if not FIRMWARE_VERSION_RE.fullmatch(value_str):
            raise ValueError(f"Invalid firmware version: '{value_str}'. Expected MAJOR.MINOR[.PATCH]")
        return str.__new__(cls, value_str)


class VehicleType(str):
    __slots__ = ()

    def __new__(cls, value: str) -> "VehicleType":
        value_str = str(value).strip()
        if value_str not in VEHICLE_TYPES:
            raise ValueError(f"Invalid vehicle type: '{value_str}'. Expected one of {sorted(VEHICLE_TYPES)}")
        return str.__new__(cls, value_str)


class ScriptStatus(str):
    __slots__ = ()

    def __new__(cls, value: str) -> "ScriptStatus":
        value_str = str(value).strip()
        if value_str not in SCRIPT_STATUSES:
            raise ValueError(f"Invalid script status: '{value_str}'. Expected one of {sorted(SCRIPT_STATUSES)}")
        return str.__new__(cls, value_str)


@dataclass
class ScriptMeta:
    name: str
    type: str  # applets | drivers | tools
    short_description: str
    min_firmware: FirmwareVersion
    version: SemVer
    date: date
    download_url: str
    page_url: str
    status: ScriptStatus = field(default_factory=lambda: ScriptStatus("working"))
    vehicle: List[VehicleType] = field(default_factory=lambda: [VehicleType("all")])
    # Full markdown body - omitted from JSON list responses
    description: Optional[str] = None
