#!/usr/bin/env python3
"""Neutralise le papier coloré sans modifier la composition des pages.

Le traitement est déterministe. Les QR du registre sont toujours composités
en dernier, après la normalisation colorimétrique.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def smoothstep(edge0: float, edge1: float, value: np.ndarray) -> np.ndarray:
    x = np.clip((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def normalize_page(source: Path) -> Image.Image:
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32) / 255.0
    maximum = rgb.max(axis=2)
    minimum = rgb.min(axis=2)
    chroma = maximum - minimum
    luminance = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

    # Renforce l'encre sombre et ouvre les tons clairs sans toucher à la géométrie.
    target_luminance = np.where(
        luminance < 0.72,
        luminance * 0.84,
        1.0 - (1.0 - luminance) * 0.42,
    )
    ratio = target_luminance / np.maximum(luminance, 1e-5)
    contrasted = np.clip(rgb * ratio[:, :, None], 0.0, 1.0)

    # Les pixels clairs et faiblement colorés correspondent au papier.
    # Leur dominante est neutralisée progressivement jusqu'au blanc pur.
    light_weight = smoothstep(0.52, 0.88, luminance)
    neutral_weight = 1.0 - smoothstep(0.10, 0.42, chroma)
    paper_weight = (light_weight * neutral_weight)[:, :, None]
    normalized = contrasted * (1.0 - paper_weight) + paper_weight
    return Image.fromarray(np.rint(np.clip(normalized, 0.0, 1.0) * 255.0).astype(np.uint8))


def registry_entry(mapping: dict, page: int) -> dict:
    for key in (f"{page:02d}", str(page), page):
        if key in mapping:
            return mapping[key] or {}
    return {}


def overlay_qrs(image: Image.Image, page: int, registry: dict, ref_width: int, ref_height: int) -> None:
    sx = image.width / ref_width
    sy = image.height / ref_height
    for qr in registry_entry(registry.get("pages", {}), page).get("qrs", []):
        box = qr["placement_px"]
        x = round(box["x"] * sx)
        y = round(box["y"] * sy)
        width = round(box["w"] * sx)
        height = round(box["h"] * sy)
        asset = Image.open(ROOT / qr["asset"]).convert("RGB")
        asset = asset.resize((width, height), Image.Resampling.NEAREST)
        image.paste(asset, (x, y))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pages", nargs="*", type=int, default=list(range(1, 17)))
    args = parser.parse_args()

    config = yaml.safe_load((ROOT / "build-config.yaml").read_text(encoding="utf-8"))
    registry = yaml.safe_load((ROOT / "qr_registry.yaml").read_text(encoding="utf-8"))
    ref = config["source"]["qr_reference_canvas"]
    output_dir = args.output_dir.resolve() if args.output_dir else ROOT / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)

    for page in args.pages:
        source = ROOT / "assets" / f"page-{page:02d}.jpg"
        image = normalize_page(source)
        overlay_qrs(image, page, registry, int(ref["width"]), int(ref["height"]))
        destination = output_dir / source.name
        image.save(destination, "JPEG", quality=96, subsampling=0, optimize=True)
        print(f"page {page:02d}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
