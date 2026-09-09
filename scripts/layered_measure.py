#!/usr/bin/env python3
"""Generic deterministic measurement tool for layered v3 composition.

Usage:
    python scripts/layered_measure.py 5
    python scripts/layered_measure.py 5 6 7 8 9 11 12

The tool never OCRs text and never approves semantic crops. It verifies the canonical
raster SHA from pages/NN.yaml, measures visually-dense components at three levels and
exports overlays, contact sheets and a JSON report for human review:

  * ``macro``   : coarse dense regions (historical v1 detector, kept for continuity);
  * ``graphic`` : painted / thick-ink objects (illustrations, heraldry, maps, QR),
                  obtained from the distance to the measured paper colour after a
                  morphological opening that removes thin text strokes;
  * ``text``    : thin-stroke line groups outside graphic objects (text-zone candidates).

It also reports the effective resolution of the canonical raster at each print size
(A5 / A2 / A1, contain-fit) against the project gates, because every fragment cut
from the raster inherits that resolution.
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

# Print gates (ppi) at the final placement size, identical for every output format
# (decision of 2026-09-09): 300 ppi for continuous-tone rasters (illustrations, maps, photos),
# 1200 ppi for line-art rasters (icons, ornaments, crosses, bitonal marks). QR and text are vector.
PAGE_SIZES_MM = {"A5": (148.0, 210.0), "A2": (420.0, 594.0), "A1": (594.0, 841.0)}
PPI_GATES = {"continuous_tone": 300.0, "line_art": 1200.0}


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def effective_ppi(width_px, height_px):
    """Resolution of the raster when contain-fitted (no crop, no upscale) on each page size."""
    out = {}
    for name, (wmm, hmm) in PAGE_SIZES_MM.items():
        scale_mm_per_px = min(wmm / width_px, hmm / height_px)
        ppi = 25.4 / scale_mm_per_px
        out[name] = {
            "effective_ppi": round(ppi, 2),
            "gate_continuous_tone_ppi": PPI_GATES["continuous_tone"],
            "pass_continuous_tone": ppi >= PPI_GATES["continuous_tone"],
            "gate_line_art_ppi": PPI_GATES["line_art"],
            "pass_line_art": ppi >= PPI_GATES["line_art"],
            "placed_size_mm": [round(width_px * scale_mm_per_px, 2), round(height_px * scale_mm_per_px, 2)],
        }
    return out


def paper_colour(rgb):
    f = rgb.astype(np.float32)
    gray = f.mean(axis=2)
    bright = f[gray > 215]
    if len(bright) == 0:
        return np.array([255.0, 255.0, 255.0], dtype=np.float32)
    return np.median(bright, axis=0)


def ink_mask(rgb, threshold=45.0):
    """Pixels that differ from the measured paper colour (colour or ink)."""
    f = rgb.astype(np.float32)
    bg = paper_colour(rgb)
    dist = np.sqrt(((f - bg) ** 2).sum(axis=2))
    return (dist > threshold).astype(np.uint8), bg


def boxes_from_mask(mask, min_area):
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = map(int, stats[i])
        if area < min_area:
            continue
        out.append({"x": x, "y": y, "w": w, "h": h, "area": area})
    out.sort(key=lambda b: (b["y"], b["x"]))
    return out


def measure_macro(rgb):
    """Historical v1 coarse detector (kept for continuity with the page-03 prototype)."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 9)
    fg = (blur < 225).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    dense = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel, iterations=2)
    H, W = gray.shape
    candidates = []
    for b in boxes_from_mask(dense, int(0.004 * W * H)):
        if b["w"] < 0.08 * W or b["h"] < 0.04 * H:
            continue
        if b["w"] > 0.94 * W and b["h"] > 0.94 * H:
            continue
        b["area_fraction"] = round(b["area"] / (W * H), 6)
        candidates.append(b)
    return candidates


def measure_graphic(ink, opening_px=7, close_px=11, min_area_fraction=0.0015):
    """Painted/thick-ink objects: opening removes thin text strokes and frame lines."""
    H, W = ink.shape
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (opening_px, opening_px))
    thick = cv2.morphologyEx(ink, cv2.MORPH_OPEN, k)
    kc = cv2.getStructuringElement(cv2.MORPH_RECT, (close_px, close_px))
    dense = cv2.morphologyEx(thick * 255, cv2.MORPH_CLOSE, kc, iterations=2)
    boxes = boxes_from_mask(dense, int(min_area_fraction * W * H))
    for b in boxes:
        b["area_fraction"] = round(b["area"] / (W * H), 6)
        b["touches_page_border"] = bool(b["x"] == 0 or b["y"] == 0 or b["x"] + b["w"] >= W or b["y"] + b["h"] >= H)
    return boxes, dense


def measure_text(ink, graphic_dense):
    """Thin-stroke line groups outside graphic objects. Diagnostics only, never OCR."""
    gd = cv2.dilate(graphic_dense, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9)))
    text = ink * 255
    text[gd > 0] = 0
    hl = cv2.morphologyEx(text, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (60, 1)))
    vl = cv2.morphologyEx(text, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60)))
    text[(hl > 0) | (vl > 0)] = 0
    lines = cv2.morphologyEx(text, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (21, 3)))
    blocks = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 13)))
    out = []
    for b in boxes_from_mask(blocks, 150):
        if b["w"] <= 25:
            continue
        out.append(b)
    return out


def number(items, key="candidate"):
    for idx, b in enumerate(items, 1):
        b[key] = idx
    return items


def render_overlay(img, layers, path):
    out = img.copy().convert("RGB")
    draw = ImageDraw.Draw(out)
    line = max(2, img.width // 700)
    for boxes, colour, offset in layers:
        for b in boxes:
            x, y, w, h = b["x"], b["y"], b["w"], b["h"]
            o = min(offset, max(0, (min(w, h) - 1) // 2))
            draw.rectangle((x + o, y + o, x + w - o, y + h - o), outline=colour, width=line)
            draw.text((x + 4 + offset, y + 4 + offset), str(b["candidate"]), fill=colour)
    out.save(path, quality=92)


def render_contact_sheet(img, candidates, path, label):
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
        draw.text((x + 10, y + 5), f"{label} {idx}", fill="black")
    sheet.save(path, quality=92)


def measure_page(page, out_root=None):
    spec_path = ROOT / f"pages/{page:02d}.yaml"
    spec = yaml.safe_load(spec_path.read_text())
    src = ROOT / spec["visual_reference"]
    expected_sha = spec["visual_reference_sha256"]
    actual_sha = sha256(src)
    if actual_sha != expected_sha:
        raise SystemExit(f"page {page:02d} SHA mismatch: {actual_sha} != {expected_sha}")

    img = Image.open(src).convert("RGB")
    rgb = np.asarray(img)
    ink, bg = ink_mask(rgb)
    macro = number(measure_macro(rgb))
    graphic, dense = measure_graphic(ink)
    graphic = number(graphic)
    text = number(measure_text(ink, dense))

    out = (out_root or (ROOT / "dist/layered-measure")) / f"page-{page:02d}"
    out.mkdir(parents=True, exist_ok=True)
    render_overlay(img, [(macro, (255, 0, 0), 0)], out / "candidate-overlay.jpg")
    render_overlay(img, [(graphic, (255, 0, 0), 0), (text, (0, 0, 255), 2)], out / "object-overlay.jpg")
    render_contact_sheet(img, macro, out / "candidate-contact-sheet.jpg", "candidate")
    render_contact_sheet(img, graphic, out / "graphic-contact-sheet.jpg", "graphic")

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
        "paper_colour_rgb": [int(round(v)) for v in bg],
        "resolution": effective_ppi(img.width, img.height),
        "candidate_count": len(macro),
        "candidates": macro,
        "graphic_candidate_count": len(graphic),
        "graphic_candidates": graphic,
        "text_candidate_count": len(text),
        "text_candidates": text,
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
        "candidates": len(macro),
        "graphic_candidates": len(graphic),
        "text_candidates": len(text),
        "a5_effective_ppi": report["resolution"]["A5"]["effective_ppi"],
        "a5_gate_300": report["resolution"]["A5"]["pass_continuous_tone"],
        "a5_gate_1200_line_art": report["resolution"]["A5"]["pass_line_art"],
        "qr_count": len(qr_entries),
        "status": report["status"],
    }, ensure_ascii=False))
    return report


def probe(page, regions, min_area=6):
    """Print the tight ink bbox and ink components inside rough regions (x,y,w,h) of a page.

    Helps a reviewer turn an approximate object location into an exact crop without OCR.
    """
    spec = yaml.safe_load((ROOT / f"pages/{page:02d}.yaml").read_text())
    img = Image.open(ROOT / spec["visual_reference"]).convert("RGB")
    ink, _ = ink_mask(np.asarray(img))
    for reg in regions:
        x, y, w, h = [int(v) for v in reg.split(",")]
        sub = ink[y:y + h, x:x + w].astype(np.uint8)
        ys, xs = np.nonzero(sub)
        if len(xs) == 0:
            print(json.dumps({"region": [x, y, w, h], "ink": None}))
            continue
        tight = [x + int(xs.min()), y + int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
        closed = cv2.morphologyEx(sub * 255, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
        comps = [{"x": x + b["x"], "y": y + b["y"], "w": b["w"], "h": b["h"], "area": b["area"]} for b in boxes_from_mask(closed, min_area)]
        print(json.dumps({"region": [x, y, w, h], "tight_ink_bbox": tight, "ink_px": int(len(xs)), "components": comps}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pages", type=int, nargs="+")
    parser.add_argument("--out", default=None, help="output root (default dist/layered-measure)")
    parser.add_argument("--probe", action="append", default=[], metavar="X,Y,W,H",
                        help="print tight ink bbox/components inside this region instead of measuring (repeatable)")
    args = parser.parse_args()
    if args.probe:
        for page in args.pages:
            probe(page, args.probe)
        return
    for page in args.pages:
        if not 1 <= page <= 16:
            raise SystemExit("page must be 1..16")
        measure_page(page, Path(args.out) if args.out else None)


if __name__ == "__main__":
    main()
