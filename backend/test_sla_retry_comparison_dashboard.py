import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "frontend/src/components/SLARetryComparisonDashboard.tsx"
CSS = ROOT / "frontend/src/components/SLARetryComparisonDashboard.css"


class TestRetryComparisonDashboard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = COMPONENT.read_text(encoding="utf-8-sig")
        cls.styles = CSS.read_text(encoding="utf-8-sig")

    def test_component_exists(self):
        self.assertTrue(COMPONENT.exists())

    def test_uses_comparison_api(self):
        self.assertIn("/api/v1/sla/retry-comparison/", self.source)

    def test_uses_authenticated_fetch(self):
        self.assertIn("authenticatedFetch", self.source)

    def test_renders_profiles_dynamically(self):
        self.assertIn("data.profiles.map", self.source)
        self.assertIn("profile.profile.toUpperCase()", self.source)
        self.assertIn("key={profile.profile}", self.source)

    def test_displays_retry_metrics(self):
        for field in (
            "max_attempts",
            "initial_delay",
            "backoff_factor",
            "total_wait_seconds",
        ):
            self.assertIn(field, self.source)

    def test_has_loading_error_and_refresh(self):
        self.assertIn("loading", self.source)
        self.assertIn("error", self.source)
        self.assertIn("loadComparison", self.source)

    def test_css_has_responsive_layout(self):
        self.assertIn("@media", self.styles)
        self.assertIn("sla-retry-comparison-grid", self.styles)

    def test_component_imports_css(self):
        self.assertIn("SLARetryComparisonDashboard.css", self.source)


if __name__ == "__main__":
    unittest.main()
