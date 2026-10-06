import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from uuid import UUID

from app.services.ad_analysis import run_ad_analysis
from app.services.phash import MediaHashError
from app.workers.analyze_ads import main as run_worker_cli


class _FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows


class _FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.statements = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, _params=None):
        self.statements.append(statement)
        if not statement.lstrip().startswith("SELECT id, media_type"):
            raise AssertionError("Uma análise com erro de mídia não deve gravar estado parcial.")
        return _FakeResult(self.rows)


class AnalysisAtomicityTests(unittest.TestCase):
    def test_media_error_aborts_before_database_writes(self) -> None:
        ads = [
            {"id": UUID("00000000-0000-4000-8000-000000000001"), "media_type": "image", "media_url": "/missing-a.png", "thumbnail_url": "/missing-a.png"},
            {"id": UUID("00000000-0000-4000-8000-000000000002"), "media_type": "image", "media_url": "/missing-b.png", "thumbnail_url": "/missing-b.png"},
        ]
        connection = _FakeConnection(ads)
        with patch("app.services.ad_analysis.connect_db", return_value=connection), patch(
            "app.services.ad_analysis.compute_ad_phash",
            side_effect=["0123456789abcdef", MediaHashError("thumbnail ausente")],
        ):
            report = run_ad_analysis()
        self.assertFalse(report["committed"])
        self.assertEqual(report["hashes_generated"], 1)
        self.assertEqual(report["scores_updated"], 0)
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(len(connection.statements), 1)

    def test_cli_returns_nonzero_for_incomplete_analysis(self) -> None:
        result = {"ads_processed": 1, "committed": False, "errors": [{"ad_id": "x", "error": "mídia inválida"}]}
        output = StringIO()
        with patch("app.workers.analyze_ads.run_ad_analysis", return_value=result), redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                run_worker_cli()
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(json.loads(output.getvalue()), result)


if __name__ == "__main__":
    unittest.main()
