from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, examples=["Buy milk"])
    description: Optional[str] = Field(None, examples=["Grab 2% from the corner shop"])
    status: Literal["active", "inactive", "archived"] = "active"


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    """All fields optional for partial updates (PATCH semantics)."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[Literal["active", "inactive", "archived"]] = None


class ItemRead(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemList(BaseModel):
    items: list[ItemRead]
    total: int
    page: int
    page_size: int
    pages: int
