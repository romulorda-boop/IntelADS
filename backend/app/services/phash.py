from __future__ import annotations

import subprocess
from io import BytesIO
from pathlib import Path
from typing import Mapping
from urllib.parse import unquote, urlparse

import imagehash
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_ROOT = PROJECT_ROOT / "apps" / "web" / "public"
DEFAULT_HAMMING_THRESHOLD = 10


class MediaHashError(RuntimeError):
    """A media source could not be read or hashed locally."""


def resolve_local_media(value: str | None) -> Path | None:
    """Resolve a project-local media URL while rejecting remote/path traversal inputs."""
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"}:
        return None
    raw = unquote(parsed.path if parsed.scheme == "file" else value)
    if raw.startswith("/mock-media/"):
        candidate = PUBLIC_ROOT / raw.lstrip("/")
    else:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = PUBLIC_ROOT / raw.lstrip("/")
    try:
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(PROJECT_ROOT) or not resolved.is_file():
            return None
        return resolved
    except (OSError, RuntimeError):
        return None


def _hash_image(image: Image.Image) -> str:
    try:
        return str(imagehash.phash(image.convert("RGB")))
    except Exception as exc:  # Pillow can reject truncated or malformed files.
        raise MediaHashError("A imagem não pôde ser decodificada.") from exc


def compute_phash_image(path: str | Path) -> str:
    """Return the standard 64-bit perceptual hash for a local image."""
    try:
        with Image.open(path) as image:
            return _hash_image(image)
    except MediaHashError:
        raise
    except Exception as exc:
        raise MediaHashError("A imagem não pôde ser aberta.") from exc


def compute_phash_video_frame(path: str | Path, timestamp_seconds: float = 2.0) -> str:
    """Extract one frame with FFmpeg and hash it; the caller owns thumbnail fallback."""
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(timestamp_seconds),
        "-i", str(path), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, timeout=20)
        if not result.stdout:
            raise MediaHashError("O vídeo não contém frame legível no instante solicitado.")
        with Image.open(BytesIO(result.stdout)) as image:
            return _hash_image(image)
    except (OSError, subprocess.SubprocessError) as exc:
        raise MediaHashError("Não foi possível extrair o frame de vídeo com FFmpeg.") from exc


def compute_ad_phash(media_type: str, media_url: str | None, thumbnail_url: str | None) -> str:
    """Hash an image/thumbnail, preferring the 2-second video frame when available."""
    media_path = resolve_local_media(media_url)
    thumbnail_path = resolve_local_media(thumbnail_url)
    failures: list[Exception] = []

    if media_type.lower() == "video" and media_path is not None:
        try:
            return compute_phash_video_frame(media_path, 2.0)
        except MediaHashError as exc:
            failures.append(exc)

    for path in (media_path, thumbnail_path):
        if path is None or (media_type.lower() == "video" and path == media_path):
            continue
        try:
            return compute_phash_image(path)
        except MediaHashError as exc:
            failures.append(exc)

    detail = str(failures[-1]) if failures else "A origem não é um arquivo local disponível."
    raise MediaHashError(detail)


def hamming_distance(left_hash: str, right_hash: str) -> int:
    """Count differing bits between two hexadecimal perceptual hashes."""
    for value in (left_hash, right_hash):
        if not isinstance(value, str) or len(value) != 16 or any(
            character not in "0123456789abcdefABCDEF" for character in value
        ):
            raise ValueError("pHash deve conter exatamente 16 dígitos hexadecimais (64 bits).")
    try:
        left, right = int(left_hash, 16), int(right_hash, 16)
    except (TypeError, ValueError) as exc:
        raise ValueError("pHash deve conter apenas dígitos hexadecimais.") from exc
    if left < 0 or right < 0 or left.bit_length() > 64 or right.bit_length() > 64:
        raise ValueError("pHash deve caber em 64 bits.")
    return (left ^ right).bit_count()


def find_similar_pairs(
    hashes: Mapping[str, str], threshold: int = DEFAULT_HAMMING_THRESHOLD
) -> list[tuple[str, str, int]]:
    """Return each canonical (id_a, id_b, distance) pair within the threshold."""
    if threshold < 0 or threshold > 64:
        raise ValueError("O limiar de Hamming deve estar entre 0 e 64.")
    items = sorted((str(ad_id), value) for ad_id, value in hashes.items())
    pairs: list[tuple[str, str, int]] = []
    for index, (left_id, left_hash) in enumerate(items):
        for right_id, right_hash in items[index + 1 :]:
            distance = hamming_distance(left_hash, right_hash)
            if distance <= threshold:
                pairs.append((left_id, right_id, distance))
    return pairs
