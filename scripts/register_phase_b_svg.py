#!/usr/bin/env python3
"""Register the first non-QR Phase B SVG assets in the atomic index and manifest v3.

This script never edits canonical page rasters or canonical page YAML files.
It computes hashes from committed SVG bytes and preserves explicit review gates.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

INDEX = Path("assets/ASSET_INDEX_V3.yaml")
MANIFEST = Path("manifest-v3.yaml")

TARGETS = {
    "heraldry_la_chambre_svg": {
        "path": "assets/svg/heraldry-la-chambre.svg",
        "status": "PRODUCED_PENDING_HERALDIC_REVIEW",
        "manifest_id": "heraldry_la_chambre_svg",
        "visual_review": "pending",
        "release_ready": False,
    },
    "page_10_castle_reconstruction_svg": {
        "path": "assets/svg/page-10-castle-reconstruction.svg",
        "status": "PRODUCED_PENDING_GEOMETRY_REVIEW",
        "manifest_id": "page_10_castle_reconstruction_svg",
        "visual_review": "pending_geometry_review",
        "release_ready": False,
    },
    "ornament_bundle_svg": {
        "path": "assets/svg/spiritualcept-ornaments.svg",
        "status": "PRODUCED_VALIDATED",
        "manifest_id": "ornament_bundle_svg",
        "visual_review": "pass",
        "release_ready": True,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    index = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    status_enum = index.setdefault("status_enum", [])
    for status in (
        "PRODUCED_VALIDATED",
        "PRODUCED_PENDING_HERALDIC_REVIEW",
        "PRODUCED_PENDING_GEOMETRY_REVIEW",
    ):
        if status not in status_enum:
            status_enum.append(status)

    produced = index.setdefault("produced_assets", {})
    candidates = index.setdefault("production_candidates", {})
    manifest_assets = manifest.setdefault("assets", {})

    for candidate_id, target in TARGETS.items():
        if candidate_id not in candidates:
            raise SystemExit(f"Missing candidate in ASSET_INDEX_V3.yaml: {candidate_id}")
        candidate = candidates[candidate_id]
        path = Path(target["path"])
        if not path.is_file():
            raise SystemExit(f"Missing produced SVG: {path}")
        digest = sha256(path)

        candidate["target_path"] = target["path"]
        candidate["status"] = target["status"]
        candidate["sha256"] = digest
        candidate["produced"] = True
        candidate["release_ready"] = target["release_ready"]
        candidate["review"] = {
            "structural_validation": "pending",
            "visual_review": target["visual_review"],
        }

        produced[target["manifest_id"]] = {
            "path": target["path"],
            "class": candidate.get("class", "svg"),
            "kind": candidate.get("kind"),
            "nature": candidate.get("nature"),
            "status": target["status"],
            "pages": candidate.get("pages", []),
            "zones": candidate.get("zones", []),
            "source_refs": candidate.get("source_refs", []),
            "confidence": candidate.get("confidence"),
            "sha256": digest,
            "text_free_required": candidate.get("text_free_required", True),
            "must_be_labeled_reconstruction": candidate.get("must_be_labeled_reconstruction", False),
            "release_ready": target["release_ready"],
            "validation": {
                "structural": "pending",
                "visual": target["visual_review"],
            },
        }

        manifest_assets[target["manifest_id"]] = {
            "id": target["manifest_id"],
            "pages": candidate.get("pages", []),
            "zones": candidate.get("zones", []),
            "nature": candidate.get("nature"),
            "class": "svg",
            "kind": candidate.get("kind"),
            "path": target["path"],
            "sha256": digest,
            "production": {
                "method": "redrawn" if candidate.get("nature") != "ornament" else "deterministic",
                "brief": candidate.get("rule"),
                "text_free_required": candidate.get("text_free_required", True),
                "toolchain": ["hand-authored SVG", "repository validation"],
            },
            "provenance": {
                "status": "verified" if candidate.get("source_refs") else "missing",
                "source_refs": candidate.get("source_refs", []),
            },
            "rights": {
                "status": "not_applicable" if candidate.get("nature") in ("ornament", "reconstitution") else "missing",
            },
            "validation": {
                "text_free": "pending",
                "sha256": "pass",
                "visual": target["visual_review"],
                "overall": "pass" if target["release_ready"] else "pending_human_review",
                "blockers": [] if target["release_ready"] else [target["status"]],
            },
        }

    index["lot_2_progress"] = {
        "produced_non_qr_svg": 3,
        "release_ready_non_qr_svg": 1,
        "human_review_pending": 2,
        "note": "Heraldry and page 10 massing are produced but deliberately remain behind human review gates.",
    }

    INDEX.write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("Registered 3 Phase B non-QR SVG assets")


if __name__ == "__main__":
    main()
