from __future__ import annotations

from collections import defaultdict


def flag_sku_barcode_collisions(add, edit_by_handle, variant_rows, *, strict_identifiers: bool) -> None:
    sku_owners: dict[str, list[tuple[str, int]]] = defaultdict(list)
    barcode_owners: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for handle, rows in edit_by_handle.items():
        for row_i, row in variant_rows(rows):
            sku = (row.get("Variant SKU") or "").strip()
            barcode = (row.get("Variant Barcode") or "").strip()
            if sku:
                sku_owners[sku].append((handle, row_i))
            if barcode:
                barcode_owners[barcode].append((handle, row_i))
    sku_severity = "BLOCK" if strict_identifiers else "REVIEW"
    sku_basis = "USER_POLICY" if strict_identifiers else "STRUCTURAL"
    for sku, owners in sku_owners.items():
        if len(owners) > 1:
            handles = ", ".join(sorted({h for h, _ in owners}))
            add(
                severity=sku_severity,
                code="DUPLICATE_SKU",
                title="Variant SKU is used more than once",
                detail=(
                    f"SKU {sku!r} appears on {len(owners)} edited variant row(s) across handle(s) {handles}. "
                    "Shopify warns against duplicate SKUs but permits them in some workflows."
                ),
                field="Variant SKU",
                edited_value=sku,
                basis=sku_basis,
            )
    for barcode, owners in barcode_owners.items():
        if len(owners) > 1:
            handles = ", ".join(sorted({h for h, _ in owners}))
            add(
                severity=sku_severity,
                code="DUPLICATE_BARCODE",
                title="Variant barcode is used more than once",
                detail=f"Barcode {barcode!r} appears on {len(owners)} edited variant row(s) across handle(s) {handles}.",
                field="Variant Barcode",
                edited_value=barcode,
                basis=sku_basis,
            )
