import shutil
import unittest
from pathlib import Path

from app.services.phash import (
    DEFAULT_HAMMING_THRESHOLD,
    compute_ad_phash,
    compute_phash_image,
    find_similar_pairs,
    hamming_distance,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEDIA = PROJECT_ROOT / "apps" / "web" / "public" / "mock-media"


class PerceptualHashTests(unittest.TestCase):
    def test_hamming_counts_changed_bits(self) -> None:
        self.assertEqual(hamming_distance("0000000000000000", "00000000000003ff"), 10)
        self.assertEqual(hamming_distance("0000000000000000", "00000000000007ff"), 11)

    def test_pairs_include_threshold_and_exclude_transitive_only_pairs(self) -> None:
        pairs = find_similar_pairs(
            {"a": "0000000000000000", "b": "0000000000000001", "c": "0000000000000003"},
            threshold=1,
        )
        self.assertEqual(pairs, [("a", "b", 1), ("b", "c", 1)])
        self.assertEqual(DEFAULT_HAMMING_THRESHOLD, 10)

    def test_local_thumbnail_generates_64_bit_hash(self) -> None:
        image = MEDIA / "fitness-app.png"
        self.assertTrue(image.is_file())
        value = compute_phash_image(image)
        self.assertEqual(len(value), 16)
        self.assertTrue(all(char in "0123456789abcdef" for char in value))

    @unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg não está instalado")
    def test_video_prefers_frame_at_two_seconds_and_returns_hash(self) -> None:
        value = compute_ad_phash("video", "/mock-media/gameplay.mp4", "/mock-media/gameplay.webp")
        self.assertEqual(len(value), 16)


if __name__ == "__main__":
    unittest.main()


class PerceptualHashValidationTests(unittest.TestCase):
    def test_hamming_rejects_hashes_that_are_not_exactly_64_bits(self) -> None:
        for invalid in ("0", "000000000000000", "00000000000000000", "00000000000000xz"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                hamming_distance(invalid, "0000000000000000")
