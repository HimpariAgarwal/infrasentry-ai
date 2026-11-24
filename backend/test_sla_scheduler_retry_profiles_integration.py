import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "backend" / "main.py"


class TestSLARetryProfilesIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = MAIN.read_text(encoding="utf-8-sig")
        cls.tree = ast.parse(cls.source)

    def test_router_import_exists(self):
        found = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "sla_scheduler_retry_profiles_router"
            and any(alias.asname == "sla_retry_profiles_router"
                    for alias in node.names)
            for node in self.tree.body
        )
        self.assertTrue(found)

    def test_router_registered(self):
        found = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "include_router"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "app"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "sla_retry_profiles_router"
            for node in ast.walk(self.tree)
        )
        self.assertTrue(found)

    def test_main_is_valid_python(self):
        ast.parse(self.source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
