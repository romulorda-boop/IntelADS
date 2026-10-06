from __future__ import annotations

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.services.stores.common import StoreLookupError, StoreMetadata


def _track_id(value: str) -> str:
    match = re.fullmatch(r"(?:id)?([0-9]+)", value.strip(), flags=re.IGNORECASE)
    if not match:
        raise StoreLookupError("O identificador do app da App Store deve ser um track ID numérico.", "invalid_store_id")
    return match.group(1)


def fetch_app_store_metadata(track_id: str, country: str = "br") -> StoreMetadata:
    """Read the public iTunes Lookup API; Apple does not publish install counts here."""
    numeric_id = _track_id(track_id)
    url = "https://itunes.apple.com/lookup?" + urlencode({"id": numeric_id, "country": country})
    request = Request(url, headers={"User-Agent": "AdIntel/1.0 (public App Store lookup)"})

    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StoreLookupError(
            "A consulta pública da App Store falhou. Tente novamente mais tarde.",
            "app_store_unavailable",
        ) from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise StoreLookupError(
            "A App Store retornou uma resposta em formato inválido.",
            "invalid_store_response",
        )

    results = payload["results"]
    if not results:
        raise StoreLookupError("Aplicativo não encontrado na App Store selecionada.", "not_found")
    result = results[0]
    if not isinstance(result, dict):
        raise StoreLookupError(
            "A App Store retornou uma resposta em formato inválido.",
            "invalid_store_response",
        )
    title = result.get("trackName")
    if not isinstance(title, str) or not title.strip():
        raise StoreLookupError("A App Store não retornou o nome do aplicativo.", "invalid_store_response")

    rating = result.get("averageUserRating")
    try:
        rating_value = float(rating) if rating is not None else None
    except (TypeError, ValueError):
        rating_value = None

    icon_url = result.get("artworkUrl512") or result.get("artworkUrl100")
    category = result.get("primaryGenreName")
    return StoreMetadata(
        title=title.strip(),
        downloads_count=None,
        rating=rating_value,
        icon_url=icon_url if isinstance(icon_url, str) and icon_url.startswith("https://") else None,
        category=category if isinstance(category, str) else None,
    )
