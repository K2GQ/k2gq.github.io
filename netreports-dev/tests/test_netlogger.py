"""Focused regression tests for native NetLogger import. OCR is not used."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_netlogger.py"
spec = importlib.util.spec_from_file_location("netlogger_native", SCRIPT)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def log_row(i, call="KC2NJ", name="Mike Abbey", city="Short Hills"):
    cells = [str(i), call, "NJ", "RF - TXA", "PRIVATE QSL",
             city, name, "(nc)", "", "", "Essex", "FN20us",
             "PRIVATE HOME ADDRESS", "PRIVATE ZIP", "291", "", "", "",
             "United States", "Michael"]
    return "|".join(cells) + "\n"


class TestNetLoggerNative(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "_netlogger-checkins").mkdir()
        (self.root / "assets/img").mkdir(parents=True)

    def create_log(self, name, content):
        (self.root / "_netlogger-checkins" / name).write_bytes(content.encode("utf-8"))

    def create_net(self, date):
        (self.root / "assets/img" / ("net-" + date + ".png")).touch()

    def test_filename_conversion_utc_to_eastern_standard_time(self):
        t = native.parse_filename("CheckInsOn01-14-2026-00-04.log")
        self.assertEqual((t["date"], t["local_time"], t["weekday"]),
                         ("2026-01-13", "19:04", "Tue"))

    def test_filename_conversion_daylight_time(self):
        t = native.parse_filename("CheckInsOn10-21-2026-00-07.log")
        self.assertEqual((t["date"],t["local_time"]), ("2026-10-20","20:07"))

    def test_monday_timestamp_is_not_tuesday(self):
        t = native.parse_filename("CheckInsOn01-13-2026-01-04.log")
        self.assertEqual(t["date"], "2026-01-12")
        self.assertEqual(t["weekday"], "Mon")

    def test_pipe_columns_and_private_fields_are_excluded(self):
        rows, errors = native.parse_log(
            (log_row(1) + log_row(2, "KB2SUL", "Maurice Naraine") +
             "3| | | | | | | | | | | | | | | | | | |\n").encode(), "log")
        self.assertEqual(len(rows), 2)
        self.assertFalse(errors)
        self.assertEqual(rows[0]["number"], 1)
        self.assertEqual(rows[0]["callsign"], "KC2NJ")
        self.assertEqual(rows[0]["remarks"], "RF - TXA")
        self.assertEqual(rows[0]["county"], "Essex")
        self.assertEqual(rows[0]["country"], "United States")
        self.assertFalse("PRIVATE" in json.dumps(rows))
        self.assertFalse("address" in json.dumps(rows).lower())
        self.assertFalse("zipcode" in json.dumps(rows).lower())

    def test_two_snapshots_choose_largest_roster_not_earliest(self):
        self.create_net("2026-05-12")
        self.create_log("CheckInsOn05-12-2026-23-13.log", log_row(1))
        self.create_log("CheckInsOn05-13-2026-00-08.log",
                        log_row(1) + log_row(2,"KB2SUL","Maurice Naraine"))
        payload,audit = native.build(self.root)
        self.assertEqual(len(payload["nets"]), 1)
        self.assertEqual(len(payload["checkins"]), 2)
        self.assertEqual(len(audit["duplicate_exports"]), 1)
        self.assertEqual(payload["nets"][0]["source_file"],
                         "CheckInsOn05-13-2026-00-08.log")

    def test_out_of_schedule_file_is_quarantined(self):
        self.create_net("2026-06-09")
        self.create_log("CheckInsOn06-09-2026-00-04.log", log_row(1))
        self.create_log("CheckInsOn06-09-2026-23-22.log", log_row(1))
        p,a = native.build(self.root)
        self.assertEqual(len(p["nets"]), 1)
        self.assertEqual(p["nets"][0]["date"], "2026-06-09")
        self.assertEqual(len(a["quarantined_exports"]), 1)
        self.assertEqual(a["quarantined_exports"][0]["timestamp_date_et"], "2026-06-08")

    def test_zip_archives_preserve_source_identifier(self):
        self.create_net("2026-01-13")
        src = self.root / "_netlogger-checkins/laptop-two.zip"
        with ZipFile(src, "w") as z:
            z.writestr("CheckIns/CheckInsOn01-14-2026-00-04.log", log_row(1))
        p,a = native.build(self.root)
        self.assertEqual(len(p["checkins"]), 1)
        self.assertEqual(a["source_file_count"], 1)
        self.assertIn("laptop-two.zip::CheckIns/",p["nets"][0]["source_file"])


    def test_tuesday_native_log_is_valid_even_without_png(self):
        self.create_log("CheckInsOn01-14-2026-00-04.log", log_row(1))
        payload, audit = native.build(self.root)
        self.assertEqual(payload["nets"][0]["date"], "2026-01-13")
        self.assertEqual(audit["native_dates_without_screenshot"], ["2026-01-13"])
        self.assertEqual(audit["screenshot_net_dates"], 0)

    def test_early_snapshot_is_flagged_not_suppressed(self):
        self.create_net("2026-05-12")
        self.create_log("CheckInsOn05-12-2026-23-13.log", log_row(1))
        payload, audit = native.build(self.root)
        self.assertEqual(payload["nets"][0]["checkin_count"], 1)
        self.assertTrue(payload["nets"][0]["possibly_early_snapshot"])
        self.assertEqual(audit["possibly_early_snapshots"][0]["source_time_et"], "19:13")

    def test_missing_dates_are_preliminary_and_all_native(self):
        self.create_net("2026-01-13")
        self.create_net("2026-01-20")
        self.create_log("CheckInsOn01-14-2026-00-04.log", log_row(1))
        p,a = native.build(self.root)
        self.assertEqual(a["missing_native_dates"], ["2026-01-20"])
        self.assertEqual(p["batch_status"], "1 of 3 (partial)")
        self.assertTrue(all("PRIVATE" not in json.dumps(row) for row in p["checkins"]))


if __name__ == "__main__":
    unittest.main()
