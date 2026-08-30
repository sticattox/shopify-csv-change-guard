# Contributing

## Fixture-first changes

If you add a new finding code:

1. Plant the failure in `tests/build_fixtures.py`.
2. Assert the exact code in `tests/test_engine.py`.
3. Confirm a clean intended edit still does not receive a false `BLOCK`.
4. Document the code in the README table.

## Severity rules

- `BLOCK` is for patterns that commonly destroy live catalog data or recreate identities.
- `REVIEW` is for differences that may be intended.
- `INFO` is for expected, allowlisted edits.
- Do not invent Shopify behavior. Cite public import/CSV rules when a check depends on platform semantics.

## Local processing

Keep the tool offline. Do not add store login, API keys, or catalog upload as a default path.

## Tests

```bash
python -m unittest discover -s tests -v
```
