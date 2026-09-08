#!/usr/bin/env python3
"""Bootstrap manifest-v3.yaml without changing the canonical manifest.yaml.

The v3 manifest is incremental: it preserves the 16 page reference entries and
adds only Phase B assets that actually exist. At this stage that means the
machine-generated SVG QR batch. Visual illustration assets are added later,
lot by lot, after their provenance/rights checks.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(legacy_path: Path, qr_lock_path: Path, approval_path: Path, out_path: Path) -> None:
    legacy = load_yaml(legacy_path)
    qr_lock = load_yaml(qr_lock_path)

    pages = []
    for item in legacy.get("pages", []):
        pages.append(
            {
                "page": item["page"],
                "file": item["file"],
                "sha256": item["sha256"],
                "role": "reference_raster",
            }
        )

    assets = {}
    for asset_id, item in qr_lock.get("assets", {}).items():
        refs = list(item.get("registry_refs", []))
        assets[asset_id] = {
            "id": asset_id,
            "pages": item["pages"],
            "zones": [f"qr:{ref}" for ref in refs],
            "nature": "functional",
            "class": "qr",
            "kind": "qr",
            "path": item["path"],
            "sha256": item["sha256"],
            "derivation": {
                "registry": "qr_registry.yaml",
                "registry_refs": refs,
                "payload_copied_here": False,
            },
            "production": {
                "method": "deterministic",
                "brief": "Generate from exact registry payload only; no image model; no styling.",
                "text_free_required": True,
                "toolchain": [item["generator"]],
                "designator": item.get("designator"),
            },
            "provenance": {
                "status": "verified",
                "sources": [
                    {
                        "path": "qr_registry.yaml",
                        "role": "functional_payload_source",
                    }
                ],
            },
            "licence": {
                "status": "not_applicable",
                "identifier": None,
                "text_or_url": None,
                "holder": None,
            },
            "rights": {
                "status": "not_applicable",
                "redistribution": True,
                "print_authorized": True,
                "web_authorized": True,
                "derivative_authorized": False,
                "notes": "Functional QR encoding; payload changes require registry validation, not graphical derivation.",
            },
            "validation": {
                "documentary": "pass",
                "rights": "not_applicable",
                "text_free": "pass",
                "sha256": "pass",
                "resolution": "vector",
                "machine_decode": "pass",
                "visual": "functional",
                "overall": "pass",
                "blockers": [],
            },
        }

    result = {
        "schema_version": 3,
        "project": "Les Seigneurs de La Chambre",
        "release": "v3.0.0",
        "status": "phase_b_in_progress",
        "phase_a_approval": {
            "path": approval_path.as_posix(),
            "sha256": sha256_file(approval_path),
            "status": "validated",
        },
        "legacy_manifest": {
            "path": legacy_path.as_posix(),
            "sha256": sha256_file(legacy_path),
            "policy": "preserved until v3 migration is complete",
        },
        "pages": pages,
        "assets": assets,
        "qr": {
            "registry": "qr_registry.yaml",
            "generator": qr_lock.get("generator"),
            "output": "svg",
            "dark": "#000000",
            "light": "#FFFFFF",
            "quiet_zone_modules": 4,
            "exact_payload_lock": True,
        },
        "fonts": {},
        "build_contract": {
            "text_source": "pages/NN.yaml:canonical_text",
            "illustrations_must_be_text_free": True,
            "qr_payload_source": "qr_registry.yaml",
            "unknown_metadata_policy": "block",
            "page_04_policy": "PAGE_04_EDITORIAL_ARBITRATION_REQUIRED",
        },
    }

    out_path.write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"Wrote {out_path} with {len(pages)} page references and {len(assets)} Phase B assets")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy", default="manifest.yaml")
    parser.add_argument("--qr-lock", default="assets/qr-svg/manifest.yaml")
    parser.add_argument("--approval", default="docs/migration-text-layer/PHASE_A_APPROVAL.md")
    parser.add_argument("--out", default="manifest-v3.yaml")
    args = parser.parse_args()
    build(Path(args.legacy), Path(args.qr_lock), Path(args.approval), Path(args.out))


if __name__ == "__main__":
    main()
