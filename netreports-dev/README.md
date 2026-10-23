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

## Experimental cell OCR v2 (PR #18)

The original `preview.json` and live development-page dataset remain
unchanged by the v2 evaluation. V2 creates separate evidence files:

- `data/cell-ocr-poc.json`: ten historical screenshot comparison, including
  exact held-out call/name matches on 38 previously reviewed check-ins.
- `data/cell-ocr-archive.json`: experimental full-archive extraction.
- `data/cell-ocr-audit.json`: per-net quality report and counts of uncertain
  OCR candidates.

The ten-image proof of concept identified all 38 reference rows and
interpreted 37/38 callsigns correctly (97.4%). Only 34/38 correct callsigns
appeared verbatim in an OCR reading: the remainder were supported by
cross-net repeat-participant evidence and constrained OCR repairs. It is
important **not to call inferred records verified**. The single known
reference callsign miss was KE9DQS, an ambiguous S/9 reading.

Exact names were correct in 27/38 baseline rows. The parser flags low
name OCR confidence and retains the raw original; names are not silently
overwritten from a registry.

This is a small, repeat-participant-heavy evaluation set, *not* an
archive-wide accuracy guarantee. Review uncommon and first-time station
callsigns particularly carefully. No automatic promotion into
`preview.json` or public site statistics is enabled.

Local usage (Tesseract, OpenCV, Pillow, NumPy and pytesseract required):

```bash
python netreports-dev/scripts/extract_cells.py --root . --dates 2026-10-20
python netreports-dev/scripts/import_cells_all.py --root .
```

**Release:** Codex review plus explicit human approval required before PR
merge; separate approval required before publishing new data or statistics.

## Development page OCR v2 display (PR #19)

The **development page only** loads three static JSON resources:

1. `data/cell-ocr-archive.json`: 162 dated screenshots and 1,724 OCR v2
   candidates, including the original/alternate readings, confidence and
   inferred callsigns. These data are **unverified**.
2. `data/preview.json`: earlier archive import (1,436 rows) used strictly
   for comparing coverage. Note that its four manually reviewed sample dates
   already had corrected check-ins overlaid.
3. `data/reviewed.json`: 38 manually checked screenshot transcriptions.
   **All rows on these four dates override v2 OCR** in the displayed weekly,
   station, and trends views. The source files are immutable.

The adapter at `scripts/view-data.js` performs this composition in the
browser, validates dates and net coverage, and retains the unmodified
provisional OCR counts for the comparison tab. The main table omits Status
and Review Status fields, offers text-link callsigns and no CSV export.

The comparison tab lists **previous import vs cell OCR v2 row counts** for
each net, a per-date difference, number of flagged v2 OCR rows, and links to
source PNGs. A flagged row requires additional inspection, but an unflagged
row must **not** be considered verified. Compare using the latest source
snapshots: the page does not run OCR itself.

Verification before merge: `node netreports-dev/tests/test_view_data.js`.
This checks all 162 dates, 1,724 candidate rows, 38 manual overrides,
1,128 OCR review flags, and guards against schema drift or unexpected source
modification. A dedicated read-only GitHub Actions workflow also runs this
test on pull requests.

Do not deploy these numbers as authoritative net attendance statistics, and
do not change production `/netreports/`. PR #19 requires Codex review and
explicit human approval to merge. OCR v2 is **not** yet automatically run
when a new weekly net PNG is published.
