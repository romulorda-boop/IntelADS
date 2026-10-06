from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    active_days: int = Field(ge=0)
    active_points: float = Field(ge=0)
    appearances_last_30_days: int = Field(ge=0)
    appearance_points: int = Field(ge=0, le=20)
    variations_count: int = Field(ge=0)
    variation_points: int = Field(ge=0, le=20)
    score: int = Field(ge=0, le=100)
