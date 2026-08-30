from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from .collisions import flag_sku_barcode_collisions
from .engine_models import (
    Finding,
    GuardResult,
    SEVERITY_ORDER,
    _first_product_row,
    _image_key,
    _image_url_ok,
    _index_by_handle,
    _looks_numeric,
    _norm_handle,
    _variant_key,
    _variant_rows,
)
from .parser import load_csv
from .schema import DESTRUCTIVE_IF_BLANKED, NUMERIC_FIELDS, PRODUCT_LEVEL, VARIANT_FIELDS


def compare_csvs(original_path, edited_path, intended_columns=None) -> GuardResult:
    original = load_csv(original_path)
    edited = load_csv(edited_path)
    intended = [c.strip() for c in (intended_columns or []) if c.strip()]
    findings: list[Finding] = []

    def add(**kwargs):
        findings.append(Finding(**kwargs))

    for issue in original.issues:
        add(severity="REVIEW", code="ORIGINAL_PARSE", title="Original file parse warning", detail=issue)
    for issue in edited.issues:
        add(severity="BLOCK" if "NUL" in issue else "REVIEW", code="EDITED_PARSE", title="Edited file parse warning", detail=issue)
    if original.encoding != edited.encoding:
        add(severity="REVIEW", code="ENCODING_CHANGED", title="File encoding changed",
            detail=f"Original decoded as {original.encoding}; edited decoded as {edited.encoding}.")
    if "Handle" not in edited.headers:
        add(severity="BLOCK", code="MISSING_HANDLE_COLUMN", title="Edited file has no Handle column",
            detail="Shopify uses Handle to group variants and overwrite matching products.")

    orig_by_handle = _index_by_handle(original)
    edit_by_handle = _index_by_handle(edited)
    blank_handle_rows = [i for i, row in enumerate(edited.rows, start=2) if not _norm_handle(row.get("Handle", ""))]
    if blank_handle_rows:
        add(severity="BLOCK", code="BLANK_HANDLE", title="Edited rows are missing Handle",
            detail=f"{len(blank_handle_rows)} data row(s) have a blank Handle, including spreadsheet row {blank_handle_rows[0]}.",
            edited_row=blank_handle_rows[0], field="Handle")

    orig_title_to_handles: dict[str, set[str]] = {}
    for handle, rows in orig_by_handle.items():
        prow = _first_product_row(rows)
        if prow and prow.get("Title"):
            orig_title_to_handles.setdefault(prow["Title"].strip().lower(), set()).add(handle)
    for handle, rows in edit_by_handle.items():
        prow = _first_product_row(rows)
        if not prow or not prow.get("Title"):
            continue
        prior = orig_title_to_handles.get(prow["Title"].strip().lower(), set())
        if prior and handle not in prior:
            add(severity="BLOCK", code="HANDLE_CHANGED", title="Product handle changed",
                detail=f'Title "{prow["Title"]}" previously used handle {sorted(prior)[0]!r} and now uses {handle!r}.',
                handle=handle, field="Handle", original_value=sorted(prior)[0], edited_value=handle)

    orig_handles = {h for h in orig_by_handle if h}
    edit_handles = {h for h in edit_by_handle if h}
    removed = sorted(orig_handles - edit_handles)
    added = sorted(edit_handles - orig_handles)
    if removed:
        add(severity="BLOCK", code="PRODUCTS_REMOVED", title="Products disappeared from the edited file",
            detail=f"{len(removed)} handle(s) present in the original export are missing: {', '.join(removed[:8])}.")
    if added:
        add(severity="REVIEW", code="PRODUCTS_ADDED", title="New handles appeared",
            detail=f"{len(added)} new handle(s): {', '.join(added[:8])}.")

    for handle in sorted(orig_handles & edit_handles):
        o_rows = orig_by_handle[handle]
        e_rows = edit_by_handle[handle]
        o_prod = _first_product_row(o_rows) or {}
        e_prod = _first_product_row(e_rows) or {}
        for field_name in sorted(PRODUCT_LEVEL):
            ov = (o_prod.get(field_name) or "").strip()
            ev = (e_prod.get(field_name) or "").strip()
            if ov == ev:
                continue
            if ov and not ev and field_name in DESTRUCTIVE_IF_BLANKED:
                add(severity="BLOCK", code="DESTRUCTIVE_BLANK", title=f"{field_name} was blanked",
                    detail=f"Handle {handle!r}: {field_name} changed from {ov!r} to blank.",
                    handle=handle, field=field_name, original_value=ov, edited_value=ev)
            elif intended and field_name not in intended:
                add(severity="REVIEW", code="UNEXPECTED_EDIT", title=f"Unexpected {field_name} change",
                    detail=f"Handle {handle!r}: {field_name} changed outside the intended-column allowlist.",
                    handle=handle, field=field_name, original_value=ov[:120], edited_value=ev[:120])
            else:
                add(severity="INFO", code="FIELD_CHANGED", title=f"{field_name} changed",
                    detail=f"Handle {handle!r}: {field_name} updated.",
                    handle=handle, field=field_name, original_value=ov[:120], edited_value=ev[:120])

        o_vars = {_variant_key(r): (i, r) for i, r in _variant_rows(o_rows)}
        e_vars = {_variant_key(r): (i, r) for i, r in _variant_rows(e_rows)}
        e_var_counts = Counter(_variant_key(r) for _, r in _variant_rows(e_rows))
        for key, n in e_var_counts.items():
            if n > 1 and any(key[1:]):
                add(severity="BLOCK", code="DUPLICATE_VARIANT", title="Duplicate variant identity",
                    detail=f"Handle {handle!r} has {n} rows with options {key[1] or '(blank)'} / {key[2] or '(blank)'} / {key[3] or '(blank)'}.",
                    handle=handle)
        lost_variants = [k for k in o_vars if k not in e_vars and any(k[1:])]
        if lost_variants:
            sample = lost_variants[0]
            add(severity="BLOCK", code="VARIANT_REMOVED", title="Variant identity disappeared",
                detail=f"Handle {handle!r} lost {len(lost_variants)} variant combination(s), including {sample[1] or '(blank)'}.",
                handle=handle, field="Option1 Value")
        for key, (e_i, e_row) in e_vars.items():
            o_match = o_vars.get(key)
            o_row = o_match[1] if o_match else {}
            o_i = o_match[0] if o_match else None
            for field_name in sorted(VARIANT_FIELDS):
                ov = (o_row.get(field_name) or "").strip()
                ev = (e_row.get(field_name) or "").strip()
                if field_name in NUMERIC_FIELDS and ev and not _looks_numeric(ev):
                    add(severity="BLOCK", code="MALFORMED_NUMBER", title=f"{field_name} is not a plain number",
                        detail=f"Handle {handle!r} row {e_i}: {field_name}={ev!r}.",
                        handle=handle, edited_row=e_i, field=field_name, edited_value=ev)
                if ov == ev:
                    continue
                if ov and not ev and field_name in DESTRUCTIVE_IF_BLANKED:
                    add(severity="BLOCK", code="DESTRUCTIVE_BLANK", title=f"{field_name} was blanked",
                        detail=f"Handle {handle!r} row {e_i}: {field_name} changed from {ov!r} to blank.",
                        handle=handle, original_row=o_i, edited_row=e_i, field=field_name, original_value=ov, edited_value=ev)
                elif intended and field_name not in intended:
                    add(severity="REVIEW", code="UNEXPECTED_EDIT", title=f"Unexpected {field_name} change",
                        detail=f"Handle {handle!r} row {e_i}: {field_name} changed outside the intended-column allowlist.",
                        handle=handle, original_row=o_i, edited_row=e_i, field=field_name, original_value=ov, edited_value=ev)
                else:
                    add(severity="INFO", code="FIELD_CHANGED", title=f"{field_name} changed",
                        detail=f"Handle {handle!r} row {e_i}: {field_name} updated.",
                        handle=handle, original_row=o_i, edited_row=e_i, field=field_name, original_value=ov, edited_value=ev)

        o_images = [_image_key(r)[1] for _, r in o_rows if r.get("Image Src")]
        e_images = [_image_key(r)[1] for _, r in e_rows if r.get("Image Src")]
        if o_images and not e_images:
            add(severity="BLOCK", code="IMAGES_DROPPED", title="All images disappeared for a product",
                detail=f"Handle {handle!r} had {len(o_images)} Image Src value(s) and now has none.",
                handle=handle, field="Image Src")
        elif set(o_images) != set(e_images):
            lost = [u for u in o_images if u not in e_images]
            if lost:
                add(severity="BLOCK", code="IMAGE_URL_REMOVED", title="Image URL removed",
                    detail=f"Handle {handle!r} lost {len(lost)} image URL(s), including {lost[0][:80]}.",
                    handle=handle, field="Image Src", original_value=lost[0])
        for _, e_row in e_rows:
            url = e_row.get("Image Src") or ""
            ok, reason = _image_url_ok(url)
            if not ok:
                add(severity="BLOCK", code="BROKEN_IMAGE_URL", title="Image Src would fail Shopify download rules",
                    detail=f"Handle {handle!r}: {reason} Value={url[:120]!r}",
                    handle=handle, field="Image Src", edited_value=url)

    orig_image_seq = [(_norm_handle(r.get("Handle", "")), r.get("Image Src") or "") for r in original.rows if r.get("Image Src")]
    edit_image_seq = [(_norm_handle(r.get("Handle", "")), r.get("Image Src") or "") for r in edited.rows if r.get("Image Src")]
    if orig_image_seq and edit_image_seq and set(orig_image_seq) == set(edit_image_seq) and orig_image_seq != edit_image_seq:
        add(severity="BLOCK", code="IMAGE_ROWS_REORDERED", title="Image rows were reordered",
            detail="The same Image Src URLs exist, but their row order relative to products changed.", field="Image Src")
    orig_row_handles = [_norm_handle(r.get("Handle", "")) for r in original.rows]
    edit_row_handles = [_norm_handle(r.get("Handle", "")) for r in edited.rows]
    if orig_row_handles and Counter(orig_row_handles) == Counter(edit_row_handles) and orig_row_handles != edit_row_handles:
        if not any(f.code == "IMAGE_ROWS_REORDERED" for f in findings):
            add(severity="REVIEW", code="ROW_ORDER_CHANGED", title="Row order changed",
                detail="Product row order differs from the original export.")

    flag_sku_barcode_collisions(add, edit_by_handle, _variant_rows)
    if any(h in edited.headers for h in VARIANT_FIELDS) and not ("Option1 Name" in edited.headers and "Option1 Value" in edited.headers):
        add(severity="BLOCK", code="OPTIONS_REQUIRED", title="Variant columns present without Option1 Name/Value",
            detail="Shopify requires Option1 Name and Option1 Value on every variant row.")
    extra_cols = [h for h in edited.headers if h not in original.headers]
    missing_cols = [h for h in original.headers if h not in edited.headers]
    if extra_cols:
        add(severity="REVIEW", code="COLUMNS_ADDED", title="Edited file added columns", detail="Added: " + ", ".join(extra_cols[:20]))
    if missing_cols:
        add(severity="REVIEW", code="COLUMNS_REMOVED", title="Edited file dropped columns", detail="Dropped: " + ", ".join(missing_cols[:20]))
    if intended:
        unknown = [c for c in intended if c not in edited.headers and c not in original.headers]
        if unknown:
            add(severity="REVIEW", code="UNKNOWN_ALLOWLIST_COLUMN", title="Intended column not found in either file",
                detail="Not found: " + ", ".join(unknown))

    verdict = "PASS"
    if any(f.severity == "REVIEW" for f in findings):
        verdict = "REVIEW"
    if any(f.severity == "BLOCK" for f in findings):
        verdict = "BLOCK"
    stats = {
        "original_rows": len(original.rows),
        "edited_rows": len(edited.rows),
        "original_handles": len(orig_handles),
        "edited_handles": len(edit_handles),
        "handles_added": len(added),
        "handles_removed": len(removed),
        "block_count": sum(1 for f in findings if f.severity == "BLOCK"),
        "review_count": sum(1 for f in findings if f.severity == "REVIEW"),
        "info_count": sum(1 for f in findings if f.severity == "INFO"),
        "original_sha256": hashlib.sha256(Path(original.path).read_bytes()).hexdigest(),
        "edited_sha256": hashlib.sha256(Path(edited.path).read_bytes()).hexdigest(),
    }
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.code, f.handle))
    return GuardResult(verdict=verdict, original=original, edited=edited, findings=findings, stats=stats, intended_columns=intended)
