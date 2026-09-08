#!/usr/bin/env python3
"""Generate deterministic SVG QR assets from qr_registry.yaml only.

No payload is accepted from the command line or copied into this script.
The registry is the sole functional source.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import segno
import yaml

GENERATOR = "segno==1.6.6"
ERROR_LEVEL = "m"
QUIET_ZONE = 4
DARK = "#000000"
LIGHT = "#FFFFFF"


def load_registry(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "pages" not in data:
        raise SystemExit(f"Invalid QR registry: {path}")
    policy = data.get("policy", {})
    if policy.get("exact_payload_lock") is not True:
        raise SystemExit("qr_registry.yaml must keep exact_payload_lock: true")
    return data


def collect_unique_qrs(registry: dict) -> dict[str, dict]:
    unique: dict[str, dict] = {}
    for page_key, page in registry["pages"].items():
        page_id = str(page_key).zfill(2)
        for qr in page.get("qrs", []) or []:
            payload = qr.get("payload")
            source_asset = qr.get("asset")
            qr_id = qr.get("id")
            if not payload or not source_asset or not qr_id:
                raise SystemExit(f"Incomplete QR record at page {page_id}")
            svg_name = Path(source_asset).with_suffix(".svg").name
            ref = f"{page_id}/{qr_id}"
            existing = unique.get(svg_name)
            if existing:
                if existing["payload"] != payload:
                    raise SystemExit(
                        f"Conflicting payloads for derived asset {svg_name}: "
                        f"{existing['refs'][0]} vs {ref}"
                    )
                existing["refs"].append(ref)
                existing["pages"].append(int(page_id))
                continue
            unique[svg_name] = {
                "payload": payload,
                "refs": [ref],
                "pages": [int(page_id)],
            }
    return unique


def generate(registry_path: Path, out_dir: Path, lock_path: Path) -> None:
    registry = load_registry(registry_path)
    qrs = collect_unique_qrs(registry)
    out_dir.mkdir(parents=True, exist_ok=True)

    lock_assets: dict[str, dict] = {}
    for svg_name in sorted(qrs):
        item = qrs[svg_name]
        qr = segno.make_qr(
            item["payload"],
            error=ERROR_LEVEL,
            boost_error=False,
        )
        out_path = out_dir / svg_name
        qr.save(
            out_path,
            kind="svg",
            scale=1,
            border=QUIET_ZONE,
            dark=DARK,
            light=LIGHT,
            xmldecl=True,
            svgns=True,
            svgclass=None,
            lineclass=None,
            nl=True,
        )
        raw = out_path.read_bytes()
        lowered = raw.lower()
        for forbidden in (b"<text", b"<tspan", b"<foreignobject", b"<script"):
            if forbidden in lowered:
                raise SystemExit(f"Forbidden SVG construct {forbidden!r} in {out_path}")
        asset_id = "qr_" + svg_name.removesuffix(".svg").replace("page-", "p").replace("-", "_")
        lock_assets[asset_id] = {
            "id": asset_id,
            "pages": sorted(set(item["pages"])),
            "registry_refs": item["refs"],
            "path": out_path.as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "generator": GENERATOR,
            "designator": qr.designator,
            "error_level": ERROR_LEVEL.upper(),
            "quiet_zone_modules": QUIET_ZONE,
            "dark": DARK,
            "light": LIGHT,
        }

    lock = {
        "schema_version": 1,
        "source": registry_path.as_posix(),
        "generator": GENERATOR,
        "policy": {
            "exact_payload_lock": True,
            "output": "svg",
            "error_level": ERROR_LEVEL.upper(),
            "quiet_zone_modules": QUIET_ZONE,
            "dark": DARK,
            "light": LIGHT,
            "text_free": True,
        },
        "assets": lock_assets,
    }
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        yaml.safe_dump(lock, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"Generated {len(lock_assets)} unique SVG QR assets from {registry_path}")
    print(f"Lock manifest: {lock_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="qr_registry.yaml")
    parser.add_argument("--out", default="assets/qr-svg")
    parser.add_argument("--lock", default="assets/qr-svg/manifest.yaml")
    args = parser.parse_args()
    generate(Path(args.registry), Path(args.out), Path(args.lock))


if __name__ == "__main__":
    main()
