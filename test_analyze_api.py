import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from openai import APIConnectionError, APITimeoutError, OpenAIError, RateLimitError

import structured_incident_app as service
from incident_api import app

PAYLOAD = {
    "severity": "High",
    "summary": "Service unavailable",
    "likely_cause": "Further evidence required",
    "troubleshooting_steps": ["Inspect service status and recent changes"],
    "recommended_action": "Review evidence before making changes",
}


class TestAnalyzeAPI(unittest.TestCase):
    def test_infrastructure_scenarios(self) -> None:
        scenarios = [
            "Windows Server share returns Access Denied after permissions change.",
            "RHEL8 httpd reports AH00072: port 80 already in use.",
            "AWS EC2 HTTPS stopped after a security group change.",
            "Kubernetes returns 503 with only 1/3 pods Ready.",
            "Clients cannot reach DHCP or obtain network addresses.",
        ]
        for description in scenarios:
            with (
                self.subTest(description=description),
                patch.object(service, "OpenAI") as factory,
            ):
                parse = factory.return_value.__enter__.return_value.responses.parse
                parse.return_value = SimpleNamespace(output_parsed=PAYLOAD)
                with (
                    patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}),
                    TestClient(app) as client,
                ):
                    response = client.post(
                        "/analyze", json={"description": description}
                    )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), PAYLOAD)
                self.assertEqual(
                    parse.call_args.kwargs["input"][1]["content"], description
                )
                factory.assert_called_once_with(timeout=30.0, max_retries=0)

    def test_invalid_requests_never_call_ai(self) -> None:
        bodies = [
            {},
            {"description": None},
            {"description": 123},
            {"description": []},
            {"description": " " * 20},
            {"description": "short"},
            {"description": "A" * 4001},
        ]
        with (
            patch("incident_api.analyze_incident") as analyze,
            TestClient(app) as client,
        ):
            for body in bodies:
                with self.subTest(body=body):
                    self.assertEqual(
                        client.post("/analyze", json=body).status_code, 422
                    )
            response = client.post(
                "/analyze", content="{", headers={"Content-Type": "application/json"}
            )
            self.assertEqual(response.status_code, 422)
            analyze.assert_not_called()

    def test_provider_errors_are_sanitized(self) -> None:
        request = httpx.Request("POST", "https://example.test")
        cases = [
            (service.AnalysisConfigurationError("secret"), 503),
            (APITimeoutError(request=request), 504),
            (APIConnectionError(request=request, message="secret"), 503),
            (
                RateLimitError(
                    "secret", response=httpx.Response(429, request=request), body=None
                ),
                503,
            ),
            (OpenAIError("secret"), 502),
            (service.InvalidAnalysisError("secret"), 502),
        ]
        for error, status in cases:
            with (
                self.subTest(error=type(error).__name__),
                patch("incident_api.analyze_incident", side_effect=error),
                TestClient(app) as client,
            ):
                response = client.post(
                    "/analyze", json={"description": "Service has failed to start"}
                )
                self.assertEqual(response.status_code, status)
                self.assertNotIn("secret", response.text)

    def test_api_does_not_save_cli_reports(self) -> None:
        with (
            patch(
                "incident_api.analyze_incident",
                return_value=service.IncidentAnalysis(**PAYLOAD),
            ),
            patch.object(service, "save_report") as save,
            TestClient(app) as client,
        ):
            response = client.post(
                "/analyze", json={"description": "Service has failed to start"}
            )
            self.assertEqual(response.status_code, 200)
            save.assert_not_called()


class TestAnalysisService(unittest.TestCase):
    def test_import_has_no_side_effects(self) -> None:
        code = (
            "from unittest.mock import patch\n"
            "with patch('builtins.input', side_effect=AssertionError('input')):\n"
            " with patch('openai.OpenAI', side_effect=AssertionError('client')):\n"
            "  import structured_incident_app\n"
            "  import incident_api\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", code], check=False, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_key_never_constructs_client(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(service, "OpenAI") as factory,
        ):
            with self.assertRaises(service.AnalysisConfigurationError):
                service.analyze_incident("Service down")
            factory.assert_not_called()

    def test_invalid_model_output(self) -> None:
        for output in [
            None,
            {**PAYLOAD, "severity": "Unknown"},
            {"summary": "Incomplete"},
        ]:
            with (
                self.subTest(output=output),
                patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}),
                patch.object(service, "OpenAI") as factory,
            ):
                factory.return_value.__enter__.return_value.responses.parse.return_value = SimpleNamespace(
                    output_parsed=output
                )
                with self.assertRaises(service.InvalidAnalysisError):
                    service.analyze_incident("Service down")

    def test_cli_saves_existing_report_format(self) -> None:
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as folder:
            try:
                os.chdir(folder)
                with (
                    patch("builtins.input", return_value="  Linux service down  "),
                    patch.object(
                        service,
                        "analyze_incident",
                        return_value=service.IncidentAnalysis(**PAYLOAD),
                    ),
                    patch("builtins.print"),
                ):
                    service.main()
                files = list(Path("incident_reports").glob("incident_*.json"))
                self.assertEqual(len(files), 1)
                data = json.loads(files[0].read_text())
                self.assertEqual(set(data), {"generated_at", "incident", "analysis"})
                self.assertEqual(data["incident"], "Linux service down")
                self.assertEqual(data["analysis"], PAYLOAD)
                self.assertTrue(data["generated_at"].endswith("+00:00"))
            finally:
                os.chdir(original)


if __name__ == "__main__":
    unittest.main()
