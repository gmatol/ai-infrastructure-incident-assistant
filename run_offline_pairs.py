from __future__ import annotations

import argparse
import json
import tempfile
from copy import deepcopy
from pathlib import Path

from record_evaluation_run import CASES, capture_attempt, sha256


def compare_pair(default: dict, candidate: dict) -> str:
    if any(
        record["outcome"] != "request_captured"
        for record in (default, candidate)
    ):
        return "not_compared"

    expected = deepcopy(default["request"])
    original = expected["input"][0]["content"]
    revised = candidate["request"]["input"][0]["content"]
    prefix = original + "\n\n"

    if not revised.startswith(prefix):
        return "mismatch"

    extra = revised[len(prefix):]
    if not extra.strip():
        return "mismatch"

    if sha256(extra) != candidate["extra_instructions_sha256"]:
        return "mismatch"

    expected["input"][0]["content"] = revised
    if candidate["request"] != expected:
        return "mismatch"

    return "matched"


def build_batch(instruction_file: Path) -> dict:
    records = []
    comparisons = []

    for case in CASES:
        default = capture_attempt(case)
        candidate = capture_attempt(
            case,
            extra_instructions_path=instruction_file,
        )
        records.extend((default, candidate))
        comparisons.append({
            "case": case.upper(),
            "status": compare_pair(default, candidate),
        })

    captured = sum(
        record["outcome"] == "request_captured"
        for record in records
    )
    hashes = sorted({
        record["extra_instructions_sha256"]
        for record in records
        if record["instruction_variant"] == "candidate"
        and record["outcome"] == "request_captured"
    })

    return {
        "mode": "simulated",
        "attempted": len(records),
        "captured": captured,
        "failed": len(records) - captured,
        "matched_pairs": sum(
            pair["status"] == "matched" for pair in comparisons
        ),
        "mismatched_pairs": sum(
            pair["status"] == "mismatch" for pair in comparisons
        ),
        "not_compared_pairs": sum(
            pair["status"] == "not_compared" for pair in comparisons
        ),
        "candidate_instruction_hashes": hashes,
        "candidate_instruction_consistent": len(hashes) == 1,
        "live_api_requests": sum(
            record["live_api_requests"] for record in records
        ),
        "records": records,
        "comparisons": comparisons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare offline default and candidate requests."
    )
    parser.add_argument("--extra-instructions", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "AI-Learning/evaluation-notes",
    )
    args = parser.parse_args()

    batch = build_batch(args.extra_instructions.expanduser())

    output_dir = args.output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    folder = Path(
        tempfile.mkdtemp(prefix="offline-pairs-", dir=output_dir)
    )
    output = folder / "batch.json"

    with output.open("x", encoding="utf-8") as handle:
        json.dump(batch, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("Mode:", batch["mode"])
    print("Attempts:", batch["attempted"])
    print("Captured:", batch["captured"])
    print("Failed:", batch["failed"])
    print("Matched pairs:", batch["matched_pairs"])
    print("Mismatched pairs:", batch["mismatched_pairs"])
    print("Not compared:", batch["not_compared_pairs"])
    print(
        "Candidate instruction consistent:",
        batch["candidate_instruction_consistent"],
    )
    print("Live API requests:", batch["live_api_requests"])
    print("Saved:", output)

    if (
        batch["failed"]
        or batch["mismatched_pairs"]
        or batch["not_compared_pairs"]
        or not batch["candidate_instruction_consistent"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
