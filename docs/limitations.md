# Limitations

- The tool only sees the two files you give it. It cannot inspect live Shopify state.
- A `PASS` is not a guarantee Shopify will accept the file or that every possible catalog hazard was found.
- Multi-location inventory exports are out of scope in v0.2.
- Matrixify / metafield-extended columns are compared as extra columns, not as a full Matrixify engine.
- Image checks inspect URL shape and row association, not whether the remote file still exists.
- Header aliases cover the classic export plus documented synonyms. Unknown custom headings pass through unchanged.
- Encoding detection is best-effort (`utf-8-sig`, `utf-8`, `cp1252`, `latin-1`).
- Reports include field values from your CSVs. Do not publish a report that contains private catalog data.
