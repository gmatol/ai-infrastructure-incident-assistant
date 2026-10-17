import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from httpx import Request, Response
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

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

    def test_provider_errors_return_sanitized_502(self) -> None:
        internal_detail = "private-provider-detail: credential=secret-test-value"
        request = Request("POST", "https://example.test")
        errors = [
            OpenAIError(internal_detail),
            APIConnectionError(message=internal_detail, request=request),
            APIStatusError(
                internal_detail,
                response=Response(500, request=request),
                body={"message": internal_detail},
            ),
            AuthenticationError(
                internal_detail,
                response=Response(401, request=request),
                body={"message": internal_detail},
            ),
            RateLimitError(
                internal_detail,
                response=Response(429, request=request),
                body={"message": internal_detail},
            ),
        ]

        fake_client = Mock()

        def override_client():
            return fake_client

        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                fake_client.reset_mock()
                fake_client.responses.parse.side_effect = error

                with patch.dict(
                    app.dependency_overrides,
                    {get_openai_client: override_client},
                ), TestClient(app) as client:
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
                self.assertNotIn(internal_detail, response.text)
                self.assertNotIn(type(error).__name__, response.text)
                fake_client.responses.parse.assert_called_once()

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