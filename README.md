# Shopify CSV Change Guard

Local preflight for Shopify product CSVs.

Give it the original export and the file you edited. It tells you what changed, what Shopify says those changes mean, and whether they match what you intended.

It does not log into Shopify. It does not upload your catalog. It does not import anything. It does not repair files.

## Why it exists

Most spreadsheet disasters produce perfectly valid CSV. The failure mode is semantic drift: a cell was blanked, a variant identity changed, a SKU collided, or something outside the intended edit changed.

Shopify's product CSV docs currently say:

- overwrite imports replace values in included columns
- blank included fields can erase existing values
- missing dependent variant columns can delete variant structure
- changing option values destroys and recreates variant IDs
- CSV files cannot bulk-delete products
- product CSVs must be UTF-8 and comma-separated
- sorting exported product CSVs can separate images from products

Change Guard is a before/after safety check, not a CSV formatter.

## Verdicts are two-axis

Severity is not the same thing as certainty.

| Severity | Means |
| --- | --- |
| **PASS** | no flagged differences |
| **REVIEW** | differences exist that may be intended, or a documented non-destructive scope change |
| **BLOCK** | the file is invalid for Shopify, a documented destructive operation is present, or you opted into a stricter policy |

| Basis | Means |
| --- | --- |
| **DOCUMENTED** | tied to a Shopify help-center rule in `docs/shopify-rules.md` |
| **STRUCTURAL** | the file itself is internally inconsistent |
| **HEURISTIC** | inferred, and labeled as such |
| **USER_POLICY** | produced by `--intend`, `--scope`, or `--strict-identifiers` |

`BLOCK / DOCUMENTED` and `REVIEW / HEURISTIC` are not the same claim.

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
shopify-change-guard export.csv edited.csv \
  --intend Price --intend Tags \
  --scope full \
  -o reports/
```

`--intend` accepts official names or aliases (`SKU`, `Price`, `URL handle`).

```bash
shopify-change-guard export.csv edited.csv --intend-file allowlist.txt --scope subset
shopify-change-guard export.csv edited.csv --strict-identifiers
shopify-change-guard export.csv edited.csv --redact-values --json
```

| Flag | Effect |
| --- | --- |
| `--scope full` | default. Absent original products become `IMPORT_SCOPE_CHANGED` / REVIEW |
| `--scope subset` | a partial catalog is expected; missing products are not suspicious |
| `--strict-identifiers` | duplicate SKU/barcode escalate from REVIEW to BLOCK |
| `--redact-values` | replace before/after values with `[REDACTED len=N]` |

Exit codes: `0` PASS, `10` REVIEW, `20` BLOCK, `2` bad arguments.

## What changed in 0.3

The comparison pipeline is now parse → generic diff → Shopify rules → intent/policy → verdict.

- Parser preserves raw cell text. Trailing-space SKU changes are visible.
- Variant identity keeps exact option text. `Navy` → `navy` is `OPTION_VALUE_CHANGED`.
- Missing products are `IMPORT_SCOPE_CHANGED` / REVIEW, not a fake bulk-delete.
- Duplicate SKUs are REVIEW unless `--strict-identifiers`.
- Non-UTF-8 and non-comma edited files BLOCK.
- Unexpected-edit detection covers every comparable changed column.
- Images are judged per product, not by global row sequence.
- Findings carry `basis`, and documented rules carry `rule_id` + source URL.

## Fixture proof

```bash
python -m unittest discover -s tests -v
```

The fixture pack includes both "this is dangerous" cases and "this looks scary but is okay" cases. A clean price edit must not receive a false `BLOCK`. Reordering whole product blocks without breaking image association must not receive a false `BLOCK`.

## What it is not

- Not a Shopify app
- Not an official Shopify product
- Not a guarantee that Shopify will accept the file
- Not a substitute for a catalog backup
- Not a tool that repairs or writes to your store
- Not connected to the Shopify API on purpose

See [docs/architecture.md](docs/architecture.md), [docs/shopify-rules.md](docs/shopify-rules.md), [docs/limitations.md](docs/limitations.md), and [docs/WHY-THIS-PRODUCT.md](docs/WHY-THIS-PRODUCT.md).

## License

MIT. See `LICENSE`.
