#!/usr/bin/env python3
"""Second-generation NetLogger image importer: cell segmentation and OCR.

This extractor is intentionally independent from the live/legacy importer.
It preserves OCR results, their row positions, source images, and uncertainty.
Recurrent participants are offered as suggestions, NEVER silently substituted.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import json
import re

import cv2
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output

from extract import find_borders

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ("2023-09-06", "2023-11-07", "2024-04-02", "2024-08-20",
          "2024-12-24", "2025-06-10", "2025-12-09", "2026-03-24",
          "2026-07-14", "2026-10-20")
COLUMNS = ("number", "callsign", "status", "name", "city", "county",
           "state", "country", "remarks")
CALL = re.compile(r"^(?:[AKNW][A-Z]?[0-9][A-Z]{1,4}|[A-Z]{2,3}[0-9][A-Z]{1,4})(?:/[A-Z0-9]{1,5})?$")
WHITELIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/"


def detect_rows(rgb):
    """Detect full-width horizontal separators, retaining empty OCR rows."""
    h, w, _ = rgb.shape
    if h < 95:
        raise ValueError("Image too short to contain table")
    # Real NetLogger horizontal rules and color-row transitions affect almost
    # every pixel across a line; actual text glyphs do not.
    a = rgb.astype(np.int16)
    diffs = np.max(np.abs(a[1:] - a[:-1]), axis=2)
    left, right = max(40, int(.06 * w)), max(50, w - 10)
    scores = np.mean(diffs[:, left:right] >= 25, axis=1)
    hits = np.where(scores > .57)[0] + 1
    clusters = []
    for y in hits:
        if not clusters or y > clusters[-1][-1] + 2:
            clusters.append([int(y)])
        else:
            clusters[-1].append(int(y))
    peaks = [max(group, key=lambda y: scores[y - 1]) for group in clusters]
    # Bottom of the header lies near pixel 65-75 in all examined screenshots.
    headings = [y for y in peaks if 54 <= y <= 95]
    header_end = min(headings, key=lambda y: abs(y - 69)) if headings else 69
    raw_bounds = [header_end] + [y for y in peaks if y > header_end + 12]
    # Use stable row pitch to detect any missing separators (e.g. repeated
    # adjacent highlights). Reject tiny spurious peaks.
    gaps = np.diff(raw_bounds)
    normal = [int(g) for g in gaps if 17 <= g <= 38]
    pitch = int(np.median(normal)) if normal else 25
    edges = [int(header_end)]
    for boundary in raw_bounds[1:]:
        distance = int(boundary) - edges[-1]
        if distance < max(14, pitch * .55):
            continue
        n = max(1, round(distance / pitch))
        if n > 1 and distance / n >= 16 and distance / n <= 40:
            edges.extend(round(edges[-1] + (distance / n) * i) for i in range(1, n + 1))
        else:
            edges.append(int(boundary))
    if h - edges[-1] >= max(16, pitch * .63):
        edges.append(h - 1)
    # The actual outermost bottom rule may be at h-1; do not invent 2px rows.
    edges = sorted(set(int(x) for x in edges if 0 <= x < h))
    spans = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)
             if 15 <= edges[i + 1] - edges[i] <= 46]
    if not spans:
        raise ValueError("No NetLogger rows detected")
    return spans, {"header_bottom": header_end, "pitch": pitch,
                   "raw_peaks": len(peaks), "detected_rows": len(spans)}


def normalize_cell(rgb, x1, x2, y1, y2, scale=3):
    """Convert colored NetLogger cell foreground to dark text on white."""
    crop = rgb[max(0, y1 + 2):max(0, y2 - 1),
               max(0, x1 + 3):max(0, x2 - 2)]
    if crop.size == 0:
        return np.full((60, 60), 255, dtype=np.uint8)
    # The background color is uniform within each cell, even for magenta,
    # aqua, and dark-gray highlighted rows. Recover glyphs by RGB distance.
    background = np.median(crop.reshape(-1, 3), axis=0)
    maxdiff = np.max(abs(crop.astype(np.float32) - background), axis=2)
    # Slightly stronger threshold reduces antialiased noise on colored rows.
    mask = np.uint8(maxdiff >= 44) * 255
    # The 1px gridlines are removed by the crop inset. Tiny isolated specks
    # shouldn't be OCR text; small punctuation inside names is retained.
    comps, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    for idx in range(1, comps):
        if stats[idx, cv2.CC_STAT_AREA] <= 1:
            mask[labels == idx] = 0
    inverted = 255 - mask
    up = cv2.resize(inverted, None, fx=scale, fy=scale,
                    interpolation=cv2.INTER_NEAREST)
    return cv2.copyMakeBorder(up, 9, 9, 9, 9,
                              cv2.BORDER_CONSTANT, value=255)


def read_sheet(cell_rows):
    """One Tesseract call for each reconstructed screenshot."""
    # OCR a clean grayscale image with individual cells aligned to known
    # coordinates and separated by gutters: avoids column-shift artifacts.
    widths = [max(cell.shape[1] for cell in row[i:i+1])
              for i in range(9) for row in cell_rows]
    widths = [max(cell_rows[r][c].shape[1] for r in range(len(cell_rows)))
              for c in range(9)]
    yheight = max(cell.shape[0] for row in cell_rows for cell in row) + 9
    xs = [8]
    for w in widths:
        xs.append(xs[-1] + w + 20)
    height = yheight * len(cell_rows) + 12
    sheet = np.full((height, xs[-1] + 10), 255, np.uint8)
    for rowidx, row in enumerate(cell_rows):
        for colidx, cell in enumerate(row):
            top = 8 + rowidx * yheight
            sheet[top:top+cell.shape[0], xs[colidx]:xs[colidx]+cell.shape[1]] = cell
    data = pytesseract.image_to_data(sheet, config="--psm 6",
                                     output_type=Output.DICT)
    items = defaultdict(list)
    confs = defaultdict(list)
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        center_x = data["left"][i] + data["width"][i] / 2
        center_y = data["top"][i] + data["height"][i] / 2
        rowidx = int((center_y - 8) // yheight)
        if not (0 <= rowidx < len(cell_rows)):
            continue
        colidx = next((j for j in range(9)
                       if xs[j] - 4 <= center_x < xs[j + 1] - 5), None)
        if colidx is None:
            continue
        items[rowidx, colidx].append((data["left"][i], text))
        confs[rowidx, colidx].append(max(0., float(data["conf"][i])))
    records = []
    for i, cells in enumerate(cell_rows):
        row = {}
        for j, col in enumerate(COLUMNS):
            row[col] = " ".join(t for x, t in sorted(items.get((i, j), [])))
        row["confidence"] = round(np.mean(confs.get((i, 1), [0])), 1)
        row["name_confidence"] = round(np.mean(confs.get((i, 3), [0])), 1)
        records.append(row)
    return records


def recognize_callsign(cell):
    """Independent call-only read with a restricted character vocabulary."""
    guess = pytesseract.image_to_string(
        cell, config=f"--psm 7 -c tessedit_char_whitelist={WHITELIST}")
    return re.sub(r"[^A-Z0-9/]", "", guess.upper())


def extract_image(path, *, call_reread=True):
    rgb = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    if rgb is None:
        raise ValueError(f"Unreadable image {path}")
    image = Image.fromarray(rgb)
    borders = find_borders(image)
    if len(borders) != 10:
        raise ValueError("Expected nine table columns")
    spans, geometry = detect_rows(rgb)
    cell_rows = [[normalize_cell(rgb, borders[j], borders[j+1], top, bottom)
                  for j in range(9)] for top, bottom in spans]
    records = read_sheet(cell_rows)
    day = path.name[4:14]
    for i, row in enumerate(records):
        raw = re.sub(r"[^A-Z0-9/]", "", row["callsign"].upper())
        alternative = recognize_callsign(cell_rows[i][1]) if call_reread else ""
        candidates = [c for c in (raw, alternative) if CALL.fullmatch(c)]
        # If two independent OCR paths disagree, do not silently choose one.
        if len(set(candidates)) == 1:
            selected = candidates[0]
        elif candidates:
            selected = candidates[0]
        else:
            selected = raw or alternative
        n = re.search(r"\d+", row.get("number", ""))
        row["number"] = int(n.group()) if n else i + 1
        row["date"] = day
        row["callsign"] = selected
        row["raw_callsign"] = raw
        row["alternate_callsign"] = alternative
        row["image_row"] = i + 1
        row["source_image"] = f"/assets/img/{path.name}"
        row["reviewed"] = False
        row["uncertain"] = (not CALL.fullmatch(selected) or
                            (len(set(candidates)) > 1) or
                            row["confidence"] < 65 or
                            row["number"] != i + 1 or
                            not row["name"])
        row["needs_review"] = row["uncertain"]
        row["review_status"] = "Unreviewed cell OCR"
    return records, geometry


def key_name(s):
    return " ".join(re.sub("[^A-Z ]", "", str(s or "").upper()).split())


def suggest_participants(records, reference):
    """Use stable operator names to suggest, never auto-apply, callsigns."""
    frequency = defaultdict(Counter)
    anchor = defaultdict(Counter)
    for item in records:
        name = key_name(item.get("name"))
        call = str(item.get("callsign", "")).upper()
        if len(name) >= 7 and CALL.fullmatch(call):
            frequency[name][call] += 1
    for item in reference:
        name = key_name(item.get("name"))
        call = str(item.get("callsign", "")).upper()
        if len(name) >= 7 and CALL.fullmatch(call):
            anchor[name][call] += 1
    suggestions = []
    for item in records:
        name = key_name(item.get("name"))
        own = item.get("callsign", "")
        anchors = anchor.get(name) or frequency.get(name, Counter())
        if not anchors:
            continue
        candidate, occurrences = anchors.most_common(1)[0]
        total = sum(anchors.values())
        # high-frequency identity: avoid suggestions for low-evidence names.
        if own != candidate and occurrences >= 3 and occurrences / total >= .70:
            # Compare an OCR candidate to the recurrent identity. Only a
            # suggestion, even when names are an exact match.
            item["suggested_callsign"] = candidate
            item["suggestion_basis"] = f"Same normalized name; {occurrences}/{total} observations of {candidate}"
            suggestions.append({"date": item["date"], "image_row": item["image_row"],
                                "extracted": own, "suggested": candidate,
                                "name": item.get("name")})
    return suggestions


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--dates", nargs="*", default=list(SAMPLE))
    p.add_argument("--out", default="netreports-dev/data/cell-ocr-poc.json")
    p.add_argument("--no-call-reread", action="store_true")
    args = p.parse_args(argv)
    root = args.root.resolve()
    day_list = sorted(set(args.dates))
    if not day_list:
        p.error("At least one date is required")
    all_rows, nets = [], []
    for day in day_list:
        path = root / "assets/img" / f"net-{day}.png"
        if not path.is_file():
            raise FileNotFoundError(path)
        rows, geo = extract_image(path, call_reread=not args.no_call_reread)
        all_rows.extend(rows)
        nets.append({"date": day, "image": f"/assets/img/net-{day}.png",
                     "rows": len(rows), "geometry": geo})
        print(day, len(rows), "rows,", sum(not x["uncertain"] for x in rows),
              "unflagged", flush=True)
    references = json.loads((root / "netreports-dev/data/reviewed.json").read_text(encoding="utf-8"))["rows"]
    suggestions = suggest_participants(all_rows, references)
    by_day_row = {(r["date"], r["number"]): r for r in references}
    compared, correct_call, correct_name = 0, 0, 0
    per_day = defaultdict(lambda: {"reference": 0, "recognized": 0,
                                   "callsign_matches": 0, "name_matches": 0})
    for n in nets:
        per_day[n["date"]]["recognized"] = n["rows"]
    for r in references:
        if r["date"] in day_list:
            per_day[r["date"]]["reference"] += 1
    for row in all_rows:
        ref = by_day_row.get((row["date"], row["image_row"]))
        if ref:
            compared += 1
            if row["callsign"] == ref["callsign"]:
                correct_call += 1
                per_day[row["date"]]["callsign_matches"] += 1
            if key_name(row.get("name")) == key_name(ref.get("name")):
                correct_name += 1
                per_day[row["date"]]["name_matches"] += 1
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "version": "cell-ocr-v2-experimental",
        "test_only": True, "sample_dates": day_list,
        "nets": nets, "checkins": all_rows,
        "identity_suggestions": suggestions,
        "evaluation": {
            "reviewed_reference_rows": sum(v["reference"] for v in per_day.values()),
            "compared_rows": compared,
            "correct_raw_callsign": correct_call,
            "correct_raw_name": correct_name,
            "per_date": dict(per_day),
            "method": "Exact callsign/name compared by physical row position; suggestions not applied."
        },
        "limitations": "All new OCR rows are unreviewed. Participant suggestions are hints, never verified substitutions."
    }
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print("Total:",len(all_rows),"exact callsigns:",correct_call,"/",compared,
          "exact names:",correct_name,"/",compared,"suggestions:",len(suggestions))


if __name__ == "__main__":
    main()
