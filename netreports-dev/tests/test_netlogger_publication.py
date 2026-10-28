"""Regression tests for unattended NetLogger publication safeguards."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_netlogger_publication.py"
spec = importlib.util.spec_from_file_location("netlogger_publication", SCRIPT)
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


def record(day, call="KC2NJ"):
    return {"date": day, "number": 1, "callsign": call, "name": "Test",
            "city": "Roseland", "county": "Essex", "state": "NJ",
            "country": "United States", "remarks": ""}


def dataset(dates, manual_dates=()):
    manual_dates = set(manual_dates)
    return {"kind": "netlogger-native-checkins",
            "nets": [{"date": day, "checkin_count": 1,
                      **({"manual": True, "source": pub.MANUAL_SOURCE}
                         if day in manual_dates else
                         {"source": "NetLogger original check-in file"})}
                     for day in dates],
            "checkins": [record(day) for day in dates],
            "source_counts": {"manual_nets": len(manual_dates)}}


def audit_for(data):
    manual = [n["date"] for n in data["nets"] if n.get("manual")]
    return {"net_count": len(data["nets"]), "checkin_count": len(data["checkins"]),
            "missing_report_dates": [], "approved_manual_net_count": len(manual),
            "approved_manual_checkin_count": len(manual),
            "approved_manual_dates": manual}


class TestPublicationProtection(unittest.TestCase):
    def test_new_weekly_log_only_date_is_accepted(self):
        old = dataset(["2026-10-20"])
        new = dataset(["2026-10-20", "2026-10-27"])
        pub.validate(old, new, audit_for(new))

    def test_missing_log_only_date_is_blocked_even_with_no_png(self):
        old = dataset(["2026-10-20", "2026-10-27"])
        new = dataset(["2026-10-20"])
        with self.assertRaisesRegex(ValueError, "missing dates"):
            pub.validate(old, new, audit_for(new))

    def test_reduced_roster_is_blocked(self):
        old = dataset(["2026-10-27"])
        new = dataset(["2026-10-27"])
        old["nets"][0]["checkin_count"] = 2
        old["checkins"].append({**record("2026-10-27", "KB2SUL"), "number": 2})
        with self.assertRaisesRegex(ValueError, "reduced rosters"):
            pub.validate(old, new, audit_for(new))

    def test_manual_reconstruction_cannot_change_silently(self):
        old = dataset(["2025-12-23"], manual_dates=["2025-12-23"])
        new = dataset(["2025-12-23"], manual_dates=["2025-12-23"])
        new["checkins"][0]["callsign"] = "KB2SUL"
        with self.assertRaisesRegex(ValueError, "changed approved manual"):
            pub.validate(old, new, audit_for(new))

    def test_native_can_supersede_approved_manual_roster(self):
        old = dataset(["2025-12-23"], manual_dates=["2025-12-23"])
        new = dataset(["2025-12-23"])
        pub.validate(old, new, audit_for(new))

    def test_manual_override_allows_explicit_correction(self):
        old = dataset(["2026-10-20", "2026-10-27"])
        new = dataset(["2026-10-20"])
        pub.validate(old, new, audit_for(new), allow_history_reduction=True)

    def test_archived_screenshot_date_loss_requires_history_override(self):
        old = dataset(["2026-10-13", "2026-10-20", "2026-10-27"])
        new = dataset(["2026-10-13", "2026-10-27"])
        audit = audit_for(new)
        audit["missing_report_dates"] = ["2026-10-20"]
        with self.assertRaisesRegex(ValueError, "Archived screenshot date"):
            pub.validate(old, new, audit)
        # A reviewed removal must be possible without deleting the old PNG.
        pub.validate(old, new, audit, allow_history_reduction=True)

    def test_override_does_not_bypass_audit_consistency(self):
        old = dataset(["2026-10-20", "2026-10-27"])
        new = dataset(["2026-10-27"])
        audit = audit_for(new)
        audit["missing_report_dates"] = ["2026-10-20"]
        audit["checkin_count"] += 1
        with self.assertRaisesRegex(ValueError, "Audit totals"):
            pub.validate(old, new, audit, allow_history_reduction=True)

    def test_private_or_unexpected_fields_are_rejected_even_with_override(self):
        old = dataset(["2026-10-27"])
        new = dataset(["2026-10-27"])
        new["checkins"][0]["address"] = "PRIVATE"
        with self.assertRaisesRegex(ValueError, "nine-field"):
            pub.validate(old, new, audit_for(new), allow_history_reduction=True)

    def test_per_date_row_count_mismatch_is_rejected(self):
        old = dataset(["2026-10-27"])
        new = dataset(["2026-10-27"])
        new["nets"][0]["checkin_count"] = 2
        with self.assertRaisesRegex(ValueError, "Per-date"):
            pub.validate(old, new, audit_for(new))


if __name__ == "__main__":
    unittest.main()
