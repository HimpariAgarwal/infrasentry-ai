import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "frontend" / "src" / "components" / "SLARetryMetricsDashboard.tsx"
STYLES = ROOT / "frontend" / "src" / "components" / "SLARetryMetricsDashboard.css"


class TestRetryMetricsDashboardFiles(unittest.TestCase):

    def test_component_exists(self):
        self.assertTrue(COMPONENT.exists())

    def test_component_uses_metrics_endpoint(self):
        source = COMPONENT.read_text(encoding="utf-8-sig")
        self.assertIn("/api/v1/sla/retry-metrics", source)
        self.assertIn("authenticatedFetch", source)

    def test_component_displays_all_metrics(self):
        source = COMPONENT.read_text(encoding="utf-8-sig")
        for field in (
            "total_runs",
            "successful_runs",
            "failed_runs",
            "total_attempts",
            "average_duration_seconds",
            "history",
        ):
            self.assertIn(field, source)

    def test_component_has_refresh_and_polling(self):
        source = COMPONENT.read_text(encoding="utf-8-sig")
        self.assertIn("setInterval", source)
        self.assertIn("loadMetrics", source)

    def test_styles_exist(self):
        self.assertTrue(STYLES.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
