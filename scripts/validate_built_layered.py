#!/usr/bin/env python3
"""Validate the v3 print PDFs (scripts/build_layered.py outputs).

Checks on the sequential A5 PDF: 16 pages; every QR of qr_registry.yaml decoded from the final
render with its exact payload; every canonical_text block of every composed page present in the
page's text layer (hyphen-tolerant); all fonts embedded; and, on the imposed/panel PDFs, page
counts and QR decode of the first registry QR as a smoke test.
"""
from pathlib import Path
import re
import sys

import cv2
import pymupdf as fitz
import numpy as np
import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
cfg = yaml.safe_load((ROOT / "build-config.yaml").read_text(encoding="utf-8"))
cfg3 = cfg["v3"]
reg = yaml.safe_load((ROOT / cfg["source"]["qr_registry"]).read_text(encoding="utf-8"))
dist = ROOT / cfg["release"]["dist_dir"]
errors = []


def normalize_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def decode_in(page, rect, payload):
    det = cv2.QRCodeDetector()
    for zoom in (4, 6, 3):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect, alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        d, _, _ = det.detectAndDecode(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
        if d == payload:
            return d
    return d


def qr_rect(page, page_no, q):
    """Registry placement (normalised on the reference canvas) mapped onto the contain-fitted raster."""
    rw, rh = float(cfg["source"]["qr_reference_canvas"]["width"]), float(cfg["source"]["qr_reference_canvas"]["height"])
    with Image.open(ROOT / "assets" / f"page-{page_no:02d}.jpg") as im:
        iw, ih = im.size
    W, H = page.rect.width, page.rect.height
    scale = min(W / iw, H / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = (W - dw) / 2, (H - dh) / 2
    b = q["placement_px"]
    x, y = dx + b["x"] / rw * dw, dy + b["y"] / rh * dh
    w, h = b["w"] / rw * dw, b["h"] / rh * dh
    m = max(3.0, w * 0.15)
    return fitz.Rect(x - m, y - m, x + w + m, y + h + m)


def main():
    seq = dist / cfg3["outputs"]["sequential_16"]["filename"]
    if not seq.exists():
        print(f"V3 PDF VALIDATION FAILED\n - missing {seq}")
        sys.exit(1)
    doc = fitz.open(seq)
    if doc.page_count != int(cfg["source"]["page_count"]):
        errors.append(f"sequential PDF has {doc.page_count} pages")
    # fonts embedded
    for i, page in enumerate(doc, 1):
        for f in page.get_fonts(full=True):
            xref, ext, ftype, basefont = f[0], f[1], f[2], f[3]
            if ext == "n/a" and ftype != "Type3":
                errors.append(f"page {i}: font {basefont} is not embedded")
    # QR
    for pkey, pdata in reg.get("pages", {}).items():
        n = int(pkey)
        for q in pdata.get("qrs", []):
            page = doc[n - 1]
            d = decode_in(page, qr_rect(page, n, q), q["payload"])
            if d != q["payload"]:
                errors.append(f"page {n} / {q['id']}: decoded={d!r} expected={q['payload']!r}")
    # text layer of composed pages
    for n in range(1, doc.page_count + 1):
        comp_path = ROOT / f"prototypes/page-{n:02d}/composition.yaml"
        if not comp_path.exists():
            continue
        comp = yaml.safe_load(comp_path.read_text(encoding="utf-8"))
        spec = yaml.safe_load((ROOT / comp["canonical_text"]["path"]).read_text(encoding="utf-8"))
        blocks = [normalize_ws(b) for b in re.split(r"\n+", spec[comp["canonical_text"].get("key", "canonical_text")]) if normalize_ws(b)]
        # Conditional captions « Armoiries de … » are composed only once the commune's arms are VERIFIED.
        arms = comp.get("communal_arms")
        if arms:
            reg = yaml.safe_load((ROOT / arms.get("registry", "assets/heraldry/communes/COMMUNES.yaml")).read_text(encoding="utf-8"))
            if (reg.get("communes", {}).get(arms["commune"]) or {}).get("status") != "VERIFIED":
                skip = {int(tb["block"]) for tb in comp.get("text_blocks", []) if tb.get("requires_communal_arms")}
                blocks = [b for i, b in enumerate(blocks) if i not in skip]
        text = normalize_ws(doc[n - 1].get_text("text"))
        joined = re.sub(r"(?<=\S-) (?=\S)", "", text)
        missing = [b for b in blocks if b not in text and b not in joined]
        if missing:
            errors.append(f"page {n}: {len(missing)} canonical block(s) missing from the text layer: {missing[:2]}")
    # forbidden strings from corrections.yaml must not appear in the final text layer
    corr = yaml.safe_load((ROOT / "corrections.yaml").read_text(encoding="utf-8")) or {}
    for key, entry in corr.items():
        if not isinstance(entry, dict):
            continue
        forb = [f for f in entry.get("forbidden", []) if isinstance(f, str)]
        if not forb:
            continue
        pages = [int(key.split("_")[1])] if re.match(r"page_\d+$", key) else range(1, doc.page_count + 1)
        for n in pages:
            text = normalize_ws(doc[n - 1].get_text("text"))
            for f in forb:
                if normalize_ws(f) and normalize_ws(f) in text:
                    errors.append(f"page {n}: forbidden string present in text layer ({key}): {f!r}")
    # other outputs: page counts + QR smoke test on the imposed sheet holding page 3
    imp = fitz.open(dist / cfg3["outputs"]["imposed_a4"]["filename"])
    if imp.page_count != len(cfg["outputs"]["imposed_a4"]["imposition"]):
        errors.append("imposed PDF sheet count mismatch")
    for key in ("panels_a2", "panels_a1"):
        d = fitz.open(dist / cfg3["outputs"][key]["filename"])
        if d.page_count != doc.page_count:
            errors.append(f"{key}: page count mismatch")
        q = reg["pages"]["03"]["qrs"][0]
        page = d[2]
        got = decode_in(page, qr_rect(page, 3, q), q["payload"])
        if got != q["payload"]:
            errors.append(f"{key}: page 3 QR decoded={got!r}")
    if errors:
        print("V3 PDF VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("V3 PDF VALIDATION OK (16 pages, QR exact, text layer complete, fonts embedded, no forbidden string)")


if __name__ == "__main__":
    main()
