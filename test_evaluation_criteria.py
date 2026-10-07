import unittest

from save_evaluation import EVALUATION_CRITERIA, validate_scores


class TestEvaluationCriteria(unittest.TestCase):

    def test_six_unique_criteria(self) -> None:
        self.assertEqual(len(EVALUATION_CRITERIA), 6)
        self.assertEqual(len(set(EVALUATION_CRITERIA)), 6)
        self.assertIn(
            "severity_is_justified",
            EVALUATION_CRITERIA
        )

    def test_full_scores_total_twelve(self) -> None:
        scores = {
            criterion: 2
            for criterion in EVALUATION_CRITERIA
        }

        validate_scores(scores)

        self.assertEqual(sum(scores.values()), 12)


if __name__ == "__main__":
    unittest.main()