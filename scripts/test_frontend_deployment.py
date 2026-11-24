from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FrontendDeploymentTests(unittest.TestCase):

    def read(self, name):
        return (ROOT / name).read_text(encoding="utf-8-sig")

    def test_frontend_dockerfile(self):
        content = self.read("frontend/Dockerfile")
        self.assertIn("node:22-alpine", content)
        self.assertIn("npm ci", content)
        self.assertIn("npm run build", content)
        self.assertIn("nginx:", content)

    def test_nginx_proxy(self):
        content = self.read("frontend/nginx.conf")
        self.assertIn("proxy_pass http://backend:8000", content)
        self.assertIn("location /api/", content)
        self.assertIn("try_files $uri $uri/ /index.html", content)
        self.assertIn("location = /health", content)

    def test_relative_api_configuration(self):
        auth = self.read("frontend/src/services/authService.ts")
        detection = self.read("frontend/src/services/detectionApi.ts")

        self.assertIn('import.meta.env.VITE_API_URL ?? ""', auth)
        self.assertIn('import.meta.env.VITE_API_URL ?? ""', detection)
        self.assertNotIn('|| "http://localhost:8000"', auth)
        self.assertNotIn('|| "http://127.0.0.1:8000"', detection)

    def test_compose_frontend_service(self):
        content = self.read("docker-compose.yml")
        self.assertIn("frontend:", content)
        self.assertIn('"3000:80"', content)
        self.assertIn("condition: service_healthy", content)
        self.assertIn("VITE_API_URL", content)

    def test_documentation_exists(self):
        self.assertTrue(
            (ROOT / "docs/day112_frontend_deployment.md").is_file()
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
