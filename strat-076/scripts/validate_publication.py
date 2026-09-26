"""Validate the STRAT-032 public case before deployment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md", "index.html", "code.html", "site.css", "app.js",
    "assets/equity_curve.svg", "data/public-metrics.json",
    "src/strat_032_data.py", "src/strat_032_engine.py",
    "reports/STRAT-032-v0.7.6-project-brief.pdf", "docs/methodology.md",
)
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".py", ".svg"}
FORBIDDEN = (
    re.compile(r"[A-Za-z]:\\(?:Users|codex)\\", re.IGNORECASE),
    re.compile(r"(?:TO" + "DO|TB" + "D|PLACE" + "HOLDER)", re.IGNORECASE),
    re.compile(r"(?:api[_-]?key|token|password)\s*[:=]\s*['\"][^'\"]+", re.IGNORECASE),
)


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_run.resolve(strict=True)
    errors: list[str] = []

    for relative in REQUIRED:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing_or_empty:{relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".qa" in path.parts or path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for pattern in FORBIDDEN:
            if pattern.search(content):
                errors.append(f"forbidden_pattern:{relative}")
        if path.suffix.lower() == ".md":
            if re.search(r"\*\*\s+\*\*", content):
                errors.append(f"bold_trailing_space:{relative}")
            if re.search(r"(?<=\S)\*\*(?=\S)", content):
                errors.append(f"bold_boundary:{relative}")

    data_path = ROOT / "data" / "public-metrics.json"
    if data_path.is_file():
        data = json.loads(data_path.read_text(encoding="utf-8"))
        expected = {
            "strategy": "STRAT-032", "version": "0.7.6",
            "source_run": "STRAT032-FULL-MAIN-20260926", "closed_trades": 55,
            "rollovers_filled": 10,
        }
        for key, value in expected.items():
            if data.get(key) != value:
                errors.append(f"metric_mismatch:{key}")
        for key, value in {
            "total_return": 50.7033067,
            "annualized_return": 0.6664020437167482,
            "max_closed_drawdown": 0.298600429110388,
            "max_drawdown": 0.4620072619827257,
        }.items():
            if abs(data.get(key, 0) - value) > 1e-10:
                errors.append(f"metric_mismatch:{key}")
        if abs(data.get("annual_account_change", {}).get("2026", {}).get("change", 0) - 6167627.8) > 0.01:
            errors.append("metric_mismatch:2026_account_change")
        if data.get("research_flags", {}).get("future_anchor_cycles") != 29:
            errors.append("metric_mismatch:future_anchor_cycles")

    frozen_source = source / "source" / "scripts" / "strategy" / "backtest"
    code_page = (ROOT / "code.html").read_text(encoding="utf-8") if (ROOT / "code.html").is_file() else ""
    for name in ("strat_032_data.py", "strat_032_engine.py"):
        public_file = ROOT / "src" / name
        original = frozen_source / name
        if public_file.is_file() and original.is_file():
            if sha256(public_file) != sha256(original):
                errors.append(f"source_excerpt_mismatch:{name}")
            if escape(public_file.read_text(encoding="utf-8")) not in code_page:
                errors.append(f"code_page_mismatch:{name}")

    pdf_path = ROOT / "reports" / "STRAT-032-v0.7.6-project-brief.pdf"
    if pdf_path.is_file():
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if len(pdf.pages) != 2:
                errors.append("pdf_page_count")
            for expected in ("5,070.33%", "66.64%", "29.86%", "46.20%", "STRAT032-FULL-MAIN-20260926"):
                if expected not in text:
                    errors.append(f"pdf_missing:{expected}")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"PASS required={len(REQUIRED)} audited_run=STRAT032-FULL-MAIN-20260926")
    return 0


if __name__ == "__main__":
    sys.exit(main())
