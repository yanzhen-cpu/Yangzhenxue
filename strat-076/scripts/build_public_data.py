"""Build a compact public record from the immutable STRAT-032 formal run."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_run.resolve(strict=True)
    names = (
        "run_manifest.json", "metrics.json", "additional_drawdowns.csv",
        "equity_daily.csv", "trades.csv", "audit.json",
        "strategy_audit.json", "test_summary.json",
    )
    paths = {name: source / name for name in names}
    if any(not path.is_file() for path in paths.values()):
        raise ValueError("formal run is missing a required source file")

    run = json.loads(paths["run_manifest.json"].read_text(encoding="utf-8"))
    metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
    audit = json.loads(paths["audit.json"].read_text(encoding="utf-8"))
    independent = json.loads(paths["strategy_audit.json"].read_text(encoding="utf-8"))
    tests = json.loads(paths["test_summary.json"].read_text(encoding="utf-8"))
    if (run.get("run_id"), run.get("strategy_version"), run.get("status")) != (
        "STRAT032-FULL-MAIN-20260926", "0.7.6", "completed"
    ):
        raise ValueError("unexpected formal run identity")
    if any(record.get("status") != "pass" for record in (audit, independent, tests)):
        raise ValueError("formal validation did not pass")

    drawdowns = read_csv(paths["additional_drawdowns.csv"])
    equity_rows = read_csv(paths["equity_daily.csv"])
    trades = read_csv(paths["trades.csv"])
    if len(equity_rows) != audit["checks"]["equity_daily.csv_rows"]:
        raise ValueError("equity row count differs from formal audit")
    if len(trades) != metrics["closed_trades"]:
        raise ValueError("trade row count differs from formal metrics")

    cycle_pnl_by_exit_year: dict[str, float] = defaultdict(float)
    for trade in trades:
        cycle_pnl_by_exit_year[trade["exit_date"][:4]] += float(trade["net_pnl"])
    for year, result in metrics["by_year"].items():
        if abs(cycle_pnl_by_exit_year[year] - result["net_pnl"]) > 0.01:
            raise ValueError(f"cycle PnL differs from metrics.by_year for {year}")

    annual_rows: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in equity_rows:
        annual_rows.setdefault(row["trade_date"][:4], []).append(row)
    previous_equity = metrics["initial_capital"]
    annual_account_change: dict[str, dict[str, float | str]] = {}
    for year, rows in annual_rows.items():
        end_equity = float(rows[-1]["equity"])
        annual_account_change[year] = {
            "end_date": rows[-1]["trade_date"],
            "start_equity": previous_equity,
            "end_equity": end_equity,
            "change": end_equity - previous_equity,
            "return": end_equity / previous_equity - 1.0,
        }
        previous_equity = end_equity
    if abs(previous_equity - metrics["ending_equity"]) > 0.01:
        raise ValueError("annual equity chain does not reconcile")

    year_2026 = annual_rows["2026"]
    high = max(year_2026, key=lambda row: float(row["equity"]))
    low = min(year_2026, key=lambda row: float(row["equity"]))
    public = {
        "strategy": "STRAT-032",
        "version": "0.7.6",
        "source_run": run["run_id"],
        "period": {"start": metrics["actual_start_date"], "end": metrics["actual_end_date"]},
        "initial_capital": metrics["initial_capital"],
        "ending_equity": metrics["ending_equity"],
        "total_return": metrics["total_return"],
        "annualized_return": metrics["annualized_return"],
        "max_drawdown": metrics["max_drawdown"],
        "max_closed_drawdown": max(float(row["realized_drawdown"]) for row in drawdowns),
        "sharpe": metrics["sharpe"],
        "closed_trades": metrics["closed_trades"],
        "open_at_end": metrics["open_at_end"],
        "win_rate": metrics["win_rate"],
        "pnl_ratio": metrics["pnl_ratio"],
        "max_portfolio_risk": metrics["max_portfolio_risk"],
        "universe_products": metrics["candidate_product_count"],
        "fixed_excluded_products": ["LC", "PD", "PS", "PT", "SI", "MA", "SH", "UR", "AG"],
        "rollovers_filled": metrics["rollovers_filled"],
        "annual_account_change": annual_account_change,
        "completed_cycle_pnl_by_exit_year": dict(cycle_pnl_by_exit_year),
        "year_2026": {
            "closed_cycles": metrics["by_year"]["2026"]["trades"],
            "completed_cycle_pnl": metrics["by_year"]["2026"]["net_pnl"],
            "high_date": high["trade_date"],
            "high_equity": float(high["equity"]),
            "low_date": low["trade_date"],
            "low_equity": float(low["equity"]),
        },
        "audit": {
            "status": audit["status"],
            "targeted_tests": tests["tests_run"],
            "independent_assertions": independent["assertions"],
            "equity_days": audit["checks"]["equity_daily.csv_rows"],
            "fills": audit["checks"]["fills.csv_rows"],
            "trades": audit["checks"]["trades.csv_rows"],
        },
        "research_flags": {
            "future_anchor_cycles": sum(row["future_anchor"] == "True" for row in trades),
            "commission": metrics["commission"],
            "slippage": metrics["slippage"],
            "source_quality": "PARTIAL",
        },
        "source_hashes": {name: sha256(path) for name, path in paths.items()},
    }
    target = ROOT / "data" / "public-metrics.json"
    target.write_text(json.dumps(public, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
