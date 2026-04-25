"""Shared pytest fixtures for the entire test suite."""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import create_app
from app.models.item import Item  # noqa: F401 – registers the model

# ── In-memory SQLite for tests ────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once per test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Per-test async session with automatic rollback."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """HTTP test client wired to the overridden DB dependency."""
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Factories ──────────────────────────────────────────────────────────────────
async def make_item(
    db: AsyncSession,
    title: str = "Test Item",
    description: str | None = "A description",
    status: str = "active",
) -> Item:
    item = Item(title=title, description=description, status=status)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item
