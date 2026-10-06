import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from incident_history import (
    find_incidents_by_severity,
    get_severity_filter
)


class TestIncidentHistory(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()

        self.reports_folder = Path(
            self.temp_directory.name
        )

        high_report = {
            "generated_at": "2026-09-24T09:00:00",
            "analysis": {
                "severity": "High",
                "summary": (
                    "Kubernetes readiness probes failed."
                )
            }
        }

        critical_report = {
            "generated_at": "2026-09-24T09:05:00",
            "analysis": {
                "severity": "Critical",
                "summary": (
                    "Production database is unavailable."
                )
            }
        }

        self.create_report(
            "incident_high.json",
            high_report
        )

        self.create_report(
            "incident_critical.json",
            critical_report
        )

    def create_report(
        self,
        file_name: str,
        report: dict
    ) -> None:
        report_path = (
            self.reports_folder / file_name
        )

        with report_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(report, file)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_high_incident_count(self) -> None:
        result = find_incidents_by_severity(
            self.reports_folder,
            "High"
        )

        self.assertEqual(len(result), 1)

    def test_critical_incident_count(self) -> None:
        result = find_incidents_by_severity(
            self.reports_folder,
            "Critical"
        )

        self.assertEqual(len(result), 1)

    def test_all_incident_count(self) -> None:
        result = find_incidents_by_severity(
            self.reports_folder,
            "All"
        )

        self.assertEqual(len(result), 2)


class TestSeverityFilter(unittest.TestCase):

    @patch(
        "builtins.input",
        return_value="high"
    )
    def test_lowercase_high(
        self,
        mock_input
    ) -> None:
        result = get_severity_filter()

        self.assertEqual(result, "High")

    @patch(
        "builtins.input",
        return_value="  critical  "
    )
    def test_spaces_are_removed(
        self,
        mock_input
    ) -> None:
        result = get_severity_filter()

        self.assertEqual(result, "Critical")

    @patch(
        "builtins.input",
        return_value="Emergency"
    )
    def test_invalid_severity(
        self,
        mock_input
    ) -> None:
        with self.assertRaises(SystemExit):
            get_severity_filter()


if __name__ == "__main__":
    unittest.main()