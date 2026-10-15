from fastapi import FastAPI

app = FastAPI(title="AI Infrastructure Incident Assistant")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}