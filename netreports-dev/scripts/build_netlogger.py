#!/usr/bin/env python3
"""Build the K2GQ development database exclusively from original NetLogger logs.

The raw CheckIns files contain private mailing addresses, ZIP codes, and
potentially other personal data. NEVER copy those fields into website JSON.
No OCR files are read. Net report screenshots are used ONLY to report dates
whose corresponding native logs have not yet been uploaded.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo
from zipfile import ZipFile, BadZipFile

EASTERN = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parents[2]
FILENAME = re.compile(r"CheckInsOn(\d{2})-(\d{2})-(\d{4})-(\d{2})-(\d{2})(.*?)\.log$", re.I)
PNG = re.compile(r"net-(\d{4}-\d{2}-\d{2})\.png$")
CALLSIGN = re.compile(r"^[A-Z0-9]{2,12}(?:/[A-Z0-9]{1,5})?$")
MAX_MEMBER = 4 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 5000


def parse_filename(filename):
    """NetLogger's filename timestamp is UTC; convert to the net's ET date."""
    m = FILENAME.fullmatch(Path(filename).name)
    if not m:
        raise ValueError("Unrecognized NetLogger log filename: " + str(filename))
    month, day, year, hour, minute = map(int, m.groups()[:5])
    timestamp = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    local = timestamp.astimezone(EASTERN)
    return {"date": local.date().isoformat(), "local_time": local.strftime("%H:%M"),
            "utc_time": timestamp.isoformat(), "weekday": local.strftime("%a")}


def decode_bytes(blob):
    try:
        return blob.decode("utf-8-sig")
    except UnicodeDecodeError:
        return blob.decode("cp1252")


def parse_log(blob, file_id):
    """Read the positional pipe-delimited CheckIns file; whitelist PUBLIC columns."""
    rows, warnings = [], []
    numbers = set()
    for line_no, raw in enumerate(decode_bytes(blob).splitlines(), 1):
        if not raw.strip():
            continue
        cells = [v.strip() for v in raw.split("|")]
        if len(cells) < 19:
            warnings.append(f"Line {line_no} has {len(cells)} fields (expected at least 19)")
            continue
        if not cells[1]:  # NetLogger includes unused blank slots below the roster.
            continue
        try:
            position = int(cells[0])
        except ValueError:
            warnings.append(f"Line {line_no} has no valid row number")
            continue
        if position < 1 or position in numbers:
            warnings.append(f"Line {line_no}: duplicate or invalid row number {position}")
            continue
        numbers.add(position)
        call = cells[1].upper()
        if not CALLSIGN.fullmatch(call):
            warnings.append(f"Line {line_no}: unrecognized callsign format")
            # Keep it as a native record, but mark source issue for review.
        rows.append({
            "number": position, "callsign": call, "name": cells[6],
            "city": cells[5], "county": cells[10], "state": cells[2],
            "country": cells[18], "remarks": cells[3],
        })
    rows.sort(key=lambda r: r["number"])
    return rows, warnings


def scan_sources(directory):
    """Read .log files and optional per-laptop ZIPs without extracting unsafe paths."""
    files = []
    for source in sorted(directory.iterdir(), key=lambda p: p.name):
        if source.is_file() and source.suffix.lower() == ".log":
            if source.stat().st_size > MAX_MEMBER:
                raise ValueError("Oversized NetLogger log: " + source.name)
            files.append((source.name, source.read_bytes()))
        elif source.is_file() and source.suffix.lower() == ".zip":
            try:
                with ZipFile(source) as archive:
                    members = [n for n in archive.infolist()
                               if not n.is_dir() and n.filename.lower().endswith(".log")]
                    if len(members) > MAX_ARCHIVE_MEMBERS:
                        raise ValueError("Too many logs in archive " + source.name)
                    for member in sorted(members, key=lambda n: n.filename):
                        if member.file_size > MAX_MEMBER:
                            raise ValueError("Oversized ZIP log in " + source.name)
                        # No extraction to disk. Preserve archive/member identifier.
                        files.append((source.name + "::" + member.filename,
                                      archive.read(member)))
            except BadZipFile as exc:
                raise ValueError("Invalid ZIP: " + source.name) from exc
    return files


def screenshot_dates(root):
    return sorted({m.group(1) for p in (root / "assets/img").glob("net-*.png")
                   if (m := PNG.fullmatch(p.name))})


def build(root):
    sources = scan_sources(root / "_netlogger-checkins")
    existing = set(screenshot_dates(root))
    parsed = []
    for file_id, blob in sources:
        try:
            metadata = parse_filename(file_id.split("::")[-1])
            rows, warnings = parse_log(blob, file_id)
            # Explicitly quarantine out-of-schedule files rather than guess.
            # Their contents remain untouched for manual evaluation.
            in_scope = metadata["date"] in existing
            reason = None
            if not in_scope:
                reason = ("Not a screenshot net date / nonstandard day: " +
                          metadata["date"] + " (" + metadata["weekday"] + ")")
            if not rows:
                reason = reason or "No nonblank check-ins"
            parsed.append({**metadata, "source": file_id, "rows": rows,
                           "count": len(rows), "warnings": warnings,
                           "eligible": in_scope and bool(rows), "quarantine": reason})
        except (ValueError, UnicodeError) as exc:
            parsed.append({"source": file_id, "eligible": False, "date": None,
                           "count": 0, "quarantine": str(exc), "warnings": []})
    groups = defaultdict(list)
    for p in parsed:
        if p["eligible"]:
            groups[p["date"]].append(p)
    output_nets, checkins, overlaps = [], [], []
    for date in sorted(groups):
        group = sorted(groups[date], key=lambda p: (p["count"], p["utc_time"]),
                       reverse=True)
        chosen = group[0]
        if len(group) > 1:
            signatures = [set((r["number"], r["callsign"]) for r in g["rows"])
                          for g in group]
            # Overlapping log exports may represent snapshots at different times.
            overlaps.append({
                "date": date, "preferred_source": chosen["source"],
                "sources": [{"file": item["source"], "rows": item["count"],
                             "time_et": item["local_time"]} for item in group],
                "conflicting_rows": any(not s.issubset(signatures[0])
                                        for s in signatures[1:])
            })
        output_nets.append({
            "date": date, "checkin_count": chosen["count"],
            "source_file": chosen["source"],
            "other_exports": len(group)-1,
            "source_warning_count": len(chosen["warnings"]),
            "source": "NetLogger original check-in file"
        })
        for row in chosen["rows"]:
            checkins.append({"date": date, **row})
    all_dates = set(groups)
    audit = {
        "source_type": "Original NetLogger CheckIns exports ONLY",
        "batch_status": "1 of 3 batches received; coverage INCOMPLETE",
        "source_file_count": len(sources),
        "matched_export_count": sum(len(g) for g in groups.values()),
        "net_count": len(output_nets),
        "checkin_count": len(checkins),
        "screenshot_net_dates": len(existing),
        "missing_native_dates": sorted(existing-all_dates),
        "native_dates_without_screenshot": sorted(all_dates-existing),
        "quarantined_exports": [
            {"file": p["source"], "timestamp_date_et": p.get("date"),
             "reason": p["quarantine"], "nonblank_rows": p["count"]}
            for p in parsed if not p["eligible"]
        ],
        "duplicate_exports": overlaps,
        "parse_warnings": [
            {"file": p["source"], "warnings": p["warnings"]}
            for p in parsed if p["warnings"]
        ],
        "limitations": ("Preliminary batch only. Native filenames are treated as UTC "
                        "and mapped to Eastern net date. Files whose date does not "
                        "match a historical net screenshot are quarantined. "
                        "Other laptops may contain missing or more complete logs. "
                        "No OCR data is used."),
    }
    payload = {
        "kind": "netlogger-native-checkins", "version": 1,
        "source": "Original NetLogger CheckIns logs only",
        "batch_status": "1 of 3 (partial)",
        "nets": output_nets, "checkins": checkins,
    }
    return payload, audit


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", default="netreports-dev/data/netlogger.json")
    ap.add_argument("--audit", default="netreports-dev/data/netlogger-audit.json")
    args = ap.parse_args(argv)
    payload, audit = build(args.root.resolve())
    for name, data in ((args.out, payload), (args.audit, audit)):
        path = args.root.resolve() / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print("Source files:", audit["source_file_count"])
    print("Distinct matched nets:", audit["net_count"])
    print("Native check-ins:", audit["checkin_count"])
    print("Unmatched exports:", len(audit["quarantined_exports"]))
    print("Missing source net dates (preliminary):", len(audit["missing_native_dates"]))
    # Safety: Never print original log data, including postal addresses.


if __name__ == "__main__":
    main()
