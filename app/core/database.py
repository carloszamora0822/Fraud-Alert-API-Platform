from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Engine — the actual connection to PostgreSQL.
# echo=True logs every SQL statement (handy for learning, turn off in prod).
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Session factory — call this to get a fresh session for each request.
# expire_on_commit=False means we can still read object attributes after committing.
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    Dependency that FastAPI will inject into route handlers.
    Opens a session, yields it for the route to use, then closes it.
    """
    async with async_session() as session:
        yield session
