import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "backend" / "main.py"


class TestRetryPreviewIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = MAIN.read_text(encoding="utf-8-sig")

    def test_router_import_exists(self):
        self.assertIn(
            "sla_scheduler_retry_preview_router",
            self.source,
        )

    def test_router_registration_exists(self):
        self.assertIn(
            "app.include_router(sla_retry_preview_router)",
            self.source,
        )

    def test_preview_service_exists(self):
        self.assertTrue(
            (ROOT / "backend" / "sla_scheduler_retry_preview.py").exists()
        )

    def test_preview_router_exists(self):
        self.assertTrue(
            (ROOT / "backend" / "sla_scheduler_retry_preview_router.py").exists()
        )


if __name__ == "__main__":
    unittest.main()
