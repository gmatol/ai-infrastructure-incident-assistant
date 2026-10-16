from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APITimeoutError, OpenAIError, RateLimitError
from pydantic import BaseModel, ConfigDict, Field

from structured_incident_app import (
    AnalysisConfigurationError,
    IncidentAnalysis,
    InvalidAnalysisError,
    analyze_incident,
)

app = FastAPI(title="AI Infrastructure Incident Assistant")


class IncidentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(
        min_length=10,
        max_length=4000,
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/incidents")
def receive_incident(incident: IncidentRequest) -> dict[str, str]:
    return {
        "message": "Incident received",
        "description": incident.description,
    }


@app.post("/analyze", response_model=IncidentAnalysis)
def analyze(incident: IncidentRequest) -> IncidentAnalysis:
    """Generate advisory text only; do not save reports or execute commands."""
    try:
        return analyze_incident(incident.description)
    except AnalysisConfigurationError:
        raise HTTPException(503, "AI service is not configured.") from None
    except APITimeoutError:
        raise HTTPException(504, "AI service timed out.") from None
    except (RateLimitError, APIConnectionError):
        raise HTTPException(503, "AI service is temporarily unavailable.") from None
    except (OpenAIError, InvalidAnalysisError):
        raise HTTPException(502, "AI service could not produce a valid analysis.") from None
