import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from openai import OpenAI, OpenAIError
from pydantic import BaseModel


class IncidentAnalysis(BaseModel):
    severity: Literal["Low", "Medium", "High", "Critical"]
    summary: str
    likely_cause: str
    troubleshooting_steps: list[str]
    recommended_action: str


client = OpenAI()

incident = input(
    "Describe your infrastructure incident:\n> "
).strip()


if not incident:
    raise SystemExit("No incident was provided. Program stopped.")


instructions = """
You are an infrastructure incident assistant.

Analyze Linux, Windows, AWS, Kubernetes, and networking incidents.
Base your conclusions only on the evidence provided.
Do not claim that you executed commands.
Recommend safe diagnostic actions before disruptive changes.
"""


try:
    response = client.responses.parse(
        model="gpt-6-astra",
        input=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": incident
            }
        ],
        text_format=IncidentAnalysis
    )

    analysis = response.output_parsed

    if analysis is None:
        print("The AI did not return a structured analysis.")
        raise SystemExit(1)

    print("\nSTRUCTURED INCIDENT ANALYSIS")
    print("-" * 40)
    print("Severity:", analysis.severity)
    print("Summary:", analysis.summary)
    print("Likely cause:", analysis.likely_cause)

    print("\nTroubleshooting steps:")

    for number, step in enumerate(
        analysis.troubleshooting_steps,
        start=1
    ):
        print(f"{number}. {step}")

    print("\nRecommended action:")
    print(analysis.recommended_action)

    generated_at = datetime.now(timezone.utc)

    report_data = {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "incident": incident,
        "analysis": analysis.model_dump()
    }

    reports_folder = Path("incident_reports")
    reports_folder.mkdir(exist_ok=True)

    filename_timestamp = generated_at.strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_path = reports_folder / (
        f"incident_{filename_timestamp}.json"
    )

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)

    print("\nReport saved to:", report_path)


except OpenAIError as error:
    print("OpenAI API request failed:", error)

except OSError as error:
    print("Could not save the incident report:", error)