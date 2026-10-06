from fastapi import FastAPI

from app.api.v1.routes import ads, advertisers

app = FastAPI(
    title="AdIntel API",
    version="0.1.0",
    description="API local do MVP Ad Intelligence com dados simulados.",
)

app.include_router(ads.router, prefix="/api/v1")
app.include_router(advertisers.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "database": "postgresql"}
