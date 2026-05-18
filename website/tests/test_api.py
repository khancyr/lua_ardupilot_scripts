from __future__ import annotations


async def test_api_reference_page(client):
    r = await client.get("/api-reference")
    assert r.status_code == 200
    assert b"API Reference" in r.content


async def test_contribute_page(client):
    r = await client.get("/contribute")
    assert r.status_code == 200
    assert b"discuss.ardupilot.org" in r.content


async def test_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["script_count"] >= 0


async def test_list_scripts(client):
    r = await client.get("/api/v1/scripts")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "results" in data
    assert isinstance(data["results"], list)


async def test_list_scripts_search(client):
    r = await client.get("/api/v1/scripts?q=hello")
    assert r.status_code == 200


async def test_list_scripts_filter_type(client):
    r = await client.get("/api/v1/scripts?type=applets")
    assert r.status_code == 200
    for s in r.json()["results"]:
        assert s["type"] == "applets"


async def test_types_endpoint(client):
    r = await client.get("/api/v1/types")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_script_detail_not_found(client):
    r = await client.get("/api/v1/scripts/applets/DoesNotExist")
    assert r.status_code == 404


async def test_script_detail(client):
    r = await client.get("/api/v1/scripts/applets/HelloWorld")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "HelloWorld"
    assert "version" in data
    assert "date" in data


async def test_script_raw(client):
    r = await client.get("/api/v1/scripts/applets/HelloWorld/raw")
    assert r.status_code == 200
    assert b"update" in r.content


async def test_home_page(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert b"ArduPilot" in r.content


async def test_browse_page(client):
    r = await client.get("/scripts")
    assert r.status_code == 200


async def test_script_detail_page(client):
    r = await client.get("/scripts/applets/HelloWorld")
    assert r.status_code == 200
