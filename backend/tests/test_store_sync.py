from __future__ import annotations

import json
from contextlib import nullcontext
from unittest import TestCase
from unittest.mock import MagicMock, patch
from uuid import UUID

from app.services.app_sync import AppSyncError, sync_app
from app.services.stores.apple_app_store import fetch_app_store_metadata
from app.services.stores.common import StoreLookupError
from app.services.stores.google_play import fetch_google_play_metadata


class GooglePlayAdapterTests(TestCase):
    @patch("app.services.stores.google_play.scrape_play_app")
    def test_maps_public_play_fields(self, scrape: MagicMock) -> None:
        scrape.return_value = {
            "title": "Brawl Stars",
            "installs": "500.000.000+",
            "score": 4.47,
            "icon": "https://play.example/icon.png",
            "genre": "Ação",
            "genreId": "GAME_ACTION",
        }

        result = fetch_google_play_metadata("com.supercell.brawlstars")

        self.assertEqual(result.title, "Brawl Stars")
        self.assertEqual(result.downloads_count, "500.000.000+")
        self.assertEqual(result.rating, 4.47)
        self.assertEqual(result.icon_url, "https://play.example/icon.png")
        self.assertEqual(result.category, "Ação")
        scrape.assert_called_once_with("com.supercell.brawlstars", lang="pt_BR", country="br")

    def test_rejects_invalid_package_id(self) -> None:
        with self.assertRaises(StoreLookupError) as raised:
            fetch_google_play_metadata("bad/id")
        self.assertEqual(raised.exception.code, "invalid_store_id")

    @patch("app.services.stores.google_play.scrape_play_app", side_effect=RuntimeError("upstream"))
    def test_hides_upstream_error_details(self, _scrape: MagicMock) -> None:
        with self.assertRaises(StoreLookupError) as raised:
            fetch_google_play_metadata("com.example.missing")
        self.assertEqual(raised.exception.code, "google_play_unavailable")
        self.assertNotIn("upstream", raised.exception.public_message)


class AppleAppStoreAdapterTests(TestCase):
    @patch("app.services.stores.apple_app_store.urlopen")
    def test_maps_lookup_fields_and_does_not_invent_downloads(self, urlopen_mock: MagicMock) -> None:
        payload = {
            "resultCount": 1,
            "results": [{
                "trackId": 1229016807,
                "trackName": "Brawl Stars",
                "averageUserRating": 4.74,
                "artworkUrl512": "https://apple.example/icon.png",
                "primaryGenreName": "Games",
            }],
        }
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps(payload).encode("utf-8")
        urlopen_mock.return_value = response

        result = fetch_app_store_metadata("1229016807", country="br")

        request = urlopen_mock.call_args.args[0]
        self.assertIn("id=1229016807", request.full_url)
        self.assertIn("country=br", request.full_url)
        self.assertEqual(result.title, "Brawl Stars")
        self.assertEqual(result.rating, 4.74)
        self.assertEqual(result.icon_url, "https://apple.example/icon.png")
        self.assertEqual(result.category, "Games")
        self.assertIsNone(result.downloads_count)

    def test_accepts_apple_id_prefix_and_rejects_non_numeric_ids(self) -> None:
        with patch("app.services.stores.apple_app_store.urlopen") as urlopen_mock:
            response = MagicMock()
            response.__enter__.return_value = response
            response.read.return_value = json.dumps({"resultCount": 1, "results": [{"trackName": "Game"}]}).encode()
            urlopen_mock.return_value = response
            fetch_app_store_metadata("id1229016807")
            self.assertIn("id=1229016807", urlopen_mock.call_args.args[0].full_url)

        with self.assertRaises(StoreLookupError) as raised:
            fetch_app_store_metadata("com.example.game")
        self.assertEqual(raised.exception.code, "invalid_store_id")

    @patch("app.services.stores.apple_app_store.urlopen")
    def test_reports_missing_app(self, urlopen_mock: MagicMock) -> None:
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"resultCount":0,"results":[]}'
        urlopen_mock.return_value = response

        with self.assertRaises(StoreLookupError) as raised:
            fetch_app_store_metadata("123456789")
        self.assertEqual(raised.exception.code, "not_found")

    @patch("app.services.stores.apple_app_store.urlopen")
    def test_rejects_unexpected_valid_json_shapes(self, urlopen_mock: MagicMock) -> None:
        for payload in ([], {"results": "unexpected"}, {"results": [None]}, {"results": [{"trackName": 7}]}):
            with self.subTest(payload=payload):
                response = MagicMock()
                response.__enter__.return_value = response
                response.read.return_value = json.dumps(payload).encode("utf-8")
                urlopen_mock.return_value = response

                with self.assertRaises(StoreLookupError) as raised:
                    fetch_app_store_metadata("123456789")
                self.assertEqual(raised.exception.code, "invalid_store_response")


class _Cursor:
    def __init__(self, row: dict | None = None) -> None:
        self.row = row

    def fetchone(self) -> dict | None:
        return self.row


class _SyncConnection:
    def __init__(self) -> None:
        self.app = {
            "id": UUID("a0000000-0000-4000-8000-000000000001"),
            "platform": "ios",
            "store_app_id": "1229016807",
        }
        self.sync_status = "mock"
        self.statements: list[str] = []

    def execute(self, query: str, _params: tuple = ()) -> _Cursor:
        compact = " ".join(query.split())
        self.statements.append(compact)
        if compact.startswith("SELECT id, platform, store_app_id"):
            return _Cursor(self.app)
        if "SET sync_status = 'syncing'" in compact:
            self.sync_status = "syncing"
        if "SET sync_status = 'error'" in compact:
            self.sync_status = "error"
        return _Cursor()


class AppSyncFailureTests(TestCase):
    @patch("app.services.app_sync.fetch_app_store_metadata", side_effect=TypeError("unexpected JSON shape"))
    def test_unexpected_adapter_exception_persists_error_state(self, _lookup: MagicMock) -> None:
        connection = _SyncConnection()
        with patch("app.services.app_sync.connect_db", return_value=nullcontext(connection)):
            with self.assertRaises(AppSyncError) as raised:
                sync_app("a0000000-0000-4000-8000-000000000001")

        self.assertEqual(raised.exception.code, "sync_failed")
        self.assertNotIn("unexpected JSON shape", raised.exception.public_message)
        self.assertEqual(connection.sync_status, "error")
        self.assertIn("SET sync_status = 'error'", connection.statements[-1])
