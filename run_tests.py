import sys
import unittest


def main() -> None:
    test_loader = unittest.TestLoader()

    test_suite = test_loader.discover(
        start_dir=".",
        pattern="test_*.py"
    )

    test_runner = unittest.TextTestRunner(
        verbosity=2
    )

    result = test_runner.run(test_suite)

    if result.wasSuccessful():
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()