import json
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI, OpenAIError

from incident_service import analyze_incident


def main() -> None:
    incident = input(
        "Describe your infrastructure incident:\n> "
    ).strip()

    if not incident:
        raise SystemExit(
            "No incident was provided. Program stopped."
        )

    try:
        client = OpenAI()
        analysis = analyze_incident(incident, client)

        print("\nSTRUCTURED INCIDENT ANALYSIS")
        print("-" * 40)
        print("Severity:", analysis.severity)
        print("Summary:", analysis.summary)
        print("Likely cause:", analysis.likely_cause)

        print("\nTroubleshooting steps:")

        for number, step in enumerate(
            analysis.troubleshooting_steps,
            start=1,
        ):
            print(f"{number}. {step}")

        print("\nRecommended action:")
        print(analysis.recommended_action)

        generated_at = datetime.now(timezone.utc)

        report_data = {
            "generated_at": generated_at.isoformat(
                timespec="seconds"
            ),
            "incident": incident,
            "analysis": analysis.model_dump(),
        }

        reports_folder = Path("incident_reports")
        reports_folder.mkdir(exist_ok=True)

        filename_timestamp = generated_at.strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        report_path = reports_folder / (
            f"incident_{filename_timestamp}.json"
        )

        with report_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(report_data, file, indent=4)

        print("\nReport saved to:", report_path)

    except OpenAIError as error:
        print("OpenAI API request failed:", error)

    except RuntimeError as error:
        print("Analysis failed:", error)

    except OSError as error:
        print("Could not save the incident report:", error)


if __name__ == "__main__":
    main()