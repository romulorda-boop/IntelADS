from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


Category = Literal["games", "ecommerce", "apps", "finance", "infoproducts"]
TargetOS = Literal["android", "ios", "desktop"]
Network = Literal["meta", "tiktok", "google", "kwai"]
SortBy = Literal["longevity_score_desc", "first_seen_desc", "active_days_desc"]


class AdSearchRequest(BaseModel):
    query: str | None = Field(default=None, max_length=160)
    category: Category | None = None
    target_os: list[TargetOS] = Field(default_factory=list)
    networks: list[Network] = Field(default_factory=list)
    min_longevity_score: int | None = Field(default=None, ge=0, le=100)
    # Optional bounds make the full Winner/Scaling/Testing bands selectable in the UI.
    max_longevity_score: int | None = Field(default=None, ge=0, le=100)
    is_active_only: bool = True
    sort_by: SortBy = "longevity_score_desc"
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=40)
    advertiser_id: str | None = Field(default=None, max_length=36)

    @field_validator("target_os", "networks")
    @classmethod
    def remove_duplicate_values(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(values))
