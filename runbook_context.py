from __future__ import annotations

from runbook_retrieval import find_runbook, resolve_runbook_path


def get_runbook_context(description: str) -> dict[str, str] | None:
    filename = find_runbook(description)

    if not filename:
        return None

    runbook_path = resolve_runbook_path(filename)

    return {
        "source": f"runbooks/{filename}",
        "text": runbook_path.read_text(encoding="utf-8"),
    }


def main() -> None:
    description = input("Describe the incident: ").strip()
    context = get_runbook_context(description)

    if context is None:
        print("No matching runbook found.")
        return

    print("Source:", context["source"])
    print("\nRunbook text:")
    print(context["text"])


if __name__ == "__main__":
    main()