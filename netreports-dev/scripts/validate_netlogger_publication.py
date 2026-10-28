#!/usr/bin/env python3
"""Fail closed if a NetLogger rebuild would damage the public check-in history.

The published JSON is the baseline. Ordinary imports may only add net dates
and cannot reduce existing rosters or silently change approved manual rows.
An explicit human-initiated workflow_dispatch can authorize corrections.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

FIELDS = {"date", "number", "callsign", "name", "city", "county",
          "state", "country", "remarks"}
MANUAL_SOURCE = "User-approved manual reconstruction"


def validate(baseline, updated, audit, allow_history_reduction=False):
    """Validate schema, historical coverage and previously approved records."""
    if updated.get("kind") != "netlogger-native-checkins":
        raise ValueError("Unexpected public data kind")

    nets = updated["nets"]
    rows = updated["checkins"]
    dates = [item["date"] for item in nets]
    if len(set(dates)) != len(dates):
        raise ValueError("Duplicate net date in rebuilt database")
    new_by_date = {item["date"]: item for item in nets}
    if any(set(row) != FIELDS for row in rows):
        raise ValueError("Public check-in row violates the nine-field whitelist")
    if any(row["date"] not in new_by_date for row in rows):
        raise ValueError("A check-in has no corresponding net")
    counts = Counter(row["date"] for row in rows)
    if any(counts[day] != item["checkin_count"] for day, item in new_by_date.items()):
        raise ValueError("Per-date check-in counts do not match")
    if len(nets) != audit["net_count"] or len(rows) != audit["checkin_count"]:
        raise ValueError("Audit totals do not match public database")
    if audit["missing_report_dates"]:
        raise ValueError("Archived screenshot date has lost check-in coverage")
    manual_nets = {day for day, item in new_by_date.items() if item.get("manual")}
    if any(new_by_date[day].get("source") != MANUAL_SOURCE for day in manual_nets):
        raise ValueError("Manual net has incorrect provenance")
    if len(manual_nets) != updated["source_counts"]["manual_nets"]:
        raise ValueError("Manual net count mismatch")
    if len(manual_nets) != audit["approved_manual_net_count"]:
        raise ValueError("Approved manual net count mismatch")
    if set(audit["approved_manual_dates"]) != manual_nets:
        raise ValueError("Approved manual dates mismatch")
    if sum(counts[day] for day in manual_nets) != audit["approved_manual_checkin_count"]:
        raise ValueError("Approved manual check-in count mismatch")

    old_by_date = {item["date"]: item for item in baseline["nets"]}
    lost = sorted(set(old_by_date) - set(new_by_date))
    shortened = sorted(day for day in old_by_date.keys() & new_by_date.keys()
                       if new_by_date[day]["checkin_count"] <
                       old_by_date[day]["checkin_count"])
    old_manual_dates = {day for day, net in old_by_date.items() if net.get("manual")}
    unchanged_manual_dates = old_manual_dates & manual_nets
    def manual_rows(payload, day):
        return sorted((row for row in payload["checkins"] if row["date"] == day),
                      key=lambda row: row["number"])
    changed_manual = sorted(day for day in unchanged_manual_dates
                            if manual_rows(baseline, day) != manual_rows(updated, day))
    if (lost or shortened or changed_manual) and not allow_history_reduction:
        raise ValueError("History protection stopped publication: "
                         f"missing dates={lost}; reduced rosters={shortened}; "
                         f"changed approved manual rows={changed_manual}. "
                         "Correct the source or use the explicit manual "
                         "workflow_dispatch override after review.")
    print(f"Validated {len(nets)} nets and {len(rows)} permitted check-ins.")
    if allow_history_reduction:
        print("Intentional history correction override was explicitly enabled.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--updated", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--allow-history-reduction", action="store_true")
    args = parser.parse_args()
    validate(json.loads(args.baseline.read_text(encoding="utf-8")),
             json.loads(args.updated.read_text(encoding="utf-8")),
             json.loads(args.audit.read_text(encoding="utf-8")),
             allow_history_reduction=args.allow_history_reduction)


if __name__ == "__main__":
    main()
