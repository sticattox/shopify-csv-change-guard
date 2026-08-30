from __future__ import annotations

import csv
from pathlib import Path

HEADERS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value", "Variant SKU", "Variant Inventory Qty",
    "Variant Price", "Variant Barcode", "Image Src", "Image Position",
    "Image Alt Text", "Variant Image", "Status",
]


def row(**kwargs) -> dict[str, str]:
    data = {h: "" for h in HEADERS}
    data.update(kwargs)
    return data


ORIGINAL = [
    row(Handle="classic-tee", Title="Classic Tee", **{"Body (HTML)": "<p>Soft cotton tee.</p>"}, Vendor="Northfield", Type="Shirts", Tags="cotton, basics", Published="TRUE", **{"Option1 Name": "Size", "Option1 Value": "S", "Variant SKU": "TEE-S", "Variant Inventory Qty": "12", "Variant Price": "24.00", "Variant Barcode": "111", "Image Src": "https://cdn.example.com/tee-front.jpg", "Image Position": "1", "Image Alt Text": "Front", "Variant Image": "https://cdn.example.com/tee-front.jpg", "Status": "active"}),
    row(Handle="classic-tee", **{"Option1 Name": "Size", "Option1 Value": "M", "Variant SKU": "TEE-M", "Variant Inventory Qty": "8", "Variant Price": "24.00", "Variant Barcode": "222", "Variant Image": "https://cdn.example.com/tee-front.jpg"}),
    row(Handle="classic-tee", **{"Option1 Name": "Size", "Option1 Value": "L", "Variant SKU": "TEE-L", "Variant Inventory Qty": "5", "Variant Price": "24.00", "Variant Barcode": "333", "Variant Image": "https://cdn.example.com/tee-front.jpg"}),
    row(Handle="classic-tee", **{"Image Src": "https://cdn.example.com/tee-back.jpg", "Image Position": "2", "Image Alt Text": "Back"}),
    row(Handle="wool-beanie", Title="Wool Beanie", **{"Body (HTML)": "<p>Warm hat.</p>"}, Vendor="Northfield", Type="Hats", Tags="wool", Published="TRUE", **{"Option1 Name": "Color", "Option1 Value": "Navy", "Variant SKU": "HAT-NVY", "Variant Inventory Qty": "20", "Variant Price": "18.00", "Variant Barcode": "444", "Image Src": "https://cdn.example.com/beanie.jpg", "Image Position": "1", "Image Alt Text": "Beanie", "Status": "active"}),
    row(Handle="canvas-tote", Title="Canvas Tote", **{"Body (HTML)": "<p>Everyday bag.</p>"}, Vendor="Northfield", Type="Bags", Tags="canvas", Published="TRUE", **{"Option1 Name": "Title", "Option1 Value": "Default Title", "Variant SKU": "TOTE-01", "Variant Inventory Qty": "30", "Variant Price": "32.00", "Variant Barcode": "555", "Image Src": "https://cdn.example.com/tote.jpg", "Image Position": "1", "Image Alt Text": "Tote", "Status": "active"}),
]


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def clone(rows):
    return [dict(r) for r in rows]


def build(root: Path) -> None:
    write_csv(root / "original.csv", ORIGINAL)
    clean = clone(ORIGINAL)
    for i in range(3):
        clean[i]["Variant Price"] = "26.00"
    write_csv(root / "clean-edit.csv", clean)
    write_csv(root / "accidental-sort.csv", [ORIGINAL[4], ORIGINAL[5], ORIGINAL[0], ORIGINAL[3], ORIGINAL[1], ORIGINAL[2]])
    blanked = clone(ORIGINAL)
    blanked[0]["Title"] = ""
    blanked[5]["Variant SKU"] = ""
    write_csv(root / "destructive-blank.csv", blanked)
    handle = clone(ORIGINAL)
    for r in handle:
        if r["Handle"] == "classic-tee":
            r["Handle"] = "classic-tshirt"
    write_csv(root / "changed-handle.csv", handle)
    dup = clone(ORIGINAL)
    dup.append(dict(ORIGINAL[1]))
    write_csv(root / "duplicate-variant.csv", dup)
    bad_price = clone(ORIGINAL)
    bad_price[0]["Variant Price"] = "$24.00"
    write_csv(root / "malformed-price.csv", bad_price)
    bad_img = clone(ORIGINAL)
    bad_img[0]["Image Src"] = "tee-front_thumb.jpg"
    write_csv(root / "broken-image-url.csv", bad_img)
    unexpected = clone(ORIGINAL)
    unexpected[4]["Vendor"] = "Other Co"
    unexpected[4]["Tags"] = "wool, sale"
    write_csv(root / "unexpected-column-edit.csv", unexpected)
    write_csv(root / "dropped-product.csv", [r for r in ORIGINAL if r["Handle"] != "wool-beanie"])
    colliding = clone(ORIGINAL)
    colliding[1]["Variant SKU"] = "TEE-S"
    write_csv(root / "duplicate-sku.csv", colliding)
    encoding = root / "encoding-issue.csv"
    text_rows = clone(ORIGINAL)
    text_rows[0]["Title"] = "Classic Tée"
    with encoding.open("w", encoding="cp1252", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(text_rows)


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1] / "fixtures")
