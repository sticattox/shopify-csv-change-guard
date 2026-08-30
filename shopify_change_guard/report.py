from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .engine import GuardResult


def to_text(result: GuardResult) -> str:
    lines = [
        "SHOPIFY CSV CHANGE GUARD",
        f"Verdict: {result.verdict}",
        f"Original: {result.original.name}  ({result.stats['original_rows']} rows, {result.stats['original_handles']} handles)",
        f"Edited:   {result.edited.name}  ({result.stats['edited_rows']} rows, {result.stats['edited_handles']} handles)",
        f"SHA-256 original: {result.stats['original_sha256']}",
        f"SHA-256 edited:   {result.stats['edited_sha256']}",
    ]
    if result.intended_columns:
        lines.append("Intended columns: " + ", ".join(result.intended_columns))
    lines.append("")
    lines.append(
        f"BLOCK {result.stats['block_count']}  |  REVIEW {result.stats['review_count']}  |  INFO {result.stats['info_count']}"
    )
    lines.append("")
    if not result.findings:
        lines.append("No differences flagged. Still back up the live catalog before importing.")
        return "\n".join(lines)
    current = None
    for f in result.findings:
        if f.severity != current:
            current = f.severity
            lines.append(f"=== {current} ===")
        loc = []
        if f.handle:
            loc.append(f"handle={f.handle}")
        if f.edited_row:
            loc.append(f"edited_row={f.edited_row}")
        if f.field:
            loc.append(f"field={f.field}")
        where = f" ({', '.join(loc)})" if loc else ""
        lines.append(f"[{f.code}] {f.title}{where}")
        lines.append(f"    {f.detail}")
        if f.original_value or f.edited_value:
            lines.append(f"    before={f.original_value!r}")
            lines.append(f"    after ={f.edited_value!r}")
        lines.append("")
    lines.append("This tool does not import anything into Shopify. It only compares the two files you supplied.")
    return "\n".join(lines)


def to_json(result: GuardResult) -> str:
    payload = {
        "verdict": result.verdict,
        "stats": result.stats,
        "intended_columns": result.intended_columns,
        "schema_version": "0.2.0",
        "original": {
            "name": result.original.name,
            "encoding": result.original.encoding,
            "headers": result.original.headers,
        },
        "edited": {
            "name": result.edited.name,
            "encoding": result.edited.encoding,
            "headers": result.edited.headers,
        },
        "findings": [f.as_dict() for f in result.findings],
    }
    return json.dumps(payload, indent=2)


def to_html(result: GuardResult) -> str:
    color = {"PASS": "#0f7b3d", "REVIEW": "#b36b00", "BLOCK": "#b42318"}[result.verdict]
    rows = []
    for f in result.findings:
        rows.append(
            "<tr>"
            f"<td>{escape(f.severity)}</td>"
            f"<td>{escape(f.code)}</td>"
            f"<td>{escape(f.handle)}</td>"
            f"<td>{escape(f.field)}</td>"
            f"<td>{escape(f.title)}<div class='d'>{escape(f.detail)}</div></td>"
            "</tr>"
        )
    table = "\n".join(rows) or "<tr><td colspan='5'>No findings.</td></tr>"
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        f"<title>Change Guard — {escape(result.verdict)}</title>\n"
        "<style>body{font-family:Arial,sans-serif;margin:32px} .badge{display:inline-block;padding:6px 12px;color:#fff;font-weight:bold}</style>\n"
        f"</head><body><h1>Shopify CSV Change Guard</h1><div class=\"badge\" style=\"background:{color}\">{escape(result.verdict)}</div>\n"
        f"<p>Original: {escape(result.original.name)} ({result.stats['original_rows']} rows)<br>"
        f"Edited: {escape(result.edited.name)} ({result.stats['edited_rows']} rows)</p>\n"
        f"<table border=\"1\" cellpadding=\"6\" cellspacing=\"0\"><thead><tr><th>Severity</th><th>Code</th><th>Handle</th><th>Field</th><th>Finding</th></tr></thead><tbody>{table}</tbody></table>\n"
        "<p>Local comparison only. Nothing was sent to Shopify or any server.</p></body></html>\n"
    )


def write_reports(result: GuardResult, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "txt": out / "change-guard-report.txt",
        "json": out / "change-guard-report.json",
        "html": out / "change-guard-report.html",
    }
    paths["txt"].write_text(to_text(result), encoding="utf-8")
    paths["json"].write_text(to_json(result), encoding="utf-8")
    paths["html"].write_text(to_html(result), encoding="utf-8")
    return {k: str(v) for k, v in paths.items()}
