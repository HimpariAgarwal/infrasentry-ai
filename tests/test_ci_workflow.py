import unittest
from pathlib import Path


class CIWorkflowTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.workflow_path = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "ci.yml"
        )
        cls.content = cls.workflow_path.read_text(encoding="utf-8-sig")

    def test_workflow_exists(self):
        self.assertTrue(self.workflow_path.is_file())

    def test_push_trigger_exists(self):
        self.assertIn("  push:", self.content)

    def test_pull_request_trigger_exists(self):
        self.assertIn("  pull_request:", self.content)

    def test_backend_regression_step_exists(self):
        self.assertIn(
            "python scripts/regression_test_runner.py",
            self.content,
        )

    def test_frontend_quality_steps_exist(self):
        self.assertIn("npm ci", self.content)
        self.assertIn("npm run lint", self.content)
        self.assertIn("npm run build", self.content)

    def test_docker_compose_validation_exists(self):
        self.assertIn("docker compose config -q", self.content)

    def test_read_only_repository_permission(self):
        self.assertIn("  contents: read", self.content)

    def test_expected_node_and_python_versions(self):
        self.assertIn('python-version: "3.11"', self.content)
        self.assertIn('node-version: "22"', self.content)


if __name__ == "__main__":
    unittest.main()
