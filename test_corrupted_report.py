import tempfile
import unittest
from pathlib import Path

from incident_history import find_incidents_by_severity


class TestCorruptedReport(unittest.TestCase):

    def test_corrupted_json_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_folder:
            reports_folder = Path(temp_folder)

            corrupted_report = (
                reports_folder / "incident_corrupted.json"
            )

            corrupted_report.write_text(
                '{"analysis": ',
                encoding="utf-8"
            )

            with self.assertLogs(
                "incident_history",
                level="WARNING"
            ) as captured_logs:
                result = find_incidents_by_severity(
                    reports_folder,
                    "All"
                )

            self.assertEqual(result, [])

            log_output = "\n".join(
                captured_logs.output
            )

            self.assertIn(
                "Could not read incident_corrupted.json",
                log_output
            )


if __name__ == "__main__":
    unittest.main()