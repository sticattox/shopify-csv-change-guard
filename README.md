# Shopify CSV Change Guard

Local preflight for Shopify product CSVs.

Give it the original export and the file you edited. It tells you whether the edited file still looks like the catalog you meant to change, or whether a spreadsheet accident is about to hit Shopify.

It does not log into Shopify. It does not upload your catalog. It does not import anything.

## Why it exists

Shopify's own import help says:

- a product CSV import cannot be canceled once it starts
- there is no import-history view
- merchants should back up first
- sorting a product CSV in spreadsheet software can disconnect images

Overwrite imports treat blank cells as "erase this field." Changing a handle creates a different product. Changing option values recreates variant IDs.

Change Guard is not another "fix my CSV" formatter. It is a before/after safety check.

## Verdicts

- **PASS** — no destructive pattern detected
- **REVIEW** — differences exist that may be intended
- **BLOCK** — a known destructive pattern is present; do not import yet

## Install

```bash
python -m pip install -e .
```

Or run from this folder with no install:

```bash
python -m shopify_change_guard ORIGINAL.csv EDITED.csv
```

## Usage

```bash
shopify-change-guard export.csv edited.csv --intend "Variant Price" --intend "Tags" -o reports/
```

Intended columns can also come from a file:

```bash
shopify-change-guard export.csv edited.csv --intend-file allowlist.txt
```

Exit codes:

- `0` PASS
- `10` REVIEW
- `20` BLOCK
- `2` file missing / bad arguments

`--quiet` prints only the verdict. `--json` prints the machine-readable report.

## What it flags

| Code | Meaning |
| --- | --- |
| `HANDLE_CHANGED` | Same title now uses a different handle |
| `DESTRUCTIVE_BLANK` | A previously filled critical field is now empty |
| `IMAGE_ROWS_REORDERED` | Same images, different row order |
| `IMAGES_DROPPED` / `IMAGE_URL_REMOVED` | Product lost image URLs |
| `BROKEN_IMAGE_URL` | Not a public http(s) URL, or forbidden `_thumb` / `_small` / `_medium` suffix |
| `DUPLICATE_VARIANT` | Two rows share the same option combination |
| `DUPLICATE_SKU` / `DUPLICATE_BARCODE` | Identity values collide in the edited file |
| `VARIANT_REMOVED` | An option combination disappeared |
| `MALFORMED_NUMBER` | Price/qty/weight is not a plain number |
| `PRODUCTS_REMOVED` | A handle from the export is gone |
| `UNEXPECTED_EDIT` | A column changed outside `--intend` |
| `ENCODING_CHANGED` | File encoding is no longer the same |

## Fixture proof

```bash
python -m unittest discover -s tests -v
```

The fixture pack plants the failure modes above. A clean price edit must not receive a false `BLOCK`.

## What it is not

- Not a Shopify app
- Not an official Shopify product
- Not a guarantee that Shopify will accept the file
- Not a substitute for a catalog backup
- Not a tool that repairs or writes to your store

See [docs/limitations.md](docs/limitations.md) and [docs/WHY-THIS-PRODUCT.md](docs/WHY-THIS-PRODUCT.md).

## License

MIT. See `LICENSE`.
