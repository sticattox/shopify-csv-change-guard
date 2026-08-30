from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shopify_change_guard.parser import load_csv
from shopify_change_guard.schema import normalize_header


class ParserTests(unittest.TestCase):
    def test_alias_normalization(self):
        self.assertEqual(normalize_header("URL handle"), "Handle")
        self.assertEqual(normalize_header("Product image URL"), "Image Src")
        self.assertEqual(normalize_header("SKU"), "Variant SKU")

    def test_bom_and_alias_headers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bom.csv"
            path.write_bytes(
                b"\xef\xbb\xbfURL handle,Title,SKU\n"
                b"hat,Wool Hat,HAT-1\n"
            )
            parsed = load_csv(path)
            self.assertTrue(parsed.has_bom)
            self.assertEqual(parsed.headers, ["Handle", "Title", "Variant SKU"])
            self.assertEqual(parsed.rows[0]["Handle"], "hat")
            self.assertEqual(parsed.rows[0]["Variant SKU"], "HAT-1")

    def test_tab_delimiter_is_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tabs.csv"
            path.write_text("Handle\tTitle\nhat\tWool Hat\n", encoding="utf-8")
            parsed = load_csv(path)
            self.assertTrue(any("Delimiter" in issue for issue in parsed.issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
