#!/usr/bin/env python3
"""Phase C — contrôle des sources HD déclarées (prototypes/page-NN/hd-sources.yaml).

Échoue (exit 1) si :
* un fichier déclaré manque ou n'a pas le SHA-256 enregistré ;
* le ratio de l'image s'écarte de plus de `hd_aspect_tolerance` (3 % par défaut) du ratio de la grille ;
* une entrée `APPROVED` n'a pas `approved_by`, `approved_on`, des droits acceptés
  (CLEARED / PROJECT_INTERNAL / ASSOCIATION_PROVIDED) ou, pour un fragment `*_captioned`,
  une `caption_resolution` ;
* une entrée vise un fragment absent de la composition, ou un fragment exclu de la voie HD
  (ex. couvertures d'ouvrages, statut BLOCKED_*) ;
* la largeur de l'image est sous le gate 300/1200 ppi à la taille A5 (les autres formats sont rapportés).
Avertit si un fichier de assets/hd/ n'est déclaré nulle part (orphelin).
"""
from pathlib import Path
import hashlib
import json
import sys

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ACCEPTED_RIGHTS = {"CLEARED", "PROJECT_INTERNAL", "ASSOCIATION_PROVIDED"}
STATUSES = {"PENDING_REVIEW", "APPROVED", "REJECTED"}


def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    manifest = json.loads((ROOT / "assets/hd/prompts/manifest.json").read_text(encoding="utf-8"))
    by_expected = {v["expected_file"]: v for v in manifest["fragments"].values()}
    fails, warns, declared, counts = [], [], set(), {"declared": 0, "approved": 0}
    for comp_path in sorted((ROOT / "prototypes").glob("page-*/composition.yaml")):
        comp = yaml.safe_load(comp_path.read_text(encoding="utf-8"))
        page = comp["page"]
        hd_path = comp_path.parent / "hd-sources.yaml"
        if not hd_path.exists():
            continue
        hd = yaml.safe_load(hd_path.read_text(encoding="utf-8")) or {}
        if int(hd.get("page", page)) != page:
            fails.append(f"{hd_path}: page {hd.get('page')} != {page}")
        frags = {f["id"]: f for f in comp.get("fragments", [])}
        tol = float(comp.get("validation", {}).get("hd_aspect_tolerance", 0.03))
        entries = dict(hd.get("fragments") or {})
        if hd.get("background"):
            entries["__background__"] = hd["background"]
        for fid, e in entries.items():
            counts["declared"] += 1
            tag = f"page {page:02d} {fid}"
            if e.get("status") not in STATUSES:
                fails.append(f"{tag}: statut inconnu {e.get('status')!r}")
            p = ROOT / str(e.get("path", ""))
            declared.add(str(e.get("path")))
            if not p.exists():
                fails.append(f"{tag}: fichier manquant {e.get('path')}")
                continue
            if sha256(p) != e.get("sha256"):
                fails.append(f"{tag}: SHA-256 différent de l'entrée (relancer hd_ingest, puis ré-approuver)")
            with Image.open(p) as im:
                iw, ih = im.size
            if fid == "__background__":
                if e.get("status") == "APPROVED" and (not e.get("approved_by") or not e.get("approved_on") or e.get("rights") not in ACCEPTED_RIGHTS):
                    fails.append(f"{tag}: APPROVED exige approved_by, approved_on et des droits acceptés")
                continue
            f = frags.get(fid)
            if f is None:
                fails.append(f"{tag}: fragment absent de la composition")
                continue
            spec = by_expected.get(str(e.get("path")))
            if spec is None or str(f.get("status", "")).startswith("BLOCKED"):
                fails.append(f"{tag}: fragment hors voie HD (non listé dans assets/hd/prompts/manifest.json ou bloqué)")
                continue
            target = f["bbox_px"]["w"] / f["bbox_px"]["h"]
            if abs(iw / ih - target) / target > tol:
                fails.append(f"{tag}: ratio {iw/ih:.4f} ≠ grille {target:.4f} (tolérance {tol:.0%})")
            # width after centre-crop to the grid ratio, compared with the per-format minimum widths
            cw = iw if iw / ih <= target else int(round(ih * target))
            below = [fmt for fmt, px in spec["min_width_px"].items() if cw < px]
            if "A5" in below:
                fails.append(f"{tag}: {cw} px < {spec['min_width_px']['A5']} px requis au gate {spec['gate_ppi']:.0f} ppi en A5")
            elif below:
                warns.append(f"{tag}: sous gate en {', '.join(below)} ({cw} px)")
            if e.get("prompt_sha256") and e.get("prompt_sha256") != spec["prompt_sha256"]:
                warns.append(f"{tag}: le prompt a changé depuis la génération ({e.get('prompt_id')})")
            if e.get("status") == "APPROVED":
                counts["approved"] += 1
                if not e.get("approved_by") or not e.get("approved_on"):
                    fails.append(f"{tag}: APPROVED exige approved_by et approved_on")
                if e.get("rights") not in ACCEPTED_RIGHTS:
                    fails.append(f"{tag}: APPROVED exige rights ∈ {sorted(ACCEPTED_RIGHTS)} (actuel {e.get('rights')!r})")
                if spec["route"].endswith("caption_to_canon") and not e.get("caption_resolution"):
                    fails.append(f"{tag}: fragment à légende raster — caption_resolution obligatoire avant APPROVED")
    for img in sorted((ROOT / "assets/hd").glob("page-*/*")):
        if img.suffix.lower() in {".png", ".jpg", ".jpeg"} and str(img.relative_to(ROOT)) not in declared:
            warns.append(f"orphelin non déclaré : {img.relative_to(ROOT)} (lancer make hd-ingest)")
    for w in warns:
        print(f"WARN [hd] {w}")
    if fails:
        print("HD SOURCES CHECK FAILED")
        for f in fails:
            print(f" - {f}")
        sys.exit(1)
    print(f"HD SOURCES CHECK OK ({counts['declared']} déclarée(s), {counts['approved']} approuvée(s))")


if __name__ == "__main__":
    main()
