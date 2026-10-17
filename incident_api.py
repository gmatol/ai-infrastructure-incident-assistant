import os
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from openai import APITimeoutError, OpenAI, OpenAIError
from pydantic import BaseModel, ConfigDict, Field

from api_observability import add_request_logging
from incident_service import IncidentAnalysis, analyze_incident

app = FastAPI(title="AI Infrastructure Incident Assistant")
add_request_logging(app)

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
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI service is not configured.",
        )

    with OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    ) as client:
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
    except APITimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="Incident analysis timed out. Try again later.",
        ) from error
    except (OpenAIError, RuntimeError) as error:
        raise HTTPException(
            status_code=502,
            detail="Incident analysis is unavailable. Try again later.",
        ) from error