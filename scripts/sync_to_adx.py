"""
Manual sync script — run this to push unsynced alerts from PG to ADX.

Usage:
    python scripts/sync_to_adx.py

This is a standalone script (not part of the FastAPI app).
It creates its own database session, runs the sync, and exits.

In production, you'd run this on a schedule (cron job, Azure Function timer,
or a background task inside the API). For now, we trigger it manually.
"""

import asyncio
import logging
import sys

# Add the project root to Python's path so we can import app modules
sys.path.insert(0, ".")

from app.core.database import async_session  # noqa: E402
from app.services.sync_service import sync_alerts_to_adx  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run a single sync cycle."""
    logger.info("Starting PG → ADX sync...")

    async with async_session() as db:
        result = await sync_alerts_to_adx(db)

    logger.info(f"Sync complete: {result}")


if __name__ == "__main__":
    asyncio.run(main())
