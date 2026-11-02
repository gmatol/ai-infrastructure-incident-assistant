import json
import unittest
from unittest.mock import Mock

from incident_service import IncidentAnalysis, analyze_incident
from runbook_context import get_runbook_context


class TestRunbookAnalysisContext(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock()
        self.analysis = IncidentAnalysis(
            severity="Medium",
            summary="Fictional DNS incident.",
            likely_cause="Not confirmed.",
            troubleshooting_steps=["Inspect the configured DNS servers."],
            recommended_action="Collect evidence before making changes.",
        )
        self.client.responses.parse.return_value.output_parsed = self.analysis

    def test_dns_source_and_text_reach_client(self) -> None:
        description = "Windows server cannot resolve Active Directory DNS."
        context = get_runbook_context(description)
        self.assertIsNotNone(context)

        result = analyze_incident(
            description,
            self.client,
            runbook_context=context,
        )

        self.client.responses.parse.assert_called_once()
        arguments = self.client.responses.parse.call_args.kwargs
        sent_content = json.loads(arguments["input"][1]["content"])

        self.assertEqual(
            sent_content["incident_description"],
            description,
        )
        self.assertEqual(
            sent_content["reference_runbook"]["source"],
            "runbooks/windows_dns.md",
        )
        self.assertIn(
            "Check Active Directory LDAP SRV record resolution.",
            sent_content["reference_runbook"]["text"],
        )
        self.assertIs(result, self.analysis)

    def test_no_match_sends_description_without_runbook(self) -> None:
        description = "Linux server disk is full."
        context = get_runbook_context(description)
        self.assertIsNone(context)

        analyze_incident(
            description,
            self.client,
            runbook_context=context,
        )

        self.client.responses.parse.assert_called_once()
        arguments = self.client.responses.parse.call_args.kwargs
        self.assertEqual(arguments["input"][1]["content"], description)


if __name__ == "__main__":
    unittest.main()