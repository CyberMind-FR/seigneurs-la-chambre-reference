#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages"
ASSETS = ROOT / "assets"
errors = []

def fail(msg: str):
    errors.append(msg)

for required in [ROOT / "style.yaml", ROOT / "manifest.yaml", ROOT / "corrections.yaml", ROOT / "REGENERATION_RULES.md"]:
    if not required.exists():
        fail(f"missing: {required.relative_to(ROOT)}")

manifest_path = ROOT / "manifest.yaml"
if manifest_path.exists():
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    pages = manifest.get("pages", [])
    if len(pages) != 15:
        fail(f"manifest: expected 15 pages, got {len(pages)}")

for n in range(1, 16):
    page_file = PAGES / f"{n:02d}.yaml"
    asset_file = ASSETS / f"page-{n:02d}.jpg"
    if not page_file.exists():
        fail(f"missing page descriptor: pages/{n:02d}.yaml")
        continue
    data = yaml.safe_load(page_file.read_text(encoding="utf-8")) or {}
    if data.get("page") != n:
        fail(f"pages/{n:02d}.yaml: page number mismatch")
    if not data.get("content_locked", False):
        fail(f"pages/{n:02d}.yaml: content_locked must be true")
    txt = str(data.get("canonical_text", "")).strip()
    if not txt:
        fail(f"pages/{n:02d}.yaml: canonical_text is empty")
    if not asset_file.exists():
        fail(f"missing visual reference: assets/page-{n:02d}.jpg")
    else:
        expected = data.get("visual_reference_sha256")
        if expected:
            actual = hashlib.sha256(asset_file.read_bytes()).hexdigest()
            if actual != expected:
                fail(f"assets/page-{n:02d}.jpg: SHA-256 mismatch")

# Garde-fous éditoriaux explicites.
p4 = yaml.safe_load((PAGES/"04.yaml").read_text(encoding="utf-8")) if (PAGES/"04.yaml").exists() else {}
if "Académie de Maurienne" in str(p4.get("canonical_text", "")):
    fail("pages/04.yaml: forbidden current-status mention 'Académie de Maurienne'")

p14 = yaml.safe_load((PAGES/"14.yaml").read_text(encoding="utf-8")) if (PAGES/"14.yaml").exists() else {}
t14 = str(p14.get("canonical_text", ""))
for forbidden in ["Collecte Fondation du Patrimoine (75%)", "Fabrice GALOPO et Gérald KERMA"]:
    if forbidden in t14:
        fail(f"pages/14.yaml: forbidden obsolete content: {forbidden}")
for required in ["Collecte Fondation du Patrimoine (66%)", "Fabrice GALOPO, André GRANGE, Gérald KERMA"]:
    if required not in t14:
        fail(f"pages/14.yaml: missing canonical content: {required}")

p15 = yaml.safe_load((PAGES/"15.yaml").read_text(encoding="utf-8")) if (PAGES/"15.yaml").exists() else {}
t15 = str(p15.get("canonical_text", ""))
for forbidden in ["Fondation du Patrimoine 75 %", "Fabrice GALOPO & Gérald KERMA"]:
    if forbidden in t15:
        fail(f"pages/15.yaml: forbidden obsolete content: {forbidden}")
for required in [
    "Fondation du Patrimoine 66 %",
    "Auteurs : Fabrice GALOPO, André GRANGE, Gérald KERMA — Commission Histoire et Patrimoine",
]:
    if required not in t15:
        fail(f"pages/15.yaml: missing canonical content: {required}")

if errors:
    print("REFERENCE VALIDATION FAILED")
    for e in errors:
        print(f" - {e}")
    sys.exit(1)

print("Reference package OK: locked content, strict corrections and visual hashes verified.")
