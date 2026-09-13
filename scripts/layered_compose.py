#!/usr/bin/env python3
"""Generic YAML-driven layered composer for the v3 pipeline.

    background -> raster fragments -> documentary vectors -> live canonical text -> deterministic QR

Usage:
    python scripts/layered_compose.py 3                      # uses prototypes/page-03/composition.yaml
    python scripts/layered_compose.py 5 --write-lock         # also records fragment SHA lock file

Everything page-specific lives in the composition YAML: page geometry, background, fragment
list (source bbox / destination bbox / treatment), vectors, text styles, text blocks mapped to
canonical_text blocks, QR overlays and validation rules. The script contains no per-page logic.

Guarantees:
  * the canonical raster is never modified and its SHA-256 is verified;
  * no OCR: text comes only from pages/NN.yaml:canonical_text;
  * QR payloads come only from the page spec / qr_registry.yaml and are redecoded from the
    final rendered PDF;
  * every produced fragment gets a SHA-256, an effective-ppi measurement, and an edge-ink
    check (a crop edge that cuts through strokes is reported, never silently accepted);
  * live text is checked for ink collisions against every raster fragment.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from xml.sax.saxutils import escape

import cv2
import numpy as np
from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A1, A2, A4, A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab import rl_config

# Binary Flate streams (no ASCII85 re-encoding, +25 % size for no gain); fragments stay lossless.
rl_config.useA85 = 0
from reportlab.platypus import Paragraph
from reportlab.graphics import renderPDF, shapes as rl_shapes
from svglib.svglib import svg2rlg
import yaml

import pymupdf as fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from heraldry_check import credit_gate_error, credit_inscribed_in_canon  # noqa: E402  (attribution gate shared with make heraldry-check)
PAGE_SIZES = {"A5": A5, "A4": A4, "A2": A2, "A1": A1}
ALIGN = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT, "justify": TA_JUSTIFY}
INK_THRESHOLD = 45.0
# Resolution gates at final placement size, every output format (decision 2026-09-09).
DEFAULT_PPI_GATES = {"continuous_tone": 300.0, "line_art": 1200.0}
LINE_ART_ROLES = {"icon", "ornament"}


# ----------------------------------------------------------------------------- helpers
def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def normalize_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def bbox_tuple(b):
    if isinstance(b, dict):
        return int(b["x"]), int(b["y"]), int(b["w"]), int(b["h"])
    x, y, w, h = b
    return int(x), int(y), int(w), int(h)


def load_yaml(path):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8")) or {}


class Geometry:
    """Maps canonical-raster pixel coordinates to PDF points (contain-fit, centred)."""

    def __init__(self, src_w, src_h, page_w, page_h):
        self.src_w, self.src_h, self.page_w, self.page_h = src_w, src_h, page_w, page_h
        content_h = page_h
        content_w = content_h * src_w / src_h
        if content_w > page_w:
            content_w = page_w
            content_h = content_w * src_h / src_w
        self.ox = (page_w - content_w) / 2
        self.oy = (page_h - content_h) / 2
        self.scale = content_w / src_w  # points per source pixel (uniform)
        self.content_w, self.content_h = content_w, content_h

    def box(self, x, y, w, h):
        return (self.ox + x * self.scale,
                self.oy + (self.src_h - (y + h)) * self.scale,
                w * self.scale, h * self.scale)

    def ppi_for(self, src_px_w, dest_pt_w):
        return src_px_w / (dest_pt_w / 72.0)


def paper_colour(rgb):
    f = rgb.astype(np.float32)
    gray = f.mean(axis=2)
    bright = f[gray > 215]
    return np.median(bright, axis=0) if len(bright) else np.array([255.0, 255.0, 255.0], np.float32)


def ink_mask(rgb, bg):
    dist = np.sqrt(((rgb.astype(np.float32) - bg) ** 2).sum(axis=2))
    return dist > INK_THRESHOLD


# ----------------------------------------------------------------------------- composer
class Composer:
    def __init__(self, page, spec_path=None, out_dir=None, page_size=None, write_lock=False):
        self.page = page
        self.spec_path = Path(spec_path) if spec_path else ROOT / f"prototypes/page-{page:02d}/composition.yaml"
        self.spec = yaml.safe_load(self.spec_path.read_text(encoding="utf-8"))
        if int(self.spec.get("page", page)) != page:
            raise SystemExit(f"composition page mismatch: {self.spec.get('page')} != {page}")
        self.out = Path(out_dir) if out_dir else ROOT / f"dist/layered/page-{page:02d}"
        self.out.mkdir(parents=True, exist_ok=True)
        self.page_size_name = page_size or self.spec.get("canvas", {}).get("page_size", "A5")
        self.page_w, self.page_h = PAGE_SIZES[self.page_size_name]
        self.write_lock = write_lock
        self.issues = []          # (severity, code, message)
        self.report = {"page": page, "spec": str(self.spec_path.relative_to(ROOT)), "page_size": self.page_size_name}
        # Phase C — HD regenerated sources are declared OUTSIDE the composition (grids untouched):
        # prototypes/page-NN/hd-sources.yaml, written by scripts/hd_ingest.py, approved by a human.
        self.hd_path = self.spec_path.parent / "hd-sources.yaml"
        self.hd = yaml.safe_load(self.hd_path.read_text(encoding="utf-8")) if self.hd_path.exists() else {}
        if self.hd and int(self.hd.get("page", page)) != page:
            raise SystemExit(f"hd-sources page mismatch: {self.hd.get('page')} != {page}")
        self.report["hd_sources"] = str(self.hd_path.relative_to(ROOT)) if self.hd else None
        # Communal coat of arms (2026-09-10): `communal_arms:` names a registry entry; the raster arms
        # fragment is replaced by the rendered official SVG only once that entry is VERIFIED.
        self.arms_spec = self.spec.get("communal_arms")
        self.arms = self.load_communal_arms() if self.arms_spec else None

    # ---- sources
    def load_sources(self):
        page_spec = load_yaml(self.spec["canonical_text"]["path"])
        src_rel = self.spec["source"]["path"]
        if page_spec.get("visual_reference") != src_rel:
            raise SystemExit(f"source path {src_rel} differs from pages/{self.page:02d}.yaml visual_reference")
        expected = self.spec["source"].get("sha256") or page_spec["visual_reference_sha256"]
        got = sha256(ROOT / src_rel)
        if got != expected or got != page_spec["visual_reference_sha256"]:
            raise SystemExit(f"canonical page-{self.page:02d} SHA mismatch: {got}")
        self.page_spec = page_spec
        self.src_path = ROOT / src_rel
        self.img = Image.open(self.src_path).convert("RGB")
        self.rgb = np.asarray(self.img)
        self.bg = paper_colour(self.rgb)
        self.ink = ink_mask(self.rgb, self.bg)
        self.geom = Geometry(self.img.width, self.img.height, self.page_w, self.page_h)
        self.report.update({
            "source": src_rel, "source_sha256": got,
            "source_px": [self.img.width, self.img.height],
            "content_pt": [round(self.geom.content_w, 2), round(self.geom.content_h, 2)],
            "source_effective_ppi": round(72.0 / self.geom.scale, 2),
        })

    def canonical_blocks(self):
        key = self.spec["canonical_text"].get("key", "canonical_text")
        text = self.page_spec[key]
        blocks = [normalize_ws(b) for b in re.split(r"\n+", text) if normalize_ws(b)]
        expected = self.spec["canonical_text"].get("expected_blocks")
        if expected is not None and len(blocks) != int(expected):
            raise SystemExit(f"canonical block count changed: got {len(blocks)}, expected {expected}")
        return blocks

    # ---- styles
    def styles(self):
        shared = load_yaml(self.spec["text_styles_from"]) if self.spec.get("text_styles_from") else {}
        defaults = dict(shared.get("defaults", {}))
        defaults.update(self.spec.get("text_defaults", {}))
        merged = dict(shared.get("styles", {}))
        for k, v in (self.spec.get("text_styles") or {}).items():
            base = dict(merged.get(k, {}))
            base.update(v)
            merged[k] = base
        self.style_defaults = defaults
        self.style_specs = merged
        # Optional TrueType fonts (Unicode glyphs the PDF base-14 fonts lack, e.g. U+1D49).
        for name, path in {**(shared.get("fonts") or {}), **(self.spec.get("fonts") or {})}.items():
            if name in pdfmetrics.getRegisteredFontNames():
                continue
            candidates = path if isinstance(path, list) else [path]
            found = next((c for c in candidates if Path(c).exists()), None)
            if not found:
                raise SystemExit(f"font {name!r}: none of {candidates} exists on this machine")
            pdfmetrics.registerFont(TTFont(name, found))
            self.report.setdefault("fonts", {})[name] = found
        # No non-embedded base-14 font may be referenced by the PDF (Helvetica preamble,
        # Times-Roman initial state of the SVG renderer): point both defaults to an embedded TTF.
        self.default_font = defaults.get("font", "LiberationSerif")
        if self.default_font not in pdfmetrics.getRegisteredFontNames():
            raise SystemExit(f"default font {self.default_font!r} is not a registered (embedded) TrueType font")
        rl_shapes.STATE_DEFAULTS["fontName"] = self.default_font

    def make_style(self, name, size=None):
        s = self.style_specs[name]
        size = size or float(s["size"])
        leading = float(s.get("leading", size * 1.12)) * (size / float(s["size"]))
        return ParagraphStyle(name, fontName=s.get("font", self.default_font), fontSize=size, leading=leading,
                              textColor=colors.HexColor(s.get("color", "#2f241e")), alignment=ALIGN[s.get("align", "left")],
                              splitLongWords=0, embeddedHyphenation=1)

    # ---- fragments
    def edge_ink(self, x, y, w, h):
        sub = self.ink[y:y + h, x:x + w]
        if sub.size == 0:
            return {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}
        return {"top": float(sub[0, :].mean()), "bottom": float(sub[-1, :].mean()),
                "left": float(sub[:, 0].mean()), "right": float(sub[:, -1].mean())}

    def grow_to_clean_edge(self, x, y, w, h, max_grow, eps):
        W, H = self.img.width, self.img.height
        grown = {"top": 0, "bottom": 0, "left": 0, "right": 0}
        for _ in range(max_grow * 4):
            e = self.edge_ink(x, y, w, h)
            dirty = [k for k, v in e.items() if v > eps]
            if not dirty:
                break
            moved = False
            if "top" in dirty and grown["top"] < max_grow and y > 0:
                y -= 1; h += 1; grown["top"] += 1; moved = True
            if "bottom" in dirty and grown["bottom"] < max_grow and y + h < H:
                h += 1; grown["bottom"] += 1; moved = True
            if "left" in dirty and grown["left"] < max_grow and x > 0:
                x -= 1; w += 1; grown["left"] += 1; moved = True
            if "right" in dirty and grown["right"] < max_grow and x + w < W:
                w += 1; grown["right"] += 1; moved = True
            if not moved:
                break
        return (x, y, w, h), grown

    def extract_fragments(self):
        val = self.spec.get("validation", {})
        accept = set(val.get("accept_fragment_statuses", ["APPROVED"]))
        eps = float(val.get("edge_ink_epsilon", 0.02))
        produced, skipped = [], []
        frag_dir = self.out / "fragments"
        frag_dir.mkdir(parents=True, exist_ok=True)
        for f in self.spec.get("fragments", []):
            if f.get("status") not in accept:
                skipped.append({"id": f["id"], "status": f.get("status")})
                continue
            x, y, w, h = bbox_tuple(f["bbox_px"])
            if min(x, y, w, h) < 0 or x + w > self.img.width or y + h > self.img.height:
                raise SystemExit(f"invalid bbox for fragment {f['id']}")
            if self.arms and f["id"] == self.arms_spec["replaces_fragment"]:
                produced.append(self.render_communal_arms(f, frag_dir))
                continue
            hd = self.hd_entry(f["id"], val)
            if hd is not None:
                produced.append(self.extract_hd_fragment(f, hd, frag_dir, val))
                continue
            before = self.edge_ink(x, y, w, h)
            grown = {"top": 0, "bottom": 0, "left": 0, "right": 0}
            treatment = f.get("treatment", "crop_only")
            if treatment == "crop_grow_to_clean_edge":
                (x, y, w, h), grown = self.grow_to_clean_edge(x, y, w, h, int(f.get("max_grow_px", 12)), eps)
            elif treatment != "crop_only":
                raise SystemExit(f"unknown treatment {treatment!r} for fragment {f['id']}")
            after = self.edge_ink(x, y, w, h)
            dirty = sorted(k for k, v in after.items() if v > eps)
            path = frag_dir / f"{f['id']}.png"
            crop = self.img.crop((x, y, x + w, y + h))
            masks = []
            for m in f.get("mask_px", []) or []:
                # Deterministic local masking of old raster text / neighbouring objects inside the
                # crop (REGENERATION_RULES: masquage de l'ancien texte, restauration locale du fond).
                # Fill: measured paper colour (default), the median colour of the mask border ring
                # (`mask_fill: border_median`, e.g. text inside a coloured banner) or a hex colour.
                if isinstance(m, dict) and "box" in m:  # per-mask fill override
                    mx, my, mw, mh = bbox_tuple(m["box"])
                    mode = m.get("fill", f.get("mask_fill", "paper"))
                else:
                    mx, my, mw, mh = bbox_tuple(m)
                    mode = f.get("mask_fill", "paper")
                if mode == "paper":
                    fill = tuple(int(round(v)) for v in self.bg)
                elif mode == "border_median":
                    ring = 3
                    y0, y1 = max(0, my - ring), min(self.img.height, my + mh + ring)
                    x0, x1 = max(0, mx - ring), min(self.img.width, mx + mw + ring)
                    region = self.rgb[y0:y1, x0:x1].astype(np.float32)
                    inner = np.zeros(region.shape[:2], dtype=bool)
                    inner[my - y0:my - y0 + mh, mx - x0:mx - x0 + mw] = True
                    fill = tuple(int(round(v)) for v in np.median(region[~inner], axis=0))
                elif isinstance(mode, str) and mode.startswith("#"):
                    fill = tuple(int(mode[i:i + 2], 16) for i in (1, 3, 5))
                else:
                    raise SystemExit(f"fragment {f['id']}: unknown mask_fill {mode!r}")
                ImageDraw.Draw(crop).rectangle((mx - x, my - y, mx - x + mw - 1, my - y + mh - 1), fill=fill)
                masks.append({"x": mx, "y": my, "w": mw, "h": mh, "fill_rgb": list(fill), "fill_mode": mode})
            dest = bbox_tuple(f["dest_bbox_px"]) if f.get("dest_bbox_px") else (x, y, w, h)
            dx, dy, dw, dh = self.geom.box(*dest)
            source_ppi = self.geom.ppi_for(w, dw)
            kind = f.get("raster_kind") or ("line_art" if f.get("role") in LINE_ART_ROLES else "continuous_tone")
            if kind not in DEFAULT_PPI_GATES:
                raise SystemExit(f"fragment {f['id']}: unknown raster_kind {kind!r}")
            # Provisional upscale (explicit project decision, never presented as HD recovery):
            # resample the fragment so that its placed resolution reaches the gate of its kind.
            ups = val.get("upscale") or {}
            gates_cfg = dict(DEFAULT_PPI_GATES)
            for gk, gv in (val.get("min_effective_ppi") or {}).items():
                if gk in gates_cfg:
                    gates_cfg[gk] = float(gv)
            upscale_factor = 1.0
            if ups.get("enabled") and source_ppi < gates_cfg[kind]:
                upscale_factor = min(float(ups.get("max_factor", 8.0)), gates_cfg[kind] / source_ppi)
                upscale_factor = float(np.ceil(upscale_factor * 100) / 100)
                new_size = (int(round(crop.width * upscale_factor)), int(round(crop.height * upscale_factor)))
                crop = crop.resize(new_size, Image.LANCZOS)
            crop.save(path)
            ppi = source_ppi * upscale_factor
            rec = {
                "id": f["id"], "role": f.get("role"), "status": f.get("status"), "raster_kind": kind,
                "path": str(path.relative_to(ROOT)), "sha256": sha256(path),
                "treatment": treatment,
                "requested_bbox_px": dict(zip("xywh", bbox_tuple(f["bbox_px"]))),
                "bbox_px": {"x": x, "y": y, "w": w, "h": h},
                "grown_px": grown,
                "masks_px": masks,
                "dest_bbox_px": dict(zip("xywh", dest)),
                "dest_pt": [round(dx, 2), round(dy, 2), round(dw, 2), round(dh, 2)],
                "effective_ppi": round(ppi, 2),
                "source_ppi": round(source_ppi, 2),
                "upscale_factor": upscale_factor,
                "upscale_provisional": upscale_factor > 1.0,
                "output_px": [crop.width, crop.height],
                "edge_ink_before": {k: round(v, 4) for k, v in before.items()},
                "edge_ink_after": {k: round(v, 4) for k, v in after.items()},
                "dirty_edges": dirty,
            }
            if dirty:
                self.issues.append((val.get("fragment_edge_ink", "warn"), "fragment_edge_ink",
                                    f"fragment {f['id']} crop edge cuts through ink on {dirty}"))
            produced.append(rec)
        self.fragments, self.skipped_fragments = produced, skipped
        (self.out / "fragments.json").write_text(json.dumps({"produced": produced, "skipped": skipped}, indent=2, ensure_ascii=False) + "\n")
        return produced

    # ---- Communal arms (registry-gated replacement of the seigneurial arms fragment)
    def load_communal_arms(self):
        reg_path = ROOT / self.arms_spec.get("registry", "assets/heraldry/communes/COMMUNES.yaml")
        registry = load_yaml(reg_path) if reg_path.exists() else {}
        slug = self.arms_spec["commune"]
        entry = (registry.get("communes") or {}).get(slug)
        if entry is None:
            raise SystemExit(f"communal_arms: commune {slug!r} absent from {reg_path}")
        status = entry.get("status")
        self.report["communal_arms"] = {"commune": slug, "name": entry.get("name"), "status": status, "active": False,
                                        "replaces_fragment": self.arms_spec["replaces_fragment"]}
        if status == "VERIFIED_CREDITS_PENDING":
            # provenance verified, but the licence requires an attribution line that is not yet in the canon
            self.issues.append(("info", "communal_arms_pending_credits",
                                f"communal arms of {entry.get('name')} verified but CC BY-SA credit line not inscribed in canon — seigneurial arms fragment kept, conditional caption not composed"))
            return None
        if status != "VERIFIED":
            self.issues.append(("info", "communal_arms_pending",
                                f"communal arms of {entry.get('name')} not verified ({status}) — seigneurial arms fragment kept, conditional caption not composed"))
            return None
        for k in ("svg", "sha256", "licence", "author", "source_url", "blazon", "blazon_source", "verified_by", "verified_on"):
            if not entry.get(k):
                raise SystemExit(f"communal_arms {slug}: VERIFIED entry lacks {k!r}")
        svg = ROOT / entry["svg"]
        if not svg.exists():
            raise SystemExit(f"communal_arms {slug}: {entry['svg']} missing")
        got = sha256(svg)
        if got != entry["sha256"]:
            raise SystemExit(f"communal_arms {slug}: SVG SHA mismatch ({got})")
        if entry.get("rights") not in ("CLEARED", "PROJECT_INTERNAL", "ASSOCIATION_PROVIDED", "ATTRIBUTION_SHAREALIKE"):
            raise SystemExit(f"communal_arms {slug}: rights {entry.get('rights')!r} not accepted")
        gate = credit_gate_error(entry)  # CC BY-SA: the credit line must be canonical text before the drawing is composed
        if gate:
            raise SystemExit(f"communal_arms {slug}: {gate}")
        self.report["communal_arms"].update({"active": True, "svg": entry["svg"], "svg_sha256": got,
                                             "licence": entry["licence"], "author": entry["author"],
                                             "credit_line": entry.get("credit_line"),
                                             "credit_pages": credit_inscribed_in_canon(entry["credit_line"]) if entry.get("credit_line") else []})
        return entry

    def render_communal_arms(self, f, frag_dir):
        """Render the verified commune SVG into the shield zone of the replaced fragment (line-art gate)."""
        import cairosvg
        x, y, w, h = bbox_tuple(f["bbox_px"])
        if self.arms_spec.get("shield_bbox_px"):
            sx, sy, sw, sh = bbox_tuple(self.arms_spec["shield_bbox_px"])
        else:  # default: upper 64 % of the fragment, 76 % of its width, centred
            sw, sh = int(round(w * 0.76)), int(round(h * 0.64))
            sx, sy = x + (w - sw) // 2, y + int(round(h * 0.04))
        dx, dy, dw, dh = self.geom.box(sx, sy, sw, sh)
        gate = float((self.spec.get("validation", {}).get("min_effective_ppi") or {}).get("line_art", DEFAULT_PPI_GATES["line_art"]))
        px_w = int(np.ceil(dw / 72.0 * gate * 1.02))  # a little above the line-art gate (rounding)
        png = frag_dir / f"{f['id']}.png"
        svg = ROOT / self.arms["svg"]
        cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=px_w)
        im = Image.open(png).convert("RGBA")
        # contain-fit inside the shield zone (SVG aspect may differ from the zone)
        scale = min(dw / im.width, dh / im.height)
        rw, rh = im.width * scale, im.height * scale
        rx, ry = dx + (dw - rw) / 2, dy + (dh - rh) / 2
        ppi = im.width / (rw / 72.0)
        dest_px = {"x": sx + int(round((sw - rw / self.geom.scale) / 2)), "y": sy + int(round((sh - rh / self.geom.scale) / 2)),
                   "w": int(round(rw / self.geom.scale)), "h": int(round(rh / self.geom.scale))}
        return {
            "id": f["id"], "role": "communal_arms_vector", "status": f.get("status"), "raster_kind": "line_art",
            "source": "svg", "svg_path": self.arms["svg"], "svg_sha256": self.report["communal_arms"]["svg_sha256"],
            "commune": self.arms_spec["commune"], "licence": self.arms["licence"], "author": self.arms["author"],
            "path": str(png.relative_to(ROOT)), "sha256": sha256(png),
            "treatment": "svg_render_contain", "requested_bbox_px": dict(zip("xywh", (x, y, w, h))),
            "bbox_px": {"x": x, "y": y, "w": w, "h": h}, "grown_px": {"top": 0, "bottom": 0, "left": 0, "right": 0},
            "masks_px": [], "dest_bbox_px": dest_px, "dest_pt": [round(rx, 2), round(ry, 2), round(rw, 2), round(rh, 2)],
            "effective_ppi": round(ppi, 2), "source_ppi": round(ppi, 2), "upscale_factor": 1.0, "upscale_provisional": False,
            "output_px": [im.width, im.height], "edge_ink_before": {}, "edge_ink_after": {}, "dirty_edges": [],
        }

    # ---- Phase C: HD regenerated sources (never upscaled, never masked, centre-cropped to the grid ratio)
    def hd_entry(self, frag_id, val):
        entry = ((self.hd or {}).get("fragments") or {}).get(frag_id)
        if not entry:
            return None
        accept = set(val.get("accept_hd_statuses", ["APPROVED"]))
        if entry.get("status") not in accept:
            self.issues.append(("info", "hd_source_pending", f"fragment {frag_id}: HD source declared but status {entry.get('status')!r} — canonical crop used"))
            return None
        return entry

    def extract_hd_fragment(self, f, hd, frag_dir, val):
        src = ROOT / hd["path"]
        if not src.exists():
            raise SystemExit(f"fragment {f['id']}: HD source {hd['path']} missing")
        got = sha256(src)
        if got != hd.get("sha256"):
            raise SystemExit(f"fragment {f['id']}: HD source SHA mismatch ({got} != {hd.get('sha256')}) — re-run hd_ingest and re-approve")
        x, y, w, h = bbox_tuple(f["bbox_px"])
        dest = bbox_tuple(f["dest_bbox_px"]) if f.get("dest_bbox_px") else (x, y, w, h)
        dx, dy, dw, dh = self.geom.box(*dest)
        im = Image.open(src)
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        target = dest[2] / dest[3]
        ratio = im.width / im.height
        tol = float(val.get("hd_aspect_tolerance", 0.03))
        if abs(ratio - target) / target > tol:
            raise SystemExit(f"fragment {f['id']}: HD source ratio {ratio:.4f} differs from grid ratio {target:.4f} by more than {tol:.0%}")
        # centre-crop to the exact grid ratio (the grid never moves; the HD image adapts)
        if ratio > target:
            cw, ch = int(round(im.height * target)), im.height
        else:
            cw, ch = im.width, int(round(im.width / target))
        cx, cy = (im.width - cw) // 2, (im.height - ch) // 2
        crop = im.crop((cx, cy, cx + cw, cy + ch))
        path = frag_dir / f"{f['id']}.png"
        crop.save(path)
        kind = f.get("raster_kind") or ("line_art" if f.get("role") in LINE_ART_ROLES else "continuous_tone")
        ppi = self.geom.ppi_for(crop.width, dw)
        gates_cfg = dict(DEFAULT_PPI_GATES)
        for gk, gv in (val.get("min_effective_ppi") or {}).items():
            if gk in gates_cfg:
                gates_cfg[gk] = float(gv)
        if ppi < gates_cfg[kind]:
            self.issues.append(("warn", "hd_source_below_gate", f"fragment {f['id']}: HD source {ppi:.1f} ppi < {gates_cfg[kind]:.0f} ppi at {self.page_size_name} (never upscaled)"))
        return {
            "id": f["id"], "role": f.get("role"), "status": f.get("status"), "raster_kind": kind,
            "source": "hd", "hd_path": hd["path"], "hd_sha256": got, "hd_px": [im.width, im.height],
            "hd_center_crop_px": {"x": cx, "y": cy, "w": cw, "h": ch}, "hd_status": hd.get("status"),
            "hd_generator": hd.get("generator"), "hd_prompt_id": hd.get("prompt_id"), "hd_rights": hd.get("rights"),
            "path": str(path.relative_to(ROOT)), "sha256": sha256(path),
            "treatment": "hd_center_crop",
            "requested_bbox_px": dict(zip("xywh", (x, y, w, h))),
            "bbox_px": {"x": x, "y": y, "w": w, "h": h},
            "grown_px": {"top": 0, "bottom": 0, "left": 0, "right": 0},
            "masks_px": [],
            "dest_bbox_px": dict(zip("xywh", dest)),
            "dest_pt": [round(dx, 2), round(dy, 2), round(dw, 2), round(dh, 2)],
            "effective_ppi": round(ppi, 2),
            "source_ppi": round(ppi, 2),
            "upscale_factor": 1.0,
            "upscale_provisional": False,
            "output_px": [crop.width, crop.height],
            "edge_ink_before": {}, "edge_ink_after": {}, "dirty_edges": [],
        }

    def draw_background_image(self, c, val):
        bg = (self.hd or {}).get("background")
        if not bg:
            return None
        accept = set(val.get("accept_hd_statuses", ["APPROVED"]))
        if bg.get("status") not in accept:
            return None
        src = ROOT / bg["path"]
        if not src.exists() or sha256(src) != bg.get("sha256"):
            raise SystemExit(f"background image {bg['path']} missing or SHA mismatch")
        mode = bg.get("mode", "cover")
        with Image.open(src) as im:
            iw, ih = im.size
        if mode == "cover":
            scale = max(self.page_w / iw, self.page_h / ih)
            w, h = iw * scale, ih * scale
            c.drawImage(str(src), (self.page_w - w) / 2, (self.page_h - h) / 2, width=w, height=h, mask="auto")
        elif mode == "tile":
            tw = float(bg.get("tile_pt", 144))
            th = tw * ih / iw
            yy = 0.0
            while yy < self.page_h:
                xx = 0.0
                while xx < self.page_w:
                    c.drawImage(str(src), xx, yy, width=tw, height=th, mask="auto")
                    xx += tw
                yy += th
        else:
            raise SystemExit(f"unknown background mode {mode!r}")
        return {"path": bg["path"], "sha256": bg["sha256"], "mode": mode}

    # ---- drawing
    def draw_fragments(self, c):
        for f in self.fragments:
            x, y, w, h = f["dest_pt"]
            c.drawImage(str(ROOT / f["path"]), x, y, width=w, height=h, preserveAspectRatio=False, mask="auto")

    def draw_vectors(self, c):
        for v in self.spec.get("vectors", []) or []:
            kind = v.get("kind")
            c.saveState()
            c.setStrokeColor(colors.HexColor(v.get("stroke", "#715240")))
            c.setLineWidth(float(v.get("width", 0.45)))
            if kind == "rect":
                x, y, w, h = self.geom.box(*bbox_tuple(v["bbox_px"]))
                fill = v.get("fill")
                if fill:
                    c.setFillColor(colors.HexColor(fill))
                c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1)
            elif kind == "line":
                (x1, y1), (x2, y2) = v["from"], v["to"]
                ax, ay, _, _ = self.geom.box(x1, y1, 0, 0)
                bx, by, _, _ = self.geom.box(x2, y2, 0, 0)
                c.line(ax, ay, bx, by)
            elif kind == "svg":
                self.draw_svg(c, ROOT / v["path"], bbox_tuple(v["bbox_px"]))
            else:
                raise SystemExit(f"unknown vector kind {kind!r}")
            c.restoreState()

    def draw_svg(self, c, path, bbox):
        d = svg2rlg(str(path))
        if d is None or d.width <= 0 or d.height <= 0:
            raise SystemExit(f"invalid SVG drawing {path}")
        x, y, w, h = self.geom.box(*bbox)
        c.saveState()
        c.translate(x, y)
        c.scale(w / d.width, h / d.height)
        renderPDF.draw(d, c, 0, 0)
        c.restoreState()

    def fit_paragraph(self, text, style_name, w_pt, h_pt):
        spec = self.style_specs[style_name]
        fit = spec.get("fit", self.style_defaults.get("fit", "shrink"))
        min_size = float(spec.get("min_size", self.style_defaults.get("min_size", 4.6)))
        step = float(spec.get("shrink_step", self.style_defaults.get("shrink_step", 0.2)))
        size = float(spec["size"])
        font = spec.get("font", "LiberationSerif")
        tokens = [t for part in text.split() for t in re.split(r"(?<=-)", part) if t]
        while True:
            style = self.make_style(style_name, size)
            p = Paragraph(escape(text), style)
            _, ah = p.wrap(w_pt, 10000)
            widest = max((stringWidth(t, font, size) for t in tokens), default=0)
            fits = ah <= h_pt + 0.01 and widest <= w_pt + 0.01
            if fits or fit != "shrink" or size - step < min_size:
                return p, size, ah
            size = round(size - step, 3)

    def draw_text(self, c, blocks):
        val = self.spec.get("validation", {})
        assigned, drawn, conditional_skipped = {}, [], []
        for tb in self.spec.get("text_blocks", []):
            idx = int(tb["block"])
            if tb.get("requires_communal_arms") and not self.arms:
                conditional_skipped.append(idx)  # caption « Armoiries de … » only with verified arms
                continue
            if idx in assigned:
                raise SystemExit(f"canonical block {idx} assigned twice ({assigned[idx]} and {tb['key']})")
            if not 0 <= idx < len(blocks):
                raise SystemExit(f"text block {tb['key']}: canonical block {idx} out of range")
            assigned[idx] = tb["key"]
            text = blocks[idx]
            expect = tb.get("expect")
            if expect and not text.startswith(normalize_ws(expect)):
                raise SystemExit(f"text block {tb['key']}: canonical block {idx} no longer starts with {expect!r}: {text[:60]!r}")
            bx, by, bw, bh = bbox_tuple(tb["bbox_px"])
            x, y, w, h = self.geom.box(bx, by, bw, bh)
            p, size, ah = self.fit_paragraph(text, tb["style"], w, h)
            valign = tb.get("valign", "top")
            top = y + h if valign == "top" else y + h - (h - ah) / 2 if valign == "middle" else y + ah
            p.drawOn(c, x, top - ah)
            overflow = ah > h + 0.01
            drawn_px_h = ah / self.geom.scale
            drawn_px_y = by + (h - (top - y)) / self.geom.scale
            rec = {"key": tb["key"], "block": idx, "style": tb["style"], "font_size": size,
                   "bbox_px": {"x": bx, "y": by, "w": bw, "h": bh},
                   "drawn_px": {"x": bx, "y": int(round(drawn_px_y)), "w": bw, "h": int(round(drawn_px_h))},
                   "overflow": overflow, "text_preview": text[:60]}
            if overflow:
                self.issues.append((val.get("text_overflow", "warn"), "text_overflow",
                                    f"text block {tb['key']} overflows its bbox ({ah:.1f}pt > {h:.1f}pt at {size}pt)"))
            drawn.append(rec)
        missing = [i for i in range(len(blocks)) if i not in assigned and i not in conditional_skipped]
        self.report["conditional_blocks_skipped"] = conditional_skipped
        if missing and val.get("all_blocks_assigned", True):
            raise SystemExit(f"canonical blocks not assigned to any text block: {missing}")
        self.text_drawn = drawn
        return drawn

    def qr_boxes(self):
        canvas_ref = self.spec.get("canvas", {}).get("qr_reference_canvas", [1920, 2880])
        registry = load_yaml(self.spec.get("qr_registry", "qr_registry.yaml"))
        page_reg = registry.get("pages", {}).get(f"{self.page:02d}", {}).get("qrs", [])
        page_qrs = {q["id"]: q for q in (self.page_spec.get("qr", {}).get("qrs") or [])}
        out = []
        for q in self.spec.get("qr", []) or []:
            spec_q = page_qrs.get(q["id"])
            reg_q = next((r for r in page_reg if r["id"] == q["id"]), None)
            if spec_q is None or reg_q is None:
                raise SystemExit(f"QR {q['id']} missing from pages/{self.page:02d}.yaml or qr_registry.yaml")
            if spec_q["payload"] != reg_q["payload"]:
                raise SystemExit(f"QR {q['id']} payload differs between page spec and registry")
            if q.get("placement", "reference_canvas") == "reference_canvas":
                p = spec_q["placement_px"]
                rw, rh = canvas_ref
                bbox = (round(p["x"] * self.img.width / rw), round(p["y"] * self.img.height / rh),
                        round(p["w"] * self.img.width / rw), round(p["h"] * self.img.height / rh))
            else:
                bbox = bbox_tuple(q["bbox_px"])
            out.append({"id": q["id"], "svg": q["svg"], "payload": spec_q["payload"], "bbox_px": dict(zip("xywh", bbox))})
        return out

    def draw_qr(self, c, qrs):
        for q in qrs:
            self.draw_svg(c, ROOT / q["svg"], bbox_tuple(q["bbox_px"]))

    def render_layers(self, pdf, blocks, qrs, only=None, record_text=True):
        c = canvas.Canvas(str(pdf), pagesize=(self.page_w, self.page_h), pageCompression=1,
                          initialFontName=self.default_font, initialFontSize=10)
        c.setTitle(self.spec.get("pdf_title", f"Composition v3 multicouche - Page {self.page:02d}"))
        c.setAuthor(self.spec.get("pdf_author", "Amis du Couvent des Cordeliers de La Chambre"))
        order = self.spec.get("layer_order", ["background", "raster_fragments", "documentary_vectors", "text_layer", "functional_overlay"])
        if order[-1] != "functional_overlay":
            raise SystemExit("functional_overlay (QR) must be the last layer")
        for layer in order:
            if only is not None and layer not in only:
                continue
            if layer == "background":
                c.setFillColor(colors.HexColor(self.spec.get("canvas", {}).get("background", "#fffdf7")))
                c.rect(0, 0, self.page_w, self.page_h, fill=1, stroke=0)
                self.report["background_image"] = self.draw_background_image(c, self.spec.get("validation", {}))
            elif layer == "raster_fragments":
                self.draw_fragments(c)
            elif layer == "documentary_vectors":
                self.draw_vectors(c)
            elif layer == "text_layer":
                saved = getattr(self, "text_drawn", None)
                self.draw_text(c, blocks)
                if not record_text and saved is not None:
                    self.text_drawn = saved
            elif layer == "functional_overlay":
                self.draw_qr(c, qrs)
            else:
                raise SystemExit(f"unknown layer {layer!r}")
        c.showPage()
        c.save()
        return pdf

    def compose(self):
        blocks = self.canonical_blocks()
        self.styles()
        self.extract_fragments()
        qrs = self.qr_boxes()
        pdf = self.render_layers(self.out / f"page-{self.page:02d}-layered-proof.pdf", blocks, qrs)
        # Diagnostic single-layer renders used for the ink-collision check (never distributed).
        diag = self.out / "diagnostics"
        diag.mkdir(exist_ok=True)
        self.pdf_text_only = self.render_layers(diag / "text-only.pdf", blocks, qrs, only={"text_layer"}, record_text=False)
        self.pdf_fragments_only = self.render_layers(diag / "fragments-only.pdf", blocks, qrs, only={"raster_fragments"})
        self.pdf, self.blocks, self.qrs = pdf, blocks, qrs
        return pdf

    # ---- validation
    def layer_ink(self, pdf, zoom=3):
        page = fitz.open(pdf)[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(np.float32)
        bg = np.array(colors.HexColor(self.spec.get("canvas", {}).get("background", "#fffdf7")).rgb()) * 255.0
        return np.sqrt(((arr - bg) ** 2).sum(axis=2)) > INK_THRESHOLD, zoom

    def text_collisions(self):
        """Pixels where rendered live text overlaps ink of a rendered raster fragment.

        Computed from single-layer renders of the same composition, so centred titles, glyph
        shapes and destination scaling are all taken into account exactly.
        """
        val = self.spec.get("validation", {})
        mode = val.get("text_ink_collision", "warn")
        min_px = int(val.get("text_ink_collision_min_px", 40))
        text_ink, zoom = self.layer_ink(self.pdf_text_only)
        frag_ink, _ = self.layer_ink(self.pdf_fragments_only)
        frag_ink = cv2.morphologyEx(frag_ink.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))) > 0
        text_ink = cv2.dilate(text_ink.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))) > 0
        both = text_ink & frag_ink
        # min_px is expressed in source-raster pixels; convert to render pixels.
        render_px_per_src = self.geom.scale * zoom
        min_render_px = min_px * render_px_per_src * render_px_per_src

        def render_rect(bx, by, bw, bh):
            x, y, w, h = self.geom.box(bx, by, bw, bh)
            x0 = int(x * zoom); y0 = int((self.page_h - (y + h)) * zoom)
            return x0, y0, int(w * zoom) + 1, int(h * zoom) + 1

        out = []
        # Blocks declared `allow_ink_overlap: true` sit on a masked wash whose non-paper fill
        # (mask_fill: border_median) the ink mask cannot distinguish from drawing ink.
        exempt = {tb["key"] for tb in self.spec.get("text_blocks", []) if tb.get("allow_ink_overlap")}
        for t in self.text_drawn:
            if t.get("key") in exempt:
                continue
            d = t["drawn_px"]
            x0, y0, w, h = render_rect(d["x"], d["y"], d["w"], d["h"])
            region = both[y0:y0 + h, x0:x0 + w]
            hits = int(region.sum())
            if hits < min_render_px:
                continue
            for f in self.fragments:
                fb = f["dest_bbox_px"]
                fx0, fy0, fw, fh = render_rect(fb["x"], fb["y"], fb["w"], fb["h"])
                ix0, iy0 = max(x0, fx0), max(y0, fy0)
                ix1, iy1 = min(x0 + w, fx0 + fw), min(y0 + h, fy0 + fh)
                if ix1 <= ix0 or iy1 <= iy0:
                    continue
                n = int(both[iy0:iy1, ix0:ix1].sum())
                if n < min_render_px:
                    continue
                src_px = int(round(n / (render_px_per_src ** 2)))
                ys, xs = np.nonzero(both[iy0:iy1, ix0:ix1])
                ox = (ix0 + xs.min()) / zoom; oy = (iy0 + ys.min()) / zoom
                ow = (xs.max() - xs.min() + 1) / zoom; oh = (ys.max() - ys.min() + 1) / zoom
                sx = int((ox - self.geom.ox) / self.geom.scale); sy = int((oy - self.geom.oy) / self.geom.scale)
                out.append({"text": t["key"], "fragment": f["id"], "ink_px": src_px,
                            "overlap_px": [sx, sy, int(ow / self.geom.scale) + 1, int(oh / self.geom.scale) + 1]})
                self.issues.append((mode, "text_ink_collision", f"text {t['key']} overlaps {src_px}px of ink in fragment {f['id']}"))
        return out

    def text_qr_overlaps(self):
        """Live text must never enter a QR placement box.

        The registry QR SVGs embed their 4-module quiet zone (assets/qr-svg/manifest.yaml), so the
        placement bbox already contains it; `qr_quiet_zone_fraction` adds an optional extra margin.
        """
        val = self.spec.get("validation", {})
        mode = val.get("text_qr_overlap", "fail")
        margin = float(val.get("qr_quiet_zone_fraction", 0.0))
        out = []
        for q in self.qrs:
            b = q["bbox_px"]
            mx, my = b["w"] * margin, b["h"] * margin
            qx0, qy0, qx1, qy1 = b["x"] - mx, b["y"] - my, b["x"] + b["w"] + mx, b["y"] + b["h"] + my
            for t in self.text_drawn:
                d = t["drawn_px"]
                if d["x"] < qx1 and d["x"] + d["w"] > qx0 and d["y"] < qy1 and d["y"] + d["h"] > qy0:
                    out.append({"text": t["key"], "qr": q["id"]})
                    self.issues.append((mode, "text_qr_overlap", f"text {t['key']} enters the quiet zone of QR {q['id']}"))
        return out

    def decode_qr(self, page, q):
        """Decode the QR from the final rendered PDF; several control windows and zooms are tried
        (neighbouring labels or QR codes can confuse the detector), the first exact match wins."""
        b = q["bbox_px"]
        last = ""
        for margin_div, zoom in ((8, 4), (4, 4), (8, 6), (2, 4), (16, 8)):
            margin = max(4, b["w"] // margin_div)
            x, y, w, h = self.geom.box(b["x"] - margin, b["y"] - margin, b["w"] + 2 * margin, b["h"] + 2 * margin)
            clip = fitz.Rect(x, self.page_h - (y + h), x + w, self.page_h - y)
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
            decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
            if decoded == q["payload"]:
                return decoded
            last = decoded or last
        return last

    def validate(self):
        val = self.spec.get("validation", {})
        doc = fitz.open(self.pdf)
        if len(doc) != 1:
            raise SystemExit("proof must have exactly one page")
        page = doc[0]
        text = normalize_ws(page.get_text("text"))
        # A line break placed after a hyphen that exists in the canon ("Notre-Dame-\ndu-Cruet") is a
        # legitimate typographic break, not a text change: compare against both readings.
        text_joined = re.sub(r"(?<=\S-) (?=\S)", "", text)
        skipped = set(self.report.get("conditional_blocks_skipped") or [])  # « Armoiries de … » while arms unverified
        missing = [b for i, b in enumerate(self.blocks) if i not in skipped
                   and normalize_ws(b) not in text and normalize_ws(b) not in text_joined]
        # Control render at 300 dpi (print gate for continuous tone).
        pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), alpha=False)
        render = self.out / f"page-{self.page:02d}-layered-proof-render.png"
        pix.save(render)
        qr_results = []
        for q in self.qrs:
            decoded = self.decode_qr(page, q)
            qr_results.append({"id": q["id"], "expected": q["payload"], "decoded": decoded, "pass": decoded == q["payload"]})
        collisions = self.text_collisions()
        qr_overlaps = self.text_qr_overlaps()
        gates = dict(DEFAULT_PPI_GATES)
        for k, v in (val.get("min_effective_ppi") or {}).items():
            if k in gates:
                gates[k] = float(v)
        ppi_min = min([f["effective_ppi"] for f in self.fragments], default=self.report["source_effective_ppi"])
        by_kind = {}
        for kind, gate_ppi in gates.items():
            kind_ppi = [f["effective_ppi"] for f in self.fragments if f["raster_kind"] == kind]
            by_kind[kind] = {"gate_ppi": gate_ppi, "fragment_count": len(kind_ppi),
                             "effective_ppi_min": round(min(kind_ppi), 2) if kind_ppi else None,
                             "pass": (min(kind_ppi) >= gate_ppi) if kind_ppi else True,
                             "failing_fragments": [f["id"] for f in self.fragments if f["raster_kind"] == kind and f["effective_ppi"] < gate_ppi]}
        resolution_pass = all(k["pass"] for k in by_kind.values())
        # Explicit human waiver (REGENERATION_RULES: « validation explicite d'un seuil inférieur »):
        # scoped to page sizes, with an accepted minimum ppi; the target gates stay reported.
        waiver = val.get("resolution_waiver") or {}
        waiver_applies = bool(waiver.get("approved")) and self.page_size_name in (waiver.get("page_sizes") or []) \
            and ppi_min >= float(waiver.get("min_ppi_accepted", 0))
        waiver_report = {"declared": bool(waiver), "applies": waiver_applies,
                         "approved_by": waiver.get("approved_by"), "date": waiver.get("date"),
                         "page_sizes": waiver.get("page_sizes"), "min_ppi_accepted": waiver.get("min_ppi_accepted")}
        frag_sha_pass = all((ROOT / f["path"]).exists() and sha256(ROOT / f["path"]) == f["sha256"] for f in self.fragments)
        lock = self.lock_check()
        fails = [i for i in self.issues if i[0] == "fail"]
        warns = [i for i in self.issues if i[0] != "fail"]
        text_pass, qr_pass = not missing, all(r["pass"] for r in qr_results)
        review = "PENDING_HUMAN_REVIEW" if any(f["status"] != "APPROVED" for f in self.fragments) else "REVIEWED"
        upscaled = [f["id"] for f in self.fragments if f.get("upscale_provisional")]
        if not (text_pass and qr_pass and frag_sha_pass) or fails:
            gate_status = "FAIL"
        elif resolution_pass and upscaled:
            gate_status = "PASS_WITH_PROVISIONAL_UPSCALE"
        elif not resolution_pass and waiver_applies:
            gate_status = "PASS_WITH_RESOLUTION_WAIVER"
        elif not resolution_pass:
            gate_status = "PASS_WITH_RESOLUTION_BLOCKER"
        else:
            gate_status = "PASS"
        metrics = {
            "page": self.page, "pdf": str(self.pdf.relative_to(ROOT)), "pdf_sha256": sha256(self.pdf),
            "render": str(render.relative_to(ROOT)),
            "canonical_text_paragraphs": len(self.blocks), "canonical_text_missing_from_pdf": missing,
            "text_layer_pass": text_pass,
            "qr": qr_results, "qr_decode_pass": qr_pass,
            "fragment_count": len(self.fragments), "fragment_sha_pass": frag_sha_pass,
            "fragments_skipped": self.skipped_fragments,
            "fragment_effective_ppi_min": round(ppi_min, 2),
            "fragment_source_ppi_min": round(min([f["source_ppi"] for f in self.fragments], default=self.report["source_effective_ppi"]), 2),
            "provisional_upscale": {"declared": bool(val.get("upscale", {}).get("enabled")), "fragments": upscaled,
                                    "approved_by": (val.get("upscale") or {}).get("approved_by"), "date": (val.get("upscale") or {}).get("date"),
                                    "note": (val.get("upscale") or {}).get("note")},
            "resolution_gate": {"page_size": self.page_size_name, "rule": "final placement size, every output format",
                                "by_raster_kind": by_kind, "pass": resolution_pass, "waiver": waiver_report},
            "text_ink_collisions": collisions,
            "text_qr_overlaps": qr_overlaps,
            "dirty_fragment_edges": [{"id": f["id"], "edges": f["dirty_edges"], "grown_px": f["grown_px"]} for f in self.fragments if f["dirty_edges"]],
            "text_overflow": [t["key"] for t in self.text_drawn if t["overflow"]],
            "fragment_lock": lock,
            "issues": [{"severity": s, "code": c, "message": m} for s, c, m in self.issues],
            "review_status": review,
            "methodology_gate": gate_status,
        }
        (self.out / "proof-validation.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
        self.report.update({"fragments": self.fragments, "text_blocks": self.text_drawn, "qr": self.qrs})
        (self.out / "composition-report.json").write_text(json.dumps(self.report, indent=2, ensure_ascii=False) + "\n")
        self.diagnostics(render, collisions)
        return metrics, fails, warns

    def lock_check(self):
        lock_path = self.spec_path.parent / "fragments.lock.yaml"
        current = {}
        for f in self.fragments:
            entry = {"sha256": f["sha256"], "bbox_px": f["bbox_px"]}
            if f.get("upscale_provisional"):  # provisional upscale is part of the audited identity
                entry.update({"source_ppi": f["source_ppi"], "upscale_factor": f["upscale_factor"],
                              "upscale_provisional": True})
            if f.get("source") == "svg":  # communal arms rendered from a verified SVG
                entry.update({"source": "svg", "svg_path": f["svg_path"], "svg_sha256": f["svg_sha256"]})
            if f.get("source") == "hd":  # HD regenerated source (Phase C) is part of the audited identity
                entry.update({"source": "hd", "hd_path": f["hd_path"], "hd_sha256": f["hd_sha256"]})
            current[f["id"]] = entry
        if self.write_lock:
            lock_path.write_text(yaml.safe_dump({
                "schema_version": 1, "page": self.page, "source": self.report["source"],
                "source_sha256": self.report["source_sha256"], "fragments": current,
            }, allow_unicode=True, sort_keys=False), encoding="utf-8")
            return {"path": str(lock_path.relative_to(ROOT)), "written": True, "match": True}
        if not lock_path.exists():
            return {"path": str(lock_path.relative_to(ROOT)), "exists": False, "match": None}
        lock = yaml.safe_load(lock_path.read_text(encoding="utf-8")) or {}
        diffs = [k for k, v in current.items() if lock.get("fragments", {}).get(k) != v]
        diffs += [k for k in lock.get("fragments", {}) if k not in current]
        if diffs and self.spec.get("validation", {}).get("fragment_lock", "warn") == "fail":
            self.issues.append(("fail", "fragment_lock", f"fragment lock mismatch: {diffs}"))
        elif diffs:
            self.issues.append(("warn", "fragment_lock", f"fragment lock mismatch: {diffs}"))
        return {"path": str(lock_path.relative_to(ROOT)), "exists": True, "match": not diffs, "diff": diffs}

    def diagnostics(self, render_path, collisions):
        """Overlay of all boxes on the rendered proof + side-by-side comparison with the canonical page."""
        render = Image.open(render_path).convert("RGB")
        sx = render.width / self.page_w
        sy = render.height / self.page_h
        draw = ImageDraw.Draw(render)

        def rect_px(bx, by, bw, bh, colour, width=2):
            x, y, w, h = self.geom.box(bx, by, bw, bh)
            draw.rectangle((x * sx, (self.page_h - (y + h)) * sy, (x + w) * sx, (self.page_h - y) * sy), outline=colour, width=width)

        for f in self.fragments:
            d = f["dest_bbox_px"]
            rect_px(d["x"], d["y"], d["w"], d["h"], (220, 30, 30))
        for t in self.text_drawn:
            d = t["drawn_px"]
            rect_px(d["x"], d["y"], d["w"], d["h"], (30, 60, 220))
        for q in self.qrs:
            b = q["bbox_px"]
            rect_px(b["x"], b["y"], b["w"], b["h"], (30, 160, 30))
        for col in collisions:
            x, y, w, h = col["overlap_px"]
            rect_px(x, y, w, h, (255, 0, 255), 4)
        render.save(self.out / f"page-{self.page:02d}-layered-proof-overlay.png")

        h = 1200
        left = self.img.resize((round(self.img.width * h / self.img.height), h))
        right = Image.open(render_path).convert("RGB")
        right = right.resize((round(right.width * h / right.height), h))
        sheet = Image.new("RGB", (left.width + right.width + 30, h + 30), "white")
        sheet.paste(left, (10, 20)); sheet.paste(right, (left.width + 20, 20))
        d = ImageDraw.Draw(sheet)
        d.text((10, 4), "canonical reference", fill="black")
        d.text((left.width + 20, 4), f"layered proof {self.page_size_name}", fill="black")
        sheet.save(self.out / f"page-{self.page:02d}-compare.jpg", quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page", type=int)
    ap.add_argument("--spec", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--page-size", default=None, choices=sorted(PAGE_SIZES))
    ap.add_argument("--write-lock", action="store_true", help="write prototypes/page-NN/fragments.lock.yaml")
    args = ap.parse_args()
    comp = Composer(args.page, args.spec, args.out, args.page_size, args.write_lock)
    comp.load_sources()
    comp.compose()
    metrics, fails, warns = comp.validate()
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("fragments_skipped",)}, indent=2, ensure_ascii=False))
    for s, code, msg in warns:
        print(f"WARN [{code}] {msg}", file=sys.stderr)
    for s, code, msg in fails:
        print(f"FAIL [{code}] {msg}", file=sys.stderr)
    if metrics["methodology_gate"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
