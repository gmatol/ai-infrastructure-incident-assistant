import json
from pathlib import Path

RUNBOOKS_FOLDER = Path(__file__).resolve().parent / "runbooks"


def find_runbook(description: str) -> str:
    index_path = RUNBOOKS_FOLDER / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))

    description = description.lower()

    for entry in index:
        if any(
            keyword.lower() in description
            for keyword in entry["keywords"]
        ):
            filename = entry["filename"]
            runbook_path = RUNBOOKS_FOLDER / filename

            if not runbook_path.is_file():
                raise FileNotFoundError(
                    f"Indexed runbook is missing: {filename}"
                )

            return filename

    return ""


def main() -> None:
    description = input("Describe the incident: ").strip()
    filename = find_runbook(description)

    if filename:
        print("Matched runbook:", filename)
    else:
        print("No matching runbook found.")


if __name__ == "__main__":
    main()
