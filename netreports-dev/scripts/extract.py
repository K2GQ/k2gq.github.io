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
        scaled = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
        scaled = ImageOps.autocontrast(scaled, cutoff=1)
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

def parse_day(day, lines):
    headers = find_header(lines)
    entries = []
    rejected = []
    for ln in lines:
        text = ln["text"].upper().replace("|", " ")
        matches = CALL.findall(text)
        if not matches:
            continue
        # A status / heading / software title may contain a callsign; keep it
        # reviewable but avoid silently adding it to the participation totals.
        cs = matches[0]
        cswords = [w for w in ln["words"] if cs in w["text"].upper()]
        if not cswords:
            rejected.append(ln["text"])
            continue
        callsign_word = cswords[0]
        confidence = min((w["confidence"] for w in ln["words"]), default=0)
        raw_fields = {}
        if headers:
            for word in ln["words"]:
                if word is callsign_word:
                    continue
                key = headers[0][0]
                for col, x in headers:
                    if word["x"] >= x - 16:
                        key = col
                raw_fields.setdefault(key, []).append(word["text"])
        fields = {k: " ".join(raw_fields.get(k, [])).strip() for k in WANTED if k != "callsign"}
        # Duplicates within the same screenshot need manual inspection.
        entries.append({
            "date": day, "callsign": cs,
            "number": int(ln["words"][0]["text"]) if ln["words"][0]["text"].isdigit() else None,
            "status": fields.get("status", ""), "name": fields.get("name", ""),
            "city": fields.get("city", ""), "county": fields.get("county", ""),
            "state": fields.get("state", ""), "country": fields.get("country", ""),
            "remarks": fields.get("remarks", ""),
            "raw_text": ln["text"], "confidence": confidence,
            "reviewed": False
        })
    seen = Counter(e["callsign"] for e in entries)
    for entry in entries:
        # Initial OCR is not validated. Highlight very weak / duplicate rows.
        entry["needs_review"] = entry["confidence"] < 65 or seen[entry["callsign"]] > 1 or not headers
    return entries, {
        "date": day, "image": "/assets/img/net-" + day + ".png",
        "ocr_rows": len(entries), "detected_columns": [k for k, _ in headers],
        "low_confidence_rows": sum(e["needs_review"] for e in entries),
        "rejected_lines": rejected[:20],
        "sample_only": True
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
        entries, net = parse_day(day, lines[day])
        nets.append(net)
        records.extend(entries)
        output.append("=== " + day + " ===")
        output.append("Detected columns: " + ", ".join(net["detected_columns"]))
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
