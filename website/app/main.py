from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import markdown as md_lib
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import HealthResponse, ScriptList, ScriptMeta, TypeCount
from .scripts import get_index, get_lua_path, get_script

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ArduPilot Lua Community Scripts",
    description="Browse and download community Lua scripts for ArduPilot.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/scripts", response_class=HTMLResponse, include_in_schema=False)
async def browse(
    request: Request,
    q: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    vehicle: Optional[str] = Query(default=None),
):
    results = _filter_scripts(q=q, script_type=type, vehicle=vehicle)
    return templates.TemplateResponse(
        request,
        "browse.html",
        {
            "scripts": results,
            "q": q or "",
            "type": type or "",
            "vehicle": vehicle or "",
            "types": _get_types(),
        },
    )


@app.get("/api-reference", response_class=HTMLResponse, include_in_schema=False)
async def api_reference(request: Request):
    return templates.TemplateResponse(request, "api_docs.html")


@app.get("/contribute", response_class=HTMLResponse, include_in_schema=False)
async def contribute(request: Request):
    return templates.TemplateResponse(request, "contribute.html")


@app.get("/scripts/{script_type}/{name}", response_class=HTMLResponse, include_in_schema=False)
async def script_detail(request: Request, script_type: str, name: str):
    script = get_script(script_type, name)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    rendered_html = md_lib.markdown(script.description or "", extensions=["tables", "fenced_code"])
    return templates.TemplateResponse(
        request,
        "script.html",
        {"script": script, "description_html": rendered_html},
    )


# ---------------------------------------------------------------------------
# GCS REST API
# ---------------------------------------------------------------------------


@app.get("/api/v1/health", response_model=HealthResponse, tags=["API"])
async def health():
    return HealthResponse(status="ok", script_count=len(get_index()))


@app.get("/api/v1/types", response_model=List[TypeCount], tags=["API"])
async def list_types():
    counts: dict[str, int] = {}
    for s in get_index():
        counts[s.type] = counts.get(s.type, 0) + 1
    return [TypeCount(type=t, count=c) for t, c in sorted(counts.items())]


@app.get("/api/v1/scripts", response_model=ScriptList, tags=["API"])
async def list_scripts(
    q: Optional[str] = Query(default=None, description="Search in name and short_description"),
    type: Optional[str] = Query(default=None, description="Filter by type: applets, drivers, tools"),
    vehicle: Optional[str] = Query(default=None, description="Filter by vehicle: copter, plane, rover"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
):
    results = _filter_scripts(q=q, script_type=type, vehicle=vehicle)
    total = len(results)
    start = (page - 1) * limit
    paged = results[start : start + limit]
    # Strip description body from list responses
    for s in paged:
        s.description = None
    return ScriptList(total=total, page=page, limit=limit, results=paged)


@app.get("/api/v1/scripts/{script_type}/{name}", response_model=ScriptMeta, tags=["API"])
async def get_script_detail(script_type: str, name: str):
    script = get_script(script_type, name)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@app.get("/api/v1/scripts/{script_type}/{name}/raw", tags=["API"])
async def download_script(script_type: str, name: str):
    script = get_script(script_type, name)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    lua_path = get_lua_path(script_type, name)
    if not lua_path or not lua_path.exists():
        raise HTTPException(status_code=404, detail="Lua file not found on disk")
    return FileResponse(
        path=str(lua_path),
        media_type="text/plain",
        filename=f"{name}.lua",
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _filter_scripts(
    q: Optional[str],
    script_type: Optional[str],
    vehicle: Optional[str],
) -> List[ScriptMeta]:
    results = list(get_index())
    if q:
        q_lower = q.lower()
        results = [s for s in results if q_lower in s.name.lower() or q_lower in s.short_description.lower()]
    if script_type:
        results = [s for s in results if s.type == script_type]
    if vehicle:
        results = [s for s in results if "all" in s.vehicle or vehicle.lower() in [v.lower() for v in s.vehicle]]
    return results


def _get_types() -> List[str]:
    return sorted({s.type for s in get_index()})
