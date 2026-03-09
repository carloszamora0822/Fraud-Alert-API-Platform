from fastapi import FastAPI

from app.core.config import settings
from app.routers import accounts, alerts

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Ingest and query fraud alerts",
    debug=settings.DEBUG,
)

app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Simple health check — returns OK if the server is running."""
    return {"status": "healthy"}
