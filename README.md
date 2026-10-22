# AI Infrastructure Incident Assistant

[![Python Tests](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml/badge.svg)](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml)

A Python portfolio application for infrastructure incident investigation, with a command-line interface and a local FastAPI REST API. Both use a shared analysis service to generate structured AI troubleshooting guidance. The command-line workflow saves JSON incident reports, filters report history, and records human evaluations; the API returns analysis without saving reports.

The API provides health, incident-validation, and incident-analysis endpoints, with input validation, error responses, request IDs, and request-duration logging. It is a local prototype that suggests guidance for administrator review; it does not connect to infrastructure or execute remediation commands.

Built for learning workflows relevant to System Administrators, Cloud Engineers, DevOps Engineers, and SREs.

## Capabilities

- Analyze fictional Linux, Windows, AWS, Kubernetes, and networking incidents.
- Validate AI response structure with Pydantic.
- Request structured guidance through the CLI or local POST `/incidents/analyze` endpoint.
- Return API validation and analysis errors, with request IDs and duration logging.
- Save timestamped incident reports as JSON.
- Filter history by Low, Medium, High, Critical, or All.
- Log history operations and skip unreadable or corrupted JSON reports.
- Record human evaluation scores linked to incident report filenames.
- Reject invalid scores and preserve existing evaluation files.
- Run isolated unit tests, Ruff checks, and GitHub Actions.

## Setup on macOS

Clone the repository and run commands from its root:

```bash
git clone https://github.com/gmatol/ai-infrastructure-incident-assistant.git
cd ai-infrastructure-incident-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install ruff==0.17.0
```

The project has been exercised locally on Python 3.9. GitHub Actions runs the automated suite on Python 3.9 and 3.11. Ruff is pinned to 0.17.0 locally and in CI, and `ruff.toml` targets Python 3.9 so lint suggestions preserve compatibility (including `timezone.utc`). Dependency and model availability may require a newer Python version or an accessible model. The unit suite does not exercise live AI API calls.

For AI analysis, configure your own OpenAI API key. API usage may incur charges. The analysis script currently specifies its model in `incident_service.py`; use a model available to your account that supports structured responses.

Create a local `.env` in VS Code with this shell assignment, replacing the placeholder privately:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Load it in each new terminal session:

```bash
source .env
python -c 'import os; print("API key configured:", bool(os.getenv("OPENAI_API_KEY")))'
git check-ignore -v .env
```

The application does not automatically load `.env`. Never commit real keys. `.env.example` contains a placeholder only. Do not place credentials or confidential customer information in incident descriptions.

## Generate an incident report

```bash
python structured_incident_app.py
```

Wait for the incident prompt, then enter one line. Visual wrapping is fine; actual newlines end the input.

Example fictional incident:

```text
One payroll administrator receives Access Denied on a Windows Server payroll share. Payroll for 200 employees is due in 30 minutes and no approved workaround exists. Group membership, share permissions, NTFS permissions, and SMB connections have not been checked.
```

The response includes severity, summary, likely cause, troubleshooting steps, and recommended action. A report is saved to `incident_reports/incident_<timestamp>.json`. Responses vary; no particular diagnosis or score is guaranteed.

## Search incident history

```bash
python incident_history.py
```

Enter `High`, another allowed severity, or `All`. The program displays matching reports and their count. Run from the repository root because incident generation and history use relative report paths.

## Save a human evaluation

Review the AI answer before scoring it:

```bash
python save_evaluation.py
```

Enter your reviewer name first, then enter the report filename only, such as `incident_20261007_230347_221575.json`, without `incident_reports/`. The corresponding report must exist locally.

Enter integer scores of 0, 1, or 2 for the six criteria, followed by an improvement note. The script writes `evaluations/evaluation_<report_filename>` and refuses to overwrite an existing evaluation. It makes no AI API call.

The name is stored in the evaluation JSON's `reviewer` field. Leading and trailing whitespace is removed; empty or whitespace-only names are rejected before scores are collected. Names may contain Unicode characters, spaces, and punctuation. Existing evaluation records are left unchanged.

Python callers can pass `reviewer="Alex Reviewer"` to `save_evaluation()`. The name must be non-empty text; invalid input raises `ValueError` before any evaluation directory or file is created. For compatibility, calls that omit `reviewer` retain the historical default, `Guot Deng Anyak`. New callers should supply their own name explicitly. The existing fourth positional argument, `project_folder`, remains supported.

### Scoring guide

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Facts are accurate | Invents or contradicts key facts | Partly accurate but misses important context | Accurately uses supplied facts |
| Uncertainty is clear | Presents an unverified cause as certain | Some uncertainty, with overconfident wording | Clearly separates hypotheses from confirmed evidence |
| Investigation is relevant | Irrelevant or misleading steps | Useful but incomplete investigation | Relevant steps tailored to the scenario |
| Actions are cautious | Unjustified disruptive or broad-access actions | Some safeguards are missing | Evidence-first, targeted actions with appropriate safeguards |
| Next evidence is clear | No useful evidence request | Vague or partial evidence requests | Identifies specific evidence needed to narrow the cause |
| Severity is justified | Ignores or contradicts business impact | Plausible rating but misses impact questions | Uses supplied impact or clearly marks the rating provisional and requests missing evidence |

Five-criterion historical reviews have a maximum of 10. New six-criterion reviews have a maximum of 12. Preserve the original score and criterion set. A 10/10 review and a 12/12 review assess different rubrics and do not establish equivalent quality.

Evaluations are subjective human reviews, not verified accuracy measurements. The small set of fictional examples does not establish overall model reliability. `cause_verified` remains false in records generated by this script.

## Tests and code quality

```bash
python run_tests.py
ruff check .
```

The suite has 44 test methods (including five provider-error subtests within one method):

- Incident filtering and severity input validation.
- Corrupted JSON handling and warning logging.
- Valid scores and rejection of text, booleans, empty scores, and out-of-range scores.
- Evaluation persistence, overwrite protection, and missing-report rejection.
- Reviewer attribution and trimming, blank/non-text rejection, existing-record preservation, and CLI name handling.
- Six unique criteria and a full-score total of 12.
- API health, incident validation, structured analysis, and error responses using simulated clients.
- Shared analysis-service behavior and API request-ID/duration logging.

Tests use temporary data and mocked input. They do not require an API key or paid model calls. Passing tests verifies covered application behavior, not the correctness of generated diagnoses or complete coverage of the interactive CLI.

GitHub Actions runs Ruff and the test suite on pull requests and pushes to main. Merge only after required checks pass.

## Main files

| File | Purpose |
|---|---|
| `first_ai_app.py` | Basic AI analysis CLI |
| `structured_incident_app.py` | CLI using the shared analysis service, with incident JSON storage |
| `incident_api.py` | FastAPI endpoints, request/response validation, client configuration, and analysis error responses |
| `incident_service.py` | Shared structured-analysis model and OpenAI analysis function used by the CLI and API |
| `api_observability.py` | API middleware for request IDs and method/path/status/duration logging |
| `incident_history.py` | Severity filtering, display, and logging |
| `save_evaluation.py` | Human evaluation entry, validation, and safe saving |
| `ai_evaluation_notes.md` | Written evaluation notes |
| `test_incident_history.py` | History and input tests |
| `test_corrupted_report.py` | Corrupted-report test |
| `test_evaluation.py` | Score validation tests |
| `test_evaluation_saving.py` | Safe-saving tests |
| `test_evaluation_criteria.py` | Shared criterion tests |
| `test_incident_api*.py` | API health, validation, analysis, and error-response tests |
| `test_incident_service.py` | Shared analysis-service tests |
| `test_api_observability.py` | Request-ID correlation, timing, and logging tests |
| `run_tests.py` | Automatic test discovery |
| `requirements.txt` | Application dependencies |
| `.github/workflows/python-tests.yml` | CI workflow |

## Local REST API

Start the server from the repository root with your virtual environment active:

```bash
source .env
python -m uvicorn incident_api:app --host 127.0.0.1 --port 8000
```

Keep this terminal running while sending requests from another terminal.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Returns application health without calling OpenAI |
| POST | `/incidents` | Validates and acknowledges an incident |
| POST | `/incidents/analyze` | Returns structured AI troubleshooting guidance |

Both POST endpoints accept JSON containing a `description`.
Surrounding whitespace is removed, and descriptions must contain
10 to 4,000 characters.

The analysis response contains severity, summary, likely cause,
troubleshooting steps, and recommended action. The API returns
guidance without executing commands or saving an incident report.
The command-line application still saves reports.

### Analysis error responses

- `422`: Incident input failed validation.
- `503`: The OpenAI API key is missing or blank.
- `504`: The OpenAI request timed out.
- `502`: Another provider error occurred or structured analysis was missing.

The analysis endpoint requires an OpenAI API key and incurs normal
API usage. Automated tests use simulated clients and make no paid
requests.

Keep the server bound to localhost. This prototype does not yet
provide authentication or rate limiting for public access.

### Local Docker demonstration

For a non-root Python 3.11 container demonstration, see [DOCKER.md](DOCKER.md). It covers building the image, localhost-only publishing, runtime security settings, and endpoint checks without credentials or paid AI calls. This remains a local demonstration; public authentication and rate limiting are not implemented.

## Safety and limitations

- The assistant suggests guidance; it does not execute commands or connect to infrastructure.
- Pydantic validates structure and field types, not factual correctness.
- Administrators must verify diagnoses and recommendations against actual evidence and approved procedures.
- Incident descriptions are sent to the configured AI API. Company use requires approval for that data flow.
- Reports and evaluations are local JSON files, without application authentication, encryption, or retention controls.
- This is a portfolio prototype, not a production incident-management or autonomous-remediation system.
- Generated incident reports and logs are ignored by Git. Only deliberately reviewed fictional evaluation examples should be shared.

## Three-minute portfolio demonstration

1. Introduce the infrastructure investigation problem.
2. Generate one structured response using a fictional one-line incident.
3. Show its saved report and retrieve it with the history filter.
4. Explain an evaluation, including its limitations and improvement note.
5. Show the test and Ruff results. Keep keys and private data off-screen.

## Interview summary

“I built a Python infrastructure incident assistant with a command-line workflow and a local FastAPI API, backed by a shared structured-analysis service. The CLI saves JSON reports for history filtering and human evaluation; the API returns troubleshooting guidance with validation, error handling, request IDs, and duration logging. I added isolated tests and GitHub Actions. An administrator verifies the guidance and performs approved actions.”

## Release milestones

- `v1.0.0`: published GitHub release for the initial incident-assistant portfolio milestone.
- `v1.1.0`: existing Git tag for the human-evaluation milestone, including safe reusable saving, six shared criteria, an 18-test suite at that milestone, and updated documentation. As of October 21, 2026, no GitHub release has been published for this tag; the published release list contains only `v1.0.0`.
- Current `main`: development beyond `v1.1.0`, including the shared analysis service, local FastAPI endpoints, analysis error handling, request observability, expanded automated tests, and a local Docker demonstration. These features are implemented on `main`; they are not part of the earlier `v1.1.0` milestone.

Public API authentication and rate limiting remain unimplemented. Public deployment and customer-infrastructure integration are outside the current prototype; remediation actions remain the administrator's responsibility.

Development continues in this repository through the established 12-week AI engineering plan.
