# K2GQ Net Reports: native logs and approved manual records (development)

This directory powers the development workspace at `/netreports-dev/`.
The public `/netreports/` page contains its own copy of the dashboard UI below
its "How to Join" section. Both pages currently load the reviewed check-in data
from `/netreports-dev/data/netlogger.json`, so data updates merged to the default
branch affect both pages. Editing `netreports-dev/index.html` alone does not
change the production interface. The previous classic reports page is preserved
at `/netreports-legacy/`.

## Source of truth

Original NetLogger CheckIns files are the primary records. For the 11
historical dates without native log files, the database includes the **66
user-approved manual check-ins** from
`netreports-dev/data/manual-checkins.csv`. No OCR-generated guesses are
accepted without explicit manual approval. Upload future native .log files or
ZIP archives of CheckIns directories to `_netlogger-checkins/`. Preserve
native filenames and source laptop structures when possible.

The database covers all **162 historical screenshot-dated reports** (151
native NetLogger records and 11 explicitly approved manual reconstructions),
plus subsequent weekly nets supplied by original NetLogger files alone.
The last archived screenshot is dated October 20, 2026; starting October 27,
2026, **screenshots are no longer required**. Upload the completed NetLogger
check-in `.log` file for each Tuesday net. Native log files are always preferred
when recovered for a previously reconstructed historical date.

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
- `.github/workflows/netlogger-native.yml` validates imports and, on
  `master` uploads, automatically regenerates the shared database, commits
  the whitelist-only JSON, and requests a GitHub Pages rebuild. Pull
  requests run validation without publishing.

Source filenames such as `CheckInsOn10-27-2026-23-05.log` represent UTC
timestamps. Convert to `America/New_York` to match the Tuesday local net
date (`2026-10-27` in this example, at 7:05 PM EDT).

Each log can contain unused blank rows. These are **not** check-ins.

When multiple exports exist for a single net, the provisional importer
selects the export with the most nonblank rows, then the latest UTC time
as a tiebreaker. It preserves an audit trail of all competing source files
and flags disagreement rather than merging identities or inventing rows.

An export whose timestamp falls **outside the usual Tuesday schedule** is
quarantined for manual review. Valid Tuesday native files are imported even
when no matching screenshot exists. Dates after the last archived screenshot
(October 20, 2026) are identified as **expected log-only nets**, not
missing screenshots. Early roster snapshots saved before 8:00 p.m. Eastern are flagged
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

For future weekly nets, upload only the saved NetLogger `.log` to
`_netlogger-checkins/` on `master`. No screenshot, CSV, or manual page edit is
needed. Check the GitHub Actions import and Pages build results. Historical
missing dates, duplicate logs, and conflicting check-ins remain auditable.

Do not merge development changes without Codex review and explicit user
approval. Changes to the development dashboard interface require a deliberate,
separate update to `netreports.md` before they appear on production. Updates to
the shared JSON dataset affect both sites once merged.
