import tempfile
import unittest
from pathlib import Path

from backend.frontend_import_audit import (
    audit_imports,
    resolve_local_import,
)


class TestFrontendImportAudit(unittest.TestCase):

    def create_file(self, root, relative, content=""):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_resolves_typescript_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.create_file(root, "App.tsx")
            self.create_file(root, "components/Card.tsx")

            result = resolve_local_import(source, "./components/Card")
            self.assertIsNotNone(result)

    def test_resolves_css_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.create_file(root, "App.tsx")
            self.create_file(root, "App.css")

            result = resolve_local_import(source, "./App.css")
            self.assertIsNotNone(result)

    def test_detects_missing_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "App.tsx",
                'import Missing from "./Missing";',
            )

            result = audit_imports(root)
            self.assertFalse(result["passed"])
            self.assertEqual(len(result["unresolved_imports"]), 1)

    def test_clean_imports_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(root, "App.tsx", 'import Card from "./Card";')
            self.create_file(root, "Card.tsx", "export default function Card() {}")

            result = audit_imports(root)
            self.assertTrue(result["passed"])

    def test_package_imports_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "App.tsx",
                'import React from "react";\n'
                'import { useState } from "react";',
            )

            result = audit_imports(root)
            self.assertTrue(result["passed"])

    def test_resolves_index_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.create_file(root, "App.tsx")
            self.create_file(root, "components/index.tsx")

            result = resolve_local_import(source, "./components")
            self.assertIsNotNone(result)
            self.assertEqual(result.name, "index.tsx")

    def test_detects_missing_css(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "App.tsx",
                'import "./missing.css";',
            )

            result = audit_imports(root)
            self.assertFalse(result["passed"])

    def test_multiline_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.create_file(
                root,
                "App.tsx",
                'import {\n  Card\n} from "./Card";',
            )
            self.create_file(root, "Card.tsx", "export const Card = 1;")

            result = audit_imports(root)
            self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
