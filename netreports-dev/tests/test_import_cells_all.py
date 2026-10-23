"""Full v2 importer integrity tests, using OCR-free image stubs."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "netreports-dev/scripts"))
spec = importlib.util.spec_from_file_location(
    "import_cells_v2", ROOT / "netreports-dev/scripts/import_cells_all.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestFullCellImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "assets" / "img").mkdir(parents=True)
        for day in ["2023-09-06", "2026-10-20"]:
            (self.root / "assets" / "img" / f"net-{day}.png").touch()

    @staticmethod
    def fake_extract(path):
        date = path.name[4:14]
        return [{
            "date": date, "image_row": 1, "number":1,
            "callsign": "KC2NJ", "raw_callsign": "KC2NJ",
            "alternate_callsign": "KC2NJ", "name":"Mike Abbey",
            "reviewed":False, "needs_review":False
        }], {"column_detection":{"method":"mock-grid"}}

    def test_select_two_dates_and_preserve_rows(self):
        nets, rows = m.import_archive(self.root, extractor=self.fake_extract)
        self.assertEqual(len(nets), 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["date"] for r in rows},
                         {"2023-09-06", "2026-10-20"})

    def test_select_date_subset(self):
        nets, rows = m.import_archive(self.root, ["2026-10-20"],
                                      extractor=self.fake_extract)
        self.assertEqual([n["date"] for n in nets], ["2026-10-20"])
        self.assertEqual(len(rows), 1)

    def test_audit_counts_remain_provisional(self):
        nets, rows = m.import_archive(self.root, extractor=self.fake_extract)
        refs = [{"date":"2023-09-06", "number":1,
                 "callsign":"KC2NJ", "name":"Mike Abbey"}]
        audit = m.build_audit(nets, rows, refs)
        self.assertEqual(audit["candidate_checkin_rows"], 2)
        self.assertEqual(audit["unverified_rows"], 2)
        self.assertEqual(audit["reference_callsign_matches"], 1)
        self.assertEqual(audit["matched_reference_rows"], 1)
        self.assertFalse(audit["nets_with_zero_rows"])


if __name__ == "__main__":
    unittest.main()
