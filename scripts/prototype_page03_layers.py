#!/usr/bin/env python3
"""Page 03 layered-composition prototype.

Deterministic prototype for the v3 pipeline:
  background -> reviewed raster fragments -> live canonical text -> deterministic QR.

No OCR is used as editorial authority. No free reconstruction is performed.
The canonical page is never modified.
"""
from pathlib import Path
import hashlib, json, re, sys

import cv2
import pymupdf as fitz
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/page-03.jpg"
PAGE_SPEC = ROOT / "pages/03.yaml"
OUT = ROOT / "dist/prototype-page-03"
BOXES = ROOT / "prototypes/page-03/fragment-boxes.yaml"
QR_SVG = ROOT / "assets/qr-svg/page-03-google-maps.svg"

EXPECTED_SOURCE_SHA = "aa327f243594a23d91a2e6c4e61a0ed0a3f0aa4c0d143444aa56cb3bb4e67955"


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def normalize_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def measure_candidates(img):
    rgb = np.asarray(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 9)
    fg = (blur < 225).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    dense = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k, iterations=2)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(dense, 8)
    H, W = gray.shape
    cand = []
    for i in range(1, n):
        x, y, w, h, area = map(int, stats[i])
        frac = area / (W * H)
        if area < 0.004 * W * H:
            continue
        if w < 0.08 * W or h < 0.04 * H:
            continue
        if w > .94 * W and h > .94 * H:
            continue
        cand.append(dict(x=x, y=y, w=w, h=h, area=area, area_fraction=round(frac, 6)))
    cand.sort(key=lambda b: (b["y"], b["x"]))
    return cand


def diagnostic(img, cand):
    d = img.copy().convert("RGB")
    dr = ImageDraw.Draw(d)
    for i, b in enumerate(cand, 1):
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        dr.rectangle((x, y, x + w, y + h), outline=(255, 0, 0), width=max(2, img.width // 700))
        dr.text((x + 4, y + 4), str(i), fill=(255, 0, 0))
    d.save(OUT / "candidate-overlay.jpg", quality=92)


def extract_reviewed(img):
    data = yaml.safe_load(BOXES.read_text()) or {}
    produced = []
    for f in data.get("fragments", []):
        if f.get("status") != "APPROVED":
            continue
        x, y, w, h = [int(f["bbox_px"][k]) for k in ("x", "y", "w", "h")]
        if min(x, y, w, h) < 0 or x + w > img.width or y + h > img.height:
            raise SystemExit(f"invalid bbox for {f['id']}")
        p = OUT / "fragments" / f"{f['id']}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        img.crop((x, y, x + w, y + h)).save(p)
        produced.append({
            "id": f["id"],
            "role": f.get("role"),
            "path": str(p.relative_to(ROOT)),
            "bbox_px": dict(x=x, y=y, w=w, h=h),
            "sha256": sha256(p),
        })
    return produced


def canonical_paragraphs():
    spec = yaml.safe_load(PAGE_SPEC.read_text())
    text = spec["canonical_text"]
    paras = [normalize_ws(x) for x in re.split(r"\n\s*\n", text) if normalize_ws(x)]
    expected_prefix = [
        "Le Couvent des Cordeliers",
        "Le testament spirituel des Seigneurs de La Chambre",
        "La vision d'un seigneur (1365)",
    ]
    if paras[:3] != expected_prefix:
        raise SystemExit(f"unexpected canonical paragraph structure: {paras[:3]}")
    return paras


def para_map(paras):
    # The YAML is canonical; this mapping only assigns canonical paragraphs to layout boxes.
    keys = [
        "title", "subtitle", "h1", "vision_p1", "vision_p2", "vision_p3",
        "h2", "necropolis_p1", "necropolis_p2", "necropolis_p3",
        "h3", "architecture_p1", "architecture_p2", "carte", "localisation",
        "lat", "lng", "google_maps", "scan", "mappe_sarde", "visite",
        "adresse", "elements", "statut", "contact",
    ]
    if len(paras) != len(keys):
        raise SystemExit(f"canonical paragraph count changed: got {len(paras)}, expected {len(keys)}")
    return dict(zip(keys, paras))


def source_to_pdf_box(x, y, w, h, page_w, page_h, src_w=1024, src_h=1536):
    content_h = page_h
    content_w = content_h * src_w / src_h
    if content_w > page_w:
        content_w = page_w
        content_h = content_w * src_h / src_w
    ox = (page_w - content_w) / 2
    oy = (page_h - content_h) / 2
    sx = content_w / src_w
    sy = content_h / src_h
    return ox + x * sx, oy + (src_h - (y + h)) * sy, w * sx, h * sy, sx, sy


def draw_crop(c, fragment, page_w, page_h):
    b = fragment["bbox_px"]
    x, y, w, h, sx, sy = source_to_pdf_box(b["x"], b["y"], b["w"], b["h"], page_w, page_h)
    c.drawImage(str(ROOT / fragment["path"]), x, y, width=w, height=h, preserveAspectRatio=True, mask='auto')
    return sx


def draw_paragraph(c, text, bbox, page_w, page_h, style):
    x, y, w, h, sx, sy = source_to_pdf_box(*bbox, page_w, page_h)
    p = Paragraph(text.replace("&", "&amp;"), style)
    aw, ah = p.wrap(w, h)
    p.drawOn(c, x, y + h - ah)


def make_styles(scale):
    sepia = colors.HexColor("#3f2d23")
    red = colors.HexColor("#8b2e2e")
    return {
        "title": ParagraphStyle("title", fontName="Times-Bold", fontSize=24, leading=25, textColor=sepia, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", fontName="Times-Italic", fontSize=10.2, leading=11, textColor=red, alignment=TA_CENTER),
        "heading": ParagraphStyle("heading", fontName="Times-Bold", fontSize=9.4, leading=10.2, textColor=red),
        "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=6.15, leading=7.05, textColor=colors.HexColor("#2f241e")),
        "small": ParagraphStyle("small", fontName="Times-Roman", fontSize=5.8, leading=6.5, textColor=colors.HexColor("#2f241e")),
        "small_bold": ParagraphStyle("small_bold", fontName="Times-Bold", fontSize=6.1, leading=6.8, textColor=colors.HexColor("#2f241e")),
        "tiny": ParagraphStyle("tiny", fontName="Times-Roman", fontSize=5.3, leading=5.8, textColor=colors.HexColor("#2f241e")),
    }


def compose_pdf(img, fragments, paras):
    page_w, page_h = A5
    pdf = OUT / "page-03-layered-proof.pdf"
    c = canvas.Canvas(str(pdf), pagesize=A5, pageCompression=1)
    c.setTitle("Prototype v3 multicouche - Page 03 - Le Couvent des Cordeliers")
    c.setAuthor("Les Amis du Couvent des Cordeliers de La Chambre")

    # Deterministic neutral paper background.
    c.setFillColor(colors.HexColor("#fffdf7"))
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    scale = None
    for f in fragments:
        scale = draw_crop(c, f, page_w, page_h)
    styles = make_styles(scale)
    P = para_map(paras)

    # Main live text, using source-relative boxes measured from the visual reference.
    text_boxes = [
        ("title", (194, 34, 650, 72), "title"),
        ("subtitle", (232, 110, 595, 42), "subtitle"),
        ("h1", (226, 190, 505, 34), "heading"),
        ("vision_p1", (226, 224, 517, 92), "body"),
        ("vision_p2", (226, 321, 517, 86), "body"),
        ("vision_p3", (226, 410, 517, 88), "body"),
        ("h2", (226, 531, 520, 34), "heading"),
        ("necropolis_p1", (226, 568, 550, 64), "body"),
        ("necropolis_p2", (226, 637, 550, 87), "body"),
        ("necropolis_p3", (226, 728, 550, 74), "body"),
        ("h3", (59, 824, 545, 34), "heading"),
        ("architecture_p1", (59, 858, 545, 88), "body"),
        ("architecture_p2", (59, 951, 545, 78), "body"),
        ("carte", (105, 1064, 185, 28), "small_bold"),
        ("localisation", (457, 1064, 204, 30), "small_bold"),
        ("lat", (462, 1104, 210, 25), "small"),
        ("lng", (462, 1128, 210, 25), "small"),
        ("google_maps", (758, 1066, 207, 30), "small_bold"),
        ("scan", (757, 1254, 205, 24), "tiny"),
        ("mappe_sarde", (83, 1294, 840, 26), "tiny"),
        ("visite", (383, 1336, 260, 28), "small_bold"),
        ("adresse", (96, 1370, 375, 26), "tiny"),
        ("elements", (96, 1400, 375, 42), "tiny"),
        ("statut", (96, 1446, 375, 26), "tiny"),
        ("contact", (96, 1478, 375, 26), "tiny"),
    ]
    for key, box, sty in text_boxes:
        draw_paragraph(c, P[key], box, page_w, page_h, styles[sty])

    # Simple vector scaffolding in place of raster frame/background content.
    sepia = colors.HexColor("#715240")
    red = colors.HexColor("#9a4938")
    c.setStrokeColor(sepia)
    c.setLineWidth(0.45)
    for box in [(35, 1058, 953, 272), (35, 1332, 860, 185)]:
        x, y, w, h, _, _ = source_to_pdf_box(*box, page_w, page_h)
        c.rect(x, y, w, h, fill=0, stroke=1)
    for box in [(400, 1058, 276, 272), (675, 1058, 313, 272)]:
        x, y, w, h, _, _ = source_to_pdf_box(*box, page_w, page_h)
        c.rect(x, y, w, h, fill=0, stroke=1)
    x1, y1, _, _, _, _ = source_to_pdf_box(335, 165, 350, 1, page_w, page_h)
    c.setStrokeColor(red)
    c.line(x1, y1, x1 + 350 * (page_h / 1536), y1)

    # Deterministic vector QR overlay, rendered last.
    qr = svg2rlg(str(QR_SVG))
    qx, qy, qw, qh, _, _ = source_to_pdf_box(778, 1118, 102, 102, page_w, page_h)
    if qr.width <= 0 or qr.height <= 0:
        raise SystemExit("invalid QR drawing")
    c.saveState()
    c.translate(qx, qy)
    c.scale(qw / qr.width, qh / qr.height)
    renderPDF.draw(qr, c, 0, 0)
    c.restoreState()

    c.showPage()
    c.save()
    return pdf, scale


def validate_pdf(pdf, paras, scale, fragments):
    doc = fitz.open(pdf)
    if len(doc) != 1:
        raise SystemExit("proof must have one page")
    page = doc[0]
    text = normalize_ws(page.get_text("text"))
    missing = [p for p in paras if normalize_ws(p) not in text]

    pix = page.get_pixmap(matrix=fitz.Matrix(4, 4), alpha=False)
    render_path = OUT / "page-03-layered-proof-render.png"
    pix.save(render_path)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    bgr = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    decoded, pts, _ = cv2.QRCodeDetector().detectAndDecode(bgr)
    expected_qr = yaml.safe_load(PAGE_SPEC.read_text())["qr"]["qrs"][0]["payload"]

    effective_ppi = 72.0 / scale
    metrics = {
        "pdf": str(pdf.relative_to(ROOT)),
        "pdf_sha256": sha256(pdf),
        "render": str(render_path.relative_to(ROOT)),
        "canonical_text_paragraphs": len(paras),
        "canonical_text_missing_from_pdf": missing,
        "text_layer_pass": not missing,
        "qr_expected": expected_qr,
        "qr_decoded": decoded,
        "qr_decode_pass": decoded == expected_qr,
        "source_to_a5_effective_ppi": round(effective_ppi, 2),
        "a5_300ppi_gate": effective_ppi >= 300,
        "fragment_count": len(fragments),
        "fragment_sha_pass": all((ROOT / f["path"]).exists() and sha256(ROOT / f["path"]) == f["sha256"] for f in fragments),
        "methodology_gate": "PASS_WITH_RESOLUTION_BLOCKER" if (not missing and decoded == expected_qr and effective_ppi < 300) else "PASS" if (not missing and decoded == expected_qr) else "FAIL",
    }
    (OUT / "proof-validation.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    if missing:
        raise SystemExit(f"text layer validation failed; missing {len(missing)} canonical paragraphs")
    if decoded != expected_qr:
        raise SystemExit(f"QR decode failed: {decoded!r} != {expected_qr!r}")
    return metrics


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if sha256(SRC) != EXPECTED_SOURCE_SHA:
        raise SystemExit("canonical page-03 SHA mismatch")
    img = Image.open(SRC).convert("RGB")
    cand = measure_candidates(img)
    (OUT / "measurement.json").write_text(json.dumps({
        "source": str(SRC.relative_to(ROOT)),
        "source_sha256": sha256(SRC),
        "width_px": img.width,
        "height_px": img.height,
        "candidates": cand,
    }, indent=2) + "\n")
    diagnostic(img, cand)
    fragments = extract_reviewed(img)
    (OUT / "fragments.json").write_text(json.dumps({"produced": fragments}, indent=2, ensure_ascii=False) + "\n")
    paras = canonical_paragraphs()
    pdf, scale = compose_pdf(img, fragments, paras)
    metrics = validate_pdf(pdf, paras, scale, fragments)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
