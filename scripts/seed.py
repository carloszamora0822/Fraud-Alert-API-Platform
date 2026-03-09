"""
Database seed script.

Run with:  python -m scripts.seed

Generates fake accounts and fraud alerts, then inserts them into PostgreSQL
using our existing CRUD service layer. Batches inserts to avoid holding
one giant transaction in memory.
"""

import asyncio
import sys
import time

from app.core.database import async_session
from app.services.account import create_account
from app.services.alert import create_alert
from scripts.generate import generate_accounts, generate_alerts

# How many of each to create.
NUM_ACCOUNTS = 20
NUM_ALERTS = 10_000
BATCH_SIZE = 500  # commit every N alerts to keep transactions small


async def seed() -> None:
    """Main seeding logic."""
    start = time.time()

    async with async_session() as db:
        # ── Step 1: Create accounts ──────────────────────────────────
        print(f"Creating {NUM_ACCOUNTS} accounts...")
        account_schemas = generate_accounts(NUM_ACCOUNTS)
        account_ids = []

        for schema in account_schemas:
            account = await create_account(db, schema)
            account_ids.append(account.id)

        print(f"  ✓ {NUM_ACCOUNTS} accounts created")

        # ── Step 2: Generate all alerts in memory ────────────────────
        print(f"\nGenerating {NUM_ALERTS:,} alerts...")
        alert_schemas = generate_alerts(account_ids, NUM_ALERTS)
        print("  ✓ Generated in memory")

        # ── Step 3: Insert alerts in batches ─────────────────────────
        print(f"\nInserting alerts (batch size {BATCH_SIZE})...")
        for i, schema in enumerate(alert_schemas, start=1):
            await create_alert(db, schema)

            if i % BATCH_SIZE == 0:
                print(f"  {i:,}/{NUM_ALERTS:,} inserted...")

        print(f"  ✓ All {NUM_ALERTS:,} alerts inserted")

    elapsed = time.time() - start
    print(
        f"\nDone! Seeded {NUM_ACCOUNTS} accounts"
        f" + {NUM_ALERTS:,} alerts in {elapsed:.1f}s"
    )


if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
