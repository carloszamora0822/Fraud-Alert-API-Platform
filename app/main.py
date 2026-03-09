from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Ingest and query fraud alerts",
    debug=settings.DEBUG,
)


@app.get("/health")
async def health_check():
    """Simple health check — returns OK if the server is running."""
    return {"status": "healthy"}
