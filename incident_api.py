from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, Field

from incident_service import IncidentAnalysis, analyze_incident

app = FastAPI(title="AI Infrastructure Incident Assistant")


class IncidentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(
        min_length=10,
        max_length=4000,
    )


class IncidentResponse(BaseModel):
    message: str
    description: str


def get_openai_client() -> Iterator[OpenAI]:
    with OpenAI(timeout=30.0, max_retries=0) as client:
        yield client


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/incidents", response_model=IncidentResponse)
def receive_incident(
    incident: IncidentRequest,
) -> IncidentResponse:
    return IncidentResponse(
        message="Incident received",
        description=incident.description,
    )


@app.post(
    "/incidents/analyze",
    response_model=IncidentAnalysis,
)
def analyze_incident_endpoint(
    incident: IncidentRequest,
    client: Annotated[OpenAI, Depends(get_openai_client)],
) -> IncidentAnalysis:
    try:
        return analyze_incident(
            incident.description,
            client,
        )
    except (OpenAIError, RuntimeError) as error:
        raise HTTPException(
            status_code=502,
            detail="Incident analysis is unavailable. Try again later.",
        ) from error