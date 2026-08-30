# Shopify rule provenance

Change Guard separates three different kinds of statement:

- **fact** — this cell changed from A to B
- **platform rule** — Shopify documents a consequence for that class of change
- **heuristic / user policy** — we inferred intent or applied an operator-supplied allowlist

Every platform-specific finding can carry a rule ID. Dates below are the last time the linked help page was checked.

Source of record: [Using CSV files to import and export products](https://help.shopify.com/en/manual/products/import-export/using-csv)

Verified against Shopify Help Center: 2026-08-30

| Rule ID | Finding | Default severity | Basis | Consequence |
| --- | --- | --- | --- | --- |
| SCG-SHOPIFY-001 | INVALID_ENCODING | BLOCK | DOCUMENTED | Product CSVs must be UTF-8. |
| SCG-SHOPIFY-002 | INVALID_DELIMITER | BLOCK | DOCUMENTED | Columns must be comma-separated. |
| SCG-SHOPIFY-003 | DESTRUCTIVE_BLANK | BLOCK | DOCUMENTED | Blank cells in included columns overwrite existing values when overwrite is enabled. |
| SCG-SHOPIFY-004 | OPTIONS_REQUIRED | BLOCK | DOCUMENTED | Variant fields depend on Option1 Name and Option1 Value. |
| SCG-SHOPIFY-005 | OPTION_VALUE_CHANGED | BLOCK | DOCUMENTED | Changing option values deletes existing variant IDs and creates new ones. |
| SCG-SHOPIFY-006 | VARIANT_ID_RECREATION_RISK | BLOCK | DOCUMENTED | Variant ID changes can break third-party dependencies. |
| SCG-SHOPIFY-007 | IMPORT_SCOPE_CHANGED | REVIEW | DOCUMENTED | CSV files cannot bulk-delete products. Absent handles change import scope, they do not delete. |
| SCG-SHOPIFY-008 | FILE_TOO_LARGE | BLOCK | STRUCTURAL | Admin uploads have long been rejected above 15 MB; confirm against the current importer. |
| SCG-SHOPIFY-009 | MISSING_HANDLE_COLUMN | BLOCK | DOCUMENTED | Updates require the URL handle column. |
| SCG-SHOPIFY-010 | BROKEN_IMAGE_URL | BLOCK | STRUCTURAL | Image Src must be a public URL Shopify can fetch. |
| SCG-SHOPIFY-011 | UNSUPPORTED_COLUMN | REVIEW | DOCUMENTED | Arbitrary added columns are outside the official product CSV contract. |

Findings without a rule ID are either generic facts (`FIELD_CHANGED`), structural file problems (`DUPLICATE_VARIANT`), heuristics (`POSSIBLE_HANDLE_CHANGE`), or user policy (`UNEXPECTED_EDIT`, `--strict-identifiers`).

Duplicate SKUs are **REVIEW / STRUCTURAL** by default. Shopify warns against them and still permits them in some workflows. `--strict-identifiers` escalates that finding to BLOCK / USER_POLICY.
