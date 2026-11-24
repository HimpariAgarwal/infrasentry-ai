import tempfile
import unittest
from pathlib import Path

from scripts.regression_test_runner import RegressionRunner


class RegressionRunnerTests(unittest.TestCase):

    def test_missing_directory(self):
        runner = RegressionRunner(
            Path("directory_that_does_not_exist_123")
        )

        with self.assertRaises(FileNotFoundError):
            runner.discover()

    def test_discover_test_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            test_dir = Path(temp) / "tests"
            test_dir.mkdir()

            (test_dir / "test_sample.py").write_text(
                "import unittest\n"
                "class SampleTests(unittest.TestCase):\n"
                "    def test_example(self):\n"
                "        self.assertEqual(2 + 2, 4)\n",
                encoding="utf-8",
            )

            runner = RegressionRunner(test_dir)
            suite = runner.discover()

            self.assertEqual(suite.countTestCases(), 1)

    def test_discover_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            test_dir = Path(temp) / "tests"
            test_dir.mkdir()

            runner = RegressionRunner(test_dir)
            suite = runner.discover()

            self.assertEqual(suite.countTestCases(), 0)


if __name__ == "__main__":
    unittest.main()
