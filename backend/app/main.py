from fastapi import FastAPI

from app.api.v1.routes import ads, advertisers, apps

app = FastAPI(
    title="AdIntel API",
    version="0.2.0",
    description="API Ad Intelligence com dados mock e enriquecimento sob demanda das lojas públicas.",
)

app.include_router(ads.router, prefix="/api/v1")
app.include_router(advertisers.router, prefix="/api/v1")
app.include_router(apps.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "database": "postgresql"}
