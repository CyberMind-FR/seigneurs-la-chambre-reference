#!/usr/bin/env python3
"""Contrôle du registre des armoiries communales (assets/heraldry/communes/COMMUNES.yaml).

Échoue si : statut inconnu ; entrée VERIFIED sans fichier SVG, SHA-256 exact, licence, auteur,
URL source, blasonnement et sa source, vérificateur et date, droits acceptés ; SVG non rendu par
cairosvg ; composition `communal_arms` visant une commune absente ou un fragment inexistant.
Avertit pour les communes non vérifiées référencées par une composition (armes seigneuriales
conservées) et pour les fichiers de assets/heraldry/communes/ non déclarés.
"""
from pathlib import Path
import hashlib
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "assets/heraldry/communes/COMMUNES.yaml"
ACCEPTED_RIGHTS = {"CLEARED", "PROJECT_INTERNAL", "ASSOCIATION_PROVIDED"}


def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    statuses = set(reg.get("status_enum") or [])
    fails, warns, verified, declared_files = [], [], 0, set()
    for slug, e in (reg.get("communes") or {}).items():
        st = e.get("status")
        if st not in statuses:
            fails.append(f"{slug}: statut inconnu {st!r}")
        if e.get("svg"):
            declared_files.add(str(e["svg"]))
        if st != "VERIFIED":
            continue
        verified += 1
        for k in ("svg", "sha256", "licence", "author", "source_url", "blazon", "blazon_source", "verified_by", "verified_on"):
            if not e.get(k):
                fails.append(f"{slug}: VERIFIED exige {k}")
        if e.get("rights") not in ACCEPTED_RIGHTS:
            fails.append(f"{slug}: rights {e.get('rights')!r} non accepté ({sorted(ACCEPTED_RIGHTS)})")
        svg = ROOT / str(e.get("svg") or "")
        if not e.get("svg") or not svg.exists():
            fails.append(f"{slug}: fichier SVG manquant ({e.get('svg')})")
            continue
        if sha256(svg) != e.get("sha256"):
            fails.append(f"{slug}: SHA-256 du SVG différent de l'entrée")
        try:
            import cairosvg
            cairosvg.svg2png(url=str(svg), output_width=64)
        except Exception as exc:  # noqa: BLE001
            fails.append(f"{slug}: SVG non rendu par cairosvg ({exc})")
    for comp_path in sorted((ROOT / "prototypes").glob("page-*/composition.yaml")):
        comp = yaml.safe_load(comp_path.read_text(encoding="utf-8"))
        arms = comp.get("communal_arms")
        if not arms:
            continue
        e = (reg.get("communes") or {}).get(arms.get("commune"))
        if e is None:
            fails.append(f"page {comp['page']:02d}: communal_arms vise une commune absente du registre ({arms.get('commune')})")
            continue
        if arms.get("replaces_fragment") not in {f["id"] for f in comp.get("fragments", [])}:
            fails.append(f"page {comp['page']:02d}: replaces_fragment {arms.get('replaces_fragment')!r} inexistant")
        if not any(tb.get("requires_communal_arms") for tb in comp.get("text_blocks", [])):
            fails.append(f"page {comp['page']:02d}: aucun bloc texte requires_communal_arms (légende « Armoiries de … »)")
        if e.get("status") != "VERIFIED":
            warns.append(f"page {comp['page']:02d}: armoiries de {e.get('name')} non vérifiées ({e.get('status')}) — armes seigneuriales conservées")
    for f in sorted((ROOT / "assets/heraldry/communes").glob("*.svg")):
        if str(f.relative_to(ROOT)) not in declared_files:
            warns.append(f"fichier non déclaré : {f.relative_to(ROOT)}")
    for w in warns:
        print(f"WARN [heraldry] {w}")
    if fails:
        print("HERALDRY CHECK FAILED")
        for f in fails:
            print(f" - {f}")
        sys.exit(1)
    print(f"HERALDRY CHECK OK ({len(reg.get('communes') or {})} communes, {verified} vérifiée(s))")


if __name__ == "__main__":
    main()
