import re
import unittest
from uuid import UUID

from fastapi.testclient import TestClient

from incident_api import app


class TestAPIObservability(unittest.TestCase):
    def test_request_id_matches_log_and_duration_is_recorded(self) -> None:
        capture = self.assertLogs("uvicorn.error", level="INFO")

        with capture as logs, TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)

        request_id = response.headers["X-Request-ID"]
        self.assertEqual(UUID(request_id).version, 4)

        message = "\n".join(logs.output)

        self.assertIn(f"request_id={request_id}", message)
        self.assertIn("method=GET path=/health status=200", message)

        duration = re.search(r"duration_ms=([0-9.]+)", message)

        self.assertIsNotNone(duration)
        self.assertGreaterEqual(float(duration.group(1)), 0)

    def test_requests_receive_different_ids(self) -> None:
        with TestClient(app) as client:
            first = client.get("/health")
            second = client.get("/health")

        self.assertNotEqual(
            first.headers["X-Request-ID"],
            second.headers["X-Request-ID"],
        )

    def test_validation_error_is_logged_without_private_input(self) -> None:
        capture = self.assertLogs("uvicorn.error", level="INFO")

        with capture as logs, TestClient(app) as client:
            response = client.post(
                "/incidents?token=TEST_QUERY_TOKEN",
                json={"description": "SECRET"},
                headers={"Authorization": "Bearer TEST_HEADER_TOKEN"},
            )

        self.assertEqual(response.status_code, 422)

        message = "\n".join(logs.output)
        request_id = response.headers["X-Request-ID"]

        self.assertIn(f"request_id={request_id}", message)
        self.assertIn("path=/incidents status=422", message)

        for private_value in [
            "SECRET",
            "TEST_QUERY_TOKEN",
            "TEST_HEADER_TOKEN",
        ]:
            self.assertNotIn(private_value, message)


if __name__ == "__main__":
    unittest.main()