import json
import tempfile
import unittest
from pathlib import Path

from save_evaluation import EVALUATION_CRITERIA, save_evaluation


class TestEvaluationFilenames(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.project_folder = Path(self.temp_directory.name)
        self.reports_folder = self.project_folder / "incident_reports"
        self.reports_folder.mkdir()

        self.scores = {
            criterion: 2 for criterion in EVALUATION_CRITERIA
        }

    def test_invalid_filenames_are_rejected(self) -> None:
        (self.reports_folder / "incident_test.json").write_text(
            '{"analysis": {"severity": "High"}}',
            encoding="utf-8",
        )

        invalid_filenames = [
            "../incident_test.json",
            "incident_reports/incident_test.json",
            "notes.json",
            "incident_test.txt",
        ]

        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                with self.assertRaisesRegex(
                    ValueError, "filename only"
                ):
                    save_evaluation(
                        filename,
                        self.scores,
                        "Fictional filename-validation test.",
                        project_folder=self.project_folder,
                        reviewer="Test Reviewer",
                    )

                self.assertFalse(
                    (self.project_folder / "evaluations").exists()
                )

    def test_valid_filenames_are_saved(self) -> None:
        valid_filenames = [
            "incident_test.json",
            "incident_20261014_094000.json",
        ]

        for filename in valid_filenames:
            with self.subTest(filename=filename):
                (self.reports_folder / filename).write_text(
                    '{"analysis": {"severity": "High"}}',
                    encoding="utf-8",
                )

                saved_path = save_evaluation(
                    filename,
                    self.scores,
                    "Fictional accepted-filename test.",
                    project_folder=self.project_folder,
                    reviewer="Test Reviewer",
                )

                self.assertEqual(
                    saved_path,
                    self.project_folder / "evaluations"
                    / f"evaluation_{filename}",
                )

                evaluation = json.loads(
                    saved_path.read_text(encoding="utf-8")
                )

                self.assertEqual(
                    evaluation["report_filename"], filename
                )


if __name__ == "__main__":
    unittest.main()