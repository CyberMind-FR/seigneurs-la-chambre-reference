#!/usr/bin/env python3
"""Validate generated SVG QR assets against qr_registry.yaml.

Checks are blocking:
- every unique registry QR has exactly one expected SVG;
- no unexpected SVG exists in the generated directory;
- SVG contains no text/script/image embedding constructs;
- SHA-256 matches the generated lock manifest;
- rendered SVG decodes to the exact registry payload, character for character.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import cairosvg
import cv2
import yaml

RENDER_SIZES = (600, 800, 1000, 1200, 1600, 2000, 2400)
FORBIDDEN = (b"<text", b"<tspan", b"<foreignobject", b"<script", b"<image")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def expected_from_registry(registry: dict) -> dict[str, dict]:
    expected: dict[str, dict] = {}
    for page_key, page in registry["pages"].items():
        page_id = str(page_key).zfill(2)
        for qr in page.get("qrs", []) or []:
            svg_name = Path(qr["asset"]).with_suffix(".svg").name
            ref = f"{page_id}/{qr['id']}"
            if svg_name in expected:
                if expected[svg_name]["payload"] != qr["payload"]:
                    raise AssertionError(f"Conflicting payloads for {svg_name}")
                expected[svg_name]["refs"].append(ref)
            else:
                expected[svg_name] = {"payload": qr["payload"], "refs": [ref]}
    return expected


def decode_svg(path: Path, expected_payload: str, temp_dir: Path) -> int:
    raw = path.read_bytes()
    for size in RENDER_SIZES:
        png = temp_dir / f"{path.stem}-{size}.png"
        cairosvg.svg2png(
            bytestring=raw,
            write_to=str(png),
            output_width=size,
            output_height=size,
            background_color="#FFFFFF",
        )
        image = cv2.imread(str(png), cv2.IMREAD_COLOR)
        if image is None:
            continue
        decoded, _points, _straight = cv2.QRCodeDetector().detectAndDecode(image)
        if decoded == expected_payload:
            return size
    return 0


def validate(registry_path: Path, out_dir: Path, lock_path: Path, report_path: Path) -> None:
    registry = load_yaml(registry_path)
    lock = load_yaml(lock_path)
    expected = expected_from_registry(registry)

    actual_names = {p.name for p in out_dir.glob("*.svg")}
    expected_names = set(expected)
    if actual_names != expected_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        raise SystemExit(f"SVG QR set mismatch; missing={missing}, extra={extra}")

    lock_by_path = {Path(v["path"]).name: v for v in lock.get("assets", {}).values()}
    if set(lock_by_path) != expected_names:
        raise SystemExit("QR SVG lock manifest does not match generated SVG set")

    temp_dir = Path("dist/qr-svg-validation")
    temp_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []

    for name in sorted(expected_names):
        path = out_dir / name
        raw = path.read_bytes()
        lowered = raw.lower()
        found_forbidden = [token.decode("ascii") for token in FORBIDDEN if token in lowered]
        sha = hashlib.sha256(raw).hexdigest()
        lock_item = lock_by_path[name]
        sha_ok = sha == lock_item.get("sha256")
        size = decode_svg(path, expected[name]["payload"], temp_dir)
        decode_ok = size > 0
        ok = not found_forbidden and sha_ok and decode_ok
        if not ok:
            failures.append(name)
        rows.append(
            {
                "refs": ", ".join(expected[name]["refs"]),
                "name": name,
                "sha": sha,
                "sha_ok": sha_ok,
                "decode_ok": decode_ok,
                "render_size": size,
                "forbidden": ",".join(found_forbidden) if found_forbidden else "none",
            }
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase B — lot QR SVG — rapport de validation",
        "",
        f"Source fonctionnelle unique : `{registry_path.as_posix()}`.",
        f"Actifs SVG uniques : **{len(rows)}**. Les placements peuvent être plus nombreux lorsqu’un même actif est réutilisé.",
        "",
        "| registre | SVG | SHA-256 | SHA lock | décodage exact | rendu validant | structures interdites |",
        "|---|---|---|:---:|:---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['refs']}` | `{row['name']}` | `{row['sha']}` | "
            f"{'OK' if row['sha_ok'] else 'FAIL'} | {'OK' if row['decode_ok'] else 'FAIL'} | "
            f"{row['render_size'] or '-'} px | `{row['forbidden']}` |"
        )
    lines += [
        "",
        f"Résultat : **{'PASS' if not failures else 'FAIL'}**.",
        "",
        "Le validateur rend chaque SVG en PNG à plusieurs tailles et n’accepte qu’un payload décodé strictement identique au registre.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failures:
        raise SystemExit(f"QR SVG validation failed: {failures}")
    print(f"QR SVG validation OK: {len(rows)} unique assets")
    print(f"Report: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="qr_registry.yaml")
    parser.add_argument("--out", default="assets/qr-svg")
    parser.add_argument("--lock", default="assets/qr-svg/manifest.yaml")
    parser.add_argument("--report", default="docs/migration-text-layer/PHASE_B_QR_BATCH.md")
    args = parser.parse_args()
    validate(Path(args.registry), Path(args.out), Path(args.lock), Path(args.report))


if __name__ == "__main__":
    main()
