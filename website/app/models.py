from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, field_validator


class ScriptMeta(BaseModel):
    name: str
    type: str  # applets | drivers | tools
    short_description: str
    vehicle: List[str] = ["all"]
    min_firmware: str
    version: str
    date: date
    download_url: str
    doc_url: str
    # Full description (markdown body, not returned in list endpoint)
    description: Optional[str] = None

    @field_validator("short_description")
    @classmethod
    def check_length(cls, v: str) -> str:
        if len(v) > 127:
            raise ValueError(f"short_description exceeds 127 characters: {len(v)}")
        return v


class ScriptList(BaseModel):
    total: int
    page: int
    limit: int
    results: List[ScriptMeta]


class TypeCount(BaseModel):
    type: str
    count: int


class HealthResponse(BaseModel):
    status: str
    script_count: int
