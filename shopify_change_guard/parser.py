from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path

from .schema import IMAGE_FIELDS, PRODUCT_LEVEL, VARIANT_FIELDS, normalize_header


@dataclass
class CsvFile:
    path: str
    encoding: str
    has_bom: bool
    headers: list[str]
    raw_headers: list[str]
    rows: list[dict[str, str]]
    raw_row_count: int
    issues: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return Path(self.path).name


def _decode(data: bytes) -> tuple[str, str, bool]:
    has_bom = data.startswith(b"\xef\xbb\xbf")
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(enc)
            return text, enc, has_bom
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace"), "latin-1-replace", has_bom


def _sniff(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t;")
    except csv.Error:
        class Default(csv.Dialect):
            delimiter = ","
            quotechar = '"'
            doublequote = True
            skipinitialspace = False
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL
        return Default()


def load_csv(path: str | Path) -> CsvFile:
    path = Path(path)
    data = path.read_bytes()
    text, encoding, has_bom = _decode(data)
    issues: list[str] = []
    if "\x00" in text:
        issues.append("File contains NUL bytes. Excel sometimes saves this when a workbook is not a true CSV.")
    dialect = _sniff(text[:8192])
    reader = csv.reader(io.StringIO(text), dialect)
    try:
        raw_headers = next(reader)
    except StopIteration:
        raise ValueError(f"{path.name} is empty.")
    headers = [normalize_header(h) for h in raw_headers]
    if any(not h for h in headers):
        issues.append("One or more header cells are blank.")
    seen: dict[str, int] = {}
    for h in headers:
        seen[h] = seen.get(h, 0) + 1
    dups = [h for h, n in seen.items() if n > 1 and h]
    if dups:
        issues.append("Duplicate headers: " + ", ".join(dups))

    rows: list[dict[str, str]] = []
    raw_count = 0
    for raw in reader:
        raw_count += 1
        if not any((cell or "").strip() for cell in raw):
            continue
        record: dict[str, str] = {}
        for i, header in enumerate(headers):
            if not header:
                continue
            value = raw[i] if i < len(raw) else ""
            record[header] = value.strip() if isinstance(value, str) else value
        rows.append(record)

    if dialect.delimiter != ",":
        issues.append(f"Delimiter is {dialect.delimiter!r}, not a comma. Shopify expects comma-separated values.")

    return CsvFile(
        path=str(path),
        encoding=encoding,
        has_bom=has_bom,
        headers=headers,
        raw_headers=raw_headers,
        rows=rows,
        raw_row_count=raw_count,
        issues=issues,
    )


def is_image_only_row(row: dict[str, str]) -> bool:
    has_image = bool(row.get("Image Src"))
    has_variant = any(row.get(k) for k in VARIANT_FIELDS)
    has_option = bool(row.get("Option1 Value"))
    has_title = bool(row.get("Title"))
    return has_image and not has_variant and not has_option and not has_title


def is_variant_row(row: dict[str, str]) -> bool:
    return bool(row.get("Option1 Value") or row.get("Variant SKU") or row.get("Variant Price"))


def product_fields_present(row: dict[str, str]) -> bool:
    return any(row.get(k) for k in PRODUCT_LEVEL)
