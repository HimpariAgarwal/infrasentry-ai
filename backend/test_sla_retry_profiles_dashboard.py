import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "frontend" / "src" / "components" / "SLARetryProfilesDashboard.tsx"
CSS = ROOT / "frontend" / "src" / "components" / "SLARetryProfilesDashboard.css"


class TestSLARetryProfilesDashboard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.component = COMPONENT.read_text(encoding="utf-8-sig")
        cls.css = CSS.read_text(encoding="utf-8-sig")

    def test_component_exists(self):
        self.assertTrue(COMPONENT.exists())

    def test_component_uses_profiles_api(self):
        self.assertIn("/api/v1/sla/retry-profiles", self.component)
        self.assertIn("authenticatedFetch", self.component)

    def test_all_profile_names_are_supported(self):
        for name in ("fast", "standard", "conservative"):
            self.assertIn(name, self.component)

    def test_profile_configuration_fields_are_displayed(self):
        for field in (
            "max_attempts",
            "initial_delay",
            "backoff_factor",
        ):
            self.assertIn(field, self.component)

    def test_loading_error_and_empty_states_exist(self):
        self.assertIn("Loading retry profiles", self.component)
        self.assertIn('role="alert"', self.component)
        self.assertIn("No retry profiles are configured", self.component)

    def test_refresh_action_exists(self):
        self.assertIn("loadProfiles", self.component)
        self.assertIn("Refresh", self.component)

    def test_component_has_css_import(self):
        self.assertIn("SLARetryProfilesDashboard.css", self.component)

    def test_responsive_styles_exist(self):
        self.assertIn(".sla-retry-profiles-grid", self.css)
        self.assertIn("@media", self.css)


if __name__ == "__main__":
    unittest.main(verbosity=2)
