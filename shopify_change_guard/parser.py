from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path

from .schema import VARIANT_FIELDS, PRODUCT_LEVEL, normalize_header

UTF8_ENCODINGS = {"utf-8", "utf-8-sig"}


@dataclass
class CsvFile:
    path: str
    encoding: str
    has_bom: bool
    headers: list[str]
    raw_headers: list[str]
    rows: list[dict[str, str]]
    raw_row_count: int
    delimiter: str = ","
    size_bytes: int = 0
    utf8_valid: bool = True
    issues: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return Path(self.path).name


def _decode(data: bytes) -> tuple[str, str, bool, bool]:
    has_bom = data.startswith(b"\xef\xbb\xbf")
    try:
        return data.decode("utf-8-sig"), "utf-8-sig" if has_bom else "utf-8", has_bom, True
    except UnicodeDecodeError:
        pass
    for enc in ("cp1252", "latin-1"):
        try:
            return data.decode(enc), enc, has_bom, False
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace"), "latin-1-replace", has_bom, False


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
    text, encoding, has_bom, utf8_valid = _decode(data)
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
            # Preserve raw cell text. Normalization is field-specific and happens later.
            record[header] = value if isinstance(value, str) else str(value)
        rows.append(record)

    if dialect.delimiter != ",":
        issues.append(f"Delimiter is {dialect.delimiter!r}, not a comma. Shopify expects comma-separated values.")
    if not utf8_valid:
        issues.append(f"File is not valid UTF-8 (decoded as {encoding}). Shopify requires UTF-8.")

    return CsvFile(
        path=str(path),
        encoding=encoding,
        has_bom=has_bom,
        headers=headers,
        raw_headers=raw_headers,
        rows=rows,
        raw_row_count=raw_count,
        delimiter=getattr(dialect, "delimiter", ","),
        size_bytes=len(data),
        utf8_valid=utf8_valid,
        issues=issues,
    )


def is_image_only_row(row: dict[str, str]) -> bool:
    has_image = bool((row.get("Image Src") or "").strip())
    has_variant = any((row.get(k) or "").strip() for k in VARIANT_FIELDS)
    has_option = bool((row.get("Option1 Value") or "").strip())
    has_title = bool((row.get("Title") or "").strip())
    return has_image and not has_variant and not has_option and not has_title


def is_variant_row(row: dict[str, str]) -> bool:
    return bool(
        (row.get("Option1 Value") or "").strip()
        or (row.get("Variant SKU") or "").strip()
        or (row.get("Variant Price") or "").strip()
    )


def product_fields_present(row: dict[str, str]) -> bool:
    return any((row.get(k) or "").strip() for k in PRODUCT_LEVEL)
