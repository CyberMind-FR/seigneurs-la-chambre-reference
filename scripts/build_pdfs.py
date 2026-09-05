#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import yaml
from PIL import Image
from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A1, A2, A4, A5, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# Évite l'encodage ASCII85 coûteux sur les gros JPEG.
rl_config.useA85 = 0

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def page_entry(mapping: dict, page_no: int) -> dict:
    for key in (f"{page_no:02d}", str(page_no), page_no):
        if key in mapping:
            return mapping[key] or {}
    return {}


def draw_page(
    c: canvas.Canvas,
    page_no: int | None,
    image_path: Path | None,
    box: tuple[float, float, float, float],
    registry: dict,
    qr_ref: tuple[int, int],
    background: str,
    metrics: list[dict] | None = None,
) -> None:
    x, y, box_w, box_h = box
    c.setFillColor(HexColor(background))
    c.rect(x, y, box_w, box_h, stroke=0, fill=1)

    if image_path is None:
        return

    with Image.open(image_path) as im:
        iw, ih = im.size

    scale = min(box_w / iw, box_h / ih)
    draw_w, draw_h = iw * scale, ih * scale
    dx = x + (box_w - draw_w) / 2
    dy = y + (box_h - draw_h) / 2

    c.drawImage(
        ImageReader(str(image_path)),
        dx,
        dy,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )

    # Les QR sont des actifs fonctionnels séparés. On les réinjecte au-dessus du raster.
    if page_no is not None:
        pdata = page_entry(registry.get("pages", {}), page_no)
        ref_w, ref_h = qr_ref
        for q in pdata.get("qrs", []):
            b = q["placement_px"]
            qx = dx + (b["x"] / ref_w) * draw_w
            qw = (b["w"] / ref_w) * draw_w
            qh = (b["h"] / ref_h) * draw_h
            # Les coordonnées du registre sont exprimées depuis le haut de l'image.
            qy = dy + draw_h - ((b["y"] + b["h"]) / ref_h) * draw_h
            qr_asset = ROOT / q["asset"]
            if not qr_asset.exists():
                raise FileNotFoundError(f"QR asset missing: {qr_asset.relative_to(ROOT)}")
            c.drawImage(
                ImageReader(str(qr_asset)),
                qx,
                qy,
                width=qw,
                height=qh,
                preserveAspectRatio=False,
                mask="auto",
            )

    if metrics is not None:
        ppi_x = iw / (draw_w / 72.0)
        ppi_y = ih / (draw_h / 72.0)
        metrics.append(
            {
                "page": page_no,
                "source_px": [iw, ih],
                "draw_pt": [round(draw_w, 2), round(draw_h, 2)],
                "effective_ppi": round(min(ppi_x, ppi_y), 1),
            }
        )


def make_sequential_pdf(
    path: Path,
    page_size: tuple[float, float],
    physical_pages: list[int | None],
    assets: dict[int, Path],
    registry: dict,
    qr_ref: tuple[int, int],
    background: str,
) -> list[dict]:
    metrics: list[dict] = []
    c = canvas.Canvas(str(path), pagesize=page_size, pageCompression=1)
    pw, ph = page_size
    for page_no in physical_pages:
        img = assets.get(page_no) if page_no is not None else None
        draw_page(c, page_no, img, (0, 0, pw, ph), registry, qr_ref, background, metrics)
        c.showPage()
    c.save()
    return metrics


def make_imposed_pdf(
    path: Path,
    pairs: list[list[int]],
    physical_map: dict[int, int | None],
    assets: dict[int, Path],
    registry: dict,
    qr_ref: tuple[int, int],
    background: str,
) -> list[dict]:
    size = landscape(A4)
    pw, ph = size
    half = pw / 2
    metrics: list[dict] = []
    c = canvas.Canvas(str(path), pagesize=size, pageCompression=1)
    for left_physical, right_physical in pairs:
        left_page = physical_map[left_physical]
        right_page = physical_map[right_physical]
        draw_page(c, left_page, assets.get(left_page) if left_page else None, (0, 0, half, ph), registry, qr_ref, background, metrics)
        draw_page(c, right_page, assets.get(right_page) if right_page else None, (half, 0, half, ph), registry, qr_ref, background, metrics)
        c.showPage()
    c.save()
    return metrics


def main() -> int:
    ap = argparse.ArgumentParser(description="Build print PDFs from locked colorized page assets")
    ap.add_argument("--config", default=str(ROOT / "build-config.yaml"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    config_path = Path(args.config).resolve()
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    out_dir = Path(args.out).resolve() if args.out else ROOT / cfg["release"]["dist_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.iterdir():
        if old.is_file():
            old.unlink()

    src = cfg["source"]
    page_count = int(src["page_count"])
    assets_dir = ROOT / src["assets_dir"]
    assets: dict[int, Path] = {}
    for page_no in range(1, page_count + 1):
        path = assets_dir / src["pattern"].format(page=page_no)
        if not path.exists():
            raise FileNotFoundError(f"Missing page asset: {path.relative_to(ROOT)}")
        assets[page_no] = path

    registry = yaml.safe_load((ROOT / src["qr_registry"]).read_text(encoding="utf-8"))
    qr_ref_cfg = src["qr_reference_canvas"]
    qr_ref = (int(qr_ref_cfg["width"]), int(qr_ref_cfg["height"]))
    background = cfg["render"]["background"]

    outputs = cfg["outputs"]
    report: dict = {
        "project": cfg["project"],
        "build_config": str(config_path.relative_to(ROOT)),
        "outputs": {},
        "notes": [
            "Le contenu des planches raster n'est pas réécrit pendant la construction.",
            "Les QR du registre sont réinjectés au-dessus des planches dans chaque PDF.",
            "La résolution effective des panneaux A2/A1 dépend des pixels réellement présents dans les sources.",
        ],
    }

    seq_cfg = outputs["sequential_15"]
    seq_path = out_dir / seq_cfg["filename"]
    report["outputs"][seq_path.name] = make_sequential_pdf(
        seq_path, A5, list(range(1, page_count + 1)), assets, registry, qr_ref, background
    )

    # Livret physique 16 pages : 1..14, verso intérieur blanc, dos = page source 15.
    physical_map = {n: n for n in range(1, 15)}
    physical_map[15] = None
    physical_map[16] = 15

    booklet_cfg = outputs["booklet_a5"]
    booklet_path = out_dir / booklet_cfg["filename"]
    booklet_pages = [physical_map[n] for n in range(1, 17)]
    report["outputs"][booklet_path.name] = make_sequential_pdf(
        booklet_path, A5, booklet_pages, assets, registry, qr_ref, background
    )

    imposed_cfg = outputs["imposed_a4"]
    imposed_path = out_dir / imposed_cfg["filename"]
    report["outputs"][imposed_path.name] = make_imposed_pdf(
        imposed_path,
        imposed_cfg["imposition"],
        physical_map,
        assets,
        registry,
        qr_ref,
        background,
    )

    a2_cfg = outputs["panels_a2"]
    a2_path = out_dir / a2_cfg["filename"]
    report["outputs"][a2_path.name] = make_sequential_pdf(
        a2_path, A2, list(range(1, page_count + 1)), assets, registry, qr_ref, background
    )

    a1_cfg = outputs["panels_a1"]
    a1_path = out_dir / a1_cfg["filename"]
    report["outputs"][a1_path.name] = make_sequential_pdf(
        a1_path, A1, list(range(1, page_count + 1)), assets, registry, qr_ref, background
    )

    report_path = out_dir / cfg["release"]["report"]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    pdfs = [seq_path, booklet_path, imposed_path, a2_path, a1_path]
    checksums_path = out_dir / cfg["release"]["checksums"]
    checksum_lines = [f"{sha256(p)}  {p.name}" for p in pdfs]
    checksum_lines.append(f"{sha256(report_path)}  {report_path.name}")
    checksums_path.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    bundle_path = out_dir / cfg["release"]["bundle"]
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in [*pdfs, report_path, checksums_path]:
            z.write(p, p.name)

    print("PDF BUILD OK")
    for p in [*pdfs, bundle_path, report_path, checksums_path]:
        print(f" - {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
