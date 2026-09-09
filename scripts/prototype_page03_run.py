#!/usr/bin/env python3
"""Compatibility runner for the page-03 layered prototype.

PyYAML folds line breaks inside the single-quoted canonical_text scalar. This runner
rebinds canonical_paragraphs() to split on preserved YAML block breaks. It also maps
the canonical 1920x2880 QR placement from pages/03.yaml onto the 1024x1536 visual
reference and applies the typography correction observed on the first rendered proof.
"""
import re
import yaml
import prototype_page03_layers as p


def canonical_paragraphs_block_aware():
    spec = yaml.safe_load(p.PAGE_SPEC.read_text())
    text = spec["canonical_text"]
    blocks = [p.normalize_ws(x) for x in re.split(r"\n+", text) if p.normalize_ws(x)]
    expected_prefix = [
        "Le Couvent des Cordeliers",
        "Le testament spirituel des Seigneurs de La Chambre",
        "La vision d'un seigneur (1365)",
    ]
    if blocks[:3] != expected_prefix:
        raise SystemExit(f"unexpected canonical block structure: {blocks[:5]}")
    if len(blocks) != 25:
        raise SystemExit(f"canonical block count changed: got {len(blocks)}, expected 25; blocks={blocks}")
    return blocks


_original_source_to_pdf_box = p.source_to_pdf_box
_original_make_styles = p.make_styles


def source_to_pdf_box_qr_normalized(x, y, w, h, page_w, page_h, src_w=1024, src_h=1536):
    # Replace only the initial prototype QR box with the normalized canonical placement
    # from pages/03.yaml: 1435,2081,234,234 on the 1920x2880 reference canvas.
    if (x, y, w, h) == (778, 1118, 102, 102):
        x = round(1435 * src_w / 1920)
        y = round(2081 * src_h / 2880)
        w = round(234 * src_w / 1920)
        h = round(234 * src_h / 2880)
    return _original_source_to_pdf_box(x, y, w, h, page_w, page_h, src_w, src_h)


def make_styles_reviewed(scale):
    styles = _original_make_styles(scale)
    # First proof wrapped the title onto two lines and collided with the subtitle.
    # Keep the canonical wording and geometry; reduce only the title typesetting.
    styles["title"].fontSize = 20.5
    styles["title"].leading = 21.0
    styles["subtitle"].fontSize = 9.8
    styles["subtitle"].leading = 10.4
    return styles


p.canonical_paragraphs = canonical_paragraphs_block_aware
p.source_to_pdf_box = source_to_pdf_box_qr_normalized
p.make_styles = make_styles_reviewed
p.main()
