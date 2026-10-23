# K2GQ Net Reports: native logs and approved manual records (development)

This directory powers the development preview at `/netreports-dev/`. The
production `/netreports/` pages and their historic posts remain unchanged.

## Source of truth

Original NetLogger CheckIns files are the primary records. For the 11
historical dates without native log files, the database includes the **66
user-approved manual check-ins** from
`netreports-dev/data/manual-checkins.csv`. No OCR-generated guesses are
accepted without explicit manual approval. Upload future native .log files or
ZIP archives of CheckIns directories to `_netlogger-checkins/`. Preserve
native filenames and source laptop structures when possible.

All upload batches have been received. The combined database covers **all
162 screenshot-dated reports**: 151 with native NetLogger records, plus 11
manually reconstructed and explicitly approved reports. The original log
files remain preferred if an original is recovered later.

## Import files

- `scripts/build_netlogger.py` parses original pipe-delimited CheckIns files
  and validates and imports approved manual check-ins for dates without them.
- `data/manual-checkins.csv` preserves the user's approved nine-column
  transcription, with dates normalized to ISO `YYYY-MM-DD`. These rows are
  **not** silently replaced by future screenshot-reading automation.
  If a real NetLogger file is later recovered for one of these dates,
  that original log takes precedence, and the conflict is audited.
- `data/netlogger.json` contains the rendered, privacy-reduced data:
  check-in number, callsign, name, city, county, state, country and
  operating remarks. It does **not** include addresses, ZIP codes, FRNs,
  phone numbers, email addresses or personal QRZ notes.
- `data/netlogger-audit.json` inventories native sources,
  duplicate/snapshot exports, ambiguous dates, manually approved dates,
  uncovered report dates, and manual dates superseded by newly found logs.
- `tests/test_netlogger.py` tests native mappings, Eastern time conversion,
  duplicate exports, manual row validation and native precedence, privacy
  protections, and ZIP handling.
- `.github/workflows/netlogger-native.yml` produces staging branch output
  and validates the pull request.

Source filenames such as `CheckInsOn10-21-2026-00-07.log` represent UTC
timestamps. Convert to `America/New_York` to match the Tuesday local net
date (`2026-10-20` in that example).

Each log can contain unused blank rows. These are **not** check-ins.

When multiple exports exist for a single net, the provisional importer
selects the export with the most nonblank rows, then the latest UTC time
as a tiebreaker. It preserves an audit trail of all competing source files
and flags disagreement rather than merging identities or inventing rows.

An export whose timestamp falls **outside the usual Tuesday schedule** is
quarantined for manual review. Valid Tuesday native files are imported even
when no matching screenshot exists; the missing screenshot is reported for
audit. Early roster snapshots saved before 8:00 p.m. Eastern are flagged
because the net may not yet have finished. The screenshots are retained
strictly as a **date inventory**, not as a check-in source.

## Privacy

The upstream `_netlogger-checkins/` directory is in a **public GitHub
repository**, even though Jekyll does not publish underscore-prefixed
folders as pages. Raw NetLogger files can contain full postal addresses and
other personal data. Do not link or embed raw files in the website. If the
source records need to be private, move them to private storage before
additional uploads. Changing the website view does not make GitHub raw
files private.

## Local development

From the repository root, with Python 3.12+:

```bash
python -m unittest discover -s netreports-dev/tests -p test_netlogger.py -v
python netreports-dev/scripts/build_netlogger.py --root .
```

## Import policy

The previous experimental screenshot text-extraction pipeline and all its
generated datasets have been removed. The explicitly approved 66 manually
reconstructed entries are preserved in `manual-checkins.csv`; no OCR pipeline
runs on site or can silently change these user-approved records. Screenshots
remain available for historical reference.

After additional NetLogger uploads, compare every available native file
against the full list of 162 screenshot net dates.
Report missing, duplicate and conflicting nets, and create manual entries
only after explicit review of the missing session data.

Do not merge development changes without Codex review and explicit user
approval. Do not replace production net reports until the new dataset and
web interface have been accepted.
