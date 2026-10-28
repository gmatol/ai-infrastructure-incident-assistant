import json
from urllib.request import urlopen


def main() -> int:
    try:
        with urlopen(
            "http://127.0.0.1:8001/health",
            timeout=5,
        ) as response:
            body = json.load(response)
            request_id = response.headers.get("X-Request-ID")

            if response.status != 200:
                raise ValueError("Expected HTTP 200.")

            if body != {"status": "ok"}:
                raise ValueError("Unexpected health response.")

            if not request_id:
                raise ValueError("Request ID is missing.")

        print("PASS: health response and request ID verified.")
        print("Request ID:", request_id)
        return 0

    except (OSError, ValueError) as error:
        print("FAIL:", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())