#!/usr/bin/env python3
"""Derive the object-level inventory of a page from its layered composition.

    python scripts/layered_inventory.py 5 [--dist dist/layered]

Writes prototypes/page-NN/page-NN.objects.yaml following the production hierarchy
``page -> regions -> objects -> subobjects -> layers``. Regions are derived deterministically
from the composition geometry (header, narrative, then one region per structural frame
rectangle). Every raster fragment carries its provenance (canonical page), its source bbox,
its SHA-256 and effective ppi from the last composition run, and its text relationship;
text zones are first-class objects composed as live text from pages/NN.yaml:canonical_text.
The inventory never adds an object that is not in the composition: it is a view, the
composition YAML stays the editable source.
"""
from pathlib import Path
import argparse
import json

import yaml

ROOT = Path(__file__).resolve().parents[1]

ROLE_CLASS = {
    "documentary_illustration": "illustration",
    "documentary_illustration_with_canonical_raster_caption": "composite",
    "documentary_detail": "illustration",
    "documentary_detail_with_canonical_raster_caption": "composite",
    "documentary_map": "documentary_map",
    "heraldry": "heraldry",
    "heraldry_with_canonical_raster_caption": "composite",
    "ornament": "ornament",
    "icon": "icon",
    "canonical_raster_caption_absent_from_yaml": "intrinsic_document_text",
    "canonical_raster_text_absent_from_yaml": "intrinsic_document_text",
}


def bbox(b):
    if isinstance(b, dict):
        return [int(b["x"]), int(b["y"]), int(b["w"]), int(b["h"])]
    return [int(v) for v in b]


def centroid_in(b, region):
    cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
    x, y, w, h = region
    return x <= cx <= x + w and y <= cy <= y + h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page", type=int)
    ap.add_argument("--dist", default="dist/layered")
    args = ap.parse_args()
    page = args.page
    comp_path = ROOT / f"prototypes/page-{page:02d}/composition.yaml"
    comp = yaml.safe_load(comp_path.read_text(encoding="utf-8"))
    page_spec = yaml.safe_load((ROOT / comp["canonical_text"]["path"]).read_text(encoding="utf-8"))
    out_dir = ROOT / args.dist / f"page-{page:02d}"
    report = json.loads((out_dir / "composition-report.json").read_text()) if (out_dir / "composition-report.json").exists() else {}
    validation = json.loads((out_dir / "proof-validation.json").read_text()) if (out_dir / "proof-validation.json").exists() else {}
    frag_report = {f["id"]: f for f in report.get("fragments", [])}
    src_w, src_h = report.get("source_px", [None, None])

    # Regions: header (above first heading/body block), narrative, one per structural frame rect.
    frames = [bbox(v["bbox_px"]) for v in comp.get("vectors", []) or [] if v.get("kind") == "rect"]
    frames.sort(key=lambda r: r[1])
    text_blocks = comp.get("text_blocks", [])
    body_tops = [bbox(t["bbox_px"])[1] for t in text_blocks if t["style"] in ("heading", "body")]
    header_bottom = min(body_tops) if body_tops else 0
    narrative_bottom = frames[0][1] if frames else (src_h or 0)
    regions = [
        {"id": "R01", "role": "header_identity", "bbox_px": [0, 0, src_w or 0, header_bottom]},
        {"id": "R02", "role": "narrative", "bbox_px": [0, header_bottom, src_w or 0, max(0, narrative_bottom - header_bottom)]},
    ]
    for i, fr in enumerate(frames, 3):
        regions.append({"id": f"R{i:02d}", "role": "structural_frame_band", "bbox_px": fr})
    regions.append({"id": f"R{len(regions) + 1:02d}", "role": "page_wide_marginalia", "bbox_px": None})

    def region_for(b):
        for r in regions:
            if r["bbox_px"] and centroid_in(b, r["bbox_px"]):
                return r["id"]
        return regions[-1]["id"]

    objects = []
    for f in comp.get("fragments", []):
        b = bbox(f["bbox_px"])
        rep = frag_report.get(f["id"], {})
        role = f.get("role", "documentary_illustration")
        objects.append({
            "id": f"P{page:02d}-O-{f['id']}",
            "visual_description": f.get("note") or f["id"].replace("_", " "),
            "object_class": ROLE_CLASS.get(role, "other_verified"),
            "source_bbox_px": b,
            "parent_region": region_for(b),
            "layer_target": "raster_fragment",
            "text_relationship": ("canonical_raster_caption" if "caption" in role or "absent_from_yaml" in role
                                  else "intrinsic_document_text" if role == "documentary_map" else "none"),
            "extraction_action": f.get("treatment", "crop_only"),
            "masks_px": rep.get("masks_px", []),
            "provenance": "canonical_pages",
            "source_ref": comp["source"]["path"],
            "sha256": rep.get("sha256"),
            "effective_ppi_a5": rep.get("effective_ppi"),
            "dirty_edges": rep.get("dirty_edges", []),
            "review_status": f.get("status"),
        })
    text_zones = []
    for t in text_blocks:
        b = bbox(t["bbox_px"])
        text_zones.append({
            "id": f"P{page:02d}-T-{t['key']}",
            "role": t["key"],
            "canonical_block": t["block"],
            "expect": t.get("expect"),
            "bbox_px": b,
            "parent_region": region_for(b),
            "layer_target": "text_layer",
            "compose_as": "live_text",
            "style": t["style"],
            "authority": f"{comp['canonical_text']['path']}:{comp['canonical_text'].get('key', 'canonical_text')}",
        })
    functional = []
    for q in report.get("qr", []):
        b = bbox(q["bbox_px"])
        functional.append({
            "id": f"P{page:02d}-F-{q['id']}",
            "object_class": "qr",
            "source_bbox_px": b,
            "parent_region": region_for(b),
            "layer_target": "functional_overlay",
            "extraction_action": "do_not_extract_use_deterministic_svg",
            "asset": q["svg"],
            "payload_authority": "qr_registry.yaml",
            "review_status": "VERIFIED_FROM_CANONICAL_PAGE_SPEC",
        })
    frames_out = [{"id": f"P{page:02d}-FR{i:02d}", "kind": v.get("kind"), "bbox_px": bbox(v["bbox_px"]) if v.get("bbox_px") else [v["from"], v["to"]],
                   "layer_target": "documentary_vector", "extraction_action": "layout_vector"}
                  for i, v in enumerate(comp.get("vectors", []) or [], 1)]

    fragments_ok = all(o["sha256"] for o in objects)
    inventory = {
        "schema_version": 2,
        "project": "Les Seigneurs de La Chambre",
        "page": page,
        "title": comp.get("title", page_spec.get("title")),
        "status": comp.get("status"),
        "generated_from": {"composition": str(comp_path.relative_to(ROOT)), "composition_run": validation.get("pdf_sha256")},
        "canonical_reference": {"path": comp["source"]["path"], "sha256": comp["source"]["sha256"], "dimensions_px": [src_w, src_h]},
        "principle": {
            "hierarchy": "page -> regions -> objects -> subobjects -> layers",
            "asset_spec_role": "macro_layout_reference_only",
            "text_zones_are_first_class_objects": True,
            "text_content_authority": f"{comp['canonical_text']['path']}:canonical_text",
            "image_text_is_not_editorial_authority": True,
            "qr_payload_authority": "qr_registry.yaml",
        },
        "regions": regions,
        "objects": objects,
        "text_zones": text_zones,
        "functional_objects": functional,
        "structural_frames": frames_out,
        "discrepancies": comp.get("discrepancies", {}),
        "completeness_gate": {
            "status": "INSPECTED_PENDING_HUMAN_REVIEW" if comp.get("status", "").startswith("INSPECTED") else "PASS" if fragments_ok else "BLOCKED",
            "native_raster_dimensions_recorded": src_w is not None,
            "all_objects_have_sha256": fragments_ok,
            "all_editorial_text_composed_live": True,
            "qr_accounted_for": bool(functional) or not (page_spec.get("qr", {}).get("present")),
            "second_visual_sweep_by_human": "pending",
            "last_methodology_gate": validation.get("methodology_gate"),
        },
    }
    out = comp_path.parent / f"page-{page:02d}.objects.yaml"
    out.write_text(yaml.safe_dump(inventory, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {len(objects)} objects, {len(text_zones)} text zones, {len(functional)} functional, gate {inventory['completeness_gate']['status']}")


if __name__ == "__main__":
    main()
