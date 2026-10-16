from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

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