# AI Infrastructure Incident Assistant

[![Python Tests](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml/badge.svg)](https://github.com/gmatol/ai-infrastructure-incident-assistant/actions/workflows/python-tests.yml)

A Python command-line portfolio project for infrastructure incident investigation. It generates structured AI guidance, saves JSON incident reports, filters report history, and records human evaluations of response quality.

Built for learning workflows relevant to System Administrators, Cloud Engineers, DevOps Engineers, and SREs.

## Capabilities

- Analyze fictional Linux, Windows, AWS, Kubernetes, and networking incidents.
- Validate AI response structure with Pydantic.
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
python -m pip install ruff
```

The project has been exercised locally on Python 3.9. GitHub Actions uses Python 3.11. Dependency and model availability may require a newer Python version or an accessible model.

For AI analysis, configure your own OpenAI API key. API usage may incur charges. The analysis script currently specifies its model in `structured_incident_app.py`; use a model available to your account that supports structured responses.

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

The suite has 24 tests:

- Incident filtering and severity input validation.
- Corrupted JSON handling and warning logging.
- Valid scores and rejection of text, booleans, empty scores, and out-of-range scores.
- Evaluation persistence, overwrite protection, and missing-report rejection.
- Reviewer attribution and trimming, blank/non-text rejection, existing-record preservation, and CLI name handling.
- Six unique criteria and a full-score total of 12.

Tests use temporary data and mocked input. They do not require an API key or paid model calls. Passing tests verifies covered application behavior, not the correctness of generated diagnoses or complete coverage of the interactive CLI.

GitHub Actions runs Ruff and the test suite on pull requests and pushes to main. Merge only after required checks pass.

## Main files

| File | Purpose |
|---|---|
| `first_ai_app.py` | Basic AI analysis CLI |
| `structured_incident_app.py` | Structured analysis and incident JSON storage |
| `incident_history.py` | Severity filtering, display, and logging |
| `save_evaluation.py` | Human evaluation entry, validation, and safe saving |
| `ai_evaluation_notes.md` | Written evaluation notes |
| `test_incident_history.py` | History and input tests |
| `test_corrupted_report.py` | Corrupted-report test |
| `test_evaluation.py` | Score validation tests |
| `test_evaluation_saving.py` | Safe-saving tests |
| `test_evaluation_criteria.py` | Shared criterion tests |
| `run_tests.py` | Automatic test discovery |
| `requirements.txt` | Application dependencies |
| `.github/workflows/python-tests.yml` | CI workflow |

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

“I built a Python infrastructure incident assistant that generates structured troubleshooting guidance, saves JSON reports, and filters history. I added human evaluation records, validation, overwrite protection, isolated tests, and GitHub Actions. The application supports investigation; an administrator verifies evidence and performs approved actions.”

## Release milestones

- `v1.0.0`: initial incident-assistant portfolio milestone.
- Planned `v1.1.0`: human evaluations, safe reusable saving, six shared criteria, 18-test suite, and updated documentation.

The next learning project is a separate Infrastructure Runbook Assistant focused on retrieving evidence from approved documents.
