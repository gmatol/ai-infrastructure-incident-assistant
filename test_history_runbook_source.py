import unittest
from contextlib import redirect_stdout
from io import StringIO

from incident_history import display_incidents


class TestHistoryRunbookSource(unittest.TestCase):
    def setUp(self) -> None:
        self.report = {
            "file_name": "incident_practice.json",
            "analysis": {
                "severity": "High",
                "summary": "Fictional Windows DNS incident.",
            },
        }

    def capture_display(self) -> str:
        output = StringIO()

        with redirect_stdout(output):
            display_incidents([self.report])

        text = output.getvalue()
        self.assertIn("Severity: High", text)
        self.assertIn("Summary: Fictional Windows DNS incident.", text)
        return text

    def test_recorded_source_is_displayed(self) -> None:
        self.report["runbook_source"] = "runbooks/windows_dns.md"

        text = self.capture_display()

        self.assertIn(
            "Runbook source: runbooks/windows_dns.md",
            text,
        )

    def test_no_match_is_displayed(self) -> None:
        self.report["runbook_source"] = None

        text = self.capture_display()

        self.assertIn(
            "Runbook source: No matching runbook supplied",
            text,
        )

    def test_older_report_without_source_is_displayed(self) -> None:
        text = self.capture_display()

        self.assertIn("Runbook source: Not recorded", text)


if __name__ == "__main__":
    unittest.main()