from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.build_fixtures import build
from shopify_change_guard.cli import main


class CliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = ROOT / "fixtures"
        build(cls.fx)

    def test_clean_edit_exit_not_block(self):
        code = main(
            [
                str(self.fx / "original.csv"),
                str(self.fx / "clean-edit.csv"),
                "--intend",
                "Variant Price",
                "--quiet",
            ]
        )
        self.assertIn(code, {0, 10})

    def test_block_exit_code(self):
        code = main(
            [
                str(self.fx / "original.csv"),
                str(self.fx / "destructive-blank.csv"),
                "--quiet",
            ]
        )
        self.assertEqual(code, 20)

    def test_missing_file_exit_2(self):
        code = main([str(self.fx / "original.csv"), str(self.fx / "nope.csv")])
        self.assertEqual(code, 2)

    def test_json_has_no_absolute_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            code = main(
                [
                    str(self.fx / "original.csv"),
                    str(self.fx / "clean-edit.csv"),
                    "--intend",
                    "Variant Price",
                    "--json",
                    "-o",
                    str(out),
                ]
            )
            self.assertIn(code, {0, 10})
            payload = json.loads((out / "change-guard-report.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "0.2.0")
            self.assertNotIn("path", payload["original"])
            self.assertEqual(payload["original"]["name"], "original.csv")


if __name__ == "__main__":
    unittest.main(verbosity=2)
