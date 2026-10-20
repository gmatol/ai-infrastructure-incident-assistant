# Local Docker demonstration on macOS

This packages the existing FastAPI application; it does not change its endpoints
or Python source. The container uses Python 3.11. The existing Python 3.9/3.11
GitHub Actions test matrix remains unchanged.

## Build

Install and open Docker Desktop for Mac before running these commands. Choose
the installer for your Mac's Apple silicon or Intel processor. Wait until its
engine is running. In VS Code, open this repository and choose Terminal > New
Terminal. Run commands from the repository root (the folder containing Dockerfile).

```bash
docker version
docker build --pull -t ai-incident-assistant:local .
```

The first build downloads the Python base image and installs requirements.
Later builds can reuse the dependency layer until requirements.txt changes.
The base tag and some existing requirements are not fully pinned, so this is
not a fully reproducible dependency lock or a production security certification.

## Start without credentials

```bash
docker run --detach --rm \
  --name ai-incident-demo \
  --publish 127.0.0.1:8000:8000 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  ai-incident-assistant:local
docker logs ai-incident-demo
```

Wait for the log message that application startup is complete. If port 8000 is
already in use by your local Uvicorn process, stop that process with Control-C
first, or use 127.0.0.1:8001:8000 and change the curl URLs to port 8001.

Do not pass an API key for this demo. The image contains no key, and Docker does
not automatically inherit your terminal's OPENAI_API_KEY. Do not add a
`--env-file`, `--env`, or a bind mount for these checks.

Uvicorn listens on 0.0.0.0 *inside* the container so Docker can reach it.
The publish address 127.0.0.1 restricts the Mac-side port to localhost.
EXPOSE only documents the container port; it does not publish it.
Keep the explicit localhost publish address. Authentication and rate limiting
are still unimplemented; this configuration is for local demonstrations.

## Verify without paid AI calls

```bash
curl --fail-with-body -i http://127.0.0.1:8000/health

curl --fail-with-body -i http://127.0.0.1:8000/incidents \
  -H 'Content-Type: application/json' \
  --data '{"description":"Fictional Linux server has stopped responding to SSH."}'
```

Both should return HTTP 200. Health returns `{"status":"ok"}`.
The incident response contains `"message":"Incident received"` and the submitted
description. POST /incidents validates and acknowledges input; it neither
calls OpenAI nor saves a report.

Optionally verify validation:

```bash
curl -i http://127.0.0.1:8000/incidents \
  -H 'Content-Type: application/json' \
  --data '{"description":"short"}'
```

Expect HTTP 422 because descriptions require 10 to 4,000 characters.
Do not call /incidents/analyze for this demo. That is the AI-backed endpoint.

Inspect the user and port binding:

```bash
docker exec ai-incident-demo id
docker port ai-incident-demo
docker logs --tail 20 ai-incident-demo
```

Expect UID and GID 10001, and 8000/tcp mapped to 127.0.0.1:8000.
The filesystem is read-only, capabilities are dropped, and privilege escalation
is disabled by the run command. The small temporary /tmp mount is writable.
These restrictions suit the API because it does not save reports.

Stop and remove the temporary container:

```bash
docker stop ai-incident-demo
```

The --rm option removes it automatically. The image remains for the next demo.
No source folder or incident data is mounted into the container.

## Credentials and build context

.dockerignore uses an allowlist. Only the Docker configuration, requirements.txt,
and the three API modules enter the build context. Local .env files, keys, Git
history, virtual environments, logs, reports, evaluations, tests, and documentation
are excluded. Dockerfile also copies only the required application files.
Keep real credentials out of source files and requirements.txt.

If you later deliberately test paid analysis, supply OPENAI_API_KEY only at
runtime, never through Dockerfile ENV, ARG, COPY, or a build command. Runtime
environment variables are visible to users with Docker access; they are not a
secret vault. The existing .env uses shell export syntax and should not be
passed directly to Docker's --env-file option.

## Existing tests

Continue running the full mocked suite in your virtual environment:

```bash
python run_tests.py
ruff check .
```

The minimal runtime image excludes tests and CLI tools. GitHub Actions continues
to validate Python 3.9 and 3.11; the Dockerfile does not replace that coverage.
The curl checks above verify the actual container separately.

## What this adds to your engineering practice

- Docker: image layers, build context, container users, port mappings, and logs.
- DevOps: a reviewable configuration change alongside existing automated checks.
- Cloud engineering: a portable API runtime and configuration supplied at runtime.
- AI engineering: separating ordinary API validation from paid model calls,
  and keeping credentials and generated incident data outside the image.

This remains the same infrastructure project in your 12-week program.
