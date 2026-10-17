import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from httpx import Request
from openai import APITimeoutError

from incident_api import app, get_openai_client


class TestIncidentAPIErrors(unittest.TestCase):
    def test_missing_key_returns_503(self) -> None:
        with patch.dict(
            "os.environ",
            {"OPENAI_API_KEY": ""},
        ), patch("incident_api.OpenAI") as constructor:
            with TestClient(app) as client:
                response = client.post(
                    "/incidents/analyze",
                    json={
                        "description": (
                            "Kubernetes pods fail readiness checks."
                        ),
                    },
                )

            constructor.assert_not_called()

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"detail": "AI service is not configured."},
        )

    def test_timeout_returns_504(self) -> None:
        fake_client = Mock()

        fake_client.responses.parse.side_effect = APITimeoutError(
            request=Request(
                "POST",
                "https://example.test",
            ),
        )

        with patch.dict(
            app.dependency_overrides,
            {get_openai_client: lambda: fake_client},
        ), TestClient(app) as client:
            response = client.post(
                "/incidents/analyze",
                json={
                    "description": (
                        "Kubernetes pods fail readiness checks."
                    ),
                },
            )

        self.assertEqual(response.status_code, 504)
        self.assertEqual(
            response.json(),
            {
                "detail": (
                    "Incident analysis timed out. "
                    "Try again later."
                ),
            },
        )
        fake_client.responses.parse.assert_called_once()


if __name__ == "__main__":
    unittest.main()