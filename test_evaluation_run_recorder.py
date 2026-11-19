import hashlib
import json
import unittest
from copy import deepcopy
from unittest.mock import patch

import incident_service
from record_evaluation_run import build_record


class TestEvaluationRunRecorder(unittest.TestCase):
    def make_record(self, case: str, **kwargs) -> dict:
        with patch(
            "record_evaluation_run.git_output",
            side_effect=["a" * 40, " M example.py"],
        ):
            return build_record(case, **kwargs)

    def test_no_match_records_simulated_request(self) -> None:
        record = self.make_record("k-u")
        request = record["request"]

        self.assertEqual(record["case"], "K-U")
        self.assertEqual(record["mode"], "simulated")
        self.assertEqual(record["outcome"], "request_captured")
        self.assertEqual(record["live_api_requests"], 0)
        self.assertIsNone(record["analysis"])
        self.assertIsNone(record["runbook_context"])
        self.assertIsNone(record["runbook_text_sha256"])
        self.assertEqual(record["application_sha"], "a" * 40)
        self.assertTrue(record["working_tree_dirty"])
        self.assertEqual(
            record["instruction_variant"],
            "application_default",
        )
        self.assertEqual(
            request["input"][1],
            {"role": "user", "content": record["incident"]},
        )
        self.assertEqual(
            request["response_format"]["name"],
            "IncidentAnalysis",
        )

        serialized = json.dumps(
            request, sort_keys=True, ensure_ascii=False
        )
        self.assertEqual(
            record["request_sha256"],
            hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        )

    def test_dns_runbook_is_preserved_in_request(self) -> None:
        record = self.make_record("w-u")
        context = record["runbook_context"]
        payload = json.loads(
            record["request"]["input"][1]["content"]
        )

        self.assertEqual(
            context["source"],
            "runbooks/windows_dns.md",
        )
        self.assertIn(
            "Check Active Directory LDAP SRV record resolution.",
            context["text"],
        )
        self.assertEqual(
            payload,
            {
                "incident_description": record["incident"],
                "reference_runbook": context,
            },
        )
        self.assertEqual(
            record["runbook_text_sha256"],
            hashlib.sha256(
                context["text"].encode("utf-8")
            ).hexdigest(),
        )

    def test_unknown_case_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "Unknown evaluation case"
        ):
            build_record("unknown")

    def test_candidate_changes_only_system_instruction(self) -> None:
        extra = "Compare affected and working systems."
        original = incident_service.INSTRUCTIONS

        for case in ("k-u", "w-u"):
            with self.subTest(case=case):
                baseline = self.make_record(case)
                candidate = self.make_record(
                    case,
                    extra_instructions=extra,
                )

                expected = deepcopy(baseline["request"])
                expected["input"][0]["content"] += "\n\n" + extra

                self.assertEqual(candidate["request"], expected)
                self.assertEqual(
                    candidate["instruction_variant"],
                    "candidate",
                )
                self.assertEqual(
                    candidate["extra_instructions_sha256"],
                    hashlib.sha256(extra.encode("utf-8")).hexdigest(),
                )
                self.assertNotEqual(
                    candidate["request_sha256"],
                    baseline["request_sha256"],
                )
                self.assertEqual(
                    candidate["runbook_context"],
                    baseline["runbook_context"],
                )
                self.assertEqual(incident_service.INSTRUCTIONS, original)

                after = self.make_record(case)
                self.assertEqual(after["request"], baseline["request"])
                self.assertEqual(
                    after["instruction_variant"],
                    "application_default",
                )

    def test_blank_extra_instructions_are_rejected(self) -> None:
        for extra in ("", " \n\t "):
            with self.subTest(extra=repr(extra)), self.assertRaisesRegex(
                ValueError,
                "Extra instructions cannot be blank",
            ):
                build_record("k-u", extra_instructions=extra)

    def test_instructions_are_restored_after_capture_error(self) -> None:
        original = incident_service.INSTRUCTIONS

        with patch(
            "record_evaluation_run.analyze_incident",
            side_effect=RuntimeError("Simulated capture failure"),
        ), self.assertRaisesRegex(
            RuntimeError,
            "Simulated capture failure",
        ):
            self.make_record(
                "k-u",
                extra_instructions="Compare affected and working systems.",
            )

        self.assertEqual(incident_service.INSTRUCTIONS, original)

if __name__ == "__main__":
    unittest.main()
