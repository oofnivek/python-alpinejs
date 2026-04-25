"""Integration tests for the Items REST API."""
import pytest
from httpx import AsyncClient

from tests.conftest import make_item
from sqlalchemy.ext.asyncio import AsyncSession


class TestCreateItem:
    async def test_create_returns_201(self, client: AsyncClient):
        res = await client.post("/api/items", json={"title": "New Item"})
        assert res.status_code == 201

    async def test_create_response_shape(self, client: AsyncClient):
        res = await client.post("/api/items", json={"title": "Shape Test"})
        data = res.json()
        assert "id" in data
        assert data["title"] == "Shape Test"
        assert data["status"] == "active"
        assert "created_at" in data

    async def test_create_with_all_fields(self, client: AsyncClient):
        payload = {"title": "Full", "description": "My desc", "status": "inactive"}
        res = await client.post("/api/items", json=payload)
        data = res.json()
        assert data["description"] == "My desc"
        assert data["status"] == "inactive"

    async def test_create_missing_title_returns_422(self, client: AsyncClient):
        res = await client.post("/api/items", json={})
        assert res.status_code == 422

    async def test_create_empty_title_returns_422(self, client: AsyncClient):
        res = await client.post("/api/items", json={"title": ""})
        assert res.status_code == 422

    async def test_create_invalid_status_returns_422(self, client: AsyncClient):
        res = await client.post("/api/items", json={"title": "x", "status": "deleted"})
        assert res.status_code == 422


class TestListItems:
    async def test_list_returns_200(self, client: AsyncClient):
        res = await client.get("/api/items")
        assert res.status_code == 200

    async def test_list_response_shape(self, client: AsyncClient):
        res = await client.get("/api/items")
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data

    async def test_list_pagination(self, client: AsyncClient, db_session: AsyncSession):
        for i in range(5):
            await make_item(db_session, title=f"Paginate {i}")
        res = await client.get("/api/items?page=1&page_size=2")
        data = res.json()
        assert len(data["items"]) <= 2

    async def test_list_search(self, client: AsyncClient, db_session: AsyncSession):
        await make_item(db_session, title="Needle in a haystack")
        res = await client.get("/api/items?search=Needle")
        data = res.json()
        assert any("Needle" in i["title"] for i in data["items"])

    async def test_list_filter_status(self, client: AsyncClient, db_session: AsyncSession):
        await make_item(db_session, title="Archived One", status="archived")
        res = await client.get("/api/items?status=archived")
        data = res.json()
        for item in data["items"]:
            assert item["status"] == "archived"

    async def test_invalid_page_returns_422(self, client: AsyncClient):
        res = await client.get("/api/items?page=0")
        assert res.status_code == 422


class TestGetItem:
    async def test_get_existing_item(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session, title="Get Me")
        res = await client.get(f"/api/items/{item.id}")
        assert res.status_code == 200
        assert res.json()["id"] == item.id

    async def test_get_nonexistent_returns_404(self, client: AsyncClient):
        res = await client.get("/api/items/999999")
        assert res.status_code == 404

    async def test_get_response_includes_timestamps(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session)
        res = await client.get(f"/api/items/{item.id}")
        data = res.json()
        assert "created_at" in data
        assert "updated_at" in data


class TestUpdateItem:
    async def test_update_title(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session, title="Before")
        res = await client.patch(f"/api/items/{item.id}", json={"title": "After"})
        assert res.status_code == 200
        assert res.json()["title"] == "After"

    async def test_partial_update(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session, title="Stays", status="active")
        res = await client.patch(f"/api/items/{item.id}", json={"status": "inactive"})
        data = res.json()
        assert data["title"] == "Stays"
        assert data["status"] == "inactive"

    async def test_update_nonexistent_returns_404(self, client: AsyncClient):
        res = await client.patch("/api/items/999999", json={"title": "Ghost"})
        assert res.status_code == 404

    async def test_update_invalid_status_returns_422(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session)
        res = await client.patch(f"/api/items/{item.id}", json={"status": "broken"})
        assert res.status_code == 422


class TestDeleteItem:
    async def test_delete_returns_204(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session, title="Delete Me")
        res = await client.delete(f"/api/items/{item.id}")
        assert res.status_code == 204

    async def test_delete_removes_item(self, client: AsyncClient, db_session: AsyncSession):
        item = await make_item(db_session, title="Gone")
        await client.delete(f"/api/items/{item.id}")
        res = await client.get(f"/api/items/{item.id}")
        assert res.status_code == 404

    async def test_delete_nonexistent_returns_404(self, client: AsyncClient):
        res = await client.delete("/api/items/999999")
        assert res.status_code == 404


class TestUIRoute:
    async def test_index_returns_html(self, client: AsyncClient):
        res = await client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
