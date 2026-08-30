# Contributing

## Fixture-first changes

If you add a new finding code:

1. Plant the failure in `tests/build_fixtures.py`.
2. Assert the exact code, severity, and basis in `tests/test_engine.py`.
3. Confirm a clean intended edit still does not receive a false `BLOCK`.
4. Add a "looks scary but is okay" fixture when the new rule could overfire.
5. If the rule is platform-specific, add it to `shopify_change_guard/rules.py` and `docs/shopify-rules.md` with a source URL and verification date.

## Severity and basis

- `BLOCK` is for files Shopify will not accept, operations Shopify documents as destructive, cases we cannot safely interpret, or an explicit stricter policy.
- `REVIEW` is for differences that may be intended, including documented non-destructive scope changes.
- `INFO` is for expected, allowlisted edits.
- `DOCUMENTED` / `STRUCTURAL` / `HEURISTIC` / `USER_POLICY` must stay distinct.
- Do not invent Shopify behavior. Cite public import/CSV rules when a check depends on platform semantics.

## Local processing

Keep the tool offline. Do not add store login, API keys, catalog upload, or automatic repair as a default path.

## Tests

```bash
python -m unittest discover -s tests -v
```
