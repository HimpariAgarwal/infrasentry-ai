import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "frontend/src/App.tsx"
COMPONENT = ROOT / "frontend/src/components/SLARetryComparisonDashboard.tsx"

class TestRetryComparisonDashboardIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8-sig")

    def test_component_exists(self):
        self.assertTrue(COMPONENT.exists())

    def test_import_exists_once(self):
        line = 'import SLARetryComparisonDashboard from "./components/SLARetryComparisonDashboard";'
        self.assertEqual(self.source.count(line), 1)

    def test_render_exists_once(self):
        self.assertEqual(self.source.count("<SLARetryComparisonDashboard />"), 1)

    def test_render_follows_retry_metrics(self):
        self.assertGreater(
            self.source.index("<SLARetryComparisonDashboard />"),
            self.source.index("<SLARetryMetricsDashboard />"),
        )

    def test_dashboard_inside_sla_analytics_section(self):
        start = self.source.index('activePage === "sla-analytics"')
        end = self.source.index("</>", start)
        self.assertIn("<SLARetryComparisonDashboard />", self.source[start:end])

if __name__ == "__main__":
    unittest.main()
