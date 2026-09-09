#!/usr/bin/env python3
"""Phase C — inscription des images HD déposées dans assets/hd/page-NN/ (jamais d'approbation).

Pour chaque `assets/hd/page-NN/<fragment>.png|jpg` dont le nom correspond à un fragment de
`prototypes/page-NN/composition.yaml`, écrit ou met à jour l'entrée correspondante de
`prototypes/page-NN/hd-sources.yaml` (fichier possédé par ce script) :

* nouvelle image, ou SHA-256 différent : statut remis à `PENDING_REVIEW`, `approved_by/on` effacés ;
* image inchangée : entrée conservée telle quelle (statut, droits, approbation) ;
* `prompt_id` / `prompt_sha256` recopiés depuis `assets/hd/prompts/manifest.json` ;
* `assets/hd/common/paper-texture.png` → entrée `background`.

Les grilles (`composition.yaml`) ne sont jamais modifiées. L'approbation (`status: APPROVED`,
`rights`, `approved_by`, `approved_on`, `caption_resolution`) est une édition humaine du fichier
`hd-sources.yaml`, contrôlée ensuite par `scripts/hd_check.py`.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import json
import sys

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXTS = {".png", ".jpg", ".jpeg"}


def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generator", default="ChatGPT (génération d'images)", help="outil déclaré pour les nouvelles entrées")
    ap.add_argument("--pages", nargs="*", type=int, help="limiter à ces pages")
    args = ap.parse_args()
    manifest = json.loads((ROOT / "assets/hd/prompts/manifest.json").read_text(encoding="utf-8"))
    by_expected = {v["expected_file"]: (pid, v) for pid, v in manifest["fragments"].items()}
    today = dt.date.today().isoformat()
    changed = 0
    for comp_path in sorted((ROOT / "prototypes").glob("page-*/composition.yaml")):
        comp = yaml.safe_load(comp_path.read_text(encoding="utf-8"))
        page = comp["page"]
        if args.pages and page not in args.pages:
            continue
        frag_ids = {f["id"] for f in comp.get("fragments", [])}
        hd_path = comp_path.parent / "hd-sources.yaml"
        hd = yaml.safe_load(hd_path.read_text(encoding="utf-8")) if hd_path.exists() else {}
        hd = hd or {"schema_version": 1, "page": page, "fragments": {}}
        hd.setdefault("fragments", {})
        dirty = False
        for img in sorted((ROOT / f"assets/hd/page-{page:02d}").glob("*")):
            if img.suffix.lower() not in EXTS:
                continue
            fid = img.stem
            if fid not in frag_ids:
                print(f"page {page:02d}: {img.name} ne correspond à aucun fragment — ignoré")
                continue
            rel = str(img.relative_to(ROOT))
            digest = sha256(img)
            with Image.open(img) as im:
                px = [im.width, im.height]
            entry = hd["fragments"].get(fid) or {}
            if entry.get("sha256") == digest and entry.get("path") == rel:
                continue
            pid, spec = by_expected.get(rel, (None, None))
            entry = {
                "path": rel, "sha256": digest, "px": px, "status": "PENDING_REVIEW",
                "generator": entry.get("generator") or args.generator,
                "prompt_id": pid, "prompt_sha256": spec["prompt_sha256"] if spec else None,
                "ingested_on": today, "rights": entry.get("rights") or "NOT_DOCUMENTED",
                "label": "reconstitution", "approved_by": None, "approved_on": None,
            }
            if spec and spec["route"].endswith("caption_to_canon"):
                entry["caption_resolution"] = entry.get("caption_resolution")  # to be filled by the reviewer
            hd["fragments"][fid] = entry
            dirty = True
            changed += 1
            print(f"page {page:02d}: {fid} ← {rel} ({px[0]}×{px[1]}) PENDING_REVIEW")
        bg = ROOT / "assets/hd/common/paper-texture.png"
        if bg.exists():
            digest = sha256(bg)
            if (hd.get("background") or {}).get("sha256") != digest:
                hd["background"] = {"path": str(bg.relative_to(ROOT)), "sha256": digest, "status": "PENDING_REVIEW",
                                    "mode": "cover", "prompt_id": manifest.get("background", {}).get("prompt_id"),
                                    "ingested_on": today, "rights": "NOT_DOCUMENTED", "approved_by": None, "approved_on": None}
                dirty = True
                changed += 1
        if dirty:
            hd_path.write_text("# Fichier possédé par scripts/hd_ingest.py — statut/droits/approbation édités par la revue humaine.\n"
                               + yaml.safe_dump(hd, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"HD INGEST OK ({changed} entrée(s) écrite(s))")


if __name__ == "__main__":
    sys.exit(main())
