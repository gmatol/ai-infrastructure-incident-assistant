from __future__ import annotations

import json
from pathlib import Path


def validate_scores(scores: dict) -> None:
    if not scores:
        raise ValueError("At least one score is required.")

    for criterion, score in scores.items():
        if type(score) is not int or score not in (0, 1, 2):
            raise ValueError(
                f"{criterion}: score must be an integer "
                f"0, 1, or 2. Received: {score!r}"
            )


def save_evaluation(
    report_filename: str,
    scores: dict,
    improvement_needed: str,
    project_folder: Path | None = None
) -> Path:
    validate_scores(scores)

    if project_folder is None:
        project_folder = Path(__file__).resolve().parent

    if (
        Path(report_filename).name != report_filename
        or not report_filename.startswith("incident_")
        or not report_filename.endswith(".json")
    ):
        raise ValueError("Enter an incident JSON filename only.")

    report_path = project_folder / "incident_reports" / report_filename

    if not report_path.is_file():
        raise ValueError(f"Report not found: {report_filename}")

    evaluation = {
        "report_filename": report_filename,
        "reviewer": "Guot Deng Anyak",
        "scores": scores,
        "total_score": sum(scores.values()),
        "maximum_score": len(scores) * 2,
        "improvement_needed": improvement_needed,
        "cause_verified": False,
    }

    evaluations_folder = project_folder / "evaluations"
    evaluations_folder.mkdir(exist_ok=True)

    evaluation_path = evaluations_folder / (
        f"evaluation_{report_filename}"
    )

    with evaluation_path.open("x", encoding="utf-8") as file:
        json.dump(evaluation, file, indent=2)

    return evaluation_path


def main() -> None:
    report_filename = input("Enter incident report filename: ").strip()

    criteria = [
        "facts_are_accurate",
        "uncertainty_is_clear",
        "investigation_is_relevant",
        "actions_are_cautious",
        "next_evidence_is_clear",
    ]

    scores = {}

    for criterion in criteria:
        scores[criterion] = int(
            input(f"{criterion} (0, 1, or 2): ").strip()
        )

    improvement_needed = input("What needs improvement? ").strip()

    saved_path = save_evaluation(
        report_filename,
        scores,
        improvement_needed
    )

    print("Evaluation saved to:", saved_path)


if __name__ == "__main__":
    try:
        main()
    except FileExistsError:
        raise SystemExit(
            "Evaluation already exists. Existing file was preserved."
        )
    except ValueError as error:
        raise SystemExit(f"Evaluation not saved: {error}")