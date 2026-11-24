import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestReleaseIntegrity(unittest.TestCase):

    def test_required_files(self):
        files = [
            "backend/main.py",
            "backend/auth_router.py",
            "backend/system_router.py",
            "backend/system_diagnostics.py",
            "backend/test_readiness_api.py",
            "backend/test_system_diagnostics_api.py",
            "docs/day105_protected_readiness_api.md",
        ]
        for item in files:
            with self.subTest(file=item):
                self.assertTrue((ROOT / item).is_file(), item)

    def test_protected_endpoints(self):
        source = (ROOT / "backend/system_router.py").read_text(encoding="utf-8-sig")
        self.assertIn('"/readiness"', source)
        self.assertIn('"/system-diagnostics"', source)
        self.assertIn("Depends(get_current_user)", source)

    def test_gitignore_rules(self):
        source = (ROOT / ".gitignore").read_text(encoding="utf-8-sig")
        for item in [".env", "logs/", "**/backups/"]:
            with self.subTest(pattern=item):
                self.assertIn(item, source)

    def test_sensitive_files_not_tracked(self):
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        sensitive = []
        for item in result.stdout.splitlines():
            name = item.rsplit("/", 1)[-1].lower()
            if name == ".env" or name.endswith(
                (".log", ".sqlite", ".db", ".pem", ".key")
            ):
                sensitive.append(item)
        self.assertEqual(sensitive, [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
