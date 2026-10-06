from __future__ import annotations

from pydantic import BaseModel


class LinkedApp(BaseModel):
    title: str
    store_id: str
    downloads: str | None = None
    platform: str


class AdvertiserProfile(BaseModel):
    advertiser_id: str
    name: str
    domain: str | None = None
    total_ads_captured: int
    active_ads: int
    inactive_ads: int
    os_distribution: dict[str, float]
    network_distribution: dict[str, float]
    apps_linked: list[LinkedApp]
