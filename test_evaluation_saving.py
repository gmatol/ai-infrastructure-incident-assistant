import json
import tempfile
import unittest
from pathlib import Path

from save_evaluation import save_evaluation


class TestEvaluationSaving(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)

        self.project_folder = Path(self.temp_directory.name)
        reports_folder = self.project_folder / "incident_reports"
        reports_folder.mkdir()

        self.report_filename = "incident_test.json"
        report_path = reports_folder / self.report_filename
        report_path.write_text(
            '{"analysis": {"severity": "Low"}}',
            encoding="utf-8"
        )

        self.scores = {
            "facts_are_accurate": 2,
            "uncertainty_is_clear": 1,
        }

    def test_evaluation_is_saved(self) -> None:
        saved_path = save_evaluation(
            self.report_filename,
            self.scores,
            "Confirm business impact.",
            project_folder=self.project_folder
        )

        with saved_path.open("r", encoding="utf-8") as file:
            evaluation = json.load(file)

        self.assertEqual(
            saved_path.parent,
            self.project_folder / "evaluations"
        )
        self.assertEqual(
            evaluation["report_filename"],
            self.report_filename
        )
        self.assertEqual(evaluation["scores"], self.scores)
        self.assertEqual(evaluation["total_score"], 3)
        self.assertEqual(evaluation["maximum_score"], 4)

    def test_existing_evaluation_is_preserved(self) -> None:
        saved_path = save_evaluation(
            self.report_filename,
            self.scores,
            "Original review.",
            project_folder=self.project_folder
        )

        original_content = saved_path.read_bytes()

        with self.assertRaises(FileExistsError):
            save_evaluation(
                self.report_filename,
                {"facts_are_accurate": 0},
                "Replacement review.",
                project_folder=self.project_folder
            )

        self.assertEqual(
            saved_path.read_bytes(),
            original_content
        )

    def test_missing_report_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            save_evaluation(
                "incident_missing.json",
                self.scores,
                "Test review.",
                project_folder=self.project_folder
            )

        self.assertFalse(
            (self.project_folder / "evaluations").exists()
        )


if __name__ == "__main__":
    unittest.main()