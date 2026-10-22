# Net Reports development archive

This directory powers only `/netreports-dev/`. The existing production
`/netreports/` and year-specific pages are not modified by the import.

## Full archive (October 22, 2026 baseline)

- Source images: `assets/img/net-YYYY-MM-DD.png`, discovered automatically.
- Archived reports discovered: **162** (September 2023–October 2026).
- OCR-derived candidate check-in rows: **1,436**.
- Manually screenshot-verified rows: **38**, from four reference reports.
- Distinct extracted callsigns: **208**, a **provisional** number.
- Potential callsign variants grouped by identical operator name: **56** review groups.

The remaining OCR rows are **not verified**, and neither the leaderboard nor
the apparent attendance trends are authoritative. Some screenshots contain
highlighted text and OCR mistakes. The source PNGs are always authoritative.

## Key files

- `scripts/extract.py` – the single-batch OCR parser, also supports `--dates`.
- `scripts/import_all.py` – discovers all net screenshots and imports in batches
  (default: four screenshots per OCR run). Can be limited with `--dates`.
- `data/reviewed.json` – manually verified records. These replace raw OCR rows
  for their respective dates; change this file only after checking the image.
- `data/preview.json` – generated website dataset; **do not edit directly**.
- `data/import-audit.json` – generated per-net review findings, including missing
  row numbers, duplicate callsigns and possible misread variants.
- `data/ocr-review.txt` – raw recognized lines, used for troubleshooting.
- `tests/` – unit tests for the extractor, subset handling and full import.

## Data verification

For each unreviewed net, compare the table with the linked original PNG.
Correct callsigns and every field, ensure the check-in row count matches, then
add all rows for that date to `data/reviewed.json`. Reviewers should
consider that the same operator may legitimately use more than one callsign;
never auto-merge identities based solely on a fuzzy match or shared name.
Re-run the importer and check the audit. Until then, site counts are estimates.

## Run locally

Install `python3`, `tesseract-ocr`, `pillow`, and `pytesseract`. From the
repository root:

```bash
python -m unittest discover -s netreports-dev/tests -v
python netreports-dev/scripts/import_all.py --root . --batch-size 4
python netreports-dev/scripts/extract.py --root . --dates 2026-10-20 \
  --out /tmp/net-preview.json --text /tmp/net-review.txt
```

The separate full-import GitHub Actions workflow is **restricted to
`feature/netreports-dev-full-archive`** and commits only the three generated
development files to that branch. It is not a production weekly-update job.

## Review and release

Changes require Codex review and explicit human approval before merging.
Do not replace production pages until the revised UI, extraction and statistics
have been accepted.
