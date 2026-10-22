#!/usr/bin/env python3
"""K2GQ NetLogger screenshot OCR proof of concept.

A single Tesseract invocation processes a contact sheet of selected screenshots.
No unvalidated OCR output is treated as a verified check-in. Review source PNGs.
"""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageOps, ImageDraw
import pytesseract
from pytesseract import Output

SAMPLE = ("2023-09-06", "2024-08-20", "2025-06-10", "2026-10-20")
CALL = re.compile(r"(?<![A-Z0-9])(?:[AKNW][A-Z]?[0-9][A-Z]{1,4}|[A-Z]{2,3}[0-9][A-Z]{1,4})(?:/[A-Z0-9]{1,5})?(?![A-Z0-9])")
HEADER = {"call": "callsign", "callsign": "callsign", "status": "status",
          "name": "name", "first": "name", "city": "city", "county": "county",
          "state": "state", "country": "country", "remarks": "remarks",
          "comments": "remarks", "comment": "remarks", "notes": "remarks"}
WANTED = ["callsign", "status", "name", "city", "county", "state", "country", "remarks"]


def preprocess(original):
    """Normalize dark/white text on NetLogger's various highlight colors."""
    gray = ImageOps.grayscale(original)
    w, h = gray.size
    out = Image.new("L", (w, h), 255)
    source, target = gray.load(), out.load()
    for y in range(h):
        # Text covers relatively little horizontal space; median gives row fill.
        values = sorted(source[x, y] for x in range(0, w, max(1, w // 100)))
        bg = values[len(values)//2]
        # Pink/gray highlighted rows have white text; aqua/white rows have dark text.
        invert = bg < 158
        for x in range(w):
            value = source[x, y]
            target[x, y] = (0 if value > bg + 35 else 255) if invert else (0 if value < bg - 35 else 255)
    return out.convert("RGB")

def find_borders(original):
    """Locate long vertical separators across the NetLogger header region."""
    gray = ImageOps.grayscale(original)
    w, h = gray.size
    pixels = gray.load()
    start, stop = 23, min(56, h - 1)
    scored = []
    for x in range(7, w-3):
        count = 0
        for y in range(start, stop):
            if abs(pixels[x,y]-pixels[x+2,y]) > 21 and abs(pixels[x,y]-pixels[x-2,y]) > 12:
                count += 1
        if count >= (stop-start) * .62:
            scored.append((x, count))
    clusters = []
    for x, n in scored:
        if clusters and x <= clusters[-1][-1][0]+3:
            clusters[-1].append((x,n))
        else:
            clusters.append([(x,n)])
    borders = [max(cluster, key=lambda x:x[1])[0] for cluster in clusters]
    # Edges are also legitimate separators but sometimes do not show two-sided contrast.
    if len(borders) >= 7:
        if borders[0] > 22:
            borders.insert(0, 10)
        if borders[-1] < w-7:
            borders.append(w-1)
    # Reuse the stable NetLogger geometry if edge detection is too noisy.
    if len(borders) != 10:
        ref = [11,35,180,234,423,566,674,762,904,1027] if w >= 980 else [12,35,161,240,422,573,670,724,867,919]
        borders = [min(w, round(x*w/ref[-1])) for x in ref]
    return borders

def fields_from_grid(line, borders):
    """Use real cell boundaries, not centered heading positions."""
    import bisect
    col_names = ["number", "callsign", "status", "name", "city", "county", "state", "country", "remarks"]
    cells = {k: [] for k in col_names}
    for word in line["words"]:
        x = (word["x"] - 8 + word["w"] / 2)/2
        index = bisect.bisect_right(borders, x) - 1
        if 0 <= index < len(col_names):
            cells[col_names[index]].append(word["text"])
    return {key:" ".join(values).strip() for key,values in cells.items()}

def image_for(root, day):
    return root / "assets" / "img" / ("net-" + day + ".png")

def prepare(root, days):
    """One combined OCR pass, while retaining absolute y-ranges per image."""
    pictures = []
    for day in days:
        path = image_for(root, day)
        if not path.exists():
            raise FileNotFoundError(path)
        img = Image.open(path).convert("RGB")
        # OCR can benefit from larger type; avoid destructive thresholding.
        scaled = preprocess(img).resize((img.width * 2, img.height * 2), Image.Resampling.NEAREST)
        pictures.append((day, img, scaled))
    width = max(im.width for _, _, im in pictures) + 16
    height = sum(im.height + 64 for _, _, im in pictures)
    sheet = Image.new("RGB", (width, height), "white")
    bounds = []
    y = 0
    for day, original, scaled in pictures:
        # Header drawn outside image OCR region.
        sheet.paste(scaled, (8, y + 32))
        bounds.append((day, y + 32, y + 32 + scaled.height, original))
        y += scaled.height + 64
    return sheet, bounds

def ocr_lines(sheet, bounds):
    result = pytesseract.image_to_data(sheet, output_type=Output.DICT, config="--psm 11")
    words = {day: [] for day, _, _, _ in bounds}
    for n, raw in enumerate(result["text"]):
        s = raw.strip()
        if not s:
            continue
        cy = result["top"][n] + result["height"][n] / 2
        for day, start, stop, _ in bounds:
            if start <= cy < stop:
                words[day].append({
                    "text": s, "x": result["left"][n],
                    "y": result["top"][n] - start, "w": result["width"][n],
                    "h": result["height"][n],
                    "confidence": max(0, round(float(result["conf"][n])))
                })
                break
    all_lines = {}
    for day, items in words.items():
        lines = []
        for word in sorted(items, key=lambda a: (a["y"] + a["h"]/2, a["x"])):
            mid = word["y"] + word["h"]/2
            candidate = min(lines, key=lambda a: abs(a["ymid"] - mid), default=None)
            if candidate and abs(candidate["ymid"] - mid) <= max(7, min(24, word["h"] * 0.55)):
                candidate["words"].append(word)
                candidate["ymid"] = (candidate["ymid"] * (len(candidate["words"]) - 1) + mid) / len(candidate["words"])
            else:
                lines.append({"ymid": mid, "words": [word]})
        for line in lines:
            line["words"].sort(key=lambda a: a["x"])
            line["text"] = " ".join(w["text"] for w in line["words"])
        all_lines[day] = sorted(lines, key=lambda a: a["ymid"])
    return all_lines

def find_header(lines):
    best = None
    for ln in lines:
        labels = []
        for w in ln["words"]:
            token = re.sub("[^a-z]", "", w["text"].lower())
            if token in HEADER:
                labels.append((HEADER[token], w["x"]))
        if not any(key == "callsign" for key, x in labels):
            continue
        if not best or len(labels) > len(best):
            best = labels
    if not best:
        return []
    unique = {}
    for key, x in best:
        unique[key] = min(x, unique.get(key, x))
    return sorted(unique.items(), key=lambda p: p[1])

def parse_day(day, lines, original):
    headers = find_header(lines)
    borders = find_borders(original)
    entries = []
    rejected = []
    for ln in lines:
        cells = fields_from_grid(ln, borders)
        raw_call = cells["callsign"].upper()
        matches = CALL.findall(raw_call)
        if not matches:
            continue
        cs = matches[0]
        # Do not mistake headings or loose text for complete rows.
        if "CHECK" in ln["text"].upper() and "INS" in ln["text"].upper():
            continue
        confidence = min((w["confidence"] for w in ln["words"]), default=0)
        num_match = re.search(r"\d+", cells["number"])
        row_num = int(num_match.group()) if num_match else None
        name = cells["name"]
        location = [cells["city"], cells["county"], cells["state"], cells["country"]]
        record = {
            "date": day, "callsign": cs, "number": row_num,
            "status": cells["status"], "name": name,
            "city": cells["city"], "county": cells["county"],
            "state": cells["state"], "country": cells["country"],
            "remarks": cells["remarks"],
            "raw_text": ln["text"], "confidence": confidence,
            "reviewed": False,
        }
        record["needs_review"] = (
            confidence < 65 or not row_num or
            not name or not cells["state"] or
            len(cs.split("/")[0].split(str(next((c for c in cs if c.isdigit()), "")))[-1]) > 3
        )
        entries.append(record)
    seen = Counter(e["callsign"] for e in entries)
    for entry in entries:
        if seen[entry["callsign"]] > 1:
            entry["needs_review"] = True
    return entries, {
        "date": day, "image": "/assets/img/net-" + day + ".png",
        "ocr_rows": len(entries), "detected_columns": list(fields_from_grid({"words":[]},borders).keys()),
        "borders": borders, "low_confidence_rows": sum(e["needs_review"] for e in entries),
        "rejected_lines": rejected[:20], "sample_only": True
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dates", nargs="*", default=list(SAMPLE))
    ap.add_argument("--out", default="netreports-dev/data/preview.json")
    ap.add_argument("--text", default="netreports-dev/data/ocr-review.txt")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    days = sorted(set(args.dates))
    sheet, bounds = prepare(root, days)
    lines = ocr_lines(sheet, bounds)
    records, nets = [], []
    output = []
    for day in days:
        entries, net = parse_day(day, lines[day], next(image for d, start, stop, image in bounds if d == day))
        nets.append(net)
        records.extend(entries)
        output.append("=== " + day + " ===")
        output.append("Detected columns: " + ", ".join(net["detected_columns"]))
        output.append("Detected image grid borders: " + repr(net["borders"]))
        output.extend(ln["text"] for ln in lines[day])
        output.append("")
    payload = {
        "kind": "ocr-proof-of-concept", "sample_only": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "reviewed": False,
        "limitations": "Unreviewed OCR. Callsign and column assignments are provisional. Statistics are sample-only.",
        "nets": nets, "checkins": records
    }
    outfile = root / args.out
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    txt = root / args.text
    txt.parent.mkdir(parents=True, exist_ok=True)
    txt.write_text("\n".join(output) + "\n", encoding="utf-8")
    print("OCR produced", len(records), "candidate rows across", len(nets), "images.")
    for n in nets:
        print(n["date"], "rows:", n["ocr_rows"], "columns:", n["detected_columns"])
    print("Unreviewed output is intentionally flagged. Source images remain authoritative.")

if __name__ == "__main__":
    main()
