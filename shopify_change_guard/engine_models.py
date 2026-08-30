from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .parser import CsvFile, is_image_only_row
from .schema import FORBIDDEN_IMAGE_SUFFIXES

SEVERITY_ORDER = {"BLOCK": 3, "REVIEW": 2, "INFO": 1, "PASS": 0}


@dataclass
class Finding:
    severity: str
    code: str
    title: str
    detail: str
    handle: str = ""
    original_row: int | None = None
    edited_row: int | None = None
    field: str = ""
    original_value: str = ""
    edited_value: str = ""

    def as_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class GuardResult:
    verdict: str
    original: CsvFile
    edited: CsvFile
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    intended_columns: list[str] = field(default_factory=list)

    @property
    def blocks(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "BLOCK"]

    @property
    def reviews(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "REVIEW"]


def _norm_handle(value: str) -> str:
    return (value or "").strip().lower()


def _variant_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        _norm_handle(row.get("Handle", "")),
        (row.get("Option1 Value") or "").strip().lower(),
        (row.get("Option2 Value") or "").strip().lower(),
        (row.get("Option3 Value") or "").strip().lower(),
    )


def _image_key(row: dict[str, str]) -> tuple[str, str]:
    return (_norm_handle(row.get("Handle", "")), (row.get("Image Src") or "").strip())


def _looks_numeric(value: str) -> bool:
    if value == "":
        return True
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", value.strip()))


def _image_url_ok(url: str) -> tuple[bool, str]:
    if not url:
        return True, ""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False, "Image Src must be a public http(s) URL, not a local filename."
    stem = Path(parsed.path).stem.lower()
    for suffix in FORBIDDEN_IMAGE_SUFFIXES:
        if stem.endswith(suffix):
            return False, f"Shopify rejects image filenames ending in {suffix}."
    return True, ""


def _index_by_handle(file: CsvFile) -> dict[str, list[tuple[int, dict[str, str]]]]:
    out: dict[str, list[tuple[int, dict[str, str]]]] = defaultdict(list)
    for i, row in enumerate(file.rows, start=2):
        handle = _norm_handle(row.get("Handle", ""))
        out[handle].append((i, row))
    return out


def _first_product_row(rows: list[tuple[int, dict[str, str]]]) -> dict[str, str] | None:
    for _, row in rows:
        if row.get("Title"):
            return row
    return rows[0][1] if rows else None


def _variant_rows(rows: list[tuple[int, dict[str, str]]]) -> list[tuple[int, dict[str, str]]]:
    out = []
    for i, row in rows:
        if is_image_only_row(row):
            continue
        if row.get("Option1 Value") or row.get("Variant SKU") or row.get("Variant Price") or row.get("Title"):
            out.append((i, row))
    return out
