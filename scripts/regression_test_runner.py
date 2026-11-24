import argparse
import sys
import unittest
from pathlib import Path


class RegressionResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed_names = []

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failed_names.append(str(test))

    def addError(self, test, err):
        super().addError(test, err)
        self.failed_names.append(str(test))


class RegressionRunner:
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir

    def discover(self) -> unittest.TestSuite:
        if not self.test_dir.is_dir():
            raise FileNotFoundError(
                f"Test directory not found: {self.test_dir}"
            )

        project_root = self.test_dir.resolve().parent
        root_string = str(project_root)

        if root_string not in sys.path:
            sys.path.insert(0, root_string)

        loader = unittest.TestLoader()

        return loader.discover(
            start_dir=str(self.test_dir.resolve()),
            pattern="test*.py",
        )

    def run(self, verbosity: int = 2) -> bool:
        suite = self.discover()

        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            resultclass=RegressionResult,
        )

        result = runner.run(suite)

        print("\nInfraSentry AI - Regression Summary")
        print("=" * 52)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")

        passed = result.wasSuccessful()
        print("RESULT:", "PASSED" if passed else "FAILED")
        print("=" * 52)

        if result.failed_names:
            print("Failed tests:")
            for name in result.failed_names:
                print(f" - {name}")

        return passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InfraSentry AI regression test runner"
    )
    parser.add_argument("--test-dir", default="tests")
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    try:
        runner = RegressionRunner(Path(args.test_dir))
        passed = runner.run(verbosity=1 if args.quiet else 2)
        return 0 if passed else 1
    except (OSError, ImportError, ValueError) as error:
        print(f"Regression runner error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
