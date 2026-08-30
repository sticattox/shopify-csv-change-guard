# Architecture

```
CSV A + CSV B
      ↓
Parse without destroying information
      ↓
Canonical representation
      ↓
Generic ChangeSet
"What actually changed?"
      ↓
Shopify rule engine
"What does Shopify say these changes mean?"
      ↓
Intent / policy layer
"Was this change expected?"
      ↓
Findings
      ↓
PASS / REVIEW / BLOCK
```

Fact, platform rule, and heuristic are not the same thing.

Example:

- Vendor changed = fact
- Blank Vendor will overwrite the existing Vendor when overwrite is enabled = documented Shopify behavior
- You probably did not mean to change Vendor = inference from `--intend`

Each finding has two axes:

- `severity`: BLOCK | REVIEW | INFO
- `basis`: DOCUMENTED | STRUCTURAL | HEURISTIC | USER_POLICY

The generic diff engine is Shopify-aware only after the ChangeSet exists. `--intend` is applied to every comparable changed column, not a hard-coded subset of field groups.

Variant identity preserves exact option text. `Navy` → `navy` is an option-value change, not a silent normalize-away.

Images are evaluated inside each product (handle + Image Src + Image Position). Reordering whole product blocks without breaking those relationships is not treated as image destruction.
