import unittest

from app.main import app


class AdAnalysisOpenAPITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.openapi = app.openapi()

    def _response_schema(self, path: str, method: str) -> dict:
        node = self.openapi["paths"][path][method]["responses"]["200"]["content"]["application/json"]["schema"]
        if "$ref" in node:
            name = node["$ref"].rsplit("/", 1)[1]
            return self.openapi["components"]["schemas"][name]
        return node

    def test_search_openapi_declares_score_breakdown_and_variants(self) -> None:
        schema = self._response_schema("/api/v1/ads/search", "post")
        self.assertIn("results", schema["properties"])
        ad_schema = self.openapi["components"]["schemas"]["AdResponse"]
        self.assertIn("longevity_score", ad_schema["properties"])
        self.assertIn("score_breakdown", ad_schema["properties"])
        self.assertIn("variants", ad_schema["properties"])

    def test_detail_openapi_declares_analysis_response(self) -> None:
        schema = self._response_schema("/api/v1/ads/{ad_id}", "get")
        self.assertIn("longevity_score", schema["properties"])
        self.assertIn("score_breakdown", schema["properties"])
        self.assertIn("variants", schema["properties"])

    def test_similars_openapi_declares_score_and_variant_list(self) -> None:
        schema = self._response_schema("/api/v1/ads/{ad_id}/similars", "get")
        for key in ("longevity_score", "badge", "score_breakdown", "results"):
            self.assertIn(key, schema["properties"])


if __name__ == "__main__":
    unittest.main()
