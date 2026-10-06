from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoreMetadata:
    title: str
    downloads_count: str | None
    rating: float | None
    icon_url: str | None
    category: str | None


class StoreLookupError(Exception):
    def __init__(self, public_message: str, code: str = "store_unavailable") -> None:
        super().__init__(public_message)
        self.public_message = public_message
        self.code = code
