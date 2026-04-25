"""Unit tests for ItemService – no HTTP, pure service layer."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.item import ItemCreate, ItemUpdate
from app.services.item_service import ItemService
from tests.conftest import make_item


# ── Create ──────────────────────────────────────────────────────────────────
class TestItemServiceCreate:
    async def test_creates_item_with_required_fields(self, db_session: AsyncSession):
        svc = ItemService(db_session)
        item = await svc.create(ItemCreate(title="Hello"))
        assert item.id is not None
        assert item.title == "Hello"
        assert item.status == "active"

    async def test_creates_item_with_all_fields(self, db_session: AsyncSession):
        svc = ItemService(db_session)
        item = await svc.create(
            ItemCreate(title="Full", description="desc", status="inactive")
        )
        assert item.description == "desc"
        assert item.status == "inactive"

    async def test_create_sets_timestamps(self, db_session: AsyncSession):
        svc = ItemService(db_session)
        item = await svc.create(ItemCreate(title="Timestamps"))
        assert item.created_at is not None
        assert item.updated_at is not None


# ── Get ─────────────────────────────────────────────────────────────────────
class TestItemServiceGet:
    async def test_get_existing_item(self, db_session: AsyncSession):
        created = await make_item(db_session, title="Find me")
        svc = ItemService(db_session)
        found = await svc.get(created.id)
        assert found is not None
        assert found.id == created.id

    async def test_get_nonexistent_returns_none(self, db_session: AsyncSession):
        svc = ItemService(db_session)
        result = await svc.get(999_999)
        assert result is None


# ── List ─────────────────────────────────────────────────────────────────────
class TestItemServiceList:
    async def test_lists_all_items(self, db_session: AsyncSession):
        for i in range(3):
            await make_item(db_session, title=f"Item {i}")
        svc = ItemService(db_session)
        result = await svc.list()
        assert result.total >= 3

    async def test_pagination_page_size(self, db_session: AsyncSession):
        for i in range(5):
            await make_item(db_session, title=f"Paged {i}")
        svc = ItemService(db_session)
        result = await svc.list(page=1, page_size=2)
        assert len(result.items) <= 2

    async def test_search_filters_by_title(self, db_session: AsyncSession):
        await make_item(db_session, title="Unique Needle")
        await make_item(db_session, title="Boring Haystack")
        svc = ItemService(db_session)
        result = await svc.list(search="Needle")
        titles = [i.title for i in result.items]
        assert any("Needle" in t for t in titles)
        assert not any("Haystack" in t for t in titles)

    async def test_filter_by_status(self, db_session: AsyncSession):
        await make_item(db_session, title="Active One",   status="active")
        await make_item(db_session, title="Inactive One", status="inactive")
        svc = ItemService(db_session)
        result = await svc.list(status="inactive")
        for item in result.items:
            assert item.status == "inactive"

    async def test_pages_calculation(self, db_session: AsyncSession):
        svc = ItemService(db_session)
        result = await svc.list(page=1, page_size=1)
        assert result.pages >= 1


# ── Update ──────────────────────────────────────────────────────────────────
class TestItemServiceUpdate:
    async def test_updates_title(self, db_session: AsyncSession):
        item = await make_item(db_session, title="Old")
        svc = ItemService(db_session)
        updated = await svc.update(item, ItemUpdate(title="New"))
        assert updated.title == "New"

    async def test_partial_update_preserves_other_fields(self, db_session: AsyncSession):
        item = await make_item(db_session, title="Keep", description="Stay")
        svc = ItemService(db_session)
        updated = await svc.update(item, ItemUpdate(status="inactive"))
        assert updated.title == "Keep"
        assert updated.description == "Stay"
        assert updated.status == "inactive"

    async def test_update_with_no_fields_is_noop(self, db_session: AsyncSession):
        item = await make_item(db_session, title="Unchanged")
        svc = ItemService(db_session)
        updated = await svc.update(item, ItemUpdate())
        assert updated.title == "Unchanged"


# ── Delete ───────────────────────────────────────────────────────────────────
class TestItemServiceDelete:
    async def test_deletes_item(self, db_session: AsyncSession):
        item = await make_item(db_session, title="Bye")
        item_id = item.id
        svc = ItemService(db_session)
        await svc.delete(item)
        result = await svc.get(item_id)
        assert result is None
