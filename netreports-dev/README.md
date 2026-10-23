# K2GQ Net Reports: native NetLogger data (development)

This directory powers the development preview at `/netreports-dev/`. The
production `/netreports/` pages and their historic posts remain unchanged.

## Source of truth

**Only original NetLogger CheckIns files are used to create this database.**
Upload .log files or ZIP archives of CheckIns directories to
`_netlogger-checkins/`. Preserve native content, file names and source
laptop folder structures wherever possible.

The first of three promised uploads is present. The development database is
**incomplete**, and the historic date-gap report is **preliminary** until
all three batches are uploaded and evaluated.

## Import files

- `scripts/build_netlogger.py` parses original pipe-delimited CheckIns files.
- `data/netlogger.json` contains the rendered, privacy-reduced data:
  check-in number, callsign, name, city, county, state, country and
  operating remarks. It does **not** include addresses, ZIP codes, FRNs,
  phone numbers, email addresses or personal QRZ notes.
- `data/netlogger-audit.json` inventories source files, duplicate/snapshot
  exports, files that cannot be matched unambiguously to Tuesday net dates,
  and dates with no uploaded native file yet.
- `tests/test_netlogger.py` tests data mappings, Eastern time conversion,
  duplicate exports, privacy protections and ZIP handling.
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
generated datasets have been removed from the development branch. Historical
screenshots remain available for gap auditing but **do not generate or
correct check-in records**.

After the user confirms all three batches have been uploaded, compare every
available native file against the full list of 162 screenshot net dates.
Report missing, duplicate and conflicting nets, and create manual entries
only after explicit review of the missing session data.

Do not merge development changes without Codex review and explicit user
approval. Do not replace production net reports until the new dataset and
web interface have been accepted.
