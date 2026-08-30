# Limitations

- The tool only sees the two files you give it. It cannot inspect live Shopify state.
- A `PASS` is not a guarantee Shopify will accept the file or that every possible catalog hazard was found.
- `BLOCK` is reserved for documented invalid files, documented destructive operations, or an explicit stricter policy. Heuristics are labeled `HEURISTIC` and usually stay `REVIEW`.
- Multi-location inventory exports are out of scope in v0.3.
- Matrixify / metafield-extended columns are compared as extra columns, not as a full Matrixify engine.
- Image checks inspect URL shape and per-product association, not whether the remote file still exists.
- Header aliases cover the classic export plus documented synonyms. Unknown custom headings pass through unchanged.
- Encoding detection tries UTF-8 first, then cp1252 / latin-1. Edited files that are not valid UTF-8 are BLOCK.
- Reports include field values from your CSVs unless you pass `--redact-values`. Do not publish a report that contains private catalog data.
- This tool never writes to Shopify and never "repairs" an edited file.
