"""Validate the public portfolio before publication."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "assets/equity_curve.svg",
    "data/public-metrics.json",
    "src/strategy_pipeline.py",
    "reports/STRAT-026-v0.6.2-project-brief.pdf",
    "docs/methodology.md",
]
TEXT_SUFFIXES = {".html", ".css", ".js", ".json", ".md", ".py", ".svg", ".csv"}
FORBIDDEN = [
    re.compile(r"[A-Za-z]:\\(?:Users|codex)\\", re.IGNORECASE),
    re.compile(r"(?:TODO|TBD|PLACEHOLDER)", re.IGNORECASE),
    re.compile(r"(?:api[_-]?key|token|password)\s*[:=]\s*['\"][^'\"]+", re.IGNORECASE),
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing_or_empty:{relative}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".qa" in path.parts:
            continue
        if path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for pattern in FORBIDDEN:
            if pattern.search(text):
                errors.append(f"forbidden_pattern:{relative}:{pattern.pattern}")
        if path.suffix.lower() == ".md":
            if re.search(r"\*\*\s+\*\*", text):
                errors.append(f"bold_trailing_space:{relative}")
            if re.search(r"(?<=\S)\*\*(?=\S)", text):
                errors.append(f"bold_boundary:{relative}")

    metrics_path = ROOT / "data/public-metrics.json"
    if metrics_path.is_file():
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        expected = {
            "strategy": "STRAT-026",
            "version": "0.6.2",
            "source_run": "STRAT026-FULL-MAIN-20260912",
            "closed_trades": 32,
        }
        for key, value in expected.items():
            if data.get(key) != value:
                errors.append(f"metric_mismatch:{key}")
        if abs(data.get("max_closed_drawdown", 0) - 0.1963260000000001) > 1e-12:
            errors.append("metric_mismatch:max_closed_drawdown")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print(f"PASS required={len(REQUIRED)} public_files={sum(1 for p in ROOT.rglob('*') if p.is_file())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
