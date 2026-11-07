from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runbook_context import get_runbook_context


class TestRunbookPathBoundary(unittest.TestCase):
    def setUp(self) -> None:
        temporary_folder = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_folder.cleanup)

        root = Path(temporary_folder.name)
        self.runbooks = root / "runbooks"
        self.runbooks.mkdir()

        self.outside_file = root / "outside.md"
        self.outside_file.write_text(
            "Fictional file outside the runbooks folder.",
            encoding="utf-8",
        )

    def load_context(self, filename: str) -> dict[str, str] | None:
        index = [{"filename": filename, "keywords": ["dns"]}]
        (self.runbooks / "index.json").write_text(
            json.dumps(index),
            encoding="utf-8",
        )

        with patch("runbook_retrieval.RUNBOOKS_FOLDER", self.runbooks):
            return get_runbook_context("Windows DNS lookup failed.")

    def test_valid_runbook_loads(self) -> None:
        instructions = "Check the configured DNS server."
        (self.runbooks / "windows_dns.md").write_text(
            instructions,
            encoding="utf-8",
        )

        self.assertEqual(
            self.load_context("windows_dns.md"),
            {
                "source": "runbooks/windows_dns.md",
                "text": instructions,
            },
        )

    def test_outside_paths_are_rejected(self) -> None:
        for filename in ("../outside.md", str(self.outside_file)):
            with (
                self.subTest(filename=filename),
                self.assertRaisesRegex(ValueError, "stay inside"),
            ):
                self.load_context(filename)

    def test_symlink_pointing_outside_is_rejected(self) -> None:
        (self.runbooks / "dns_link.md").symlink_to(self.outside_file)

        with self.assertRaisesRegex(ValueError, "stay inside"):
            self.load_context("dns_link.md")


if __name__ == "__main__":
    unittest.main()