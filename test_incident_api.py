import unittest

from fastapi.testclient import TestClient

from incident_api import app


class TestIncidentAPI(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_valid_incident_is_accepted(self) -> None:
        description = (
            "Kubernetes application returns HTTP 503 "
            "and two pods fail readiness checks."
        )

        with TestClient(app) as client:
            response = client.post(
                "/incidents",
                json={"description": description},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "message": "Incident received",
                "description": description,
            },
        )

    def test_short_description_is_rejected(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/incidents",
                json={"description": "down"},
            )

        self.assertEqual(response.status_code, 422)

        error = response.json()["detail"][0]

        self.assertEqual(
            error["loc"],
            ["body", "description"],
        )
        self.assertEqual(
            error["type"],
            "string_too_short",
        )


if __name__ == "__main__":
    unittest.main()