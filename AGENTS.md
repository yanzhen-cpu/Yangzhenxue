# Yangzhenxue Strategy Portfolio Project

## Project purpose

This repository is a public recruitment portfolio for the STRAT-026 v0.6.2 commodity-futures research project. It presents verified research results, methodology, selected code, and reproducibility boundaries without publishing private databases or the full proprietary strategy implementation.

## Directory contract

- `index.html`, `styles.css`, `app.js`: GitHub Pages site.
- `assets/`: verified charts and static visual assets.
- `data/`: compact public result data derived from the immutable formal run.
- `src/`: public, reviewable architecture excerpts; no private data paths or credentials.
- `reports/`: downloadable recruiter-facing reports.
- `docs/`: methodology and execution records.
- `scripts/`: deterministic local build and validation helpers.
- `.qa/`: generated local QA artifacts; never publish.

## Source boundary

- Read-only source: the immutable STRAT-026 formal result package; its machine-local path is deliberately not recorded in this public repository.
- Formal source run: `STRAT026-FULL-MAIN-20260912`.
- Never modify or overwrite the source strategy project.
- Do not publish raw databases, complete private rules, local absolute paths, credentials, full input snapshots, or private news data.

## Validation

- All displayed metrics must trace to the formal run's `metrics.json`, `presentation.json`, or daily equity data.
- Run `scripts/validate_publication.py` before every public update.
- Preview through a local HTTP server and inspect desktop and mobile layouts.
- Scan Markdown bold boundaries, unfinished markers, local paths, and secrets before commit.

## Git

- Commit substantive changes with `YYYY-MM-DD <task>` messages.
- Do not commit `.qa/`, caches, credentials, or generated browser profiles.
