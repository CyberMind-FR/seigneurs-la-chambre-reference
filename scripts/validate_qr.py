#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import yaml

ROOT = Path(__file__).resolve().parents[1]
registry = yaml.safe_load((ROOT / "qr_registry.yaml").read_text(encoding="utf-8")) or {}
errors: list[str] = []
detector = cv2.QRCodeDetector()
count = 0

for pkey, pdata in registry.get("pages", {}).items():
    page = int(pkey)
    for q in pdata.get("qrs", []):
        count += 1
        asset = ROOT / q["asset"]
        if not asset.exists():
            errors.append(f"page {page} / {q['id']}: missing QR asset {q['asset']}")
            continue

        img = cv2.imread(str(asset))
        if img is None:
            errors.append(f"page {page} / {q['id']}: unreadable QR asset")
            continue

        # Grossissement nearest-neighbour pour un décodage robuste sans altérer les modules.
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        decoded, points, _ = detector.detectAndDecode(img)
        if decoded != q["payload"]:
            errors.append(
                f"page {page} / {q['id']}: decoded={decoded!r}, expected={q['payload']!r}"
            )

        b = q.get("placement_px", {})
        if not all(int(b.get(k, 0)) > 0 for k in ("w", "h")):
            errors.append(f"page {page} / {q['id']}: invalid placement dimensions")

if count == 0:
    errors.append("qr_registry.yaml contains no QR")

if errors:
    print("QR VALIDATION FAILED")
    for item in errors:
        print(" -", item)
    sys.exit(1)

print(f"QR VALIDATION OK: {count} deterministic QR assets")
