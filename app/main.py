from fastapi import FastAPI

app = FastAPI(
    title="Fraud Alert API",
    version="0.1.0",
    description="Ingest and query fraud alerts",
)


@app.get("/health")
async def health_check():
    """Simple health check — returns OK if the server is running."""
    return {"status": "healthy"}
