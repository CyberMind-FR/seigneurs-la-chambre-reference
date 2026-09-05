#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Fichiers structurants obligatoires.
for name in [
    "manifest.yaml",
    "style.yaml",
    "corrections.yaml",
    "build-config.yaml",
    "qr_registry.yaml",
    "REGENERATION_RULES.md",
]:
    if not (ROOT / name).exists():
        error(f"missing required file: {name}")

manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8")) or {}
entries = manifest.get("pages", [])
if len(entries) != 15:
    error(f"manifest must contain 15 pages, got {len(entries)}")

seen: set[int] = set()
for entry in entries:
    page = int(entry.get("page", 0))
    seen.add(page)
    expected_file = f"assets/page-{page:02d}.jpg"
    if entry.get("file") != expected_file:
        error(f"page {page}: manifest file must be {expected_file}")
    asset = ROOT / expected_file
    if not asset.exists():
        error(f"page {page}: missing asset {expected_file}")
    else:
        actual = sha256(asset)
        if entry.get("sha256") != actual:
            error(f"page {page}: manifest SHA-256 mismatch")

    descriptor = ROOT / "pages" / f"{page:02d}.yaml"
    if not descriptor.exists():
        error(f"page {page}: missing descriptor pages/{page:02d}.yaml")
        continue
    data = yaml.safe_load(descriptor.read_text(encoding="utf-8")) or {}
    if int(data.get("page", 0)) != page:
        error(f"page {page}: descriptor page number mismatch")
    if not data.get("content_locked", False):
        error(f"page {page}: content_locked must be true")
    if not str(data.get("canonical_text", "")).strip():
        error(f"page {page}: canonical_text is empty")

if seen != set(range(1, 16)):
    error(f"manifest page numbers must be 1..15, got {sorted(seen)}")

# Charte colorisée désormais obligatoire.
style = yaml.safe_load((ROOT / "style.yaml").read_text(encoding="utf-8")) or {}
if style.get("version") != "2.0-colorized-exhibition":
    error("style.yaml must use version 2.0-colorized-exhibition")
profile = style.get("colorization_profile", {})
if profile.get("status") != "locked":
    error("colorization_profile must be locked")

# Ordre canonique déclaré dans le build.
build = yaml.safe_load((ROOT / "build-config.yaml").read_text(encoding="utf-8")) or {}
source = build.get("source", {})
if int(source.get("page_count", 0)) != 15:
    error("build-config.yaml source.page_count must be 15")
order = source.get("canonical_order", {})
if len(order) != 15:
    error("build-config.yaml canonical_order must contain 15 entries")

# Garde-fous éditoriaux connus.
for page, forbidden in {
    4: ["Académie de Maurienne"],
    13: ["sdlc.gk2.secubox.in", "sdlc.../diaporama", "sdlc.../livret.pdf"],
    14: ["Collecte Fondation du Patrimoine (75%)", "Fabrice GALOPO et Gérald KERMA"],
    15: ["Fondation du Patrimoine 75 %", "Fabrice GALOPO & Gérald KERMA"],
}.items():
    descriptor = ROOT / "pages" / f"{page:02d}.yaml"
    if not descriptor.exists():
        continue
    text = str((yaml.safe_load(descriptor.read_text(encoding="utf-8")) or {}).get("canonical_text", ""))
    for token in forbidden:
        if token in text:
            error(f"page {page}: obsolete/forbidden content: {token}")

corrections = yaml.safe_load((ROOT / "corrections.yaml").read_text(encoding="utf-8")) or {}
page10_forbidden = corrections.get("page_10", {}).get("forbidden", [])
if "Vous êtes ici" not in page10_forbidden:
    error("corrections.yaml page_10 must forbid 'Vous êtes ici'")
page14_forbidden = corrections.get("page_14", {}).get("forbidden", [])
if not any("portrait" in str(v).lower() and "philippe" in str(v).lower() for v in page14_forbidden):
    error("corrections.yaml page_14 must forbid the Philippe DEMARIO portrait")

if errors:
    print("REFERENCE VALIDATION FAILED")
    for item in errors:
        print(" -", item)
    sys.exit(1)

print("REFERENCE VALIDATION OK")
