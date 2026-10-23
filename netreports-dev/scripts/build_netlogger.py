#!/usr/bin/env python3
"""Build the K2GQ development database exclusively from original NetLogger logs.

The raw CheckIns files contain private mailing addresses, ZIP codes, and
potentially other personal data. NEVER copy those fields into website JSON.
No OCR files are read. Net report screenshots are used ONLY to report dates
whose corresponding native logs have not yet been uploaded.
"""
import argparse
import csv
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
MANUAL_FIELDS = ("date", "number", "callsign", "name", "city", "county",
                 "state", "country", "remarks")


def read_approved_manual(root):
    """Validate approved transcription CSV, never synthesize participant data.

    The CSV is a permanent, human-approved record, separate from raw
    NetLogger exports. Each missing date has one complete roster.
    """
    path = root / "netreports-dev/data/manual-checkins.csv"
    if not path.exists():
        return {}
    groups = defaultdict(list)
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != MANUAL_FIELDS:
            raise ValueError("Manual check-in CSV has unexpected fields")
        used = set()
        for csv_line, source in enumerate(reader, start=2):
            if None in source or any(value is None for value in source.values()):
                raise ValueError(f"Malformed approved CSV line {csv_line}")
            row = {key: str(source[key]).strip() for key in MANUAL_FIELDS}
            day = row["date"]
            try:
                if datetime.strptime(day, "%Y-%m-%d").strftime("%Y-%m-%d") != day:
                    raise ValueError("Noncanonical date")
            except ValueError as exc:
                raise ValueError(f"Invalid approved net date at line {csv_line}") from exc
            try:
                number = int(row["number"])
            except ValueError as exc:
                raise ValueError(f"Invalid approved check-in number on {day}") from exc
            if number < 1 or str(number) != row["number"]:
                raise ValueError(f"Invalid approved row number on {day}")
            call = row["callsign"].upper()
            if not CALLSIGN.fullmatch(call):
                raise ValueError(f"Invalid approved callsign on {day}, row {number}")
            if not row["name"]:
                raise ValueError(f"Approved name is empty on {day}, row {number}")
            key = (day, number)
            if key in used:
                raise ValueError(f"Duplicate approved row number on {day}: {number}")
            used.add(key)
            row["number"] = number
            row["callsign"] = call
            groups[day].append(row)
    for day, rows in groups.items():
        rows.sort(key=lambda r: r["number"])
        if [r["number"] for r in rows] != list(range(1, len(rows) + 1)):
            raise ValueError(f"Incomplete approved net sequence on {day}")
    return dict(groups)



def parse_filename(filename):
    """NetLogger's filename timestamp is UTC; convert to the net's ET date."""
    m = FILENAME.fullmatch(Path(str(filename).replace("\\", "/")).name)
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
    for source in sorted(directory.rglob("*"),
                         key=lambda p: p.relative_to(directory).as_posix()):
        if not source.is_file():
            continue
        identifier = source.relative_to(directory).as_posix()
        if source.suffix.lower() == ".log":
            if source.stat().st_size > MAX_MEMBER:
                raise ValueError("Oversized NetLogger log: " + identifier)
            files.append((identifier, source.read_bytes()))
        elif source.suffix.lower() == ".zip":
            try:
                with ZipFile(source) as archive:
                    members = [n for n in archive.infolist()
                               if not n.is_dir() and n.filename.lower().endswith(".log")]
                    if len(members) > MAX_ARCHIVE_MEMBERS:
                        raise ValueError("Too many logs in archive " + identifier)
                    for member in sorted(members, key=lambda n: n.filename):
                        if member.file_size > MAX_MEMBER:
                            raise ValueError("Oversized ZIP log in " + identifier)
                        # No extraction to disk. Preserve archive/member identifier.
                        files.append((identifier + "::" + member.filename,
                                      archive.read(member)))
            except BadZipFile as exc:
                raise ValueError("Invalid ZIP: " + identifier) from exc
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
            # A valid Tuesday original log is authoritative even when the
            # screenshot directory has no matching PNG. Screenshots are only
            # used to identify outstanding/missing coverage later.
            historical_wednesday = (metadata["weekday"] == "Wed" and
                                    "2023-08-30" <= metadata["date"] <= "2023-11-01")
            normal_net_day = metadata["weekday"] == "Tue" or historical_wednesday
            reason = None
            if not normal_net_day:
                reason = ("Not on the historical net schedule: " +
                          metadata["date"] + " (" + metadata["weekday"] + ")")
            if not rows:
                reason = reason or "No nonblank check-ins"
            parsed.append({**metadata, "source": file_id, "rows": rows,
                           "count": len(rows), "warnings": warnings,
                           "eligible": normal_net_day and bool(rows),
                           "quarantine": reason})
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
            # Also compare the public field values, not only row+callsign.
            # Two snapshots can disagree on names, places or operating mode
            # even when every callsign and row number is identical.
            def public_index(item):
                return {(r["number"], r["callsign"]): r for r in item["rows"]}
            primary = public_index(chosen)
            conflicting = False
            for other in group[1:]:
                for key, alternative in public_index(other).items():
                    if key not in primary or primary[key] != alternative:
                        conflicting = True
                        break
                if conflicting:
                    break
            overlaps.append({
                "date": date, "preferred_source": chosen["source"],
                "sources": [{"file": item["source"], "rows": item["count"],
                             "time_et": item["local_time"]} for item in group],
                "conflicting_rows": conflicting
            })
        output_nets.append({
            "date": date, "checkin_count": chosen["count"],
            "source_file": chosen["source"],
            "source_time_et": chosen["local_time"],
            "possibly_early_snapshot": chosen["local_time"] < "20:00",
            "other_exports": len(group)-1,
            "source_warning_count": len(chosen["warnings"]),
            "source": "NetLogger original check-in file"
        })
        for row in chosen["rows"]:
            checkins.append({"date": date, **row})
    # Original NetLogger check-ins are always the primary source.
    # Approved manual reconstructions fill ONLY dates without native logs.
    approved = read_approved_manual(root)
    native_dates = set(groups)
    unused_manual_dates = sorted(native_dates.intersection(approved))
    manual_dates = sorted(set(approved).difference(native_dates))
    for day in manual_dates:
        rows = approved[day]
        output_nets.append({
            "date": day, "checkin_count": len(rows),
            "source_file": "netreports-dev/data/manual-checkins.csv",
            "source_time_et": None, "possibly_early_snapshot": False,
            "other_exports": 0, "source_warning_count": 0,
            "source": "User-approved manual reconstruction",
            "manual": True,
        })
        checkins.extend(rows)
    output_nets.sort(key=lambda n: n["date"])
    checkins.sort(key=lambda r: (r["date"], r["number"]))
    all_dates = native_dates.union(manual_dates)
    audit = {
        "source_type": "Original NetLogger CheckIns exports and approved manual records",
        "batch_status": "Uploads complete; gap review in progress",
        "source_file_count": len(sources),
        "matched_export_count": sum(len(g) for g in groups.values()),
        "net_count": len(output_nets),
        "checkin_count": len(checkins),
        "screenshot_net_dates": len(existing),
        "missing_native_dates": sorted(existing-native_dates),
        "missing_report_dates": sorted(existing-all_dates),
        "approved_manual_net_count": len(manual_dates),
        "approved_manual_checkin_count": sum(len(approved[d]) for d in manual_dates),
        "approved_manual_dates": manual_dates,
        "approved_manual_superseded_by_native": unused_manual_dates,
        "native_dates_without_screenshot": sorted(native_dates-existing),
        "possibly_early_snapshots": [
            {"date": n["date"], "source_file": n["source_file"],
             "source_time_et": n["source_time_et"]}
            for n in output_nets if n["possibly_early_snapshot"]
        ],
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
        "limitations": ("Native NetLogger logs are authoritative when available. "
                        "Manually reconstructed check-ins come exclusively from the "
                        "user-approved CSV and are never auto-generated from OCR. "
                        "UTC log timestamps are mapped to Eastern net dates. "
                        "Off-schedule files remain quarantined (historical "
                        "Wednesday nets from August to November 2023 are accepted); "
                        "early snapshots may be incomplete."),
    }
    payload = {
        "kind": "netlogger-native-checkins", "version": 1,
        "source": "Original NetLogger logs plus approved manual check-ins",
        "batch_status": "Uploads complete; gap review in progress",
        "nets": output_nets, "checkins": checkins,
        "source_counts": {
            "native_nets": len(native_dates),
            "native_checkins": len(checkins) - audit["approved_manual_checkin_count"],
            "manual_nets": len(manual_dates),
            "manual_checkins": audit["approved_manual_checkin_count"],
        },
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
    print("Total net dates:", audit["net_count"])
    print("Total check-ins:", audit["checkin_count"])
    print("Approved manual net dates:", audit["approved_manual_net_count"])
    print("Unmatched exports:", len(audit["quarantined_exports"]))
    print("Uncovered screenshot net dates:", len(audit["missing_report_dates"]))
    # Safety: Never print original log data, including postal addresses.


if __name__ == "__main__":
    main()
