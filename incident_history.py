import json
import logging
from pathlib import Path

logging.basicConfig(
    filename="incident_history.log",
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


def get_severity_filter() -> str:
    allowed_filters = [
        "Low",
        "Medium",
        "High",
        "Critical",
        "All"
    ]

    severity_filter = input(
        "Enter severity "
        "(Low, Medium, High, Critical, or All):\n> "
    ).strip().title()

    if severity_filter not in allowed_filters:
        raise SystemExit(
            "Invalid severity. Choose Low, Medium, "
            "High, Critical, or All."
        )

    return severity_filter


def find_incidents_by_severity(
    reports_folder: Path,
    severity_filter: str
) -> list:
    matching_reports = []

    report_files = sorted(
        reports_folder.glob("incident_*.json"),
        reverse=True
    )

    for report_path in report_files:
        try:
            with report_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                report = json.load(file)

            analysis = report.get("analysis", {})
            severity = analysis.get(
                "severity",
                "Unknown"
            )

            if (
                severity_filter != "All"
                and severity != severity_filter
            ):
                continue

            report["file_name"] = report_path.name
            matching_reports.append(report)

        except (OSError, json.JSONDecodeError) as error:
            logger.warning(
                "Could not read %s: %s",
                report_path.name,
                error
            )

    return matching_reports


def display_incidents(reports: list) -> None:
    for number, report in enumerate(
        reports,
        start=1
    ):
        analysis = report.get("analysis", {})

        print(f"\nReport {number}")
        print(
            "File:",
            report.get("file_name", "Unknown")
        )
        print(
            "Generated:",
            report.get("generated_at", "Unknown")
        )
        print(
            "Severity:",
            analysis.get("severity", "Unknown")
        )
        print(
            "Summary:",
            analysis.get("summary", "Not available")
        )


def main() -> None:
    reports_folder = Path("incident_reports")

    if not reports_folder.exists():
        raise SystemExit(
            "The incident_reports folder does not exist."
        )

    severity_filter = get_severity_filter()

    print(f"\nINCIDENT HISTORY — {severity_filter}")
    print("-" * 50)

    matching_reports = find_incidents_by_severity(
        reports_folder,
        severity_filter
    )

    logger.info(
        "Severity filter %s returned %s report(s).",
        severity_filter,
        len(matching_reports)
    )

    if not matching_reports:
        print(
            f"No {severity_filter} incidents were found."
        )
    else:
        display_incidents(matching_reports)

        print(
            f"\nTotal matching reports: "
            f"{len(matching_reports)}"
        )


if __name__ == "__main__":
    main()