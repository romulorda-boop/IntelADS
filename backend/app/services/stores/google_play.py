from __future__ import annotations

from google_play_scraper import app as scrape_play_app

from app.services.stores.common import StoreLookupError, StoreMetadata


def _format_install_bucket(value: object) -> str | None:
    if value is None:
        return None
    # google-play-scraper returns the public install bucket, e.g. "100,000,000+".
    return str(value).replace(",", ".")


def fetch_google_play_metadata(package_id: str) -> StoreMetadata:
    """Read the public Play listing; installs are a public range, not an exact count."""
    package_id = package_id.strip()
    if not package_id or "/" in package_id:
        raise StoreLookupError("O identificador do pacote Google Play é inválido.", "invalid_store_id")

    try:
        result = scrape_play_app(package_id, lang="pt_BR", country="br")
    except Exception as exc:
        raise StoreLookupError(
            "A Google Play não respondeu à consulta. Tente novamente mais tarde.",
            "google_play_unavailable",
        ) from exc

    title = result.get("title")
    if not title:
        raise StoreLookupError("Aplicativo não encontrado na Google Play.", "not_found")

    rating = result.get("score")
    try:
        rating_value = float(rating) if rating is not None else None
    except (TypeError, ValueError):
        rating_value = None

    return StoreMetadata(
        title=str(title),
        downloads_count=_format_install_bucket(result.get("installs")),
        rating=rating_value,
        icon_url=result.get("icon"),
        category=result.get("genre") or result.get("genreId"),
    )
