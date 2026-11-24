import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN_FILE = ROOT / "backend" / "main.py"


class TestRetryMetricsRouterIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = MAIN_FILE.read_text(encoding="utf-8-sig")
        cls.tree = ast.parse(cls.source)

    def test_router_import_exists(self):
        found = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "sla_scheduler_retry_metrics_router"
            and any(
                alias.name == "router"
                and alias.asname == "sla_retry_metrics_router"
                for alias in node.names
            )
            for node in self.tree.body
        )
        self.assertTrue(found)

    def test_router_registered_with_fastapi_app(self):
        found = any(
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "app"
            and node.value.func.attr == "include_router"
            and node.value.args
            and isinstance(node.value.args[0], ast.Name)
            and node.value.args[0].id == "sla_retry_metrics_router"
            for node in ast.walk(self.tree)
        )
        self.assertTrue(found)

    def test_registration_occurs_after_app_creation(self):
        app_line = None
        registration_line = None

        for node in self.tree.body:
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "app"
                    for target in node.targets
                )
            ):
                app_line = node.end_lineno

        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == "app"
                and node.value.func.attr == "include_router"
                and node.value.args
                and isinstance(node.value.args[0], ast.Name)
                and node.value.args[0].id == "sla_retry_metrics_router"
            ):
                registration_line = node.lineno

        self.assertIsNotNone(app_line)
        self.assertIsNotNone(registration_line)
        self.assertGreater(registration_line, app_line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
