#!/usr/bin/env python3
"""Import all dated NetLogger screenshots into the *development* archive.

OCR candidates are NOT verified facts. Keep original images, per-image
audit findings, and four existing screenshot-reviewed reference nets.

The existing extract.py CLI is reused in small batches: do not concatenate
years of full-size screenshots into one Tesseract image (OOM risk).
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, date, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

IMAGE_RE = re.compile(r"^net-(\d{4}-\d{2}-\d{2})\.png$")
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JSON = "netreports-dev/data/preview.json"
DEFAULT_AUDIT = "netreports-dev/data/import-audit.json"
DEFAULT_LOG = "netreports-dev/data/ocr-review.txt"
FIELDS = ("date", "number", "callsign", "name", "city", "county",
          "state", "country", "remarks", "reviewed")
CALL_RE = re.compile(r"^[A-Z0-9]{2,8}(?:/[A-Z0-9]{1,5})?$")


def discover_dates(root):
    """Only images with real ISO dates are source net records."""
    matches = []
    for p in (root / "assets" / "img").iterdir():
        m = IMAGE_RE.fullmatch(p.name)
        if m:
            try:
                date.fromisoformat(m.group(1))
            except ValueError:
                continue
            matches.append(m.group(1))
    return sorted(set(matches))


def chunks(values, size):
    for offset in range(0, len(values), size):
        yield values[offset: offset + size]


def merge_batches(root, days, batch_size, runner=None):
    """Invoke existing extractor with selected dates, collect raw diagnostics."""
    runner = runner or subprocess.run
    nets, checkins, diagnostic = [], [], []
    with tempfile.TemporaryDirectory(prefix="k2gq-netlogs-") as folder:
        tmp = Path(folder)
        for i, group in enumerate(chunks(days, batch_size), 1):
            out = tmp / f"part-{i}.json"
            log = tmp / f"part-{i}.txt"
            cmd = [sys.executable, str(root / "netreports-dev/scripts/extract.py"),
                   "--root", str(root), "--dates", *group,
                   "--out", str(out), "--text", str(log)]
            print(f"OCR batch {i}: {group[0]} .. {group[-1]}", flush=True)
            runner(cmd, check=True, timeout=240)
            part = json.loads(out.read_text(encoding="utf-8"))
            actual = {n["date"] for n in part["nets"]}
            if actual != set(group):
                raise ValueError(f"OCR batch {i} lost dates: {set(group) - actual}")
            nets.extend(part["nets"])
            checkins.extend(part["checkins"])
            diagnostic.append(log.read_text(encoding="utf-8"))
    return nets, checkins, "\n".join(diagnostic)


def audit_archive(days, nets, rows):
    """Surface OCR incompleteness rather than silently certifying the results."""
    by_date = defaultdict(list)
    for row in rows:
        by_date[row["date"]].append(row)
    findings = []
    for net in sorted(nets, key=lambda x:x["date"]):
        day = net["date"]
        entries = by_date[day]
        calls = [str(r.get("callsign", "")).upper() for r in entries]
        nums = [r.get("number") for r in entries if isinstance(r.get("number"), int)]
        duplicates = sorted(k for k, v in Counter(calls).items() if k and v > 1)
        missing_numbers = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        invalid_calls = sorted({c for c in calls if not CALL_RE.fullmatch(c)})
        low_conf = sum(bool(r.get("needs_review")) for r in entries)
        issue = []
        if not entries:
            issue.append("No check-ins recognized")
        if missing_numbers and not net.get("reviewed"):
            issue.append("Numbered rows missing from OCR output")
        if duplicates:
            issue.append("Repeated callsign in one net")
        if invalid_calls:
            issue.append("Unexpected callsign format")
        if low_conf and not net.get("reviewed"):
            issue.append("Low-confidence OCR entries")
        if net.get("reviewed") and low_conf:
            issue.append("Reviewed data unexpectedly marked uncertain")
        findings.append({
            "date": day, "source_image": net["image"],
            "recognized_rows": len(entries), "reviewed": bool(net.get("reviewed")),
            "low_confidence_rows": low_conf, "missing_row_numbers": missing_numbers,
            "duplicate_callsigns": duplicates, "invalid_callsigns": invalid_calls,
            "issues": issue
        })
    # Identify possible misread callsigns without silently merging different stations.
    # Exact normalized names are only a review hint, not proof of station identity.
    names = defaultdict(lambda: defaultdict(set))
    for row in rows:
        name = re.sub(r"[^A-Z ]", "", str(row.get("name") or "").upper())
        name = " ".join(name.split())
        call = str(row.get("callsign") or "").upper()
        if len(name) >= 8 and CALL_RE.fullmatch(call):
            names[name][call].add(row["date"])
    possible_aliases = [
        {
            "operator_name": name,
            "callsigns": [
                {"call": call, "net_count": len(dates)}
                for call, dates in sorted(calls.items(),
                                         key=lambda p: (-len(p[1]), p[0]))
            ]
        }
        for name, calls in names.items() if len(calls) > 1
    ]
    possible_aliases.sort(
        key=lambda item: (-sum(c["net_count"] for c in item["callsigns"]),
                          item["operator_name"]))
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_image_count": len(days),
        "imported_net_count": len(nets),
        "extracted_checkin_rows": len(rows),
        "reviewed_nets": sum(bool(n.get("reviewed")) for n in nets),
        "unreviewed_nets": sum(not n.get("reviewed") for n in nets),
        "nets_with_no_recognized_rows": [n["date"] for n in nets if not by_date[n["date"]]],
        "possible_callsign_variants_by_name": possible_aliases,
        "nets_flagged_for_review": sum(bool(f["issues"]) or not f["reviewed"] for f in findings),
        "limitations": "OCR candidates have not been compared against source images except explicit reviewed dates. Missing check-ins and callsign errors remain possible.",
        "findings": findings
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--dates", nargs="*", default=None,
                   help="Optional date subset; default imports every net-YYYY-MM-DD.png")
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--out", default=DEFAULT_JSON)
    p.add_argument("--audit", default=DEFAULT_AUDIT)
    p.add_argument("--text", default=DEFAULT_LOG)
    args = p.parse_args(argv)
    if args.batch_size < 1 or args.batch_size > 6:
        p.error("--batch-size must be between 1 and 6")
    root = args.root.resolve()
    available = discover_dates(root)
    if not available:
        p.error("No dated net screenshots found")
    if args.dates is not None:
        days = sorted(set(args.dates))
        absent = set(days) - set(available)
        if absent:
            p.error("Unknown source net dates: " + ", ".join(sorted(absent)))
        if not days:
            p.error("Specify at least one date or omit --dates to import all")
    else:
        days = available
    nets, checkins, text = merge_batches(root, days, args.batch_size)
    nets.sort(key=lambda item: item["date"])
    checkins.sort(key=lambda r: (r["date"], r.get("number") or 999, r["callsign"]))
    if len(nets) != len(days) or {n["date"] for n in nets} != set(days):
        raise ValueError("Imported nets do not match selected source images")
    if len({n["date"] for n in nets}) != len(nets):
        raise ValueError("Duplicate net date in source import")
    audit = audit_archive(days, nets, checkins)
    payload = {
        "kind": "netlogs-dev-archive", "sample_only": False,
        "generated_utc": audit["generated_utc"],
        "reviewed": False,
        "reviewed_rows": sum(bool(r.get("reviewed")) for r in checkins),
        "limitations": audit["limitations"],
        "nets": nets, "checkins": checkins
    }
    for path, obj in [(args.out, payload), (args.audit, audit)]:
        output = root / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    path = root / args.text
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Imported {len(nets)} net logs, {len(checkins)} OCR candidate check-ins; "
          f"{audit['reviewed_nets']} reports manually reviewed; "
          f"{len(audit['nets_with_no_recognized_rows'])} reports recognized zero rows.",
          flush=True)


if __name__ == "__main__":
    main()
