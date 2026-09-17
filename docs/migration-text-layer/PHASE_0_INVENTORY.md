# Phase 0 — audit et inventaire

## Périmètre et preuves

Checkout audité : `f31480874023e32b04c88d8160a46a944938c9a4`. La commande `git fetch origin main && git rev-parse HEAD && git rev-parse origin/main` a retourné deux fois ce SHA.

Les 16 SHA256 réels concordent avec `manifest.yaml`, `manifest-pages.json` et `pages/NN.yaml`. Le script d'inventaire a retourné `True True` pour chaque page 1 à 16. Les deux manifestes contiennent chacun 16 entrées et les couples `file`/`sha256` concordent 16 fois sur 16.

Méthodes :

- `words`, `chars`, `paras`, dimensions, octets, ratios et ppi : extraction Python depuis les YAML et JPEG ;
- `zones visuelles` et `candidats vecteur` : comptage manuel sur une planche 4 × 4 rendue depuis les 16 JPEG ; ce sont des unités de travail, pas une reconnaissance sémantique automatique ;
- ppi : minimum des deux axes à la taille physique, sans recadrage ;
- QR : comptage de `qr_registry.yaml`.

## Inventaire par page

| p. | type | mots | car. | § | zones visuelles* | candidats SVG* | QR | raster | ratio | ppi A5 | ppi A4 | ppi A2 | ppi A1 | décision de réemploi |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | cover | 49 | 336 | 5 | 9 | 6 | 0 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 2 | history | 571 | 3616 | 8 | 8 | 5 | 0 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 3 | site | 466 | 3054 | 6 | 9 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 4 | site | 316 | 1919 | 7 | 8 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | **bloquée : conflit éditorial** |
| 5 | site | 268 | 1752 | 6 | 8 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 6 | site | 295 | 1911 | 6 | 8 | 4 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 7 | site | 274 | 1795 | 6 | 9 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 8 | site | 258 | 1664 | 6 | 8 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 9 | site | 97 | 688 | 4 | 7 | 5 | 1 | 1024×1536 | 0,6667 | 175,7 | 123,9 | 61,9 | 43,8 | référence visuelle seulement |
| 10 | site | 502 | 3174 | 7 | 8 | 6 | 1 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | plan distinct présent, autres visuels absents |
| 11 | site | 125 | 808 | 4 | 8 | 5 | 1 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | référence visuelle seulement |
| 12 | site | 282 | 1977 | 6 | 10 | 6 | 1 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | référence visuelle seulement |
| 13 | synthesis | 187 | 1422 | 6 | 6 | 15 | 6 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | référence visuelle ; QR réutilisables par payload |
| 14 | association | 181 | 1276 | 1 | 11 | 6 | 0 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | référence visuelle seulement |
| 15 | back_cover | 165 | 1183 | 1 | 14 | 8 | 0 | 1055×1491 | 0,7076 | 180,3 | 127,5 | 63,8 | 45,0 | référence visuelle seulement |
| 16 | page_finale** | 76 | 492 | 6 | 4 | 3 | 1 | 768×1024 | 0,7500 | 123,9 | 87,6 | 43,8 | 30,9 | référence visuelle seulement |

\* Comptage manuel de zones à retrouver, détourer ou redessiner en vecteur après autorisation ; une zone peut contenir plusieurs objets.
\** `pages/16.yaml` porte `role: page_finale`, sans clé `type`.

## Actifs réellement séparés

| classe | mesure | réemploi |
|---|---:|---|
| pages aplaties | 16 JPEG, 17,9 Mo au total | référence de composition uniquement ; texte pixel interdit dans la cible |
| QR bitmap | 16 PNG ; 17 placements ; 16 payloads uniques | payloads réutilisables ; PNG remplacés au build par SVG déterministe |
| source visuelle distincte | 1 fichier : `assets/reference/page-10-plan-reel.jpg`, 520×256, 30 602 octets | géométrie de référence ; résolution et droits insuffisamment documentés |
| illustrations/photos distinctes | 0 dans `assets/illus/` ou `assets/photos/` | manquantes |
| vecteurs distincts | 0 dans `assets/vector/` | manquants |
| fontes versionnées | 0 | manquantes |
| licences de fontes | 0 | manquantes |

`manifest.yaml` ne contient que `page`, `file` et `sha256`. Aucun champ de provenance, licence ou droit de diffusion n'y est présent. Le fichier de référence de la page 10 et les QR n'y sont pas enregistrés.

### Inventaire des actifs QR distincts

| usage | actif courant | octets | cible v2 |
|---|---|---:|---|
| p. 3 navigation | `assets/qr/page-03-google-maps.png` | 2207 | SVG généré depuis `03/google_maps` |
| p. 4 navigation | `assets/qr/page-04-google-maps.png` | 2171 | page bloquée ; payload conservé |
| p. 5 navigation | `assets/qr/page-05-google-maps.png` | 2195 | SVG généré depuis `05/google_maps` |
| p. 6 navigation | `assets/qr/page-06-google-maps.png` | 2208 | SVG généré depuis `06/google_maps` |
| p. 7 navigation | `assets/qr/page-07-google-maps.png` | 1848 | SVG généré depuis `07/google_maps` |
| p. 8 navigation | `assets/qr/page-08-google-maps.png` | 2192 | SVG généré depuis `08/google_maps` |
| p. 9 navigation | `assets/qr/page-09-google-maps.png` | 1847 | SVG généré depuis `09/google_maps` |
| p. 10 navigation | `assets/qr/page-10-google-maps.png` | 2197 | SVG généré depuis `10/google_maps` |
| p. 11 navigation | `assets/qr/page-11-google-maps.png` | 2221 | SVG généré depuis `11/google_maps` |
| p. 12 navigation | `assets/qr/page-12-google-maps.png` | 1866 | SVG généré depuis `12/google_maps` |
| p. 13 association, réutilisé p. 16 | `assets/qr/page-13-01-association.png` | 1850 | un SVG, deux placements |
| p. 13 vidéos | `assets/qr/page-13-02-videos.png` | 3303 | SVG généré depuis `13/videos` |
| p. 13 visite virtuelle | `assets/qr/page-13-03-virtual_visit.png` | 2200 | SVG généré depuis `13/virtual_visit` |
| p. 13 Fondation | `assets/qr/page-13-04-fondation.png` | 2919 | SVG généré depuis `13/fondation` |
| p. 13 commune | `assets/qr/page-13-05-commune.png` | 2206 | SVG généré depuis `13/commune` |
| p. 13 documents | `assets/qr/page-13-06-documents.png` | 2477 | SVG généré depuis `13/documents` |

Le registre contient 17 placements parce que le même actif/payload `association` est placé en pages 13 et 16. Aucun payload n'est recopié dans ce tableau : le registre reste la seule source fonctionnelle.

## Plafond physique des rasters existants

Largeur maximale à 300 ppi, sans interpolation :

| largeur source | largeur physique maximale |
|---:|---:|
| 1024 px | 86,7 mm |
| 1055 px | 89,3 mm |
| 768 px | 65,0 mm |

À placement relatif inchangé, détourer une illustration ne change pas son ppi effectif. Pour atteindre 300 ppi en A5, les zones des groupes 1024 px et 1055 px devraient être placées à environ 59–60 % de leur largeur relative actuelle ; la page 16 à environ 41 %. Ce n'est donc pas une reproduction à géométrie constante.

Pixels minimaux à 300 ppi :

| format fini | sans fond perdu | avec 3 mm sur chaque bord |
|---|---:|---:|
| A5 | 1749×2481 | 1819×2552 |
| A4 | 2481×3508 | 2552×3579 |
| A2 | 4961×7016 | 5032×7087 |
| A1 | 7016×9934 | 7087×10004 |

Le fond perdu de 3 mm est une hypothèse de spécification à faire confirmer par l'imprimeur, pas une donnée canonique existante.

## Voies A/B/C et charge

Hypothèses de chiffrage, exprimées en heures de production et non en devis :

- A = `4 + 0,75 × zones + 0,50 × vecteurs` ; recherche, contrôle de droits, préparation et composition ;
- B = `4 + 1,75 × zones + 0,75 × vecteurs` ; détourage/nettoyage déterministe et composition ;
- C = `6 + 5 × zones + 2 × vecteurs` ; nouvelle prise de vue, numérisation ou dessin vectoriel documenté et composition ;
- intervalle = 75 % à 150 % du point central ; attente d'archives, déplacements, acquisition de droits et validation de la Commission exclus.

| p. | A — sources originales | B — extraction assistée | C — refonte authentique |
|---:|---:|---:|---:|
| 1 | 10–21 h | 18–36 h | 47–94 h |
| 2 | 9–19 h | 16–33 h | 42–84 h |
| 3 | 10–20 h | 18–35 h | 46–92 h |
| 4 | **bloquée** | **bloquée** | **bloquée** |
| 5 | 9–19 h | 16–33 h | 42–84 h |
| 6 | 9–18 h | 16–32 h | 40–81 h |
| 7 | 10–20 h | 18–35 h | 46–92 h |
| 8 | 9–19 h | 16–33 h | 42–84 h |
| 9 | 9–18 h | 15–30 h | 38–76 h |
| 10 | 10–20 h | 17–34 h | 44–87 h |
| 11 | 9–19 h | 16–33 h | 42–84 h |
| 12 | 11–22 h | 20–39 h | 51–102 h |
| 13 | 12–24 h | 19–39 h | 50–99 h |
| 14 | 11–23 h | 21–42 h | 55–110 h |
| 15 | 14–28 h | 26–52 h | 69–138 h |
| 16 | 6–13 h | 10–20 h | 24–48 h |
| **total hors p. 4** | **150–300 h** | **262–524 h** | **677–1354 h** |

Ces fourchettes sont des estimations paramétriques fondées sur 127 zones visuelles et 89 candidats vectoriels, pas des temps observés. Aucun coût monétaire n'est calculable sans tarif, droits et choix A/B/C.

## Défauts de référentiel constatés, non corrigés ici

| preuve | constat | effet sur la migration |
|---|---|---|
| `make validate` → code 2 | `REFERENCE VALIDATION FAILED` avant le contrôle QR | une branche de migration ne peut pas être déclarée verte tant que `main` reste ainsi |
| `git ls-files` | 21 PDF, 4 planches contact, 7 notes historiques ; les PDF suivis totalisent environ 490 MiB | contraire à la règle « artefacts hors dépôt » |
| `build-config.yaml` | `render.background: '#F5E8CE'` | contredit `style.yaml` et `corrections.yaml`, qui imposent le blanc neutre |
| `build-config.yaml` | `sequential_16` et `booklet_a5` activés tous deux en A5/16 pages | risque de sortie dupliquée |
| `corrections.yaml` | pas de clé `page_04_divergence` ; seulement `page_04: canonical_override` | le conflit historique n'est pas représenté comme blocage explicite dans le fichier courant |
| inventaire | aucun dossier `fonts/`, `assets/illus/`, `assets/photos/`, `assets/vector/` | sources de migration absentes |

Aucun de ces écarts n'a été modifié dans les phases 0–1.

## Conflit page 4

Le YAML affirme notamment : construction au XIIIe siècle ; propriété du comte de Savoie ; vente par Guilemet au comte Amé le 14 novembre 1285 pour 340 florins ; vente par le duc Louis à Aymon de La Chambre le 22 décembre 1456.

L'OCR anglais du raster, exécuté par `tesseract assets/page-04.jpg stdout -l eng --psm 3`, lit notamment : titre « Centre seigneurial de La Chambre (XIe–XVIe siècle) » ; édification attribuée à Pierre Ier de La Chambre ; intervention d'Antonio Formigine ; habitation privée jusqu'en 1902 ; classement Monument historique en 1943 ; plan schématique et liste architecturale. Les erreurs diacritiques de cet OCR ne sont pas utilisées pour corriger le contenu.

Verdict : divergence structurelle confirmée. La page 4 reste hors recomposition jusqu'à décision écrite de la Commission.
