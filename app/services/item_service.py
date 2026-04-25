import math
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemList, ItemRead, ItemUpdate


class ItemService:
    """All database operations for the Item resource."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────
    async def create(self, payload: ItemCreate) -> Item:
        item = Item(**payload.model_dump())
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    # ── Read (single) ─────────────────────────────────────────────────────────
    async def get(self, item_id: int) -> Optional[Item]:
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        return result.scalar_one_or_none()

    # ── Read (list) ───────────────────────────────────────────────────────────
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> ItemList:
        query = select(Item)

        if search:
            query = query.where(Item.title.ilike(f"%{search}%"))
        if status:
            query = query.where(Item.status == status)

        # Total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        # Paginated rows
        offset = (page - 1) * page_size
        result = await self.db.execute(
            query.order_by(Item.created_at.desc()).offset(offset).limit(page_size)
        )
        items = result.scalars().all()

        return ItemList(
            items=[ItemRead.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=math.ceil(total / page_size) if total else 1,
        )

    # ── Update ────────────────────────────────────────────────────────────────
    async def update(self, item: Item, payload: ItemUpdate) -> Item:
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        await self.db.flush()
        await self.db.refresh(item)
        return item

    # ── Delete ────────────────────────────────────────────────────────────────
    async def delete(self, item: Item) -> None:
        await self.db.delete(item)
        await self.db.flush()
