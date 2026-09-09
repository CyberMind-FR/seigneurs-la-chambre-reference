# Phase C — régénération HD des croquis par prompts (grilles inchangées)

## Statut

**CIRCUIT LIVRÉ le 2026-09-09** (gkerma : « Go, régénère les croquis en HD » puis proposition de
passer par des prompts ChatGPT pour les croquis et le fond, sans modifier les grilles).
**Aucune image HD n'est encore produite** : l'environnement de travail n'a pas d'outil de
génération d'images. Le dépôt contient désormais tout ce qu'il faut pour générer, déposer,
contrôler et composer les images HD, la génération elle-même se faisant dans ChatGPT.

## 1. Décision de méthode

Le dépôt ne contenait ni sources HD ni prompts : les croquis n'existent que dans les pages
canoniques (`assets/page-NN.jpg`, 1024 × 1536 px, 181–186 ppi à la taille A5). La régénération
se fait donc **par reconstitution guidée par référence** : pour chaque fragment, ChatGPT reçoit le
crop canonique brut (même sujet, même cadrage, même composition) et un prompt dérivé du dépôt.
La grille (`composition.yaml`, bboxes, couches, texte, QR) n'est pas modifiée : la source HD est
déclarée à côté, dans `prototypes/page-NN/hd-sources.yaml`, et le compositeur la recadre au
centre au ratio exact de la bbox, sans jamais l'agrandir.

Ce que ce circuit couvre, et ce qu'il exclut :

| Voie | Fragments | Pourquoi |
|---|---|---|
| Prompt image (ChatGPT) | 91 illustrations et détails documentaires + le fond de page | sujets artistiques, déjà des reconstitutions ; la référence garantit la composition |
| dont légende raster à inscrire au canon d'abord | 35 fragments `*_captioned` | la légende raster disparaît avec le fragment ; elle doit exister dans `pages/NN.yaml` (ou être abandonnée par décision éditoriale) avant approbation |
| Jamais par génération d'image | 17 armoiries/blasons, 12 cartes et plans, 68 ornements, 43 icônes, 19 textes raster/cartouches/logo, 3 couvertures d'ouvrages, QR | contenu documentaire, héraldique ou textuel : SVG d'après blasonnement officiel, redessin vectoriel d'après source, couche texte, fichier de l'association, droits, registre QR |

Le fragment `P10-chronology_box_captioned` (texte + pictogrammes) est exclu de la voie image
(couche texte + icônes SVG). Le plan réel de la page 10 reste l'autorité géométrique.

## 2. Livrables

| Fichier | Rôle |
|---|---|
| `assets/hd/briefs.yaml` | 95 briefs d'observation (sujet visible, éléments à ne pas reproduire, contraintes, exclusions) + style commun + mention illustrations (proposition) |
| `scripts/hd_prompt_pack.py` (`make hd-prompts`, `make hd-pack`, `--check`) | génère `assets/hd/prompts/STYLE.md`, `page-NN.md`, `manifest.json` ; avec `--pack`, `dist/hd-pack/` + zip (crops de référence bruts, non upscalés) |
| `assets/hd/prompts/` | 91 prompts committés (ratio, canevas natif conseillé, minima px par format, couverture des gates, SHA du prompt) |
| `scripts/hd_ingest.py` (`make hd-ingest`) | inscrit les PNG déposés dans `assets/hd/page-NN/` dans `hd-sources.yaml` (PENDING_REVIEW, SHA-256, taille, prompt) ; ne modifie jamais `composition.yaml` ; n'approuve jamais |
| `scripts/hd_check.py` (`make hd-check`, dans `make validate`) | prompts à jour, fichiers, SHA, ratio (3 %), gates par format, statuts/droits/approbations, `caption_resolution`, orphelins |
| `scripts/layered_compose.py` | source HD `APPROVED` → remplace le crop (recadrage centré, aucun masque, aucun upscale, SHA vérifié, identité HD dans `fragments.lock.yaml`) ; fond de page optionnel (`background`, `cover`/`tile`) |
| `scripts/layered_inventory.py`, `scripts/register_layered.py` | provenance `hd_regeneration`, compteur `hd_regenerated_fragments` |
| `assets/hd/README.md` | contrat et cycle |

## 3. Inventaire des prompts

| Page | Prompts | dont légende raster à inscrire au canon |
|---|---:|---:|
| 01 | 5 | 4 |
| 02 | 8 | 8 |
| 03 | 10 | 6 |
| 05 | 5 | 3 |
| 06 | 7 | 3 |
| 07 | 7 | 4 |
| 08 | 5 | 2 |
| 09 | 4 | 1 |
| 10 | 4 | 1 |
| 11 | 5 | 2 |
| 12 | 7 | 1 |
| 13 | 3 | 0 |
| 14 | 6 | 0 |
| 15 | 14 | 0 |
| 16 | 1 | 0 |
| **Total** | **91** | **35** |

## 4. Gates et tailles

Gates inchangés : 300 ppi demi-teintes, 1200 ppi trait, à la taille de placement finale de chaque
format. Les tailles natives connues de la génération ChatGPT plafonnent à 1536 px de grand côté.
Au canevas natif, après recadrage au ratio de la grille :

| Format | Fragments couverts sans agrandissement | Non couverts |
|---|---:|---:|
| A5 | 86 / 91 | 5 (`P08-hero_captioned`, `P09-hero`, `P12-network_panorama_captioned`, `P13-bottom_band`, `P16-landscape`) |
| A4 | 79 / 91 | 12 |
| A2 | 66 / 91 | 25 |
| A1 | 51 / 91 | 40 |

Chaque prompt demande « la plus grande taille disponible » : si l'outil produit plus grand que
1536 px, la couverture s'améliore d'autant. Une source HD n'est **jamais** agrandie par le
pipeline ; un format non couvert reste rapporté sous gate (`hd_source_below_gate`), et
l'upscale provisoire ne s'applique pas aux sources HD. Tant qu'un fragment n'a pas de source HD
approuvée, son crop canonique (upscale provisoire déclaré) reste utilisé : la migration est
progressive, page par page, fragment par fragment.

## 5. Test du circuit (2026-09-09, sans image générée)

Image synthétique (crop canonique ré-échantillonné ×4, ratio décalé de 2 %) déclarée pour
`P05-localization_vignette` dans un répertoire de travail non committé :

- `PENDING_REVIEW` → crop canonique conservé, information `hd_source_pending` ;
- `APPROVED` → source HD utilisée, recadrage centré (décalage 10 px), 743 ppi A5, `upscale_provisional: false` ;
- SHA-256 altéré → arrêt du compositeur (`HD source SHA mismatch`).

`make validate` (avec `hd-check`) : voir le rapport de PR.

## 5 bis. Mise à jour du 2026-09-09 — légendes inscrites au canon

Les 35 légendes raster ont été inscrites au canon et composées en couche texte
(`CANON_AMENDMENT_CAPTIONS_2026_09_09.md`). Les 35 fragments sont désormais en voie `prompt_image`
(`caption_in_canon: true` dans `assets/hd/prompts/manifest.json`) : leur approbation HD n'exige
plus `caption_resolution`. Le point 1 ci-dessous est donc réglé, sous réserve de relecture.

## 6. Décisions attendues du propriétaire

1. **Légendes raster → canon** : 35 fragments `*_captioned`. Les textes visibles sont transcrits
   par observation dans `assets/hd/briefs.yaml` (champ `remove`) et dans les notes des
   compositions ; ce sont des PROPOSITIONS à valider avant inscription dans `pages/NN.yaml`
   (amendement de canon, `corrections.yaml`). Sans cela, ces 35 illustrations ne peuvent pas être
   approuvées en HD (contrôle `caption_resolution`).
2. **Droits des images générées** : `rights` doit être déclaré à l'approbation (`PROJECT_INTERNAL`
   si les conditions d'utilisation du compte de génération le permettent — à confirmer par le
   propriétaire ; l'index de provenance ne présume rien).
3. **Mention sur les illustrations** : formulation proposée dans `briefs.yaml:style.label_fr`,
   à valider et à inscrire au canon (point ouvert depuis la RC1).
4. **Poids du dépôt** : 91 PNG HD ≈ 2–4 Mo chacun. Recommandation : Git LFS pour `assets/hd/`
   (`.gitattributes`) avant le premier dépôt massif ; non activé ici (décision d'infrastructure).
5. **Fond de page** : optionnel ; le fond par défaut reste la couleur unie `#fffdf7`.
6. **Ordre conseillé** : pages sans légende raster d'abord (13, 14, 15, 16), puis la famille site.
