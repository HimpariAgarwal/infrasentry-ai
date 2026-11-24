import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "frontend" / "src" / "App.tsx"


class TestRetryDashboardIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = APP.read_text(encoding="utf-8-sig")

    def test_component_import_exists(self):
        self.assertIn(
            'import SLARetryMetricsDashboard from "./components/SLARetryMetricsDashboard";',
            self.source
        )

    def test_component_is_rendered(self):
        self.assertIn("<SLARetryMetricsDashboard />", self.source)

    def test_existing_sla_controls_are_preserved(self):
        self.assertIn("<SLASchedulerControls />", self.source)

    def test_dashboard_is_inside_sla_analytics_section(self):
        position = self.source.find("<SLASchedulerControls />")
        dashboard_position = self.source.find("<SLARetryMetricsDashboard />")
        self.assertGreater(dashboard_position, position)
        self.assertLess(dashboard_position - position, 500)

    def test_dashboard_component_file_exists(self):
        component = ROOT / "frontend" / "src" / "components" / "SLARetryMetricsDashboard.tsx"
        self.assertTrue(component.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
