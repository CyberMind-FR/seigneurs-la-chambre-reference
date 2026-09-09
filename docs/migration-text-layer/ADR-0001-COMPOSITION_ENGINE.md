# ADR-0001 — moteur de composition

- Statut : **proposé pour validation humaine**
- Date : 2026-09-08
- Décision : **WeasyPrint 69.0 piloté par Python/PyYAML**
- Portée : choix technique de phase 1 ; aucune page canonique recomposée

## Cas d'essai

Une page A5 représentative de type `site` a été construite hors dépôt depuis `pages/11.yaml`, avec : titre, sous-titre, texte canonique complet, grille à deux colonnes, deux zones vectorielles, fond perdu de 3 mm et QR SVG généré par Segno depuis le payload exact de `qr_registry.yaml`.

Le test ne constitue pas le prototype de phase 2 : aucune illustration n'a été extraite et aucune comparaison de fidélité avec la page 11 n'a été acceptée.

Environnement mesuré :

```text
Python 3.12.13
typst (module Python) 0.15.0
WeasyPrint 69.0
LuaHBTeX 1.17.0 / LaTeX2e 2023-11-01
Ghostscript 10.02.1
Inkscape 1.2.2
Node 24.19.0
```

`context`, `scribus`, `pagedjs-cli` et un navigateur Chromium ne sont pas présents. `lualatex` est présent, mais `luaotfload-main` manque.

## Résultats bruts synthétiques

| contrôle | Typst 0.15 | WeasyPrint 69 | LuaLaTeX |
|---|---:|---:|---|
| compilation page représentative | 0,037–0,045 s | 0,603–0,614 s | échec à 0,258–0,299 s |
| PDF produit | 31 048 octets | 18 177 octets | aucun |
| pages | 1 | 1 | aucun |
| texte extrait vs canon | exact après suppression des césures discrétionnaires | exact après suppression des césures discrétionnaires | non vérifiable |
| fontes | 2 sous-ensembles CID TrueType, embarqués, Unicode | 3 sous-ensembles CID TrueType, embarqués, Unicode | non vérifiable |
| images raster dans le PDF de test | 0 (`pdfimages -list`) | 0 (`pdfimages -list`) | non vérifiable |
| QR | SVG placé comme vecteur ; payload source contrôlé exact | SVG placé comme vecteur ; payload source contrôlé exact | non vérifiable |
| redécodage QR depuis le PDF | non vérifié : aucun décodeur disponible dans l'environnement de test | idem | non vérifiable |
| PDF bit-identique avec horodatage fixé | oui, 2/2 SHA identiques | oui en PDF normal, 2/2 SHA identiques | non vérifiable |
| PDF/X-4 bit-identique avec `SOURCE_DATE_EPOCH=0` | non applicable | non, 2 SHA différents | non vérifiable |

Normalisation du contrôle texte : `U+00AD` et le blanc qui suit une césure discrétionnaire sont retirés, puis les blancs sont compactés. Le résultat contient 805 caractères dans la source et 805 après extraction pour les deux moteurs.

La première tentative Typst a échoué avec `unexpected argument: orphan-penalty`. La documentation de `par` ne contient ni paramètre `orphan` ni `widow`. La première tentative LuaLaTeX a échoué avec :

```text
module 'luaotfload-main' not found
Font ... lmroman10-regular ... not loadable
Fatal error occurred, no output PDF file produced
```

## Typographie et composition

Typst et WeasyPrint ont tous deux rendu : grille, encadré, colonnes, texte justifié, fonte embarquée et SVG. Typst active la césure selon `text(lang: "fr")` et propose un algorithme de rupture optimisé ; sa propre documentation relie explicitement langue, motifs de césure et justification. Il ne fournit cependant pas le contrôle direct des veuves/orphelines demandé ici. Voir la [documentation Typst des paragraphes](https://typst.app/docs/reference/model/par/) et du [texte multilingue](https://typst.app/docs/reference/text/text/).

WeasyPrint a exécuté `hyphens:auto`, `orphans:3`, `widows:3`, CSS Grid, colonnes et position fixe dans le test. Sa documentation annonce la prise en charge de `@page`, `bleed` et `marks`. Voir la [référence WeasyPrint 69](https://doc.courtbouillon.org/weasyprint/v69.0/api_reference.html).

La qualité visuelle définitive, l'approche et le choix des fontes restent **non vérifiés** : DejaVu Serif/Sans ne servaient qu'au banc et ne sont pas une décision graphique.

## Fond perdu, traits de coupe et boîtes PDF

| moteur | mesure | frontière retenue |
|---|---|---|
| Typst | `MediaBox 436,54×612,28 pt`, `TrimBox` décalée de 8,50 pt sur chaque bord | fond perdu natif confirmé ; aucun mécanisme natif de traits de coupe trouvé/testé |
| WeasyPrint | mêmes dimensions ; `TrimBox 419,53×595,28 pt` ; traits de coupe et croix visibles au rendu | `@page { bleed:3mm; marks:crop cross }` retenu |
| LuaLaTeX | paquet `crop.sty` trouvé, mais aucun PDF compilé | non retenu sans image CI réparée |

Typst documente que `page(bleed: ...)` crée un `TrimBox` lors de l'export PDF : [référence officielle](https://typst.app/docs/reference/layout/page/). WeasyPrint documente nativement les propriétés CSS `size`, `bleed` et `marks` : [référence officielle](https://doc.courtbouillon.org/weasyprint/v69.0/api_reference.html).

## PDF/X, CMYK et ICC

### Typst

- `pdf_standards=['a-2u']` : compilation réussie et `OutputIntent` sRGB mesuré ;
- `pdf_standards=['x-4']` : échec `unknown pdf standard: x-4` ;
- la documentation officielle expose PDF/A et PDF/UA, pas PDF/X : [export PDF Typst](https://typst.app/docs/reference/pdf/).

Conclusion : Typst ne couvre pas seul le fichier imprimeur demandé.

### WeasyPrint

- `--pdf-variant pdf/x-4` : PDF 1.6 produit, métadonnées XMP `PDF/X-4`, groupe de transparence `/DeviceCMYK` ;
- sans profil explicite : aucun `/OutputIntents` dans le catalogue ; ce résultat n'est pas accepté comme fichier imprimeur ;
- avec `@color-profile` pointant sur le profil CMYK de test et `--output-intent=--print-profile` : `/OutputIntents`, `/S /GTS_PDFX` et `/DestOutputProfile` sont présents ;
- le profil de test est `Artifex CMYK SWOP Profile`. Il prouve le mécanisme mais n'est **pas** le profil de production ;
- un JPEG RGB placé reste `/DeviceRGB` et est embarqué sans conversion ;
- un JPEG préconverti CMYK est resté `/DeviceCMYK` et son flux de 3 394 224 octets a été embarqué tel quel.

La documentation WeasyPrint 69 liste PDF/X-1a, X-3, X-4, X-5g, `--output-intent`, `device-cmyk()` et `@color-profile` : [référence officielle](https://doc.courtbouillon.org/weasyprint/v69.0/api_reference.html). La conformité ISO complète n'a pas été validée par un outil de preflight PDF/X dans cet environnement : **non vérifiée**.

### Ghostscript

La conversion testée avec `-sColorConversionStrategy=CMYK -sProcessColorModel=DeviceCMYK` a bien transformé le JPEG en CMYK, mais l'a réencodé de 1 206 572 à 649 Kio et a réécrit le PDF. Cette voie n'est donc pas retenue comme traitement automatique final des photographies.

La documentation Ghostscript impose pour PDF/X un profil ICC et un `OutputCondition`, et décrit les `TrimBox`/`BleedBox` : [documentation officielle](https://ghostscript.readthedocs.io/en/latest/VectorDevices.html). Elle est contradictoire sur PDF/X-4 dans la même page ; la section de procédure n'annonce que X-1/X-3. L'installation 10.02.1 n'est donc pas choisie pour fabriquer le PDF/X-4 maître.

## Chaîne proposée jusqu'à l'imprimeur

1. Python charge et valide YAML, registre QR, manifeste et schéma.
2. Segno génère les QR en SVG, avec payload exact, noir pur, fond blanc et bord de 4 modules.
3. Les sources raster sont normalisées **une fois** vers un dérivé de build correspondant au profil ICC approuvé : CMYK JPEG 4:4:4 pour photo ; TIFF/PNG lossless pour trait fin.
4. WeasyPrint 69 compose HTML/CSS en PDF/X-4 avec `@color-profile`, `--output-intent`, fond perdu et traits de coupe.
5. Les validateurs extraient le texte, mesurent le ppi de chaque image placée, contrôlent fontes et boîtes, rendent chaque QR et le redécodent.
6. Un preflight PDF/X externe nommé par l'imprimeur valide le fichier et le profil. Cette étape reste bloquée tant que l'imprimeur n'a pas fourni profil, fond perdu, standard PDF/X et réglages de noir.
7. L'épreuve contractuelle et le RIP restent chez l'imprimeur.

La conversion colorimétrique n'est pas laissée à un post-traitement aveugle du PDF : elle intervient sur les dérivés d'actifs avant composition, puis WeasyPrint les embarque sans réencodage. Le profil source et le profil de sortie doivent être enregistrés dans le manifeste.

## Matrice de décision

Scores 0–5. Seuls les moteurs ayant produit un PDF sont notés.

| critère | poids | Typst | WeasyPrint | justification mesurée |
|---|---:|---:|---:|---|
| typographie française | 20 % | 3,5 | 4,0 | césure/extraction exactes ; veuves/orphelines absentes de Typst |
| gabarit riche | 15 % | 4,5 | 4,5 | grille, colonnes, encadrés, SVG réussis |
| données structurées | 15 % | 5,0 | 4,0 | YAML natif Typst ; conversion Python requise côté HTML |
| fontes/export | 10 % | 4,0 | 4,5 | fontes embarquées dans les deux ; PDF/X disponible côté WeasyPrint |
| prépresse | 20 % | 2,5 | 4,5 | Typst : bleed seulement ; WeasyPrint : marks, PDF/X, ICC testés |
| reproductibilité | 10 % | 5,0 | 3,5 | bit-identique avec temps fixé ; PDF/X Weasy reste horodaté/aléatoire |
| maintenance solo | 10 % | 4,5 | 4,0 | Typst plus compact ; Weasy réutilise Python et CSS mais ajoute un moteur web |
| **total pondéré** | **100 %** | **3,98** | **4,18** | — |

## Alternatives non retenues

| alternative | état exécuté | décision |
|---|---|---|
| Typst 0.15 | oui | excellente solution de composition, écartée au profit de WeasyPrint pour veuves/orphelines et prépresse natif |
| LuaLaTeX | tentative en échec | non retenu dans l'image actuelle ; réévaluable après installation complète et benchmark identique |
| ConTeXt | binaire absent | non vérifié, non retenu |
| Paged.js | CLI et Chromium absents | non vérifié ; WeasyPrint couvre le candidat HTML/CSS sans navigateur |
| Scribus scripté | binaire absent | non vérifié ; coût de maintenance et sérialisation git non mesurés ici |
| InDesign | non testé | exclu par la contrainte git du projet |

## Conséquences assumées

- dépendances à pinner : Python, PyYAML, WeasyPrint, Pango/Cairo, Segno et profils ICC ;
- le PDF/X de WeasyPrint ne dispense pas du preflight imprimeur ;
- les JPEG RGB ne sont pas magiquement convertis par l'OutputIntent ; les actifs doivent être préparés avant placement ;
- le PDF/X-4 n'est pas bit-reproductible dans le test actuel, car WeasyPrint 69 injecte l'heure et un identifiant XMP malgré `SOURCE_DATE_EPOCH=0` ; un test de reproductibilité sémantique et une normalisation de métadonnées seront nécessaires ;
- aucune fonte de production n'est choisie avant contrôle de licence et validation graphique.
