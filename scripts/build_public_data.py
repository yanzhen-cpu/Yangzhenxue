"""Build compact public artifacts from an immutable STRAT-026 formal run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics_path = args.source_run / "metrics.json"
    drawdowns_path = args.source_run / "additional_drawdowns.csv"
    audit_path = args.source_run / "audit.json"
    strategy_audit_path = args.source_run / "strategy_audit.json"
    tests_path = args.source_run / "test_summary.json"
    run_manifest_path = args.source_run / "run_manifest.json"

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    strategy_audit = json.loads(strategy_audit_path.read_text(encoding="utf-8"))
    tests = json.loads(tests_path.read_text(encoding="utf-8"))
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    with drawdowns_path.open(encoding="utf-8-sig", newline="") as stream:
        drawdown_rows = list(csv.DictReader(stream))
    max_closed = max(float(row["realized_drawdown"]) for row in drawdown_rows)

    public = {
        "strategy": "STRAT-026",
        "version": "0.6.2",
        "source_run": run_manifest["run_id"],
        "period": {
            "start": metrics["actual_start_date"],
            "end": metrics["actual_end_date"],
        },
        "initial_capital": metrics["initial_capital"],
        "ending_equity": metrics["ending_equity"],
        "total_return": metrics["total_return"],
        "annualized_return": metrics["annualized_return"],
        "max_drawdown": metrics["max_drawdown"],
        "max_closed_drawdown": max_closed,
        "sharpe": metrics["sharpe"],
        "closed_trades": metrics["closed_trades"],
        "win_rate": metrics["win_rate"],
        "pnl_ratio": metrics["pnl_ratio"],
        "max_portfolio_risk": metrics["max_portfolio_risk"],
        "approved_products": metrics["approved_product_count"],
        "yearly_realized_pnl": {
            year: values["net_pnl"] for year, values in metrics["by_year"].items()
        },
        "audit": {
            "status": audit["status"],
            "tests": tests.get("tests") or next(
                command["test_count"]
                for command in tests["commands"]
                if command.get("label") == "all-tests"
            ),
            "assertions": strategy_audit["assertions"],
            "equity_days": strategy_audit["checks"]["daily_equity_replayed_from_fills"],
            "fills": audit["checks"]["fills.csv_rows"],
            "trades": audit["checks"]["trades.csv_rows"],
        },
        "costs": {"commission": metrics["commission"], "slippage": metrics["slippage"]},
        "research_flags": {
            "future_anchor": metrics["future_anchor"],
            "entry_equity_is_approximation": metrics["entry_equity_is_approximation"],
        },
        "source_hashes": {
            "metrics.json": sha256(metrics_path),
            "additional_drawdowns.csv": sha256(drawdowns_path),
            "audit.json": sha256(audit_path),
            "strategy_audit.json": sha256(strategy_audit_path),
            "test_summary.json": sha256(tests_path),
            "run_manifest.json": sha256(run_manifest_path),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
