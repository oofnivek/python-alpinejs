"""Unit tests for Pydantic schemas – no DB required."""
import pytest
from pydantic import ValidationError

from app.schemas.item import ItemCreate, ItemUpdate


class TestItemCreate:
    def test_valid_minimal(self):
        item = ItemCreate(title="Hello")
        assert item.title == "Hello"
        assert item.status == "active"
        assert item.description is None

    def test_valid_full(self):
        item = ItemCreate(title="Full", description="desc", status="inactive")
        assert item.description == "desc"

    def test_title_required(self):
        with pytest.raises(ValidationError):
            ItemCreate()  # type: ignore[call-arg]

    def test_title_cannot_be_empty(self):
        with pytest.raises(ValidationError):
            ItemCreate(title="")

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            ItemCreate(title="x", status="deleted")  # type: ignore[arg-type]

    def test_title_max_length(self):
        with pytest.raises(ValidationError):
            ItemCreate(title="x" * 256)


class TestItemUpdate:
    def test_all_optional(self):
        update = ItemUpdate()
        assert update.title is None
        assert update.status is None

    def test_partial_title(self):
        update = ItemUpdate(title="Updated")
        assert update.title == "Updated"

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            ItemUpdate(status="deleted")  # type: ignore[arg-type]
