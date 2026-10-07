# AI Infrastructure Incident Assistant

[![Python Tests](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml/badge.svg)](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml)

A Python-based infrastructure troubleshooting project that analyzes incidents, produces structured results, stores reports as JSON, searches incident history, and handles damaged report files safely.

## Project Purpose

This project demonstrates how AI and Python can support System Administrators, Cloud Engineers, DevOps Engineers, and SRE teams during incident investigation.

Example scenarios include:

- Kubernetes readiness failures and HTTP 503 errors
- Linux web-server port conflicts
- Windows file-share permission problems
- AWS security-group connectivity issues

## Features

- Command-line incident input
- AI-generated incident analysis
- Structured output using Pydantic
- JSON incident-report storage
- Severity filtering
- Input validation
- Timestamped operational logging
- Safe handling of corrupted JSON files
- Automated unit tests
- Automatic test discovery

## Main Files

| File | Purpose |
|---|---|
| `first_ai_app.py` | Basic AI incident-analysis application |
| `structured_incident_app.py` | Produces structured incident results |
| `incident_history.py` | Searches and displays saved reports |
| `test_incident_history.py` | Tests filtering and input validation |
| `test_corrupted_report.py` | Tests corrupted JSON handling |
| `run_tests.py` | Discovers and runs all automated tests |
| `requirements.txt` | Lists external Python dependencies |
| `.gitignore` | Excludes secrets and generated files |

## Requirements

- Python 3.9 or newer
- OpenAI API key for the AI-analysis programs

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Set the OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Never save a real API key inside the Python source code.

## Run the Incident History Application

```bash
python incident_history.py
```

Example selection:

```text
Enter severity (Low, Medium, High, Critical, or All):
> All
```

Example output:

```text
INCIDENT HISTORY — All
--------------------------------------------------

Report 1
Severity: High
Summary: Users are receiving HTTP 503 errors because
two application pods are failing readiness checks.

Total matching reports: 1
```

## Run the Automated Tests

```bash
python run_tests.py
```

Expected result:

```text
Ran 7 tests
OK
```

The tests verify:

- Severity filtering
- Input normalization
- Invalid-input rejection
- Corrupted JSON handling
- Warning-log generation

## Logging

Application events are written to:

```text
incident_history.log
```

Example:

```text
INFO | Severity filter All returned 1 report(s).
WARNING | Could not read incident_corrupted.json.
```

## Skills Demonstrated

- Python functions and type hints
- JSON file processing
- Pydantic structured data
- OpenAI API integration
- Exception handling
- Python logging
- Unit testing
- Temporary test data
- Test discovery
- Secure dependency and environment management
- GitHub Actions continuous integration
- Ruff static code analysis

## Interview Summary

> I built a Python-based infrastructure incident assistant that uses AI and structured output to analyze operational problems. It stores reports as JSON, filters incident history by severity, logs operational events, and includes automated tests for validation and corrupted-data handling.