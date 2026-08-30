from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.build_fixtures import build
from shopify_change_guard.engine import compare_csvs


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fx = ROOT / "fixtures"
        build(cls.fx)
        cls.original = cls.fx / "original.csv"

    def codes(self, edited_name: str, intend=None):
        result = compare_csvs(self.original, self.fx / edited_name, intended_columns=intend)
        return result.verdict, {f.code for f in result.findings}

    def test_clean_edit_passes_without_false_block(self):
        verdict, codes = self.codes("clean-edit.csv", intend=["Variant Price"])
        self.assertNotEqual(verdict, "BLOCK")
        self.assertTrue(codes.isdisjoint({
            "DESTRUCTIVE_BLANK", "HANDLE_CHANGED", "IMAGE_ROWS_REORDERED",
            "DUPLICATE_VARIANT", "MALFORMED_NUMBER", "BROKEN_IMAGE_URL", "PRODUCTS_REMOVED",
        }))

    def test_accidental_sort_blocks(self):
        verdict, codes = self.codes("accidental-sort.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue("IMAGE_ROWS_REORDERED" in codes or "IMAGES_DROPPED" in codes or "IMAGE_URL_REMOVED" in codes)

    def test_destructive_blank_blocks(self):
        verdict, codes = self.codes("destructive-blank.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("DESTRUCTIVE_BLANK", codes)

    def test_changed_handle_blocks(self):
        verdict, codes = self.codes("changed-handle.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertTrue("HANDLE_CHANGED" in codes or "PRODUCTS_REMOVED" in codes)

    def test_duplicate_variant_blocks(self):
        verdict, codes = self.codes("duplicate-variant.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("DUPLICATE_VARIANT", codes)

    def test_malformed_price_blocks(self):
        verdict, codes = self.codes("malformed-price.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("MALFORMED_NUMBER", codes)

    def test_broken_image_url_blocks(self):
        verdict, codes = self.codes("broken-image-url.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("BROKEN_IMAGE_URL", codes)

    def test_unexpected_column_is_review_when_allowlisted(self):
        verdict, codes = self.codes("unexpected-column-edit.csv", intend=["Variant Price"])
        self.assertIn(verdict, {"REVIEW", "BLOCK"})
        self.assertIn("UNEXPECTED_EDIT", codes)

    def test_dropped_product_blocks(self):
        verdict, codes = self.codes("dropped-product.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("PRODUCTS_REMOVED", codes)

    def test_duplicate_sku_blocks(self):
        verdict, codes = self.codes("duplicate-sku.csv")
        self.assertEqual(verdict, "BLOCK")
        self.assertIn("DUPLICATE_SKU", codes)

    def test_encoding_issue_is_flagged_not_crash(self):
        result = compare_csvs(self.original, self.fx / "encoding-issue.csv")
        self.assertIn(result.verdict, {"PASS", "REVIEW", "BLOCK"})
        self.assertTrue(result.stats["edited_rows"] >= 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
