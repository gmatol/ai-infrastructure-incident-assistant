import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from incident_service import IncidentAnalysis
from structured_incident_app import main


class TestCLIRunbookContext(unittest.TestCase):
    def setUp(self) -> None:
        temporary_folder = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_folder.cleanup)
        self.reports_folder = Path(temporary_folder.name) / "incident_reports"

        self.client = Mock()
        self.client.responses.parse.return_value.output_parsed = (
            IncidentAnalysis(
                severity="Medium",
                summary="Fictional practice incident.",
                likely_cause="Not confirmed.",
                troubleshooting_steps=["Collect diagnostic evidence."],
                recommended_action="Investigate before changing settings.",
            )
        )

    def run_cli(self, description: str) -> str:
        with (
            patch("builtins.input", return_value=description),
            patch("builtins.print"),
            patch(
                "structured_incident_app.OpenAI",
                return_value=self.client,
            ),
            patch(
                "structured_incident_app.Path",
                return_value=self.reports_folder,
            ),
        ):
            main()

        self.client.responses.parse.assert_called_once()

        reports = list(self.reports_folder.glob("incident_*.json"))
        self.assertEqual(len(reports), 1)

        report = json.loads(reports[0].read_text(encoding="utf-8"))
        self.assertEqual(report["incident"], description)
        self.assertEqual(report["analysis"]["severity"], "Medium")

        arguments = self.client.responses.parse.call_args.kwargs
        return arguments["input"][1]["content"]

    def test_dns_runbook_is_automatically_supplied(self) -> None:
        description = "Windows server cannot resolve Active Directory DNS."

        content = json.loads(self.run_cli(description))

        self.assertEqual(content["incident_description"], description)
        self.assertEqual(
            content["reference_runbook"]["source"],
            "runbooks/windows_dns.md",
        )
        self.assertIn(
            "Check Active Directory LDAP SRV record resolution.",
            content["reference_runbook"]["text"],
        )

    def test_no_match_sends_description_only(self) -> None:
        description = "Linux server disk is full."

        content = self.run_cli(description)

        self.assertEqual(content, description)


if __name__ == "__main__":
    unittest.main()