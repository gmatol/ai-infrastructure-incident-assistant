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


def save_evaluation() -> Path:
    scores = {
        "facts_are_accurate": 2,
        "uncertainty_is_clear": 2,
        "investigation_is_relevant": 2,
        "actions_are_cautious": 2,
        "next_evidence_is_clear": 2,
    }

    validate_scores(scores)

    evaluation = {
        "report_filename": "incident_20261007_193759_013394.json",
        "reviewer": "Guot Deng Anyak",
        "scores": scores,
        "total_score": sum(scores.values()),
        "maximum_score": len(scores) * 2,
        "improvement_needed": (
            "Justify severity using business impact, "
            "affected users, and outage duration."
        ),
        "cause_verified": False,
    }

    evaluations_folder = Path(__file__).resolve().parent / "evaluations"
    evaluations_folder.mkdir(exist_ok=True)

    evaluation_path = evaluations_folder / (
        "evaluation_incident_20261007_193759_013394.json"
    )

    with evaluation_path.open("w", encoding="utf-8") as file:
        json.dump(evaluation, file, indent=2)

    return evaluation_path


if __name__ == "__main__":
    try:
        saved_path = save_evaluation()
        print("Evaluation saved to:", saved_path)
    except ValueError as error:
        raise SystemExit(f"Evaluation not saved: {error}")