from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import incident_service
from incident_service import IncidentAnalysis, analyze_incident
from runbook_context import get_runbook_context

PROJECT = Path(__file__).resolve().parent
CASES = ("w-u", "w-c", "l-u", "l-c", "a-u", "a-c", "k-u", "k-c")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_output(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments],
        cwd=PROJECT,
        text=True,
    ).strip()


def build_record(
    case: str,
    *,
    extra_instructions: str | None = None,
) -> dict:
    if case not in CASES:
        raise ValueError(f"Unknown evaluation case: {case}")

    if extra_instructions is not None:
        extra_instructions = extra_instructions.strip()
        if not extra_instructions:
            raise ValueError("Extra instructions cannot be blank.")

    prompt_path = (
        PROJECT / "evaluation_cases/uncertain-impact/prompts" / f"{case}.txt"
    )
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    context = get_runbook_context(prompt)

    client = Mock()
    client.responses.parse.return_value.output_parsed = IncidentAnalysis(
        severity="Medium",
        summary="Simulated placeholder; not a model assessment.",
        likely_cause="Not assessed.",
        troubleshooting_steps=["No infrastructure checks were executed."],
        recommended_action="Review the captured request.",
    )

    original_instructions = incident_service.INSTRUCTIONS
    instruction_scope = (
        patch.object(
            incident_service,
            "INSTRUCTIONS",
            original_instructions + "\n\n" + extra_instructions,
        )
        if extra_instructions is not None
        else nullcontext()
    )

    with instruction_scope:
        analyze_incident(prompt, client, runbook_context=context)
    client.responses.parse.assert_called_once()
    arguments = client.responses.parse.call_args.kwargs

    request = {
        "model": arguments["model"],
        "input": arguments["input"],
        "response_format": {
            "name": arguments["text_format"].__name__,
            "schema": arguments["text_format"].model_json_schema(),
        },
    }
    serialized_request = json.dumps(
        request, sort_keys=True, ensure_ascii=False
    )

    return {
        "case": case.upper(),
        "mode": "simulated",
        "outcome": "request_captured",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "application_sha": git_output("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git_output("status", "--porcelain")),
        "entry_point": "incident_service.analyze_incident",
        "instruction_variant": (
            "candidate"
            if extra_instructions is not None
            else "application_default"
        ),
        "extra_instructions_sha256": (
            sha256(extra_instructions)
            if extra_instructions is not None
            else None
        ),
        "incident": prompt,
        "incident_sha256": sha256(prompt),
        "instructions_sha256": sha256(arguments["input"][0]["content"]),
        "runbook_context": context,
        "runbook_text_sha256": (
            sha256(context["text"]) if context is not None else None
        ),
        "request": request,
        "request_sha256": sha256(serialized_request),
        "live_api_requests": 0,
        "analysis": None,
    }


def capture_attempt(
    case: str,
    *,
    extra_instructions_path: Path | None = None,
) -> dict:
    extra = None
    stage = "instruction_read"

    try:
        if extra_instructions_path is not None:
            extra = extra_instructions_path.expanduser().read_text(
                encoding="utf-8"
            )

        stage = "request_capture"
        return build_record(case, extra_instructions=extra)

    except (
        OSError,
        ValueError,
        RuntimeError,
        AssertionError,
        subprocess.SubprocessError,
    ) as error:
        commit = None
        dirty = None
        try:
            commit = git_output("rev-parse", "HEAD")
            dirty = bool(git_output("status", "--porcelain"))
        except (OSError, subprocess.SubprocessError):
            pass

        return {
            "case": case.upper(),
            "mode": "simulated",
            "outcome": "failed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "application_sha": commit,
            "working_tree_dirty": dirty,
            "entry_point": "incident_service.analyze_incident",
            "instruction_variant": (
                "candidate"
                if extra_instructions_path is not None
                else "application_default"
            ),
            "extra_instructions_sha256": (
                sha256(extra.strip()) if extra is not None else None
            ),
            "failure_stage": stage,
            "error_category": type(error).__name__,
            "request": None,
            "request_sha256": None,
            "live_api_requests": 0,
            "analysis": None,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Capture an evaluation request without calling a model."
    )
    parser.add_argument("case", choices=CASES)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "AI-Learning/evaluation-notes",
    )
    parser.add_argument(
        "--extra-instructions",
        type=Path,
        help="Append instructions from a UTF-8 file for simulated capture.",
    )
    args = parser.parse_args()

    record = capture_attempt(
        args.case,
        extra_instructions_path=args.extra_instructions,
    )

    output_dir = args.output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    folder = Path(
        tempfile.mkdtemp(
            prefix=f"{args.case}-simulated-",
            dir=output_dir,
        )
    )
    output = folder / "record.json"

    with output.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("Case:", record["case"])
    print("Mode:", record["mode"])
    print("Instruction variant:", record["instruction_variant"])
    print("Outcome:", record["outcome"])

    if record["outcome"] == "failed":
        print("Failure stage:", record["failure_stage"])
        print("Error category:", record["error_category"])
    else:
        context = record["runbook_context"]
        print("Runbook:", context["source"] if context else "no match")

    print("Live API requests:", record["live_api_requests"])
    print("Saved:", output)

    if record["outcome"] == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
