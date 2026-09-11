#!/usr/bin/env python3
"""Contrôle du registre des armoiries communales (assets/heraldry/communes/COMMUNES.yaml).

Échoue si : statut inconnu ; entrée VERIFIED ou VERIFIED_CREDITS_PENDING sans fichier SVG, SHA-256
exact, licence, auteur, URL source, blasonnement et sa source, vérificateur et date ; droits non
acceptés ; entrée VERIFIED sous droits ATTRIBUTION_SHAREALIKE dont la ligne de crédit n'est pas
inscrite au canon (pages/NN.yaml:canonical_text) ; SVG non rendu par cairosvg ; entrée liée au
registre documentaire du propriétaire (assets/svg/blasons/REGISTRY.yaml) dont le chemin ou le
SHA-256 diverge ; composition `communal_arms` visant une commune absente ou un fragment inexistant.
Avertit pour les communes non actives référencées par une composition (armes seigneuriales
conservées) et pour les fichiers SVG d'armoiries non déclarés.
"""
from pathlib import Path
import hashlib
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "assets/heraldry/communes/COMMUNES.yaml"
ACCEPTED_RIGHTS = {"CLEARED", "PROJECT_INTERNAL", "ASSOCIATION_PROVIDED", "ATTRIBUTION_SHAREALIKE"}
CREDIT_REQUIRED_RIGHTS = {"ATTRIBUTION_SHAREALIKE"}
PROVENANCE_FIELDS = ("svg", "sha256", "licence", "author", "source_url", "blazon", "blazon_source", "verified_by", "verified_on")
ACTIVE_STATUS = "VERIFIED"
PENDING_CREDITS_STATUS = "VERIFIED_CREDITS_PENDING"
SVG_DIRS = ("assets/heraldry/communes", "assets/svg/blasons")


def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def credit_inscribed_in_canon(credit_line, root=ROOT):
    """Return the list of page numbers whose canonical_text contains credit_line verbatim (whitespace-normalised)."""
    needle = _norm(credit_line)
    if not needle:
        return []
    pages = []
    for p in sorted((root / "pages").glob("[0-9][0-9].yaml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if needle in _norm(d.get("canonical_text")):
            pages.append(int(p.stem))
    return pages


def credit_gate_error(entry):
    """None when the entry may be composed as far as attribution is concerned, else the reason."""
    if entry.get("rights") not in CREDIT_REQUIRED_RIGHTS:
        return None
    if not entry.get("credit_line"):
        return "droits ATTRIBUTION_SHAREALIKE sans credit_line"
    if not credit_inscribed_in_canon(entry["credit_line"]):
        return f"ligne de crédit non inscrite au canon (pages/NN.yaml:canonical_text) : {entry['credit_line']!r}"
    return None


def main():
    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    statuses = set(reg.get("status_enum") or [])
    fails, warns, active, pending, declared_files = [], [], 0, 0, set()
    owner_reg_path = ROOT / str(reg.get("owner_registry") or "")
    owner_assets = {}
    if reg.get("owner_registry"):
        if not owner_reg_path.exists():
            fails.append(f"owner_registry introuvable : {reg['owner_registry']}")
        else:
            for c in (yaml.safe_load(owner_reg_path.read_text(encoding="utf-8")) or {}).get("communes") or []:
                if c.get("asset"):
                    owner_assets[str(c.get("insee"))] = c["asset"]
    for slug, e in (reg.get("communes") or {}).items():
        st = e.get("status")
        if st not in statuses:
            fails.append(f"{slug}: statut inconnu {st!r}")
        if e.get("svg"):
            declared_files.add(str(e["svg"]))
        if st not in (ACTIVE_STATUS, PENDING_CREDITS_STATUS):
            continue
        for k in PROVENANCE_FIELDS:
            if not e.get(k):
                fails.append(f"{slug}: {st} exige {k}")
        if e.get("rights") not in ACCEPTED_RIGHTS:
            fails.append(f"{slug}: rights {e.get('rights')!r} non accepté ({sorted(ACCEPTED_RIGHTS)})")
        svg = ROOT / str(e.get("svg") or "")
        if not e.get("svg") or not svg.exists():
            fails.append(f"{slug}: fichier SVG manquant ({e.get('svg')})")
            continue
        got = sha256(svg)
        if got != e.get("sha256"):
            fails.append(f"{slug}: SHA-256 du SVG différent de l'entrée")
        owner = owner_assets.get(str(e.get("insee")))
        if owner is not None:
            if str(owner.get("path")) != str(e.get("svg")):
                fails.append(f"{slug}: chemin SVG différent du registre du propriétaire ({owner.get('path')})")
            if str(owner.get("sha256")) != got:
                fails.append(f"{slug}: SHA-256 différent du registre du propriétaire")
        try:
            import cairosvg
            cairosvg.svg2png(url=str(svg), output_width=64)
        except Exception as exc:  # noqa: BLE001
            fails.append(f"{slug}: SVG non rendu par cairosvg ({exc})")
        gate = credit_gate_error(e)
        if st == ACTIVE_STATUS:
            if gate:
                fails.append(f"{slug}: VERIFIED mais {gate}")
            else:
                active += 1
        else:
            pending += 1
            warns.append(f"{slug}: {PENDING_CREDITS_STATUS} — {gate or 'crédit à inscrire au canon'} ; armes seigneuriales conservées")
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
        if e.get("status") != ACTIVE_STATUS:
            warns.append(f"page {comp['page']:02d}: armoiries de {e.get('name')} non actives ({e.get('status')}) — armes seigneuriales conservées")
    for d in SVG_DIRS:
        for f in sorted((ROOT / d).glob("*.svg")):
            if str(f.relative_to(ROOT)) not in declared_files:
                warns.append(f"fichier non déclaré : {f.relative_to(ROOT)}")
    for w in warns:
        print(f"WARN [heraldry] {w}")
    if fails:
        print("HERALDRY CHECK FAILED")
        for f in fails:
            print(f" - {f}")
        sys.exit(1)
    print(f"HERALDRY CHECK OK ({len(reg.get('communes') or {})} communes, {active} active(s), {pending} en attente de crédit)")


if __name__ == "__main__":
    main()
