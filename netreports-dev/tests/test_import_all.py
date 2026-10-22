"""Fast full-archive discovery and batching tests (no OCR invocation)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "netreports_full_import", BASE / "netreports-dev/scripts/import_all.py")
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class TestFullImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "assets/img").mkdir(parents=True)
        self.days = ["2023-09-06", "2024-08-20", "2026-10-20"]
        for day in self.days:
            (self.root / "assets/img" / f"net-{day}.png").touch()
        for bad in ["netlogger.jpg", "net-2026-14-99.png", "net-old.png"]:
            (self.root / "assets/img" / bad).touch()

    def test_dated_images_only(self):
        self.assertEqual(app.discover_dates(self.root), self.days)

    def test_chunking(self):
        self.assertEqual(list(app.chunks(self.days, 2)),
                         [self.days[:2], self.days[2:]])

    def test_archive_is_batched_and_outputs_qa(self):
        calls = []
        def fake_run(cmd, check, timeout):
            self.assertTrue(check)
            self.assertEqual(timeout, 240)
            i = cmd.index("--dates")
            j = cmd.index("--out")
            group = cmd[i+1:j]
            calls.append(group)
            out = Path(cmd[j+1])
            log = Path(cmd[cmd.index("--text")+1])
            data = {
                "nets": [{"date":d, "image":f"/assets/img/net-{d}.png",
                          "ocr_rows":1, "reviewed":False} for d in group],
                "checkins": [{
                    "date":d, "number":1, "callsign":"KC2NJ",
                    "name":"Mike", "reviewed":False, "needs_review":True
                } for d in group]
            }
            out.write_text(json.dumps(data), encoding="utf-8")
            log.write_text("OCR stub\n", encoding="utf-8")
        with patch.object(app.subprocess, "run", side_effect=fake_run):
            app.main(["--root", str(self.root), "--batch-size", "2"])
        self.assertEqual(calls, [self.days[:2], self.days[2:]])
        dest = self.root / "netreports-dev/data"
        p = json.loads((dest / "preview.json").read_text())
        a = json.loads((dest / "import-audit.json").read_text())
        self.assertEqual(len(p["nets"]), 3)
        self.assertEqual(len(p["checkins"]), 3)
        self.assertFalse(p["sample_only"])
        self.assertEqual(a["source_image_count"], 3)
        self.assertEqual(a["nets_flagged_for_review"], 3)
        self.assertEqual(len(a["findings"]), 3)

    def test_date_subset_only(self):
        def fake_merge(root, days, batch_size, runner=None):
            return ([{"date":d,"image":f"/assets/img/net-{d}.png",
                      "ocr_rows":0,"reviewed":False} for d in days], [], "")
        with patch.object(app, "merge_batches", side_effect=fake_merge) as call:
            app.main(["--root", str(self.root), "--dates", "2026-10-20"])
        self.assertEqual(call.call_args.args[1], ["2026-10-20"])
        obj = json.loads((self.root/"netreports-dev/data/import-audit.json").read_text())
        self.assertEqual(obj["nets_with_no_recognized_rows"], ["2026-10-20"])

    def test_rejects_unknown_day(self):
        with self.assertRaises(SystemExit):
            app.main(["--root", str(self.root), "--dates", "2023-09-01"])


if __name__ == "__main__":
    unittest.main()
