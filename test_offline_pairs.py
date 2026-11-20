import hashlib
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from run_offline_pairs import build_batch, compare_pair


class TestOfflinePairs(unittest.TestCase):
    def setUp(self) -> None:
        self.extra = "Compare affected and working systems."
        self.default = {
            "mode": "simulated",
            "outcome": "request_captured",
            "instruction_variant": "application_default",
            "live_api_requests": 0,
            "analysis": None,
            "request": {
                "model": "test-model",
                "input": [
                    {"role": "system", "content": "Base instructions."},
                    {"role": "user", "content": "Fictional incident."},
                ],
                "response_format": {"name": "TestSchema"},
            },
        }
        self.candidate = deepcopy(self.default)
        self.candidate["instruction_variant"] = "candidate"
        self.candidate["request"]["input"][0]["content"] += (
            "\n\n" + self.extra
        )
        self.candidate["extra_instructions_sha256"] = hashlib.sha256(
            self.extra.encode("utf-8")
        ).hexdigest()

    def test_instruction_only_change_matches(self) -> None:
        self.assertEqual(
            compare_pair(self.default, self.candidate),
            "matched",
        )

    def test_model_and_incident_changes_are_mismatches(self) -> None:
        for change in ("model", "incident"):
            with self.subTest(change=change):
                candidate = deepcopy(self.candidate)

                if change == "model":
                    candidate["request"]["model"] = "different-model"
                else:
                    candidate["request"]["input"][1]["content"] = (
                        "Different incident."
                    )

                self.assertEqual(
                    compare_pair(self.default, candidate),
                    "mismatch",
                )

    def test_failed_capture_is_not_compared(self) -> None:
        candidate = deepcopy(self.candidate)
        candidate["outcome"] = "failed"
        candidate["request"] = None

        self.assertEqual(
            compare_pair(self.default, candidate),
            "not_compared",
        )

    def test_batch_counts_and_retains_failed_attempt(self) -> None:
        failure = {
            "case": "K-U",
            "mode": "simulated",
            "outcome": "failed",
            "instruction_variant": "candidate",
            "error_category": "RuntimeError",
            "request": None,
            "analysis": None,
            "live_api_requests": 0,
        }

        def fake_capture(case, *, extra_instructions_path=None):
            is_candidate = extra_instructions_path is not None
            if case == "k-u" and is_candidate:
                return deepcopy(failure)

            record = deepcopy(
                self.candidate if is_candidate else self.default
            )
            record["case"] = case.upper()
            return record

        with patch(
            "run_offline_pairs.capture_attempt",
            side_effect=fake_capture,
        ) as capture:
            batch = build_batch(Path("fictional-candidate.txt"))

        self.assertEqual(capture.call_count, 16)
        self.assertEqual(batch["attempted"], 16)
        self.assertEqual(batch["captured"], 15)
        self.assertEqual(batch["failed"], 1)
        self.assertEqual(batch["matched_pairs"], 7)
        self.assertEqual(batch["mismatched_pairs"], 0)
        self.assertEqual(batch["not_compared_pairs"], 1)
        self.assertEqual(len(batch["records"]), 16)
        self.assertIn(failure, batch["records"])
        self.assertEqual(batch["live_api_requests"], 0)


if __name__ == "__main__":
    unittest.main()
