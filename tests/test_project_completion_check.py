import tempfile
import unittest
from pathlib import Path

from scripts.project_completion_check import (
    FINAL_DELIVERABLES,
    inspect_project,
)


class ProjectCompletionTests(unittest.TestCase):

    def test_empty_project_is_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            passed, missing = inspect_project(Path(directory))

            self.assertFalse(passed)
            self.assertEqual(len(missing), len(FINAL_DELIVERABLES))

    def test_all_deliverables_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            for item in FINAL_DELIVERABLES:
                path = root / item
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test", encoding="utf-8")

            passed, missing = inspect_project(root)

            self.assertTrue(passed)
            self.assertEqual(missing, [])

    def test_missing_single_deliverable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            for item in FINAL_DELIVERABLES:
                path = root / item
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test", encoding="utf-8")

            missing_file = FINAL_DELIVERABLES[0]
            (root / missing_file).unlink()

            passed, missing = inspect_project(root)

            self.assertFalse(passed)
            self.assertEqual(missing, [missing_file])


if __name__ == "__main__":
    unittest.main()
