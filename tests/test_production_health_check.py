import unittest
from unittest.mock import patch
from urllib.error import URLError

from scripts.production_health_check import (
    check_endpoint,
    run_checks,
)


class FakeResponse:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ProductionHealthTests(unittest.TestCase):

    @patch("scripts.production_health_check.urlopen")
    def test_healthy_endpoint(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(200)

        result = check_endpoint("Frontend", "http://test/health")

        self.assertTrue(result.healthy)
        self.assertEqual(result.status_code, 200)

    @patch("scripts.production_health_check.urlopen")
    def test_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")

        result = check_endpoint("Backend", "http://test/health")

        self.assertFalse(result.healthy)
        self.assertIsNone(result.status_code)

    @patch("scripts.production_health_check.urlopen")
    def test_non_200_response(self, mock_urlopen):
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            "http://test/health", 503, "Unavailable", {}, None
        )

        result = check_endpoint("Backend", "http://test/health")

        self.assertFalse(result.healthy)
        self.assertEqual(result.status_code, 503)

    @patch("scripts.production_health_check.urlopen")
    def test_both_services_healthy(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(200)

        result = run_checks(
            "http://frontend/health",
            "http://backend/health",
        )

        self.assertTrue(result)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("scripts.production_health_check.urlopen")
    def test_one_service_unhealthy(self, mock_urlopen):
        mock_urlopen.side_effect = [
            FakeResponse(200),
            URLError("Backend unavailable"),
        ]

        result = run_checks(
            "http://frontend/health",
            "http://backend/health",
        )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
