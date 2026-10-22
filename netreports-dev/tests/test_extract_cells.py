"""Unit tests for second-generation NetLogger cell OCR components."""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "netreports-dev/scripts"))
SPEC = importlib.util.spec_from_file_location("cell_ocr_v2", ROOT / "netreports-dev/scripts/extract_cells.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestCellOCRV2(unittest.TestCase):
    def test_background_invariant_white_letters_on_magenta(self):
        image = np.zeros((30, 140, 3), np.uint8)
        image[:] = [255, 0, 255]
        cv2.putText(image, "KC2NJ", (4, 24), cv2.FONT_HERSHEY_SIMPLEX, .65, (255,255,255), 2)
        cell = module.normalize_cell(image, 0, 139, 0, 29)
        self.assertEqual(cell.ndim, 2)
        self.assertGreater(int(np.count_nonzero(cell < 50)), 50)

    def test_background_invariant_dark_letters_on_aqua(self):
        image = np.zeros((30, 140, 3), np.uint8)
        image[:] = [45,255,255]
        cv2.putText(image, "KB2SUL", (4, 24), cv2.FONT_HERSHEY_SIMPLEX, .65, (0,0,0), 2)
        cell = module.normalize_cell(image, 0, 139, 0, 29)
        self.assertGreater(int(np.count_nonzero(cell < 50)), 50)

    def test_geometry_detects_several_colored_rows(self):
        image = np.zeros((220, 600, 3), np.uint8)
        image[:] = [238,238,238]
        backgrounds = [
            (255,255,255), (255, 0, 255), (45,255,255),
            (128,128,128), (255,255,255), (45,255,255)]
        for i,color in enumerate(backgrounds):
            top = 68+25*i
            image[top:top+25,:] = color
            image[top,:] = [170,170,170]
        image[68+6*25,:] = [170,170,170]
        spans, geo = module.detect_rows(image)
        self.assertGreaterEqual(len(spans), 5)
        self.assertLessEqual(len(spans), 7)

    def test_same_name_variants_only_suggested(self):
        reviewed = [{"name":"Mike Abbey", "callsign":"KC2NJ"}]*4
        new = [
            {"date":"2026-10-20", "image_row":1, "name":"Mike Abbey",
             "callsign":"KC2N"},
            {"date":"2026-10-20", "image_row":2, "name":"Other Operator",
             "callsign":"K2XYZ"}
        ]
        original = [r["callsign"] for r in new]
        suggestions = module.suggest_participants(new, reviewed)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["suggested"], "KC2NJ")
        self.assertEqual([r["callsign"] for r in new], original)


if __name__ == "__main__":
    unittest.main()
