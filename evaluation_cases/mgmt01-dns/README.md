# MGMT01 DNS evaluation case

A sanitized, symptom-only evaluation of the existing assistant using a completed
Windows administration lab. No application changes, AWS access or new project is
required. This case is prepared; no live AI response or score is included.

## 1. Prepare on your Mac (no API request)

In Terminal, use your existing checkout:

```bash
cd "$HOME/ai-infrastructure-incident-assistant"
git status --short
git pull --ff-only origin main
source .venv/bin/activate
cat evaluation_cases/mgmt01-dns/prompt.txt
```

After this case is merged, main contains these files. Before merge, fetch and switch
to the PR branch only if your working tree is clean:

```bash
git fetch origin
git switch --track origin/eval/mgmt01-dns-recovery
```

If that local branch already exists, use `git switch eval/mgmt01-dns-recovery`.
If Git reports local changes, stop and preserve them before switching. Do not reset
or discard work. If `.venv` is missing, follow the root README setup first.

Read prompt.txt now; keep REFERENCE.md closed until output has been captured.
It contains the answer key. Do not paste the source report or reference into input.
The prompt is a single line because the existing CLI reads one line.

## 2. Generate only after approving API cost

**STOP: the next block makes a paid-capable OpenAI API request.** Run it only when
you decide to authorize that cost. No API request was made to prepare this case.
Check the model configured in incident_service.py and account access first. The
SDK can retry failed requests; do not assume a fixed request count or dollar cost.
Keep your API key private in your existing ignored .env; never paste it into chat.

```bash
source .env
python structured_incident_app.py < evaluation_cases/mgmt01-dns/prompt.txt
```

The CLI prints a report path after successful generation. Save that exact filename.
If it reports an error and no new file, stop: do not score an older report. This
command only submits the sanitized prompt and saves guidance; it executes no Windows
commands. Do not recreate the DNS fault or touch the separate RDP exercise.

## 3. Review and record locally (no API request)

Open the generated `incident_reports/incident_<timestamp>.json` in VS Code. Compare
its actual guidance with REFERENCE.md and fill in that file's results-record fields
in a local note. Record the application commit with:

```bash
git rev-parse HEAD
python save_evaluation.py
```

Enter your name, then the exact new report filename WITHOUT `incident_reports/`.
Give each of the existing six criteria 0, 1 or 2 and enter a specific improvement
note. The script saves `evaluations/evaluation_<report_filename>` and preserves an
existing evaluation rather than overwriting it. Leave cause_verified=false.

The scorer asks for numbers; use the reference anchors to decide them only after
reading the answer. Record quoted evidence and diagnosis agreement in your local
note because the scorer does not store those fields separately. Keep raw responses,
review notes and generated evaluations local until you have checked them for secrets
or unexpected content. Incident reports are ignored; evaluations are not automatically
ignored, so inspect `git status --short` before staging anything. Never use blanket
`git add .` to publish a run.

Optional software checks, using installed project dependencies:

```bash
python run_tests.py
ruff check .
```

These make no paid model requests. A passing suite does not show that this scenario
was diagnosed correctly. The /12 review is subjective; reference agreement describes
one case and is not a model-wide reliability metric.

## Portfolio evidence

The existing administration report demonstrates fault reproduction, DNS resolver
comparison and verified recovery. This case adds sanitized input design, separation
of model evidence from a reference answer, reproducible report capture and explicit
human evaluation. Once an answer is recorded, explain its actual strengths and errors.
Until then, say "I built an evaluation case from my verified DNS lab," not "the AI
correctly diagnosed it." No new production impact, timing or user-login claim follows.
