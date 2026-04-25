"""Seed the database with sample data."""
import asyncio
import random

from app.database import AsyncSessionLocal
from app.models.item import Item


SAMPLE_ITEMS = [
    {"title": "Buy groceries",         "description": "Milk, eggs, bread",       "status": "active"},
    {"title": "Read Clean Architecture","description": "Chapter 5 onwards",       "status": "active"},
    {"title": "Fix login bug",          "description": "JWT expiry not handled",  "status": "inactive"},
    {"title": "Write unit tests",       "description": "Service layer coverage",  "status": "active"},
    {"title": "Deploy to staging",      "description": None,                      "status": "archived"},
    {"title": "Update README",          "description": "Add Docker instructions", "status": "active"},
    {"title": "Code review PR #42",     "description": None,                      "status": "active"},
    {"title": "Migrate to Postgres",    "description": "From SQLite",             "status": "inactive"},
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for data in SAMPLE_ITEMS:
            session.add(Item(**data))
        await session.commit()
    print(f"✅  Inserted {len(SAMPLE_ITEMS)} seed items.")


if __name__ == "__main__":
    asyncio.run(seed())
