import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICE = ROOT / "frontend" / "src" / "services" / "slaRetryReportService.ts"
COMPONENT = ROOT / "frontend" / "src" / "components" / "SLARetryMetricsDashboard.tsx"
CSS = ROOT / "frontend" / "src" / "components" / "SLARetryMetricsDashboard.css"


class TestRetryReportExports(unittest.TestCase):

    def test_export_service_exists(self):
        self.assertTrue(SERVICE.exists())

    def test_csv_and_pdf_exports_exist(self):
        source = SERVICE.read_text(encoding="utf-8-sig")
        self.assertIn("exportRetryMetricsCSV", source)
        self.assertIn("exportRetryMetricsPDF", source)
        self.assertIn("sla-retry-metrics.csv", source)
        self.assertIn("sla-retry-metrics.pdf", source)

    def test_dashboard_imports_export_functions(self):
        source = COMPONENT.read_text(encoding="utf-8-sig")
        self.assertIn("exportRetryMetricsCSV", source)
        self.assertIn("exportRetryMetricsPDF", source)

    def test_dashboard_has_export_actions(self):
        source = COMPONENT.read_text(encoding="utf-8-sig")
        self.assertIn("exportRetryMetricsCSV(metrics)", source)
        self.assertIn("exportRetryMetricsPDF(metrics)", source)
        self.assertIn("Export CSV", source)
        self.assertIn("Export PDF", source)

    def test_export_styles_exist(self):
        source = CSS.read_text(encoding="utf-8-sig")
        self.assertIn(".sla-retry-export", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
