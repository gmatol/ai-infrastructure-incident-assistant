import unittest

from save_evaluation import validate_scores


class TestEvaluationScores(unittest.TestCase):

    def test_valid_scores(self) -> None:
        scores = {
            "facts_are_accurate": 0,
            "uncertainty_is_clear": 1,
            "actions_are_cautious": 2,
        }

        self.assertIsNone(validate_scores(scores))

    def test_score_above_two_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_scores({"facts_are_accurate": 3})

    def test_negative_score_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_scores({"facts_are_accurate": -1})

    def test_text_score_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_scores({"facts_are_accurate": "2"})

    def test_boolean_score_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_scores({"facts_are_accurate": True})

    def test_empty_scores_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_scores({})


if __name__ == "__main__":
    unittest.main()