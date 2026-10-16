from typing import Literal

from openai import OpenAI
from pydantic import BaseModel


class IncidentAnalysis(BaseModel):
    severity: Literal["Low", "Medium", "High", "Critical"]
    summary: str
    likely_cause: str
    troubleshooting_steps: list[str]
    recommended_action: str


INSTRUCTIONS = """
You are an infrastructure incident assistant.

Analyze Linux, Windows, AWS, Kubernetes, and networking incidents.
Base your conclusions only on the evidence provided.
Do not claim that you executed commands.
Recommend safe diagnostic actions before disruptive changes.
"""


def analyze_incident(
    description: str,
    client: OpenAI,
) -> IncidentAnalysis:
    description = description.strip()

    if not description:
        raise ValueError("Incident description cannot be blank.")

    response = client.responses.parse(
        model="gpt-6-astra",
        input=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": description},
        ],
        text_format=IncidentAnalysis,
    )

    analysis = response.output_parsed

    if analysis is None:
        raise RuntimeError("AI did not return a structured analysis.")

    return analysis