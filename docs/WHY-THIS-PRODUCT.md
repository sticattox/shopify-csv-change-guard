# Why this product exists

Shopify product CSV imports are high-consequence and weakly reversible.

Official product-import help currently documents that:

- an import cannot be canceled once it starts
- there is no import-history view
- merchants should back up product data first
- sorting a product CSV in spreadsheet software can disconnect images

Overwrite imports treat blank cells as instructions to erase existing fields. Changing a handle creates a different product. Changing option values recreates variant IDs.

Merchants still do the obvious thing: export, edit in Excel or Google Sheets, re-import. That workflow is where titles get blanked, image-only rows drift away from their product, SKUs collide, and prices pick up currency symbols.

Paid CSV utilities already exist. Most of them format or "fix" a file. Change Guard does a different job: compare the original export with the edited file and say whether the difference looks like the change you meant to make.

The first edition stays local. The catalog never leaves the machine. Nothing is imported. A report is not a promise that Shopify will accept the file; it is evidence you can review before you press Import.
