#!/usr/bin/env python3
"""Apply the three verified local text corrections without using a font."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def save_and_measure(path: Path, edited: np.ndarray, zones: list[tuple[int, int, int, int]]) -> dict:
    with Image.open(path) as src:
        before = np.asarray(src.convert("RGB"))
        qtables = src.quantization
    Image.fromarray(edited).save(path, "JPEG", qtables=qtables, subsampling=0)
    after = np.asarray(Image.open(path).convert("RGB"))
    delta = np.abs(after.astype(np.int16) - before.astype(np.int16)).sum(axis=2)
    inside = np.zeros(delta.shape, dtype=bool)
    for x0, y0, x1, y1 in zones:
        inside[y0:y1, x0:x1] = True
    return {
        "asset": str(path.relative_to(ROOT)),
        "zones_xyxy": zones,
        "pixels_delta_gt_12_inside": int(((delta > 12) & inside).sum()),
        "pixels_delta_gt_12_outside": int(((delta > 12) & ~inside).sum()),
        "max_rgb_delta_outside": int(delta[~inside].max()),
    }


def page14() -> dict:
    path = ROOT / "assets/page-14.jpg"
    with Image.open(path) as src:
        arr = np.asarray(src.convert("RGB")).copy()
    original = arr.copy()
    # couventdeelachambre -> couventdelachambre: delete the second e and its
    # nine-pixel advance, then shift the untouched suffix left.
    arr[642:672, 346:451] = original[642:672, 355:460]
    arr[642:672, 451:460] = original[642:672, 460:469]
    return save_and_measure(path, arr, [(346, 642, 469, 672)])


def page15() -> dict:
    path = ROOT / "assets/page-15.jpg"
    with Image.open(path) as src:
        arr = np.asarray(src.convert("RGB")).copy()
    original = arr.copy()
    # "de patrimoine" -> "le patrimoine": erase d with a nearby background
    # sample, then reuse the italic l from "la" on the same line.
    arr[1126:1162, 404:413] = original[1126:1162, 740:749]
    arr[1126:1162, 406:413] = original[1126:1162, 625:632]
    # GALLOPO -> GALOPO: remove the second L's eight-pixel advance and shift
    # the remainder of the legal line left by the same amount.
    arr[1355:1378, 344:782] = original[1355:1378, 352:790]
    arr[1355:1378, 782:790] = original[1355:1378, 790:798]
    return save_and_measure(
        path,
        arr,
        [(404, 1126, 422, 1162), (344, 1355, 798, 1378)],
    )


if __name__ == "__main__":
    print(json.dumps([page14(), page15()], ensure_ascii=False, indent=2))
