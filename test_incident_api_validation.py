import unittest

from fastapi.testclient import TestClient

from incident_api import app


class TestIncidentAPIValidation(unittest.TestCase):
    def test_missing_description_is_rejected(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/incidents",
                json={},
            )

        self.assertEqual(response.status_code, 422)

        error = response.json()["detail"][0]

        self.assertEqual(
            error["loc"],
            ["body", "description"],
        )
        self.assertEqual(error["type"], "missing")

    def test_blank_description_is_rejected(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/incidents",
                json={"description": "            "},
            )

        self.assertEqual(response.status_code, 422)

        error = response.json()["detail"][0]

        self.assertEqual(
            error["type"],
            "string_too_short",
        )

    def test_oversized_description_is_rejected(self) -> None:
        with TestClient(app) as client:
            response = client.post(
                "/incidents",
                json={"description": "A" * 4001},
            )

        self.assertEqual(response.status_code, 422)

        error = response.json()["detail"][0]

        self.assertEqual(
            error["type"],
            "string_too_long",
        )


if __name__ == "__main__":
    unittest.main()