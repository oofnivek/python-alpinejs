from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.item import ItemCreate, ItemList, ItemRead, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/api/items", tags=["items"])


def get_service(db: AsyncSession = Depends(get_db)) -> ItemService:
    return ItemService(db)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    svc: ItemService = Depends(get_service),
) -> ItemRead:
    item = await svc.create(payload)
    return ItemRead.model_validate(item)


@router.get("", response_model=ItemList)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    svc: ItemService = Depends(get_service),
) -> ItemList:
    return await svc.list(page=page, page_size=page_size, search=search, status=status)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: int,
    svc: ItemService = Depends(get_service),
) -> ItemRead:
    item = await svc.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int,
    payload: ItemUpdate,
    svc: ItemService = Depends(get_service),
) -> ItemRead:
    item = await svc.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = await svc.update(item, payload)
    return ItemRead.model_validate(updated)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    svc: ItemService = Depends(get_service),
) -> None:
    item = await svc.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    await svc.delete(item)
