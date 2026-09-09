#!/usr/bin/env python3
"""Phase C — pack de prompts pour la régénération HD des croquis.

Génère, à partir des compositions (grilles inchangées) et des briefs d'observation
(`assets/hd/briefs.yaml`) :

* `assets/hd/prompts/STYLE.md` et `assets/hd/prompts/page-NN.md` (committés) : un prompt par
  fragment régénérable, avec ratio, taille native conseillée et couverture des gates 300 ppi ;
* `assets/hd/prompts/manifest.json` (committé) : contrat machine (fichier attendu, ratio, px
  minimum par format, sha256 du prompt) lu par `hd_ingest.py` et `hd_check.py` ;
* avec `--pack` : `dist/hd-pack/` (jamais committé) = prompts + crops de référence bruts
  (non upscalés) découpés dans la page canonique + `hd-pack.zip`.

`--check` vérifie que les fichiers committés sont à jour (utilisé par `make validate`).
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import shutil
import sys
import zipfile

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from layered_compose import Geometry, PAGE_SIZES, DEFAULT_PPI_GATES, LINE_ART_ROLES  # noqa: E402

PROMPT_ROLES = {"documentary_illustration", "documentary_illustration_with_canonical_raster_caption",
                "documentary_detail", "documentary_detail_with_canonical_raster_caption"}
ROUTES = {
    "documentary_illustration": "prompt_image",
    "documentary_illustration_with_canonical_raster_caption": "prompt_image_caption_to_canon",
    "documentary_detail": "prompt_image",
    "documentary_detail_with_canonical_raster_caption": "prompt_image_caption_to_canon",
    "ornament": "vector_svg",
    "icon": "vector_svg",
    "heraldry": "vector_svg_official_blazon",
    "heraldry_with_canonical_raster_caption": "vector_svg_official_blazon_caption_to_canon",
    "documentary_map": "documentary_vector_redraw",
    "canonical_raster_text_absent_from_yaml": "editorial_text_to_canon",
    "canonical_raster_caption_absent_from_yaml": "editorial_text_to_canon",
}
# Known native output sizes of ChatGPT image generation (long side 1536 px). If the tool offers
# a larger size, the prompts say to take it: the pipeline never upscales an HD source.
NATIVE_SIZES = {"portrait": (1024, 1536), "landscape": (1536, 1024), "square": (1024, 1024)}
FORMAT_SCALE = {"A5": 1.0, "A4": math.sqrt(2), "A2": 2.0, "A1": 2.0 * math.sqrt(2)}


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_yaml(p):
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


def native_choice(ratio):
    """Closest native canvas for a w/h ratio, and the exact-ratio crop it yields."""
    if ratio >= 1.15:
        name = "landscape"
    elif ratio <= 0.87:
        name = "portrait"
    else:
        name = "square"
    W, H = NATIVE_SIZES[name]
    # centre-crop the native canvas to the fragment ratio
    if W / H > ratio:
        cw, ch = int(H * ratio), H
    else:
        cw, ch = W, int(W / ratio)
    return name, (W, H), (cw, ch)


def fragment_targets(page, comp, frag):
    """Pixel requirements of a fragment at the gate of its kind, per output format."""
    src = Image.open(ROOT / comp["source"]["path"])
    geom = Geometry(src.width, src.height, *PAGE_SIZES["A5"])
    b = frag["bbox_px"]
    dest = frag.get("dest_bbox_px") or b
    _, _, dw_pt, dh_pt = geom.box(dest["x"], dest["y"], dest["w"], dest["h"])
    kind = frag.get("raster_kind") or ("line_art" if frag.get("role") in LINE_ART_ROLES else "continuous_tone")
    gate = DEFAULT_PPI_GATES[kind]
    req = {}
    for fmt, scale in FORMAT_SCALE.items():
        w_in = dw_pt * scale / 72.0
        req[fmt] = int(math.ceil(w_in * gate))
    return {"ratio": round(b["w"] / b["h"], 4), "canonical_px": [b["w"], b["h"]], "dest_pt_a5": [round(dw_pt, 2), round(dh_pt, 2)],
            "raster_kind": kind, "gate_ppi": gate, "min_width_px": req}


def build(briefs):
    style = briefs["style"]
    pages_out, manifest = {}, {"schema_version": 1, "style": style["name"], "fragments": {}, "background": {}}
    for comp_path in sorted((ROOT / "prototypes").glob("page-*/composition.yaml")):
        comp = load_yaml(comp_path)
        page = comp["page"]
        page_briefs = briefs["pages"].get(page, {})
        entries = []
        # captions already inscribed in the canon and composed as live text (text_blocks[].caption_of)
        captioned_in_canon = {tb.get("caption_of") for tb in comp.get("text_blocks", []) if tb.get("caption_of")}
        for f in comp.get("fragments", []):
            role = f.get("role")
            route = ROUTES.get(role, "unknown")
            caption_in_canon = False
            if route == "prompt_image_caption_to_canon" and f["id"] in captioned_in_canon:
                route, caption_in_canon = "prompt_image", True
            brief = page_briefs.get(f["id"])
            if role in PROMPT_ROLES:
                if brief is None:
                    raise SystemExit(f"page {page:02d}: fragment {f['id']} ({role}) has no brief in assets/hd/briefs.yaml")
                if "exclude" in brief:
                    entries.append({"id": f["id"], "role": role, "route": "excluded", "reason": brief["exclude"]})
                    continue
                if f.get("status") != "APPROVED":
                    entries.append({"id": f["id"], "role": role, "route": "excluded", "reason": f"statut {f.get('status')}"})
                    continue
                t = fragment_targets(page, comp, f)
                name, native, crop = native_choice(t["ratio"])
                coverage = {fmt: crop[0] >= px for fmt, px in t["min_width_px"].items()}
                pid = f"P{page:02d}-{f['id']}"
                orientation = {"portrait": "portrait (plus haut que large)", "landscape": "paysage (plus large que haut)", "square": "carré"}[name]
                remove = list(brief.get("remove") or [])
                if route == "prompt_image_caption_to_canon" or caption_in_canon:
                    remove.append("toute légende ou annotation présente dans l'image de référence"
                                  + (" (légende inscrite au canon et composée en couche texte)" if caption_in_canon else ""))
                lines = [
                    "Redessine l'illustration jointe en haute définition, en conservant exactement le même sujet, le même point de vue, le même cadrage et la même composition (mêmes positions des éléments principaux). Ne rajoute aucun élément historique ou architectural absent de la référence.",
                    f"Sujet : {brief['subject']}",
                    f"Style : {style['fr']}",
                    f"À ne pas reproduire : {'; '.join(remove) if remove else 'rien à retirer'}. {style['negative_fr']}",
                    f"Format : {orientation}, ratio largeur/hauteur ≈ {t['ratio']:.2f}. Le sujet doit rester entièrement dans le cadre avec une légère marge de papier crème uni sur les bords (l'image sera recadrée au centre à ce ratio exact, sans agrandissement). Produis la plus grande taille disponible (au minimum {native[0]}×{native[1]} px).",
                ]
                if brief.get("notes"):
                    lines.append(f"Contrainte : {brief['notes']}")
                prompt = "\n".join(lines)
                rec = {"id": f["id"], "role": role, "route": route, "caption_in_canon": caption_in_canon,
                       "prompt_id": pid, "prompt": prompt,
                       "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
                       "expected_file": f"assets/hd/page-{page:02d}/{f['id']}.png",
                       "reference_crop": f"reference/page-{page:02d}/{f['id']}.png",
                       "native_canvas": name, "native_px": list(native), "crop_px_at_native": list(crop),
                       "coverage_at_native": coverage, **t}
                entries.append(rec)
                manifest["fragments"][pid] = {k: v for k, v in rec.items() if k != "prompt"} | {"page": page}
            else:
                entries.append({"id": f["id"], "role": role, "route": route})
        pages_out[page] = entries
    bg = briefs.get("background", {}).get("paper_texture")
    if bg:
        prompt = "\n".join([
            f"Génère une texture de fond : {bg['subject']}",
            f"{style['negative_fr']}",
            "Format : carré, la plus grande taille disponible (au minimum 1024×1024 px). La texture doit être tuilable (bords raccordables) et presque uniforme.",
        ])
        manifest["background"] = {"prompt_id": "BG-paper_texture", "expected_file": "assets/hd/common/paper-texture.png",
                                  "prompt_sha256": sha256_bytes(prompt.encode("utf-8")), "prompt": prompt, "notes": bg.get("notes")}
    return pages_out, manifest


def render_style_md(briefs, manifest):
    s = briefs["style"]
    fr_pages = sorted(manifest_pages(manifest))
    n = len(manifest["fragments"])
    out = [
        "# Prompts HD — style commun et mode d'emploi", "",
        "> Fichier généré par `scripts/hd_prompt_pack.py` depuis `assets/hd/briefs.yaml` et les",
        "> `prototypes/page-NN/composition.yaml` (grilles inchangées). Ne pas éditer à la main :",
        "> modifier les briefs puis `make hd-prompts`.", "",
        f"{n} illustrations régénérables par prompt sur les pages {', '.join(f'{p:02d}' for p in fr_pages)}.", "",
        "## Style commun", "", s["fr"], "", "**Exclusions :** " + s["negative_fr"], "",
        "**Mention à porter dans le livret (formulation à valider) :** " + s["label_fr"], "",
        "## Mode d'emploi (ChatGPT, génération d'images)", "",
        "1. `make hd-pack` produit `dist/hd-pack/` : ce fichier, un `page-NN.md` par page et les crops de",
        "   référence bruts `reference/page-NN/<fragment>.png` (découpés dans la page canonique, sans upscale).",
        "2. Pour chaque fragment : joindre le crop de référence, coller le prompt tel quel, demander la plus",
        "   grande taille disponible. Ne jamais accepter une image comportant du texte.",
        "3. Enregistrer le résultat sous le nom attendu (`assets/hd/page-NN/<fragment>.png`, PNG, sRGB).",
        "4. `make hd-ingest` inscrit chaque fichier dans `prototypes/page-NN/hd-sources.yaml`",
        "   (statut `PENDING_REVIEW`, SHA-256, taille, identifiant et SHA du prompt).",
        "5. Revue humaine : comparer au crop de référence (même sujet, même cadrage, aucun texte, aucun",
        "   ajout), renseigner `rights`, `approved_by`, `approved_on`, passer le statut à `APPROVED`.",
        "   Pour les fragments `*_captioned`, renseigner d'abord `caption_resolution` (légende inscrite au",
        "   canon ou abandon éditorial motivé) : la légende raster disparaît avec le fragment.",
        "6. `make layered-compose` (le compositeur remplace le crop canonique par la source HD, recadrée au",
        "   centre au ratio exact, jamais agrandie), puis `make validate`, `make build-v3`.", "",
        "## Tailles et couverture des gates", "",
        "Les gates sont 300 ppi (demi-teintes) et 1200 ppi (trait) à la taille de placement finale de",
        "chaque format. Les tailles natives connues de ChatGPT plafonnent à 1536 px de grand côté : la",
        "colonne « couverture » de chaque prompt indique les formats atteints sans agrandissement ; un",
        "format non couvert reste sous gate et sera rapporté tel quel (aucun upscale d'une source HD).", "",
    ]
    return "\n".join(out)


def manifest_pages(manifest):
    return {v["page"] for v in manifest["fragments"].values()}


def render_page_md(page, entries, comp):
    title = comp.get("title") or comp.get("canonical_text", {}).get("key") or ""
    out = [f"# Page {page:02d} — prompts HD", "",
           "> Généré par `scripts/hd_prompt_pack.py` — ne pas éditer à la main.", ""]
    prompted = [e for e in entries if e["route"].startswith("prompt_image")]
    others = [e for e in entries if not e["route"].startswith("prompt_image")]
    out += [f"{len(prompted)} illustration(s) à régénérer par prompt ; {len(others)} fragment(s) par une autre voie (voir tableau final).", ""]
    for e in prompted:
        cov = " ".join(f"{fmt} {'✔' if ok else '✘'}(≥{e['min_width_px'][fmt]} px)" for fmt, ok in e["coverage_at_native"].items())
        out += [f"## {e['prompt_id']}", "",
                f"- Fichier attendu : `{e['expected_file']}`",
                f"- Référence à joindre : `{e['reference_crop']}` (crop canonique {e['canonical_px'][0]}×{e['canonical_px'][1]} px)",
                f"- Ratio L/H : {e['ratio']:.4f} — canevas natif conseillé : {e['native_canvas']} {e['native_px'][0]}×{e['native_px'][1]} → recadrage centré {e['crop_px_at_native'][0]}×{e['crop_px_at_native'][1]} px",
                f"- Gate {e['gate_ppi']} ppi ({e['raster_kind']}) — couverture au canevas natif : {cov}",
                ("- Légende raster : à inscrire au canon avant approbation (`caption_resolution`)" if e["route"].endswith("caption_to_canon")
                 else "- Légende raster : inscrite au canon (2026-09-09) et composée en couche texte — ne pas la dessiner" if e.get("caption_in_canon")
                 else "- Sans légende raster"),
                "", "```text", e["prompt"], "```", ""]
    out += ["## Fragments hors voie « prompt image »", "", "| Fragment | Rôle | Voie |", "|---|---|---|"]
    for e in others:
        extra = f" — {e['reason']}" if e.get("reason") else ""
        out.append(f"| `{e['id']}` | `{e['role']}` | `{e['route']}`{extra} |")
    out.append("")
    return "\n".join(out)


def write_outputs(pages_out, manifest, briefs, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    files["STYLE.md"] = render_style_md(briefs, manifest)
    for page, entries in pages_out.items():
        comp = load_yaml(ROOT / f"prototypes/page-{page:02d}/composition.yaml")
        files[f"page-{page:02d}.md"] = render_page_md(page, entries, comp)
    files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return files


def reference_pack(manifest, pack_dir):
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    (pack_dir / "reference").mkdir(parents=True)
    for pid, rec in manifest["fragments"].items():
        comp = load_yaml(ROOT / f"prototypes/page-{rec['page']:02d}/composition.yaml")
        frag = next(f for f in comp["fragments"] if f["id"] == rec["id"])
        b = frag["bbox_px"]
        src = Image.open(ROOT / comp["source"]["path"]).convert("RGB")
        crop = src.crop((b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]))
        dest = pack_dir / rec["reference_crop"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        crop.save(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if committed prompts are stale")
    ap.add_argument("--pack", action="store_true", help="also write dist/hd-pack/ with reference crops and a zip")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    briefs = load_yaml(ROOT / "assets/hd/briefs.yaml")
    pages_out, manifest = build(briefs)
    prompts_dir = ROOT / "assets/hd/prompts"
    files = write_outputs(pages_out, manifest, briefs, prompts_dir)
    if args.check:
        stale = [n for n, c in files.items() if not (prompts_dir / n).exists() or (prompts_dir / n).read_text(encoding="utf-8") != c]
        if stale:
            print("HD PROMPTS STALE: " + ", ".join(stale) + " — run `make hd-prompts`")
            sys.exit(1)
        print(f"HD PROMPTS OK ({len(manifest['fragments'])} prompts, {len(pages_out)} pages)")
        return
    for n, c in files.items():
        (prompts_dir / n).write_text(c, encoding="utf-8")
    print(f"HD PROMPTS WRITTEN ({len(manifest['fragments'])} prompts → {prompts_dir.relative_to(ROOT)})")
    if args.pack:
        pack_dir = ROOT / args.out / "hd-pack"
        reference_pack(manifest, pack_dir)
        for n, c in files.items():
            (pack_dir / n).write_text(c, encoding="utf-8")
        zip_path = ROOT / args.out / "hd-pack.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(pack_dir.rglob("*")):
                if p.is_file():
                    z.write(p, p.relative_to(pack_dir))
        print(f"HD PACK WRITTEN ({pack_dir.relative_to(ROOT)}, {zip_path.relative_to(ROOT)})")


if __name__ == "__main__":
    main()
