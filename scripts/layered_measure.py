#!/usr/bin/env python3
"""Generic deterministic measurement tool for layered v3 composition.

Usage:
    python scripts/layered_measure.py 5

The tool never OCRs text and never approves semantic crops. It verifies the canonical
raster SHA from pages/NN.yaml, measures coarse visually-dense components, and exports
an overlay, contact sheet and JSON report for human review.
"""
from pathlib import Path
import argparse
import hashlib
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw
import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measure_candidates(img):
    rgb = np.asarray(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 9)
    fg = (blur < 225).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    dense = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel, iterations=2)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(dense, 8)
    H, W = gray.shape
    candidates = []
    for i in range(1, n):
        x, y, w, h, area = map(int, stats[i])
        frac = area / (W * H)
        if area < 0.004 * W * H:
            continue
        if w < 0.08 * W or h < 0.04 * H:
            continue
        if w > 0.94 * W and h > 0.94 * H:
            continue
        candidates.append({
            "candidate": len(candidates) + 1,
            "x": x, "y": y, "w": w, "h": h,
            "area": area,
            "area_fraction": round(frac, 6),
        })
    candidates.sort(key=lambda b: (b["y"], b["x"]))
    for idx, b in enumerate(candidates, 1):
        b["candidate"] = idx
    return candidates


def render_overlay(img, candidates, path):
    out = img.copy().convert("RGB")
    draw = ImageDraw.Draw(out)
    line = max(2, img.width // 700)
    for b in candidates:
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        draw.rectangle((x, y, x + w, y + h), outline=(255, 0, 0), width=line)
        draw.text((x + 4, y + 4), str(b["candidate"]), fill=(255, 0, 0))
    out.save(path, quality=92)


def render_contact_sheet(img, candidates, path):
    if not candidates:
        Image.new("RGB", (900, 300), "white").save(path, quality=92)
        return
    thumbs = []
    for b in candidates:
        crop = img.crop((b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]))
        crop.thumbnail((420, 300))
        thumbs.append((b["candidate"], crop.copy()))
    cols, cell_w, cell_h = 3, 450, 340
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    for j, (idx, thumb) in enumerate(thumbs):
        x = (j % cols) * cell_w
        y = (j // cols) * cell_h
        sheet.paste(thumb, (x + 10, y + 25))
        draw.text((x + 10, y + 5), f"candidate {idx}", fill="black")
    sheet.save(path, quality=92)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("page", type=int)
    args = parser.parse_args()
    page = args.page
    if not 1 <= page <= 16:
        raise SystemExit("page must be 1..16")

    spec_path = ROOT / f"pages/{page:02d}.yaml"
    spec = yaml.safe_load(spec_path.read_text())
    src = ROOT / spec["visual_reference"]
    expected_sha = spec["visual_reference_sha256"]
    actual_sha = sha256(src)
    if actual_sha != expected_sha:
        raise SystemExit(f"page {page:02d} SHA mismatch: {actual_sha} != {expected_sha}")

    img = Image.open(src).convert("RGB")
    candidates = measure_candidates(img)
    out = ROOT / f"dist/layered-measure/page-{page:02d}"
    out.mkdir(parents=True, exist_ok=True)

    overlay = out / "candidate-overlay.jpg"
    contact = out / "candidate-contact-sheet.jpg"
    render_overlay(img, candidates, overlay)
    render_contact_sheet(img, candidates, contact)

    qr = spec.get("qr", {})
    qr_entries = qr.get("qrs", []) if qr.get("present") else []
    report = {
        "page": page,
        "title": spec.get("title"),
        "type": spec.get("type"),
        "source": str(src.relative_to(ROOT)),
        "source_sha256": actual_sha,
        "width_px": img.width,
        "height_px": img.height,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "qr": [{
            "id": q.get("id"),
            "payload": q.get("payload"),
            "placement_reference_px": q.get("placement_px"),
        } for q in qr_entries],
        "status": "MEASURED_REVIEW_REQUIRED",
        "warning": "Candidates are diagnostics only; no semantic crop is approved automatically.",
    }
    (out / "measurement.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "page": page,
        "title": spec.get("title"),
        "size": f"{img.width}x{img.height}",
        "sha256": actual_sha,
        "candidates": len(candidates),
        "qr_count": len(qr_entries),
        "status": report["status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
