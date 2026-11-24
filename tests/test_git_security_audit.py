import unittest

from scripts.git_security_audit import (
    audit_tracked_files,
    is_sensitive_path,
)


class GitSecurityAuditTests(unittest.TestCase):

    def test_env_file_is_sensitive(self):
        self.assertTrue(is_sensitive_path("backend/.env"))

    def test_env_example_is_allowed(self):
        self.assertFalse(is_sensitive_path("backend/.env.example"))

    def test_private_key_is_sensitive(self):
        self.assertTrue(is_sensitive_path("certificates/private.pem"))

    def test_credentials_file_is_sensitive(self):
        self.assertTrue(is_sensitive_path("config/credentials.json"))

    def test_backup_directory_is_sensitive(self):
        self.assertTrue(is_sensitive_path("backups/old_config.py"))

    def test_normal_source_file_is_allowed(self):
        self.assertFalse(is_sensitive_path("backend/main.py"))

    def test_safe_repository_passes(self):
        result = audit_tracked_files([
            "backend/main.py",
            "frontend/src/App.tsx",
            "README.md",
        ])

        self.assertTrue(result.passed)
        self.assertEqual(result.findings, [])

    def test_sensitive_repository_fails(self):
        result = audit_tracked_files([
            "backend/main.py",
            "backend/.env",
        ])

        self.assertFalse(result.passed)
        self.assertIn("backend/.env", result.findings)


if __name__ == "__main__":
    unittest.main()
