import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from save_evaluation import main, save_evaluation


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
        self.assertEqual(evaluation["reviewer"], "Guot Deng Anyak")
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
                project_folder=self.project_folder,
                reviewer="Another Reviewer",
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


    def test_reviewer_is_saved_and_trimmed(self) -> None:
        saved_path = save_evaluation(
            self.report_filename,
            self.scores,
            "Confirm impact.",
            self.project_folder,
            reviewer="  José O'Neill  ",
        )
        evaluation = json.loads(saved_path.read_text(encoding="utf-8"))
        self.assertEqual(evaluation["reviewer"], "José O'Neill")

    def test_blank_reviewer_is_rejected_without_writing(self) -> None:
        for reviewer in ("", "   ", "\t\n"):
            with self.subTest(reviewer=reviewer):
                with self.assertRaisesRegex(ValueError, "Reviewer name"):
                    save_evaluation(
                        self.report_filename, self.scores, "Test review.",
                        self.project_folder, reviewer=reviewer,
                    )
                self.assertFalse((self.project_folder / "evaluations").exists())

    def test_non_text_reviewer_is_rejected_without_writing(self) -> None:
        for reviewer in (None, 123, True, [], {}):
            with self.subTest(reviewer=reviewer):
                with self.assertRaisesRegex(ValueError, "Reviewer name"):
                    save_evaluation(
                        self.report_filename, self.scores, "Test review.",
                        self.project_folder, reviewer=reviewer,
                    )
                self.assertFalse((self.project_folder / "evaluations").exists())

    def test_invalid_reviewer_preserves_existing_evaluation(self) -> None:
        saved_path = save_evaluation(
            self.report_filename, self.scores, "Original review.",
            self.project_folder, reviewer="Original Reviewer",
        )
        original_content = saved_path.read_bytes()
        with self.assertRaises(ValueError):
            save_evaluation(
                self.report_filename, self.scores, "Replacement review.",
                self.project_folder, reviewer="   ",
            )
        self.assertEqual(saved_path.read_bytes(), original_content)

    def test_cli_passes_reviewer_to_saving_function(self) -> None:
        answers = ["  Alex Reviewer  ", self.report_filename] + ["2"] * 6
        answers.append("Confirm impact.")
        with patch("builtins.input", side_effect=answers), patch(
            "save_evaluation.save_evaluation"
        ) as save, patch("builtins.print"):
            main()
        self.assertEqual(save.call_args.kwargs["reviewer"], "Alex Reviewer")

    def test_cli_rejects_blank_reviewer_before_collecting_scores(self) -> None:
        with patch("builtins.input", return_value="   ") as prompt, patch(
            "save_evaluation.save_evaluation"
        ) as save, self.assertRaisesRegex(ValueError, "Reviewer name"):
            main()
        prompt.assert_called_once_with("Enter reviewer name: ")
        save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
