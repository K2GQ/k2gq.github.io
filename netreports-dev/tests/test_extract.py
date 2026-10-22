"""Regression tests for netreports-dev's reviewed-row overlay.

These exercise the real main()/argparse/JSON logic. OCR and image processing
are stubbed so subset behavior can be verified quickly and deterministically.
"""
import importlib.util
import json
from pathlib import Path
from shutil import copyfile
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
EXTRACT_PATH = REPO_ROOT / "netreports-dev" / "scripts" / "extract.py"
REVIEWED_PATH = REPO_ROOT / "netreports-dev" / "data" / "reviewed.json"

spec = importlib.util.spec_from_file_location("netreports_dev_extract", EXTRACT_PATH)
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


class TestSubsetReviewedOverlay(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data_dir = self.root / "netreports-dev" / "data"
        self.data_dir.mkdir(parents=True)
        copyfile(REVIEWED_PATH, self.data_dir / "reviewed.json")

    @staticmethod
    def mock_prepare(root, days):
        # Real prepare() is replaced, but returns the same bounds tuple shape.
        return None, [(day, 0, 1, object()) for day in days]

    @staticmethod
    def mock_lines(sheet, bounds):
        return {day: [{"text": "sample OCR"}] for day, _, _, _ in bounds}

    @staticmethod
    def mock_parse_day(day, lines, original):
        # One raw OCR candidate per date, deliberately overridden for reviewed dates.
        return [
            {
                "date": day,
                "number": 1,
                "callsign": "W1RAW",
                "reviewed": False,
                "needs_review": True,
                "raw_text": "1 W1RAW",
                "confidence": 25,
            }
        ], {
            "date": day,
            "image": f"/assets/img/net-{day}.png",
            "ocr_rows": 1,
            "detected_columns": ["number", "callsign"],
            "borders": [],
            "low_confidence_rows": 1,
            "sample_only": True,
        }

    def run_extractor(self, dates=None):
        args = ["extract.py", "--root", str(self.root)]
        if dates is not None:
            args += ["--dates", *dates]
        with (
            patch.object(extract, "prepare", side_effect=self.mock_prepare),
            patch.object(extract, "ocr_lines", side_effect=self.mock_lines),
            patch.object(extract, "parse_day", side_effect=self.mock_parse_day),
            patch.object(sys, "argv", args),
        ):
            extract.main()
        json_file = self.data_dir / "preview.json"
        diagnostics = self.data_dir / "ocr-review.txt"
        self.assertTrue(json_file.is_file(), "JSON output must be written")
        self.assertTrue(diagnostics.is_file(), "OCR diagnostic output must be written")
        return json.loads(json_file.read_text(encoding="utf-8")), diagnostics.read_text()

    def test_one_reviewed_date_does_not_lookup_other_dates(self):
        """Regression: --dates 2026-10-20 cannot raise StopIteration."""
        data, diagnostics = self.run_extractor(["2026-10-20"])
        self.assertEqual([n["date"] for n in data["nets"]], ["2026-10-20"])
        self.assertEqual(data["reviewed_rows"], 13)
        self.assertEqual(len(data["checkins"]), 13)
        self.assertEqual(data["nets"][0]["ocr_candidate_rows"], 1)
        self.assertTrue(all(row["date"] == "2026-10-20" and row["reviewed"]
                            for row in data["checkins"]))
        self.assertIn("2026-10-20", diagnostics)
        self.assertNotIn("2023-09-06", diagnostics)

    def test_two_reviewed_dates_only(self):
        data, _ = self.run_extractor(["2025-06-10", "2023-09-06"])
        self.assertEqual([n["date"] for n in data["nets"]],
                         ["2023-09-06", "2025-06-10"])
        self.assertEqual(data["reviewed_rows"], 6 + 8)
        self.assertEqual(len(data["checkins"]), 14)
        self.assertEqual({row["date"] for row in data["checkins"]},
                         {"2023-09-06", "2025-06-10"})

    def test_default_sample_still_imports_all_reviewed_rows(self):
        data, _ = self.run_extractor()
        self.assertEqual(len(data["nets"]), 4)
        self.assertEqual(len(data["checkins"]), 38)
        self.assertEqual(data["reviewed_rows"], 38)
        self.assertEqual({n["date"]: n["ocr_rows"] for n in data["nets"]}, {
            "2023-09-06": 6,
            "2024-08-20": 11,
            "2025-06-10": 8,
            "2026-10-20": 13,
        })

    def test_mixed_reviewed_and_new_ocr_date(self):
        data, _ = self.run_extractor(["2026-10-13", "2026-10-20"])
        self.assertEqual([n["date"] for n in data["nets"]],
                         ["2026-10-13", "2026-10-20"])
        self.assertEqual(data["reviewed_rows"], 13)
        self.assertEqual(len(data["checkins"]), 14)
        raw = [r for r in data["checkins"] if r["date"] == "2026-10-13"]
        self.assertEqual(len(raw), 1)
        self.assertFalse(raw[0]["reviewed"])
        self.assertEqual(raw[0]["review_status"], "OCR only — not reviewed")
        self.assertEqual(data["nets"][0]["ocr_rows"], 1)
        self.assertEqual(data["nets"][1]["ocr_rows"], 13)

    def test_missing_reviewed_file_uses_raw_ocr(self):
        (self.data_dir / "reviewed.json").unlink()
        data, _ = self.run_extractor(["2026-10-20"])
        self.assertEqual(data["reviewed_rows"], 0)
        self.assertEqual(len(data["checkins"]), 1)
        self.assertEqual(data["checkins"][0]["callsign"], "W1RAW")
        self.assertEqual(data["checkins"][0]["review_status"],
                         "OCR only — not reviewed")


if __name__ == "__main__":
    unittest.main()
