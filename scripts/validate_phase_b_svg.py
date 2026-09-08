#!/usr/bin/env python3
"""Validate the first non-QR Phase B SVG batch.

Checks are structural and policy-oriented. Human review gates remain explicit for
heraldry and page 10 geometry; this script must not silently upgrade them.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

INDEX = Path("assets/ASSET_INDEX_V3.yaml")
REPORT = Path("docs/migration-text-layer/PHASE_B_SVG_BATCH.md")
FORBIDDEN_TAGS = {"text", "tspan", "image", "script", "foreignObject"}
EXPECTED = (
    "heraldry_la_chambre_svg",
    "page_10_castle_reconstruction_svg",
    "ornament_bundle_svg",
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_svg(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.fromstring(path.read_bytes())
    except Exception as exc:
        return [f"invalid XML: {exc}"]

    for elem in root.iter():
        name = local_name(elem.tag)
        if name in FORBIDDEN_TAGS:
            errors.append(f"forbidden element <{name}>")
        href = elem.attrib.get("href") or elem.attrib.get("{http://www.w3.org/1999/xlink}href")
        if href and not href.startswith("#"):
            errors.append(f"external href: {href}")
    return errors


def main() -> None:
    index = yaml.safe_load(INDEX.read_text(encoding="utf-8"))
    produced = index.get("produced_assets", {})
    rows = []
    failures = []

    for asset_id in EXPECTED:
        item = produced.get(asset_id)
        if not item:
            failures.append(f"{asset_id}: missing produced asset registration")
            continue
        path = Path(item["path"])
        if not path.is_file():
            failures.append(f"{asset_id}: missing file {path}")
            continue

        digest = sha256(path)
        sha_ok = digest == item.get("sha256")
        errors = inspect_svg(path)
        source_ok = bool(item.get("source_refs"))
        text_policy_ok = item.get("text_free_required") is True and not errors

        if asset_id == "page_10_castle_reconstruction_svg":
            review_ok = item.get("status") == "PRODUCED_PENDING_GEOMETRY_REVIEW" and item.get("release_ready") is False
        elif asset_id == "heraldry_la_chambre_svg":
            review_ok = item.get("status") == "PRODUCED_PENDING_HERALDIC_REVIEW" and item.get("release_ready") is False
        else:
            review_ok = item.get("status") == "PRODUCED_VALIDATED" and item.get("release_ready") is True

        ok = sha_ok and source_ok and text_policy_ok and review_ok
        if not ok:
            failures.append(asset_id)

        rows.append({
            "id": asset_id,
            "path": path.as_posix(),
            "sha": digest,
            "sha_ok": sha_ok,
            "source_ok": source_ok,
            "text_ok": text_policy_ok,
            "review_gate_ok": review_ok,
            "status": item.get("status"),
            "errors": ", ".join(errors) if errors else "none",
        })

    heraldry_path = Path("assets/svg/heraldry-la-chambre.svg")
    if heraldry_path.is_file():
        raw = heraldry_path.read_text(encoding="utf-8").lower()
        for color in ("#245a93", "#d8b34a", "#963536"):
            if color not in raw:
                failures.append(f"heraldry missing canonical semantic color {color}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Phase B — premier lot SVG documentaire / reconstitution",
        "",
        "Ce rapport valide la structure et les verrous de politique. Il ne remplace pas la revue humaine héraldique ni la revue géométrique du château de Notre-Dame-du-Cruet.",
        "",
        "| actif | SHA | sources | texte/embedding | gate de revue | statut | erreurs |",
        "|---|:---:|:---:|:---:|:---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | {'OK' if row['sha_ok'] else 'FAIL'} | {'OK' if row['source_ok'] else 'FAIL'} | "
            f"{'OK' if row['text_ok'] else 'FAIL'} | {'OK' if row['review_gate_ok'] else 'FAIL'} | "
            f"`{row['status']}` | `{row['errors']}` |"
        )
    lines += [
        "",
        f"Résultat structurel : **{'PASS' if not failures else 'FAIL'}**.",
        "",
        "Gates humains conservés :",
        "- héraldique : revue visuelle/héraldique requise avant usage final ;",
        "- page 10 : revue géométrique contre `assets/reference/page-10-plan-reel.jpg` requise avant usage final ;",
        "- ornements : utilisables comme éléments non documentaires sans texte.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failures:
        raise SystemExit("Phase B SVG validation failed: " + "; ".join(failures))
    print("Phase B SVG structural validation OK: 3 assets")


if __name__ == "__main__":
    main()
