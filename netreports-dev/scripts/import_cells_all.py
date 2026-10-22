#!/usr/bin/env python3
"""Full historical *development-only* import using cell OCR v2.

Outputs are experimental. Do not replace preview.json or claim that guessed
callsigns are verified; keep every OCR interpretation and review flag.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from extract_cells import extract_image, score_callsign_candidates, key_name
from import_all import discover_dates

ROOT = Path(__file__).resolve().parents[2]


def import_archive(root, dates=None, extractor=extract_image):
    available = discover_dates(root)
    selected = sorted(set(dates)) if dates is not None else available
    if not selected or not set(selected).issubset(available):
        raise ValueError("No dates selected or one or more images unavailable")
    nets, rows = [], []
    for day in selected:
        path = root / "assets" / "img" / f"net-{day}.png"
        checkins, geometry = extractor(path)
        nets.append({"date": day, "image": f"/assets/img/{path.name}",
                     "ocr_rows": len(checkins), "reviewed": False,
                     "geometry": geometry})
        rows.extend(checkins)
        print(day, len(checkins), "physical rows", flush=True)
    return nets, rows


def build_audit(nets, rows, references):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["date"]].append(row)
    known = {(r["date"], r["number"]): r for r in references}
    reference_hits, correct_calls, exact_names = 0, 0, 0
    reference_dates = defaultdict(int)
    finding = []
    for net in nets:
        entries = grouped[net["date"]]
        calls = [r.get("callsign") for r in entries if r.get("callsign")]
        dup = sorted(c for c, n in Counter(calls).items() if n > 1)
        flags = [r for r in entries if r.get("needs_review")]
        missing_calls = [r["image_row"] for r in entries if not r.get("callsign")]
        finding.append({
            "date": net["date"],
            "source_image": net["image"],
            "detected_rows": len(entries),
            "review_needed_rows": len(flags),
            "missing_callsign_rows": missing_calls,
            "duplicate_callsigns": dup,
            "geometry_method": net["geometry"]["column_detection"]["method"],
        })
        for r in entries:
            ref = known.get((r["date"], r["image_row"]))
            if ref is None:
                continue
            reference_hits += 1
            reference_dates[r["date"]] += 1
            correct_calls += r["callsign"] == ref["callsign"]
            exact_names += key_name(r.get("name")) == key_name(ref.get("name"))
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_nets": len(nets),
        "candidate_checkin_rows": len(rows),
        "unverified_rows": len(rows),
        "review_needed_rows": sum(r.get("needs_review", False) for r in rows),
        "nets_with_zero_rows": [n["date"] for n in nets if not grouped[n["date"]]],
        "nets_with_duplicate_callsigns": [
            f["date"] for f in finding if f["duplicate_callsigns"]],
        "reviewed_reference_rows_in_scope": sum(
            1 for ref in references if ref["date"] in {n["date"] for n in nets}),
        "matched_reference_rows": reference_hits,
        "reference_callsign_matches": correct_calls,
        "reference_name_matches": exact_names,
        "reference_rows_by_date": dict(reference_dates),
        "net_findings": finding,
        "warning": "All derived callsigns and attendance figures are provisional, including repeat-participant interpretations; they are not verified historical facts."
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--dates", nargs="+", default=None)
    parser.add_argument("--out", default="netreports-dev/data/cell-ocr-archive.json")
    parser.add_argument("--audit", default="netreports-dev/data/cell-ocr-audit.json")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    nets, rows = import_archive(root, args.dates)
    references = json.loads(
        (root / "netreports-dev/data/reviewed.json").read_text(encoding="utf-8")
    )["rows"]

    # The same operator frequently appears over many weeks. Compare only
    # different-date observations; preserve raw OCR, candidate list, and source
    # image for audit. Pre-group by first name to keep multi-year joins bounded.
    ref_by_first = defaultdict(list)
    for r in references:
        name = key_name(r.get("name")).split()
        if name: ref_by_first[name[0]].append(r)
    row_by_first = defaultdict(list)
    for r in rows:
        name = key_name(r.get("name")).split()
        if name: row_by_first[name[0]].append(r)
    for row in rows:
        name = key_name(row.get("name")).split()
        first = name[0] if name else ""
        score_callsign_candidates(
            row, row_by_first[first], ref_by_first[first])

    rows.sort(key=lambda r:(r["date"],r["image_row"]))
    audit = build_audit(nets, rows, references)
    payload = {
        "kind": "cell-ocr-v2-full-archive-experimental",
        "version": 2, "verified": False, "generated_utc": audit["generated_utc"],
        "nets": nets, "checkins": rows,
        "limitations": audit["warning"]
    }
    for location, data in ((args.out, payload), (args.audit, audit)):
        path = root / location
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n",
                        encoding="utf-8")
    print("Nets",len(nets),"candidate rows",len(rows),
          "review flags",audit["review_needed_rows"])
    print("Reference callsigns",audit["reference_callsign_matches"],
          "/",audit["matched_reference_rows"])
    print("Reference exact names",audit["reference_name_matches"],
          "/",audit["matched_reference_rows"])


if __name__ == "__main__":
    main()
