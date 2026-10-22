FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy only the modules needed by the API; no credentials or incident data.
COPY incident_api.py incident_service.py api_observability.py ./

USER 10001:10001

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "incident_api:app", "--host", "0.0.0.0", "--port", "8000"]
