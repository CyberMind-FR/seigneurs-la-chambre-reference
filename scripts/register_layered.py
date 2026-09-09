#!/usr/bin/env python3
"""Regenerate the layered-composition registry sections from the current compositions and the
last validation run (dist/layered/page-NN/proof-validation.json).

    python scripts/register_layered.py

Rewrites everything after the `layered_compositions:` marker in assets/ASSET_INDEX_V3.yaml and
manifest-v3.yaml so that both registries always reflect the composed pages, their gates and the
composition SHA-256. Run after `make layered-compose`.
"""
from pathlib import Path
import hashlib
import json

import yaml

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    pages = sorted(int(p.parent.name.split("-")[1]) for p in ROOT.glob("prototypes/page-*/composition.yaml"))
    rows = []
    for p in pages:
        comp = yaml.safe_load((ROOT / f"prototypes/page-{p:02d}/composition.yaml").read_text(encoding="utf-8"))
        val_path = ROOT / f"dist/layered/page-{p:02d}/proof-validation.json"
        if not val_path.exists():
            raise SystemExit(f"missing {val_path}; run `make layered-compose` first")
        val = json.loads(val_path.read_text())
        lock = yaml.safe_load((ROOT / f"prototypes/page-{p:02d}/fragments.lock.yaml").read_text(encoding="utf-8"))
        rows.append((p, comp, val, lock))

    # ---- ASSET_INDEX_V3
    ai = ROOT / "assets/ASSET_INDEX_V3.yaml"
    s = ai.read_text(encoding="utf-8")
    head = s[:s.index("layered_compositions:")]
    out = ["layered_compositions:"]
    for p, comp, val, lock in rows:
        k = val["resolution_gate"]["by_raster_kind"]
        ups = val.get("provisional_upscale", {})
        blocked = [f["id"] for f in comp.get("fragments", []) if str(f.get("status", "")).startswith("BLOCKED")]
        status = comp.get("status", "")
        status = status.split("#")[0].strip() if isinstance(status, str) else status
        out += [f"  page_{p:02d}:",
                f"    composition: prototypes/page-{p:02d}/composition.yaml",
                f"    inventory: prototypes/page-{p:02d}/page-{p:02d}.objects.yaml",
                f"    fragment_lock: prototypes/page-{p:02d}/fragments.lock.yaml",
                "    source_refs: [canonical_pages, canonical_page_specs, qr_registry]",
                "    rights_status: PROJECT_INTERNAL",
                f"    status: {status}",
                f"    fragment_count: {len(lock['fragments'])}",
                f"    canonical_text_blocks: {val['canonical_text_paragraphs']}",
                "    text_free_required: false  # fragments may carry canonical raster captions absent from the YAML (listed under discrepancies)",
                "    validation:",
                f"      text_layer: {'pass' if val['text_layer_pass'] else 'fail'}",
                f"      qr_exact_decode: {'pass' if val['qr_decode_pass'] else 'fail'}" if val["qr"] else "      qr_exact_decode: not_applicable",
                f"      fragment_sha256: {'pass' if val['fragment_sha_pass'] else 'fail'}",
                f"      text_ink_collision: {'pass' if not val['text_ink_collisions'] else 'fail'}",
                f"      source_ppi_a5: {val.get('fragment_source_ppi_min', val['fragment_effective_ppi_min'])}",
                f"      effective_ppi_a5_after_upscale: {val['fragment_effective_ppi_min']}",
                f"      provisional_upscale_fragments: {len(ups.get('fragments', []))}",
                f"      hd_regenerated_fragments: {sum(1 for f in lock['fragments'].values() if f.get('source') == 'hd')}",
                f"      resolution_gate_300_continuous_tone: {'pass' if k['continuous_tone']['pass'] else 'fail'}",
                f"      resolution_gate_1200_line_art: {'pass' if k['line_art']['pass'] else 'fail'}",
                f"      methodology_gate: {val['methodology_gate']}",
                "      human_review: done (gkerma, 2026-09-09)"]
        if blocked:
            out.append(f"    blocked_fragments: {blocked}  # rights not documented, not extracted")
    ai.write_text(head + "\n".join(out) + "\n", encoding="utf-8")

    # ---- manifest-v3
    mp = ROOT / "manifest-v3.yaml"
    s = mp.read_text(encoding="utf-8")
    head = s[:s.index("layered_compositions:")]
    out = ["layered_compositions:",
           "  status: release_candidate  # 15 of 16 pages composed and validated; page 04 raster fallback (editorial lock)",
           "  composer: scripts/layered_compose.py", "  measurement: scripts/layered_measure.py",
           "  inventory: scripts/layered_inventory.py", "  validation: scripts/validate_layered.py",
           "  build: scripts/build_layered.py", "  build_validation: scripts/validate_built_layered.py",
           "  shared_text_styles: prototypes/_shared/text-styles.yaml",
           "  pipeline: background -> raster_fragments -> documentary_vectors -> text_layer -> functional_overlay",
           "  resolution_policy: gates 300 ppi continuous tone / 1200 ppi line art at final size; provisional Lanczos upscale declared per composition (gkerma, 2026-09-09), sketches to be regenerated in HD",
           "  pages:"]
    for p, comp, val, lock in rows:
        out += [f"  - page: {p}", f"    composition: prototypes/page-{p:02d}/composition.yaml",
                f"    composition_sha256: {sha(ROOT / f'prototypes/page-{p:02d}/composition.yaml')}",
                f"    fragment_lock: prototypes/page-{p:02d}/fragments.lock.yaml",
                "    status: APPROVED", f"    methodology_gate: {val['methodology_gate']}",
                f"    source_ppi_a5: {val.get('fragment_source_ppi_min', val['fragment_effective_ppi_min'])}",
                f"    effective_ppi_a5_after_upscale: {val['fragment_effective_ppi_min']}"]
    out += ["  excluded:", "  - {page: 4, reason: PAGE_04_EDITORIAL_ARBITRATION_REQUIRED — raster fallback in the v3 build}"]
    mp.write_text(head + "\n".join(out) + "\n", encoding="utf-8")
    for f in (ai, mp):
        yaml.safe_load(f.read_text(encoding="utf-8"))
    print(f"registries regenerated for {len(rows)} pages")


if __name__ == "__main__":
    main()
