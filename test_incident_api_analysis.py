import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from incident_api import app, get_openai_client
from incident_service import IncidentAnalysis


class TestIncidentAPIAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        self.fake_client = Mock()

        app.dependency_overrides[get_openai_client] = (
            lambda: self.fake_client
        )

        self.addCleanup(
            app.dependency_overrides.pop,
            get_openai_client,
            None,
        )

    def test_analysis_is_returned(self) -> None:
        expected = IncidentAnalysis(
            severity="High",
            summary="Fictional Kubernetes readiness failure.",
            likely_cause="Not confirmed.",
            troubleshooting_steps=["Inspect pod events."],
            recommended_action="Collect evidence before changes.",
        )

        self.fake_client.responses.parse.return_value.output_parsed = (
            expected
        )

        with TestClient(app) as client:
            response = client.post(
                "/incidents/analyze",
                json={
                    "description": (
                        "Kubernetes pods fail readiness checks."
                    ),
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected.model_dump())
        self.fake_client.responses.parse.assert_called_once()

    def test_short_input_does_not_request_analysis(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/incidents/analyze",
                json={"description": "down"},
            )

        self.assertEqual(response.status_code, 422)
        self.fake_client.responses.parse.assert_not_called()

    def test_missing_analysis_returns_clear_error(self) -> None:
        self.fake_client.responses.parse.return_value.output_parsed = (
            None
        )

        with TestClient(app) as client:
            response = client.post(
                "/incidents/analyze",
                json={
                    "description": (
                        "Kubernetes pods fail readiness checks."
                    ),
                },
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.json(),
            {
                "detail": (
                    "Incident analysis is unavailable. "
                    "Try again later."
                ),
            },
        )


if __name__ == "__main__":
    unittest.main()