import unittest
from unittest.mock import Mock

from incident_service import IncidentAnalysis, analyze_incident


class TestIncidentService(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock()

    def test_structured_analysis_is_returned(self) -> None:
        expected = IncidentAnalysis(
            severity="High",
            summary="Fictional Kubernetes readiness failure.",
            likely_cause="Not confirmed.",
            troubleshooting_steps=["Inspect pod events."],
            recommended_action="Collect evidence before changes.",
        )

        self.client.responses.parse.return_value.output_parsed = (
            expected
        )

        result = analyze_incident(
            "  Kubernetes pods fail readiness checks.  ",
            self.client,
        )

        self.assertIs(result, expected)

        arguments = self.client.responses.parse.call_args.kwargs

        self.assertEqual(
            arguments["input"][-1]["content"],
            "Kubernetes pods fail readiness checks.",
        )

    def test_blank_description_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be blank"):
            analyze_incident("   ", self.client)

        self.client.responses.parse.assert_not_called()

    def test_missing_analysis_is_rejected(self) -> None:
        self.client.responses.parse.return_value.output_parsed = None

        with self.assertRaisesRegex(
            RuntimeError,
            "did not return a structured analysis",
        ):
            analyze_incident(
                "Kubernetes pods fail readiness checks.",
                self.client,
            )


if __name__ == "__main__":
    unittest.main()