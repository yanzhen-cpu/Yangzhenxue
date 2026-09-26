# STRAT-032 v0.7.6 public case

## Purpose

This directory is the independent recruitment presentation of the immutable formal run `STRAT032-FULL-MAIN-20260926`. The root of the repository continues to show STRAT-026 v0.6.2.

## Files and names

- `index.html`, `code.html`, `app.js`: public project and code pages.
- `assets/equity_curve.svg`: verified chart copied from the formal delivery.
- `data/public-metrics.json`: compact facts rebuilt from the frozen formal run.
- `src/`: exact public excerpts of the frozen STRAT-032 source modules, with their original dependency boundary disclosed on `code.html`.
- `reports/STRAT-032-v0.7.6-project-brief.pdf`: recruiter-facing brief.
- `docs/methodology.md`: method and material research limitations.
- `scripts/`: deterministic data, code-page and PDF builders plus public-content validation.
- `.qa/`: temporary renders and checks, excluded from Git. Remove only with explicit user authorization.

## Rules

- Never modify the original strategy-workflow or formal run.
- Every displayed number must trace to `metrics.json`, `additional_drawdowns.csv`, `equity_daily.csv`, `trades.csv`, `audit.json`, `strategy_audit.json`, or `test_summary.json` in the formal run.
- The year table is realized PnL by exit year. Do not label it yearly total return.
- Lead risk disclosure with the future-anchor flag, zero-cost assumption, and daily matching limitations.
- Publish no raw databases, full input snapshot, private paths, credentials, or the complete inherited execution engine.
- Run the local validation script, inspect desktop/mobile layouts, render the PDF, and verify all public URLs after deployment.
