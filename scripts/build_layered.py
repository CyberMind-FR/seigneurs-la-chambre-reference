#!/usr/bin/env python3
"""Build the v3 print PDFs from the layered compositions.

    python scripts/build_layered.py [--out dist]

For every page 1..16: compose from prototypes/page-NN/composition.yaml (scripts/layered_compose.py,
live text + canonical fragments + deterministic QR SVG, embedded TrueType fonts); a page without
composition falls back to the canonical raster + registry QR overlay (v2 method) when allowed by
build-config.yaml:v3.fallback_raster_pages_allowed. The per-page PDFs are then assembled with
PyMuPDF into the sequential A5 booklet, the A4 recto-verso imposition (pairs from build-config)
and the A2/A1 panels, keeping text and QR as vectors. Outputs, checksums, report and bundle go to
dist/; nothing is committed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import zipfile

import pymupdf as fitz  # PyMuPDF
import yaml
from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A1, A2, A4, A5, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab import rl_config

# Binary Flate streams (no ASCII85 re-encoding, +25 % size for no gain); fragments stay lossless.
rl_config.useA85 = 0

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from layered_compose import Composer  # noqa: E402

PAGE_SIZES = {"A1": A1, "A2": A2, "A4": A4, "A5": A5, "A4-landscape": landscape(A4)}
PAGE_MM = {"A5": 148.0, "A2": 420.0, "A1": 594.0}


def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def register_embedded_fonts():
    """Register the shared TrueType fonts from prototypes/_shared/text-styles.yaml; return the default one."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    styles = yaml.safe_load((ROOT / "prototypes/_shared/text-styles.yaml").read_text(encoding="utf-8"))
    default = (styles.get("defaults") or {}).get("font", "LiberationSerif")
    for name, path in (styles.get("fonts") or {}).items():
        if name in pdfmetrics.getRegisteredFontNames():
            continue
        candidates = path if isinstance(path, list) else [path]
        found = next((c for c in candidates if Path(c).exists()), None)
        if not found:
            raise SystemExit(f"font {name!r}: none of {candidates} exists on this machine")
        pdfmetrics.registerFont(TTFont(name, found))
    if default not in pdfmetrics.getRegisteredFontNames():
        raise SystemExit(f"default font {default!r} is not registered")
    return default


def raster_fallback_pdf(page_no, cfg, reg, out_pdf):
    """v2 method: canonical raster contain-fitted on A5 + registry QR PNG overlay."""
    src = cfg["source"]
    image = ROOT / src["assets_dir"] / src["pattern"].format(page=page_no)
    rw, rh = float(src["qr_reference_canvas"]["width"]), float(src["qr_reference_canvas"]["height"])
    pw, ph = A5
    # Register the embedded TrueType fonts and use one as the canvas initial font so that
    # no non-embedded base-14 font (Helvetica preamble) is referenced by the fallback page.
    font_name = register_embedded_fonts()
    c = canvas.Canvas(str(out_pdf), pagesize=A5, pageCompression=1, initialFontName=font_name, initialFontSize=10)
    c.setFillColor(HexColor(cfg["render"]["background"]))
    c.rect(0, 0, pw, ph, stroke=0, fill=1)
    with Image.open(image) as im:
        iw, ih = im.size
    scale = min(pw / iw, ph / ih)
    dw, dh = iw * scale, ih * scale
    dx, dy = (pw - dw) / 2, (ph - dh) / 2
    c.drawImage(ImageReader(str(image)), dx, dy, width=dw, height=dh, preserveAspectRatio=True, mask="auto")
    for q in reg.get("pages", {}).get(f"{page_no:02d}", {}).get("qrs", []):
        b = q["placement_px"]
        qx = dx + (b["x"] / rw) * dw
        qw = (b["w"] / rw) * dw
        qh = (b["h"] / rh) * dh
        qy = dy + dh - ((b["y"] + b["h"]) / rh) * dh
        c.drawImage(ImageReader(str(ROOT / q["asset"])), qx, qy, width=qw, height=qh, preserveAspectRatio=False, mask="auto")
    c.showPage()
    c.save()
    return {"page": page_no, "method": "raster_fallback_v2", "source": str(image.relative_to(ROOT)),
            "source_sha256": sha256(image), "effective_ppi_a5": round(iw / (dw / 72.0), 2)}


def compose_page(page_no, out_root):
    comp = Composer(page_no, None, out_root / f"page-{page_no:02d}", "A5", False)
    comp.load_sources()
    comp.compose()
    metrics, fails, warns = comp.validate()
    if metrics["methodology_gate"] == "FAIL":
        raise SystemExit(f"page {page_no:02d}: composition FAILED: {[i['message'] for i in metrics['issues'] if i['severity'] == 'fail']}")
    return comp.pdf, {"page": page_no, "method": "layered_composition", "composition": metrics["pdf"],
                      "gate": metrics["methodology_gate"], "fragments": metrics["fragment_count"],
                      "effective_ppi_a5": metrics["fragment_effective_ppi_min"],
                      "text_layer": metrics["text_layer_pass"], "qr": metrics["qr_decode_pass"],
                      "issues": [i for i in metrics["issues"] if i["severity"] == "fail"]}


def assemble(page_pdfs, cfg3, out, meta):
    outputs = cfg3["outputs"]
    seq = fitz.open()
    for p in page_pdfs:
        seq.insert_pdf(fitz.open(p))
    seq.set_metadata({"title": meta["title"], "author": meta["author"], "subject": meta["subject"],
                      "creator": "scripts/build_layered.py", "producer": "PyMuPDF + ReportLab"})
    p_seq = out / outputs["sequential_16"]["filename"]
    seq.save(p_seq, garbage=3, deflate=True)
    produced = [p_seq]

    # A4 landscape imposition, pairs from the v2 config (physical page numbers).
    pairs = cfg3["_imposition"]
    w, h = PAGE_SIZES["A4-landscape"]
    imp = fitz.open()
    for left, right in pairs:
        page = imp.new_page(width=w, height=h)
        page.show_pdf_page(fitz.Rect(0, 0, w / 2, h), seq, left - 1)
        page.show_pdf_page(fitz.Rect(w / 2, 0, w, h), seq, right - 1)
    imp.set_metadata(seq.metadata)
    p_imp = out / outputs["imposed_a4"]["filename"]
    imp.save(p_imp, garbage=3, deflate=True)
    produced.append(p_imp)

    for key in ("panels_a2", "panels_a1"):
        w, h = PAGE_SIZES[outputs[key]["page_size"]]
        doc = fitz.open()
        for i in range(seq.page_count):
            page = doc.new_page(width=w, height=h)
            page.show_pdf_page(fitz.Rect(0, 0, w, h), seq, i)
        doc.set_metadata(seq.metadata)
        p = out / outputs[key]["filename"]
        doc.save(p, garbage=3, deflate=True)
        produced.append(p)
    return produced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "build-config.yaml").read_text(encoding="utf-8"))
    cfg3 = cfg["v3"]
    cfg3["_imposition"] = cfg["outputs"]["imposed_a4"]["imposition"]
    reg = yaml.safe_load((ROOT / cfg["source"]["qr_registry"]).read_text(encoding="utf-8"))
    out = Path(args.out).resolve() if args.out else ROOT / cfg["release"]["dist_dir"]
    out.mkdir(parents=True, exist_ok=True)
    work = out / "layered"
    count = int(cfg["source"]["page_count"])
    allowed_fallback = set(cfg3.get("fallback_raster_pages_allowed", []))

    pages = []
    page_pdfs = []
    for n in range(1, count + 1):
        if (ROOT / f"prototypes/page-{n:02d}/composition.yaml").exists():
            pdf, rec = compose_page(n, work)
        elif n in allowed_fallback:
            pdf = work / f"page-{n:02d}" / f"page-{n:02d}-raster-fallback.pdf"
            pdf.parent.mkdir(parents=True, exist_ok=True)
            rec = raster_fallback_pdf(n, cfg, reg, pdf)
        else:
            raise SystemExit(f"page {n:02d}: no composition and raster fallback not allowed")
        for size in ("A2", "A1"):
            rec[f"effective_ppi_{size.lower()}"] = round(rec["effective_ppi_a5"] * PAGE_MM["A5"] / PAGE_MM[size], 2)
        pages.append(rec)
        page_pdfs.append(pdf)
        print(f"page {n:02d}: {rec['method']} ({rec.get('gate', 'raster')}, {rec['effective_ppi_a5']} ppi A5)")

    produced = assemble(page_pdfs, cfg3, out, cfg3["pdf_metadata"])
    report = {
        "project": cfg["project"], "version": cfg3["version"], "method": "layered_v3",
        "resolution_gates": {"continuous_tone": 300, "line_art": 1200, "a5_waiver_min_ppi": 180},
        "pages": pages,
        "outputs": {p.name: {"sha256": sha256(p), "pages": fitz.open(p).page_count} for p in produced},
    }
    rp = out / cfg3["release"]["report"]
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sp = out / cfg3["release"]["checksums"]
    sp.write_text("".join(f"{sha256(p)}  {p.name}\n" for p in [*produced, rp]), encoding="utf-8")
    zp = out / cfg3["release"]["bundle"]
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in [*produced, rp, sp]:
            z.write(p, p.name)
    print("PDF V3 BUILD OK")


if __name__ == "__main__":
    main()
