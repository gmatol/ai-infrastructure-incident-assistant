import json
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from httpx import Response

from incident_api import app, get_openai_client
from incident_service import IncidentAnalysis


class TestAPIRunbookContext(unittest.TestCase):
    def setUp(self) -> None:
        self.fake_client = Mock()
        self.fake_client.responses.parse.return_value.output_parsed = (
            IncidentAnalysis(
                severity="Medium",
                summary="Fictional infrastructure incident.",
                likely_cause="Not confirmed.",
                troubleshooting_steps=["Collect diagnostic evidence."],
                recommended_action="Investigate before changing settings.",
            )
        )

    def post_incident(self, description: str) -> Response:
        with (
            patch.dict(
                app.dependency_overrides,
                {get_openai_client: lambda: self.fake_client},
            ),
            TestClient(app) as client,
        ):
            return client.post(
                "/incidents/analyze",
                json={"description": description},
            )

    def test_dns_runbook_reaches_analysis(self) -> None:
        description = "Windows server cannot resolve Active Directory DNS."

        response = self.post_incident(description)

        self.assertEqual(response.status_code, 200)
        self.fake_client.responses.parse.assert_called_once()
        arguments = self.fake_client.responses.parse.call_args.kwargs
        payload = json.loads(arguments["input"][1]["content"])

        self.assertEqual(payload["incident_description"], description)
        self.assertEqual(
            payload["reference_runbook"]["source"],
            "runbooks/windows_dns.md",
        )
        self.assertIn(
            "Check Active Directory LDAP SRV record resolution.",
            payload["reference_runbook"]["text"],
        )

    def test_no_match_sends_description_only(self) -> None:
        description = "Linux server disk is full."

        response = self.post_incident(description)

        self.assertEqual(response.status_code, 200)
        self.fake_client.responses.parse.assert_called_once()
        arguments = self.fake_client.responses.parse.call_args.kwargs
        self.assertEqual(arguments["input"][1]["content"], description)

    def test_retrieval_failure_does_not_request_analysis(self) -> None:
        with patch(
            "incident_api.get_runbook_context",
            side_effect=ValueError("Fictional internal path detail"),
        ):
            response = self.post_incident("Windows DNS lookup failed.")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "Runbook retrieval is unavailable."},
        )
        self.fake_client.responses.parse.assert_not_called()


if __name__ == "__main__":
    unittest.main()