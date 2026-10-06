from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.ad_analysis import ScoreBreakdown
from app.schemas.ads import Category, Network, TargetOS


ScoreBadge = Literal["Winner", "Scaling", "Testing"]


class AdvertiserSummaryResponse(BaseModel):
    id: str
    name: str


class AppSummaryResponse(BaseModel):
    id: str
    store_app_id: str | None
    title: str
    platform: str
    downloads_count: str | None
    rating: float | None
    icon_url: str | None
    sync_status: Literal["mock", "syncing", "synced", "error"]
    last_synced_at: str | None


class AdVariantResponse(BaseModel):
    id: str
    title: str
    source_network: Network
    thumbnail_url: str
    hamming_distance: int = Field(ge=0, le=64)


class AdResponse(BaseModel):
    id: str
    title: str
    caption: str | None
    media_type: str
    media_url: str
    thumbnail_url: str
    source_network: Network
    category: Category
    target_os: list[TargetOS]
    longevity_score: int = Field(ge=0, le=100)
    badge: ScoreBadge
    score_breakdown: ScoreBreakdown
    active_days: int = Field(ge=0)
    first_seen_at: str
    is_active: bool
    variations_count: int = Field(ge=0)
    variants: list[AdVariantResponse]
    destination_url: str | None
    advertiser: AdvertiserSummaryResponse | None
    app: AppSummaryResponse | None


class AdSearchResponse(BaseModel):
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    results: list[AdResponse]


class SimilarAdsResponse(BaseModel):
    ad_id: str
    hamming_threshold: int = Field(ge=0, le=64)
    longevity_score: int = Field(ge=0, le=100)
    badge: ScoreBadge
    score_breakdown: ScoreBreakdown
    results: list[AdVariantResponse]
